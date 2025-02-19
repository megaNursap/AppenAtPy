"""
update metadata for contributors tests
"""
import allure
import numpy as np
import pandas as pd
import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_user_api_key, get_data_file, \
    save_file_with_content
from adap.api_automation.services_config.hosted_channel import HC
from adap.ui_automation.utils.pandas_utils import add_data_in_csv, copy_file_csv, collect_data_from_file, create_updated_csv

faker = Faker()
API_KEY = get_user_api_key('test_hc_account')

@pytest.fixture(scope="module")
def _channel(tmpdir_factory):
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(API_KEY).create_channel(payload)
    hc_res.assert_response_status(201)
    _channel_id = hc_res.json_response['id']
    sample_file = get_data_file("/hosted_channel/dod_data_58.csv")
    # replace_column_in_csv(sample_file, 'channel_id', _channel_id)
    _new_file = create_updated_csv(sample_file, 'channel_id', _channel_id, "temp_file.csv", tmpdir_factory.mktemp("data"))

    hc_res = HC(API_KEY).upload_list_of_contributors(_new_file)
    hc_res.assert_response_status(202)

    return {"channel_id": _channel_id}


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token')])
def test_update_contributors_with_invalid_api_key(api_key_type, api_key, expected_status, expected_msg):
    sample_file = get_data_file("/hosted_channel/dod_data_58_update.csv")
    res = HC(api_key).update_list_of_contributors(sample_file)
    res.assert_response_status(expected_status)
    if expected_msg: assert res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
@pytest.mark.parametrize('file_type', ('.txt', '.json', '.pdf'))
def test_update_metadata_upload_unsupported_file_format(file_type, _channel):
    f_name = get_data_file("/hosted_channel/test" + file_type)
    with open(f_name, 'r') as fb:
        res = HC(API_KEY).update_list_of_contributors(f_name)
        res.assert_response_status(422)
        assert res.json_response['errors'] == ['Unsupported file format']
        fb.close()


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
def test_update_metadata(_channel, tmpdir):
    sample_file = get_data_file("/hosted_channel/dod_data_58_update.csv")
    # replace_column_in_csv(sample_file, 'channel_id', _channel['channel_id'])
    new_file = create_updated_csv(sample_file, 'channel_id', _channel['channel_id'], "metadate_temp.csv", tmpdir)
    hc = HC(API_KEY)
    res = hc.update_list_of_contributors(new_file)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'

    res = hc.download_hc(_channel['channel_id'])
    file_name = tmpdir + '/temp.csv'
    save_file_with_content(file_name, res.content)
    data = pd.read_csv(file_name)
    data.replace(np.NaN, '', inplace=True)
    _data = data.drop(columns=['pending_invite', 'status_last_updated'])

    data_csv = pd.read_csv(new_file)
    data_csv.replace(np.NaN, '', inplace=True)

    def comparable(df, index_col='email'):
        return df.fillna(value=0).set_index(index_col).to_dict('index')

    assert comparable(data_csv) == comparable(_data)


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
def test_update_metadata_contributor_not_exist(_channel, tmpdir):
    sample_file = get_data_file("/hosted_channel/dod_data_58_update.csv")
    # replace_column_in_csv(sample_file, 'channel_id', _channel['channel_id'])
    new_file = create_updated_csv(sample_file, 'channel_id', _channel['channel_id'], 'new_temp.csv', tmpdir)

    new_data = {"email": "new_email@dod.com", "last_name": "new", "first_initial": "not exist", "unit": "unit1",
                "parent": "1", "group": "group1", "service": "service2", "channel_id": ''}
    add_data_in_csv(new_file, new_data)
    hc = HC(API_KEY)
    res = hc.update_list_of_contributors(new_file)
    res.assert_response_status(400)
    assert res.json_response['errors'] == [
        "Email: new_email@dod.com, Error: There\'s not a contributor profile associated with new_email@dod.com"]
    # delete_data_from_csv_by_condition(sample_file, column='email', value='new_email@dod.com')


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
def test_update_metadata_empty_email(tmpdir, _channel):
    sample_file = get_data_file("/hosted_channel/dod_data_58_update.csv")
    # replace_column_in_csv(sample_file, 'channel_id', _channel['channel_id'])
    new_file = create_updated_csv(sample_file, 'channel_id', _channel['channel_id'], 'new_temp.csv', tmpdir)
    new_data = {"email": "", "channel_id": _channel['channel_id']}
    add_data_in_csv(new_file, new_data)
    hc = HC(API_KEY)
    res = hc.update_list_of_contributors(new_file)
    res.assert_response_status(400)
    assert res.json_response['errors'] == ["Email: , Error: Empty list of attributes to change"]
    # delete_data_from_csv_by_condition(sample_file, column='email', value='')


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
def test_update_metadata_channel_not_exist(tmpdir):
    sample_file = get_data_file("/hosted_channel/dod_data_58_update.csv")
    # replace_column_in_csv(sample_file, 'channel_id', 9999)
    new_file = create_updated_csv(sample_file, 'channel_id', 9999, 'new999_temp.csv', tmpdir)
    hc = HC(API_KEY)
    res = hc.update_list_of_contributors(new_file)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'


@allure.parent_suite('/hosted_channels/contributors/metadata:put')
@pytest.mark.hosted_channel
@pytest.mark.skip
def test_update_metadata_email_not_case_sensitive(tmpdir):
    sample_file = get_data_file("/hosted_channel/dod_data_58_update.csv")
    # modify email  - upper case
    new_name = "temp.csv"
    new_file = copy_file_csv(sample_file, tmpdir, new_name)
    df = collect_data_from_file(new_file)
    df['email'] = df['email'].str.upper()
    df.to_csv(new_file, index=False, )

    hc = HC(API_KEY)
    # replace_column_in_csv(sample_file, 'channel_id', 193)
    new_file = create_updated_csv(sample_file, 'channel_id', 193, 'new193_temp.csv', tmpdir)
    res = hc.update_list_of_contributors(new_file)

    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'
