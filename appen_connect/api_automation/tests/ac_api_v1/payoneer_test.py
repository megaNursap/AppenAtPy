# These are tests for stage only!!!

from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_payoneer, pytest.mark.ac_api]


AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_approve_user_api():
    api = AC_API_V1(AUTH_KEY)
    payeeid = get_test_data("test_active_vendor_account", 'payeeid')
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_approve_user(payeeid, programid)
    resp.assert_response_status(200)
    assert resp.text == "OK"


def test_get_approve_user_invalid_payeeid_api():
    api = AC_API_V1(AUTH_KEY)
    payeeid = "12DF45"
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_approve_user(payeeid, programid)
    resp.assert_response_status(400)
    assert resp.text == ""


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_approve_user_api_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    payeeid = get_test_data("test_active_vendor_account", 'payeeid')
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_decline_user(payeeid, programid)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


@pytest.mark.ac_api_uat
def test_get_decline_user_api():
    api = AC_API_V1(AUTH_KEY)
    payeeid = get_test_data("test_active_vendor_account", 'payeeid')
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_decline_user(payeeid, programid)
    resp.assert_response_status(200)
    assert resp.text == "OK"


def test_get_decline_user_invalid_payeeid_api():
    api = AC_API_V1(AUTH_KEY)
    payeeid = "12DF45"
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_decline_user(payeeid, programid)
    resp.assert_response_status(400)
    assert resp.text == ""


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_decline_user_api_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    payeeid = get_test_data("test_active_vendor_account", 'payeeid')
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_decline_user(payeeid, programid)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


@pytest.mark.ac_api_uat
def test_get_payoneer_registration_api():
    api = AC_API_V1(AUTH_KEY)
    payeeid = get_test_data("test_active_vendor_account", 'payeeid')
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')
    payoneerid = payeeid

    resp = api.get_payoneer_registration(payeeid, programid, payoneerid)
    resp.assert_response_status(200)
    assert resp.text == "OK"


def test_get_payoneer_registration_invalid_payeeid_api():
    api = AC_API_V1(AUTH_KEY)
    payeeid = "12DF45"
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')

    resp = api.get_payoneer_registration(payeeid, programid)
    resp.assert_response_status(400)
    assert resp.text == ""


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_get_payoneer_registration_api_invalid_auth_key(auth_key, expected_status, error_msg):
    api = AC_API_V1(auth_key)
    payeeid = get_test_data("test_active_vendor_account", 'payeeid')
    programid = get_test_data("test_active_vendor_account", 'payoneer_program_id')
    resp = api.get_payoneer_registration(payeeid, programid)
    resp.assert_response_status(expected_status)
    assert len(resp.json_response) > 0
    assert resp.json_response == error_msg


#To test cancel payment, you can use same client reference id, or payout amount less than 20, or not existing payee id.
# will update the test to run
@pytest.mark.skip(reason='Bug')
def test_get_cancel_payment1():
    api = AC_API_V1(AUTH_KEY)
    payee_id = get_test_data("test_active_vendor_account", 'payeeid')
    #p+last_payment_id (from the payments table) this is not available to read from UI or other API.
    client_reference_id = "p17"
    payment_amount = "4.99" #Amount on the "Paid" invoice
    reason_code = "10301-Insufficient balance" #one of the listed Reasoncodes from Payoneer
    reason_description = "10301-Insufficient balance"
    resp = api.get_cancel_payment( client_reference_id, payment_amount, reason_code, reason_description, payee_id)
    resp.assert_response_status(200)