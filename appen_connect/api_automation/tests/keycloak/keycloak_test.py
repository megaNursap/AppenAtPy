from appen_connect.api_automation.services_config.keycloak import Keycloak
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_keycloak, pytest.mark.ac_api]

USER_EMAIL = get_user_email('test_ui_account')
PWD = get_user_password('test_ui_account')
CLIENT_SECRET = get_test_data('keycloak', 'client_secret')


@pytest.mark.ac_api_uat
def test_keycloak_tokenID_token():
    payload = {
        "client_id": "appen-connect",
        "grant_type": "client_credentials",
        "scope": "openid",
        "client_secret": CLIENT_SECRET
    }
    api = Keycloak()
    resp = api.retrieve_token(payload)
    resp.assert_response_status(200)
    assert resp.json_response['expires_in'] == 600
    assert resp.json_response['refresh_expires_in'] == 0


@pytest.mark.parametrize('client_id, client_secret, expected_status, error_msg',
                         [("appen-connect", "fdsffff", 401, {'error': 'unauthorized_client',
                                                             'error_description': 'Invalid client secret'}),
                          ("appen", CLIENT_SECRET, 400, {'error': 'invalid_client',
                                                         'error_description': 'Invalid client credentials'})])
def test_keycloak_tokenID_token_invalid_client_credentials(client_id, client_secret, expected_status, error_msg):
    payload = {
        "client_id": client_id,
        "grant_type": "client_credentials",
        "scope": "openid",
        "client_secret": client_secret
    }
    api = Keycloak()
    resp = api.retrieve_token(payload)
    resp.assert_response_status(expected_status)
    assert resp.json_response == error_msg


def test_keycloak_token_master():
    payload = {
        "client_id": "appen-connect",
        "grant_type": "password",
        "username": USER_EMAIL,
        "password": PWD,
        "scope": "openid",
        "client_secret": CLIENT_SECRET
    }
    api = Keycloak()
    resp = api.retrieve_token(payload)
    resp.assert_response_status(200)
    assert resp.json_response['expires_in'] == 600
    assert resp.json_response['refresh_expires_in'] == 28800


@pytest.mark.parametrize('client_id, client_secret, expected_status, error_msg',
                         [("appen-connect", "fdsffff", 401, {'error': 'unauthorized_client',
                                                             'error_description': 'Invalid client secret'}),
                          ("appen", CLIENT_SECRET, 400, {'error': 'invalid_client',
                                                         'error_description': 'Invalid client credentials'})])
def test_keycloak_token_master_token_invalid_client_credentials(client_id, client_secret, expected_status, error_msg):
    payload = {
        "client_id": client_id,
        "grant_type": "password",
        "username": USER_EMAIL,
        "password": PWD,
        "scope": "openid",
        "client_secret": client_secret
    }
    api = Keycloak()
    resp = api.retrieve_token(payload)
    resp.assert_response_status(expected_status)
    assert resp.json_response == error_msg


def test_get_user_info_application_level():
    payload = {
        "client_id": "appen-connect",
        "grant_type": "client_credentials",
        "scope": "openid",
        "client_secret": CLIENT_SECRET
    }
    api = Keycloak()
    _resp = api.retrieve_token(payload)
    bearer_token = _resp.json_response['access_token']
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + bearer_token
    }
    resp = api.get_user_info(headers=headers)
    resp.assert_response_status(200)
    assert resp.json_response['email_verified'] == False
    assert resp.json_response['preferred_username'] == 'service-account-appen-connect'


@pytest.mark.ac_api_uat
def test_get_user_info():
    payload = {
        "client_id": "appen-connect",
        "grant_type": "password",
        "username": USER_EMAIL,
        "password": PWD,
        "scope": "openid",
        "client_secret": CLIENT_SECRET
    }
    api = Keycloak()
    _resp = api.retrieve_token(payload)
    bearer_token = _resp.json_response['access_token']
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + bearer_token
    }
    resp = api.get_user_info(headers=headers)
    resp.assert_response_status(200)
    assert resp.json_response['email_verified'] == True
    assert resp.json_response['email'] == USER_EMAIL
    assert resp.json_response['preferred_username'] == USER_EMAIL


def test_get_user_info_invalid_auth():
    bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGVU56a0FVYXk0MVd1VUtpQmtUUkZ1Njh"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + bearer_token
    }
    api = Keycloak()
    resp = api.get_user_info(headers=headers)
    resp.assert_response_status(401)
    assert resp.json_response['error'] == "invalid_token"
