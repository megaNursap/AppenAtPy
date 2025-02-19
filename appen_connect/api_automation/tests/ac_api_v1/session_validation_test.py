from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_session_validation, pytest.mark.ac_api]

AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_user_session_valid_token_api(ac_api_cookie):
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_ui_account', 'id')
    session_cookies = ac_api_cookie
    session_id = ""
    if session_cookies:
        session_id = session_cookies['actx']
    resp = api.user_token_validation_api(userId=user_id, tenantId=1, data=session_id)
    resp.assert_response_status(200)
    assert resp.json_response == True


@pytest.mark.ac_api_uat
def test_user_session_invalid_key_api():
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_ui_account', 'id')
    resp = api.user_token_validation_api(userId=user_id, tenantId=1, data="fsawrwdsg9fde3fss")
    resp.assert_response_status(200)
    assert resp.json_response == False


def test_user_session_invalid_user_id_api(ac_api_cookie):
    api = AC_API_V1(AUTH_KEY)
    session_id = ac_api_cookie['actx']
    resp = api.user_token_validation_api(userId=2398, tenantId=1, data=session_id)
    resp.assert_response_status(404)
    assert resp.json_response == {}


def test_user_session_invalid_tenant_id_api(ac_api_cookie):
    api = AC_API_V1(AUTH_KEY)
    user_id = get_test_data('test_ui_account', 'id')
    session_id = ac_api_cookie['actx']
    resp = api.user_token_validation_api(userId=user_id, tenantId=6, data=session_id)
    resp.assert_response_status(404)
    assert resp.json_response == {}


@pytest.mark.parametrize('auth_key, expected_status, error_msg',
                         [("1221jjidefghijklmn123opQRSTUVWreo09014bE", 403, {'error': 'Forbidden'}),
                          ("", 403, {'error': 'Forbidden'})])
def test_user_session_invalid_auth_key(ac_api_cookie, expected_status, error_msg, auth_key):
    api = AC_API_V1(auth_key)
    user_id = get_test_data('test_ui_account', 'id')
    session_id = ac_api_cookie['actx']
    resp = api.user_token_validation_api(userId=user_id, tenantId=6, data=session_id)
    resp.assert_response_status(expected_status)
    assert resp.json_response == error_msg
