"""
upload contributors tests
"""
import os

import allure
import numpy as np
import pandas as pd
import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_user_api_key, get_data_file, \
    save_file_with_content, file_exists
from adap.api_automation.services_config.hosted_channel import HC
from adap.ui_automation.utils.pandas_utils import replace_column_in_csv, create_updated_csv

faker = Faker()
API_KEY = get_user_api_key('test_hc_account')


@pytest.fixture(scope="module")
def _channel():
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(API_KEY).create_channel(payload)
    hc_res.assert_response_status(201)
    return hc_res.json_response['id']


@allure.parent_suite('/hosted_channels/{hostedChannelId}/contributors:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [
                          ("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token'),
                          ("valid_key", get_user_api_key('test_hc_account'), 201, '')])
def test_upload_contributor_with_api_key(api_key_type, api_key, expected_status, expected_msg, _channel):
    valid_email = faker.email()
    payload = {
        "email": valid_email
    }
    contributor_res = HC(api_key).upload_contributor(_channel, payload)
    contributor_res.assert_response_status(expected_status)
    if expected_msg: assert contributor_res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels/{hostedChannelId}/contributors:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('test_name, email, expected_status, expected_msg',
                         [("empty_email", "", 400, ['Validation failed: Email is invalid']),
                          ("invalid_email", "test@gmail", 400, ['Validation failed: Email is invalid']),
                          ("invalid_email2", "testgmail.com", 400, ['Validation failed: Email is invalid']),
                          ("empty_email_spaces", "    ", 400, ['Validation failed: Email is invalid']),
                          ("valid_email", "test@figure-eight.com", 201, "")])
def test_upload_contributor_with_invalid_email(test_name, email, expected_status, expected_msg, _channel):
    payload = {
        "email": email
    }
    contributor_res = HC(API_KEY).upload_contributor(_channel, payload)
    contributor_res.assert_response_status(expected_status)
    if expected_msg: assert contributor_res.json_response['errors'] == expected_msg


@allure.parent_suite('/hosted_channels/{hostedChannelId}/contributors:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('test_name, channel, expected_status, expected_msg, error_message',
                         [
                          ("empty_channel", "", 405, "", ""),
                          ("not_exist", 99999, 404, "Invalid Hosted Channel ID.", ""),
                          ("invalid_type", "asd", 400, "", [{'code': 'INVALID_REQUEST_PARAMETER', 'errors': [{'code': 'INVALID_TYPE', 'message': 'Expected type integer but found type string', 'path': []}], 'in': 'path', 'message': 'Invalid parameter (hostedChannelId): Expected type integer but found type string', 'name': 'hostedChannelId', 'path': []}])
                          ])
def test_upload_contributor_with_invalid_channel_id(test_name, channel, expected_status, expected_msg, error_message):
    valid_email = faker.email()
    payload = {
        "email": valid_email
    }

    contributor_res = HC(API_KEY).upload_contributor(channel, payload)
    contributor_res.assert_response_status(expected_status)
    if expected_msg: assert contributor_res.json_response['message'] == expected_msg
    if error_message: assert contributor_res.json_response['errors'] == error_message


@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@allure.parent_suite('/hosted_channels/{hostedChannelId}/contributors:post')
def test_test_upload_contributor_with_parameters(_channel, tmpdir):
    valid_email = faker.email()
    first_name = faker.first_name()
    last_name = faker.last_name()
    first_initial = "%s %s" % (first_name[0],last_name[0])
    payload = {
        "email": valid_email,
        "last_name": last_name,
        "first_initial": first_initial,
        "unit": "unit1",
        "parent": "parent1",
        "group": "group1",
        "service": "service1"
    }

    hc = HC(API_KEY)
    contributor_res = hc.upload_contributor(_channel, payload)
    contributor_res.assert_response_status(201)

    hc.download_channel_and_validate_metadata(_channel, valid_email, payload, tmpdir)


@pytest.mark.hosted_channel
@pytest.mark.fed_api
@allure.parent_suite('/hosted_channels/{hostedChannelId}/contributors:post')
@pytest.mark.parametrize('param, value, expected_status, expected_msg',
                         [("last_name", 1, 400, ""),
                          ("first_initial", 1, 400, ""),
                          ("unit", 1, 400, ""),
                          ("parent", 1, 400, ""),
                          ("group", 1, 400, ""),
                          ("service", 1, 400, "")])
def test_test_upload_contributor_with_invalid_parameters(param, value, expected_status, expected_msg, _channel):
    valid_email = faker.email()
    payload = {"email": valid_email, param: value}
    contributor_res = HC(API_KEY).upload_contributor(_channel, payload)
    contributor_res.assert_response_status(400)
    assert contributor_res.json_response['errors'][0]['errors'][0]['message'] == 'Expected type string but found type integer'
    assert contributor_res.json_response['errors'][0]['errors'][0]['path'] == [param]


#  upload list of contributors
@pytest.mark.hosted_channel
@pytest.mark.parametrize('file_type',('.txt', '.json', '.pdf'))
def test_upload_unsupported_file_format(file_type, _channel):
    f_name =  get_data_file("/hosted_channel/test" + file_type)
    with open(f_name, 'r') as fb:
        res = HC(API_KEY).upload_list_of_contributors(f_name)
        res.assert_response_status(422)
        assert res.json_response['errors'] == ['Unsupported file format']
        fb.close()


@pytest.mark.hosted_channel
def test_upload_invalid_ontology_csv(_channel):
    pass
# #  todo, when validation for csv file will be implemented - blank column, duplicate ...


@pytest.mark.hosted_channel
def test_upload_invalid_emails_csv(_channel):
    pass
#  todo, when endpoint for getting info from hosted channel will be implemented


@allure.parent_suite('/hosted_channels/{hostedChannelId}/contributors:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
def test_upload_valid_csv(_channel, tmpdir):
    sample_file = get_data_file('/hosted_channel/valid_list.csv')

    # replace_column_in_csv(sample_file, 'channel_id', _channel)
    new_file = create_updated_csv(sample_file, 'channel_id', _channel, "valid_temp.csv", tmpdir)
    hc = HC(API_KEY)
    res = hc.upload_list_of_contributors(new_file)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'

    # data validation
    data_csv = pd.read_csv(new_file)
    data_csv.replace(np.NaN, '', inplace=True)

    res = hc.download_hc(_channel)
    file_name = tmpdir + '/temp_list_metadata.csv'
    save_file_with_content(file_name, res.content)
    data = pd.read_csv(file_name)
    data.replace(np.NaN, '', inplace=True)
    _data = data.drop(columns=['pending_invite', 'status_last_updated'])

    def comparable(df, index_col='email'):
        return df.fillna(value=0).set_index(index_col).to_dict('index')

    # assert comparable(data_csv) == comparable(_data)


