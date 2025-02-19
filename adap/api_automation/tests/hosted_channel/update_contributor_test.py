import allure
import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, save_file_with_content
from adap.api_automation.services_config.hosted_channel import HC

faker = Faker()
api_key = get_user_api_key('test_hc_account')
team_id = get_user_team_id('test_hc_account')

VALID_PAYLOAD = {
    "last_name": "Last Name",
    "first_initial": "First Initial",
    "unit": "Test unit",
    "parent": "Test parent",
    "group": "Test group",
    "service": "Test Service"
}

EMPTY_METADATA = {"last_name": '',
                  "first_initial": '',
                  "unit": '',
                  "parent": '',
                  "group": '',
                  "service": ''}


@pytest.fixture(scope="module")
def _contributor():
    """
    create new hosted channel and upload contributor
    """
    global _channel

    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(api_key).create_channel(payload)
    hc_res.assert_response_status(201)
    _channel = hc_res.json_response['id']

    valid_email = faker.email()
    payload = {
        "email": valid_email
    }
    contributor_res = HC(api_key).upload_contributor(_channel, payload)
    contributor_res.assert_response_status(201)
    return valid_email


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token')])
def test_update_contributor_with_invalid_api_key(api_key_type, api_key, expected_status, expected_msg, _contributor):
    res = HC(api_key).update_metedata_for_contributor(_contributor, payload=VALID_PAYLOAD)
    res.assert_response_status(expected_status)
    if expected_msg: assert res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('email_type, email, expected_status, expected_msg',
                         [("empty_email", "", 500, ''),
                          ("invalid_email", "test@goole", 404, "Not Found"),
                          ("not_exist", "12345678@qwerty.com", 404, "Not Found")
                          ])
def test_update_contributor_with_invalid_email(email_type, email, expected_status, expected_msg, _contributor):
    res = HC(api_key).update_metedata_for_contributor(email, payload=VALID_PAYLOAD)
    res.assert_response_status(expected_status)
    if expected_msg: assert res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_update_metadata_invalid_email_in_payload(_contributor):
    payload = {
        "email": "test@test.com",
        "last_name": "Last Name",
        "first_initial": "First Initial",
        "unit": "Test unit",
        "parent": "Test parent",
        "group": "Test group",
        "service": "Test Service"
    }
    res = HC(api_key).update_metedata_for_contributor(_contributor, payload=payload)
    res.assert_response_status(404)
    assert res.json_response['errors'] == ["There's not a contributor profile associated with test@test.com"]


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
def test_update_metadata_happy_path(_contributor, tmpdir):
    hc = HC(api_key)
    res = hc.update_metedata_for_contributor(_contributor, payload=VALID_PAYLOAD)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'

    hc.download_channel_and_validate_metadata(_channel, _contributor, VALID_PAYLOAD, tmpdir)


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('param', ('last_name', 'first_initial', 'unit', 'parent', 'group', 'service'))
def test_update_single_parameter_for_metadata(param, _contributor):
    payload = {
        param: "Updated"
    }
    res = HC(api_key).update_metedata_for_contributor(_contributor, payload=payload)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.parametrize('param', ('last_name', 'first_initial', 'unit', 'parent', 'group', 'service'))
def test_update_single_parameter_with_invalid_value(param, _contributor):
    payload = {
        param: 111
    }
    res = HC(api_key).update_metedata_for_contributor(_contributor, payload=payload)
    res.assert_response_status(400)
    assert res.json_response['errors'][0]['errors'][0]['message'] == 'Expected type string but found type integer'
    assert res.json_response['errors'][0]['errors'][0]['path'] == [param]


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_update_metadata_blank_payload(_contributor, tmpdir):
    hc = HC(api_key)
    res = hc.update_metedata_for_contributor(_contributor, payload={})
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'


@allure.parent_suite('/hosted_channels/contributors/{email}/metadata:get')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_update_metadata_empty_param(_contributor, tmpdir):

    hc = HC(api_key)
    res = hc.update_metedata_for_contributor(_contributor, payload=EMPTY_METADATA)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'accepted'

    hc.download_channel_and_validate_metadata(_channel, _contributor, EMPTY_METADATA, tmpdir)

