"""
download hosted channel tests
"""
import pandas as pd

import allure
import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, file_exists, \
    save_file_with_content
from adap.api_automation.services_config.hosted_channel import HC

faker = Faker()
API_KEY = get_user_api_key('test_hc_account')
TEAM_ID = get_user_team_id('test_hc_account')


def create_channel_for_another_team():
    """
    create_channel_for_another_team
    """
    team_api_key = get_user_api_key('non_cf_team')
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(team_api_key).create_channel(payload)
    return hc_res.json_response['id']


@pytest.fixture(scope="module")
def _channel():
    """
    pytest fixture - create new channel and upload contributor
    """

    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(API_KEY).create_channel(payload)
    hc_res.assert_response_status(201)
    _channel_id = hc_res.json_response['id']

    # upload contributor
    valid_email = faker.email()
    first_name = faker.first_name()
    last_name = faker.last_name()
    first_initial = "%s %s" % (first_name[0], last_name[0])
    payload = {
        "email": valid_email,
        "last_name": last_name,
        "first_initial": first_initial,
        "unit": "unit1",
        "parent": "parent1",
        "group": "group1",
        "service": "service1"
    }

    contributor_res = HC(API_KEY).upload_contributor(_channel_id, payload)
    contributor_res.assert_response_status(201)

    return {'channel_id': _channel_id,
            'contributor': payload,
            'other_team_channel_id': create_channel_for_another_team()
            }


@allure.parent_suite('/api-proxy/v1/hosted_channels/{hostedChannelId}/contributors/export:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [
                             ("empty_key", "", 403, 'Unauthorized token'),
                             ("invalid_key", "12345678qwerty", 403, 'Unauthorized token'),
                             ("valid_key", API_KEY, 200, '')])
def test_download_hc_with_api_key(api_key_type, api_key, expected_status, expected_msg, tmpdir, _channel):
    """
    test_download_hc_with_api_key
    """
    res = HC(api_key).download_hc(_channel['channel_id'])
    res.assert_response_status(expected_status)
    if expected_msg:
        assert res.json_response['message'] == expected_msg
    else:
        file_name = tmpdir + '/%s.csv' % api_key_type
        open(file_name, 'wb').write(res.content)
        assert file_exists(file_name)


@allure.parent_suite('/api-proxy/v1/hosted_channels/{hostedChannelId}/contributors/export:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('channel_id_type, channel_id, expected_status, expected_msg',
                         [
                             ("empty_id", "", 404, ''),
                             ("not_exist_id", 9999999, 404, ''),
                             ("invalid_id", "000we9999", 400, [{"code": "INVALID_REQUEST_PARAMETER", "errors": [
                                 {"code": "INVALID_TYPE", "message": "Expected type integer but found type string",
                                  "path": []}], "in": "path",
                                                                "message": "Invalid parameter (hostedChannelId): "
                                                                           "Expected type integer but found type "
                                                                           "string",
                                                                "name": "hostedChannelId", "path": []}])
                             # ("other_TEAM_ID", '', 403, 'Unauthorized token')  not working right now
                         ])
def test_download_hc_with_channel_id(channel_id_type, channel_id, expected_status, expected_msg, _channel):
    """
    test_download_hc_with_channel_id
    """
    if channel_id_type == 'other_team_id':
        res = HC(API_KEY).download_hc(_channel['other_team_channel_id'])
    else:
        res = HC(API_KEY).download_hc(channel_id)
    res.assert_response_status(expected_status)
    if expected_status == 400 and expected_msg: assert res.json_response['errors'] == expected_msg
    if expected_status == 404 and expected_msg: assert res.json_response['message'] == expected_msg


@allure.parent_suite('/api-proxy/v1/hosted_channels/{hostedChannelId}/contributors/export:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_validate_csv(_channel, tmpdir):
    """
    test_download_hc_with_channel_id
    """
    hc = HC(API_KEY)
    res = hc.download_hc(_channel['channel_id'])
    res.assert_response_status(200)
    file_name = tmpdir + '/test.csv'
    save_file_with_content(file_name, res.content)
    assert file_exists(file_name)

    data = pd.read_csv(file_name)
    assert list(data.keys()) == ['channel_id', 'email', 'last_name', 'first_initial', 'unit', 'group', 'parent',
                                 'service', 'pending_invite', 'status_last_updated']
    hc.validate_metadata_for_contributor(_channel['contributor']['email'], _channel['contributor'], data)
