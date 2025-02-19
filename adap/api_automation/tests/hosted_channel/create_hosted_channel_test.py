import allure
import pytest
from faker import Faker
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id
from adap.api_automation.services_config.hosted_channel import HC

faker = Faker()
api_key = get_user_api_key('test_hc_account')
team_id = get_user_team_id('test_hc_account')

pytestmark = pytest.mark.fed_api_smoke


@allure.parent_suite('/hosted_channels:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [
                          ("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token'),
                          ("valid_key", get_user_api_key('test_hc_account'), 201, '')])
def test_create_hc_with_api_key(api_key_type, api_key, expected_status, expected_msg):
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(api_key).create_channel(payload)
    hc_res.assert_response_status(expected_status)
    if expected_msg: assert hc_res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('type, hc_name, expected_status, expected_msg',
                         [("empty_name", "", 400, 'Name can\'t be blank'),
                          ("spaces", "     ", 400, 'Name can\'t be blank') ])
def test_create_hc_with_empty_name(type, hc_name, expected_status, expected_msg):
    payload = {
        "name": hc_name
    }
    hc_res = HC(api_key).create_channel(payload)
    hc_res.assert_response_status(expected_status)
    if expected_msg: assert hc_res.json_response['error'] == str([expected_msg])


@allure.parent_suite('/hosted_channels:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_create_hc_with_existing_name():
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc = HC(api_key)

    hc_res = hc.create_channel(payload)
    hc_res.assert_response_status(201)

    hc_res = hc.create_channel(payload)
    hc_res.assert_response_status(400)
    assert hc_res.json_response['error'] == "[\"Name has already been taken\"]"


@allure.parent_suite('/hosted_channels:post')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_create_hcs_for_different_teams():
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }

    team1 = HC(api_key)
    hc_res = team1.create_channel(payload)
    hc_res.assert_response_status(201)

    assert hc_res.json_response['name'] == valid_hc_name
    assert hc_res.json_response['team_id'] == team_id
    # verify response payload
    assert list(hc_res.json_response.keys()) == ['id', 'name', 'team_id', 'nda', 'hosted', 'conversion_rate',
                                                 'conversion_name', 'enabled', 'language', 'adult', 'secret_key',
                                                 'start_uri', 'finish_uri', 'default',
                                                 'require_contributor_verification']

    api_key2 = get_user_api_key('non_cf_team')
    team2 = HC(api_key2)
    hc_res = team2.create_channel(payload)
    hc_res.assert_response_status(201)
    assert hc_res.json_response['name'] == valid_hc_name
    assert hc_res.json_response['team_id'] == get_user_team_id('non_cf_team')





