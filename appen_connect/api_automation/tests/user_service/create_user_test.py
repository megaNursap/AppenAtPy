import pytest

from appen_connect.api_automation.services_config.ac_user_service import UserService

pytestmark = [pytest.mark.regression_ac_user_service, pytest.mark.regression_ac, pytest.mark.ac_api_user_service,
              pytest.mark.ac_api_user_service_create_user, pytest.mark.ac_api]

API = UserService()


@pytest.mark.parametrize('param, expected_status',
                         [('email', 422),
                          ('password', 422),
                          ('firstName', 422),
                          ('lastName', 422),
                          ('country', 400),
                          # ('adultCertify', 422),
                          # ('taxDocumentation', 422),
                          # ('state', 422),
                          ('verificationCode', 422)
                          ])
def test_new_vendor_payload_required_data(param, expected_status):
    payload = {"email": "SignUPQA006connect.stage.xyz@gmail.com", "password": "Testing123!", "firstName": "SignUP",
               "lastName": "QA006", "country": "CA", "adultCertify": 'true', "taxDocumentation": 'true', "state": "QC",
               "verificationCode": "0534A9"}

    current_value = payload.pop(param)
    res = API.new_vendor(payload)
    res.assert_response_status(expected_status)

    payload[param] = ''
    res = API.new_vendor(payload)
    res.assert_response_status(expected_status)
    if param == "country":
        assert res.json_response['error'] == 'Validation error'
    else:
        assert res.json_response['error'] == 'Validation error'
        assert res.json_response['fieldErrors'] == [{'field': param, 'message': 'must not be blank', 'code': 'NotBlank'}]


@pytest.mark.ac_api_uat
def test_vendor_verification_code_wrong(ac_api_cookie):
    payload = {"email": "SignUPQA006connect.stage.xyz@gmail.com", "password": "Testing123!", "firstName": "SignUP",
               "lastName": "QA006", "country": "CA", "adultCertify": 'true', "taxDocumentation": 'true', "state": "QC",
               "verificationCode": "SignUPQA006"}

    res = API.new_vendor(payload, cookies=ac_api_cookie)
    res.assert_response_status(400)
    assert res.json_response['error'] == "Invalid code. Try again or resend email."


@pytest.mark.ac_api_uat
def test_vendor_invalid_email():
    payload = {"email": "SignUPQA006connect.stage.xyzgmail.com", "password": "12345", "firstName": "SignUP",
               "lastName": "QA006", "country": "CA", "adultCertify": 'true', "taxDocumentation": 'true', "state": "QC",
               "verificationCode": "0534A9"}

    res = API.new_vendor(payload)
    res.assert_response_status(422)
    assert res.json_response['error'] == 'Validation error'
    assert res.json_response['fieldErrors'] == [
        {'field': 'email', 'message': 'must be a well-formed email address', 'code': 'Email'}]


@pytest.mark.ac_api_uat
def test_vendor_exist(ac_api_cookie):
    payload = {"email": "SignUPQA006connect.stage.xyz@gmail.com", "password": "Testing123!", "firstName": "SignUP",
               "lastName": "QA006", "country": "CA", "adultCertify": 'true', "taxDocumentation": 'true', "state": "QC",
               "verificationCode": "0534A9"}

    res = API.new_vendor(payload, cookies=ac_api_cookie)
    res.assert_response_status(400)
    assert res.json_response['error'] == 'The email address is already registered.'
#     Completed fix this tests  ^^^ Fixed with proper error message for existing user
