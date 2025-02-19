"""
delete contributors from HC
"""
import allure
import pytest
from faker import Faker
import pandas as pd

from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, save_file_with_content, \
    get_data_file
from adap.api_automation.services_config.hosted_channel import HC
from adap.ui_automation.utils.pandas_utils import replace_column_in_csv, copy_file_csv, add_data_in_csv, \
    collect_data_from_file, create_updated_csv

faker = Faker()
API_KEY = get_user_api_key('test_hc_account')
TEAM_ID = get_user_team_id('test_hc_account')
CONTRIBUTORS = get_data_file("/hosted_channel/dod_data_58.csv")


def create_channel_with_contributors(api_key, tmpdir=None):
    """
    create new channel and upload list of contributors
    """
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(api_key).create_channel(payload)
    hc_res.assert_response_status(201)

    _channel_id = hc_res.json_response['id']
    new_file = create_updated_csv(CONTRIBUTORS, 'channel_id', _channel_id, (str(_channel_id)+"_temp.csv"), tmpdir)

    hc_res = HC(API_KEY).upload_list_of_contributors(new_file)
    hc_res.assert_response_status(202)

    return {"hc_id": _channel_id, "hc_file": new_file}


@pytest.fixture(scope="module")
def _channel(tmpdir_factory):
    """
    pytest fixture - create new channel
    """
    return create_channel_with_contributors(API_KEY, tmpdir_factory.mktemp("data"))


#  delete list of contributors from hc
@allure.parent_suite('/hosted_channels/{hostedChannelId}:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token'),
                          ("valid_key", get_user_api_key('test_hc_account'), 202, '')])
def test_delete_hc_list_of_contributors_with_api_key(api_key_type, api_key, expected_status, expected_msg, _channel):
    """
    delete contributors from HC
    """
    hc_res = HC(api_key).delete_list_of_contributors(_channel['hc_id'], CONTRIBUTORS)
    hc_res.assert_response_status(expected_status)
    if expected_msg:
        assert hc_res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels/{hostedChannelId}:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('id_type, hc_id, expected_status, expected_msg',
                         [("empty_id", "", 404, ''),
                          ("invalid_id", "12345678qwerty", 400, [{'code': 'INVALID_REQUEST_PARAMETER', 'errors': [
                              {'code': 'INVALID_TYPE', 'message': 'Expected type integer but found type string',
                               'path': []}], 'in': 'path',
                                                                  'message': 'Invalid parameter (hostedChannelId): '
                                                                             'Expected type integer but found type '
                                                                             'string',
                                                                  'name': 'hostedChannelId', 'path': []}]),
                          ("not_exist", 99999, 404, '')])
def test_delete_hc_invalid_channel_id(id_type, hc_id, expected_status, expected_msg):
    """
    delete contributors  for invalid channels
    """
    hc_res = HC(API_KEY).delete_list_of_contributors(hc_id, CONTRIBUTORS)
    hc_res.assert_response_status(expected_status)
    if expected_msg: assert hc_res.json_response['errors'] == expected_msg


@allure.parent_suite('/hosted_channels/{hostedChannelId}:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_delete_hc_invalid_file_type(tmpdir):
    """
    delete contributors from HC with json
    """
    hc_info = create_channel_with_contributors(API_KEY, tmpdir)
    hc_res = HC(API_KEY).delete_list_of_contributors(hc_info['hc_id'], get_data_file("/hosted_channel/test.json"))
    hc_res.assert_response_status(422)
    assert hc_res.json_response['errors'] == ['Unsupported file format']


@allure.parent_suite('/hosted_channels/{hostedChannelId}:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_delete_hc_contributor_is_not_in_channel(tmpdir):
    """
    delete contributor from HC with no invitation
    """
    hc_info = create_channel_with_contributors(API_KEY, tmpdir)
    new_file = hc_info['hc_file']

    new_data = {"email": "test@test.com"}
    add_data_in_csv(new_file, new_data)

    hc_res = HC(API_KEY).delete_list_of_contributors(hc_info['hc_id'], new_file)

    hc_res.assert_response_status(404)
    assert hc_res.json_response['errors'] == ['The following emails had no corresponding invitation or assignment to '
                                              'channel %s: test@test.com' % hc_info['hc_id']]


@allure.parent_suite('/hosted_channels/{hostedChannelId}:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_delete_hc_contributor_upper_case(tmpdir):
    """
    verify emails is not case sensitive
    """
    hc_info = create_channel_with_contributors(API_KEY, tmpdir)

    # new_name = "temp.csv"
    # new_file = copy_file_csv(CONTRIBUTORS, tmpdir, new_name)
    new_file = hc_info['hc_file']
    df = collect_data_from_file(new_file)

    df['email'] = df['email'].str.upper()
    # update csv file
    df.to_csv(new_file, index=False, )

    hc = HC(API_KEY)
    hc_res = hc.delete_list_of_contributors(hc_info['hc_id'], new_file)
    hc_res.assert_response_status(202)
    assert hc_res.json_response['status'] == 'accepted'

    res = hc.download_hc(hc_info['hc_id'])
    file_name = tmpdir + '/hc_info.csv'
    save_file_with_content(file_name, res.content)
    data = pd.read_csv(file_name)
    #  verify no contributors in the channel
    assert data.shape[0] == 0


@allure.parent_suite('/hosted_channels/{hostedChannelId}:delete')
@pytest.mark.skip(reason='Not implemented yet')
@pytest.mark.hosted_channel
def test_delete_hc_contributor_for_other_team(tmpdir):
    """
    delete contributors from other team channel
    """
    hc_info = create_channel_with_contributors(API_KEY, tmpdir)

    api_key_other_team = get_user_api_key('test_predefined_jobs')
    hc_res = HC(api_key_other_team).delete_list_of_contributors(hc_info['hc_id'], hc_info['hc_file'])
    hc_res.assert_response_status(404)
