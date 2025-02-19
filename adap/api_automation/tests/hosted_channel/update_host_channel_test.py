"""
update hosted channel name tests
https://appen.atlassian.net/browse/DED-2451
"""
import allure
import pytest
from faker import Faker
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id,generate_random_string
from adap.api_automation.services_config.hosted_channel import HC

faker = Faker()
API_KEY = get_user_api_key('cf_internal_role')
TEAM_ID = get_user_team_id('cf_internal_role')

pytestmark = [pytest.mark.hosted_channel, pytest.mark.fed_api]

def create_hc(api_key):
    """
    new channel
    """
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(api_key).create_channel(payload)
    hc_res.assert_response_status(201)
    return hc_res.json_response['id']


@pytest.fixture(scope="module")
def _channel():
    """
    pytest fixture - create new channel
    """
    return create_hc(API_KEY)


@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [
                          ("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token'),
                          ("valid_key", get_user_api_key('cf_internal_role'), 200, '')
                          ])
def test_update_hc_name_with_api_key(api_key_type, api_key, expected_status, expected_msg, _channel):
    payload = {"name": generate_random_string()}
    hc_res = HC(api_key).update_channel_name(_channel, payload)
    hc_res.assert_response_status(expected_status)
    if expected_msg: assert hc_res.json_response['message'] == expected_msg


@pytest.mark.parametrize('test_name, hc_id, expected_status, expected_msg',
                         [
                          ("empty_id", "", 405, ''),
                          ("not_exist", 99999, 404, 'Invalid Hosted Channel ID.'),
                          ("invalid_type", 'abc', 404, 'Invalid Hosted Channel ID.'),
                          ("unsupported_format", 10.23, 404, 'Invalid Hosted Channel ID.')
                          ])
def test_update_hc_name_invalid_id(test_name, hc_id, expected_status, expected_msg):
    payload = {"name": generate_random_string()}
    res = HC(API_KEY).update_channel_name(hc_id, payload)
    res.assert_response_status(expected_status)
    if expected_msg: assert res.json_response['message'] == expected_msg


def test_cf_internal_update_hc_name_from_another_team():
    team_api_key = get_user_api_key('test_predefined_jobs')
    hc_id = create_hc(team_api_key)
    payload = {"name": generate_random_string()}
    res = HC(API_KEY).update_channel_name(hc_id, payload)
    res.assert_response_status(200)


def test_non_admin_update_hc_name_another_team_for_cf_internal():
    team_api_key = get_user_api_key('test_predefined_jobs')
    hc_id = create_hc(API_KEY)
    payload = {"name": generate_random_string()}
    res = HC(team_api_key).update_channel_name(hc_id, payload)
    res.assert_response_status(404)
    assert res.json_response['message'] == "Invalid Hosted Channel ID."


def test_update_channel_name_invalid_payload(_channel):
    payload = {"name": ""}
    hc_res = HC(get_user_api_key('cf_internal_role')).update_channel_name(_channel, payload)
    hc_res.assert_response_status(422)
    hc_res.json_response['errors'][0] == "Name can't be blank"