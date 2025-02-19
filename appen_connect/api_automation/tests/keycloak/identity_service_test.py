import time

import pytest, urllib, json, requests
from bs4 import BeautifulSoup
from appen_connect.api_automation.services_config.identity_service import IdentityService
from adap.api_automation.utils.data_util import get_user, get_test_data

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_identity_service, pytest.mark.ac_api_kc, pytest.mark.ac_api]

try:
    user = get_user('adap_keycloak', env=pytest.env)
    CLIENT_SECRET = get_test_data('keycloak', 'client_secret')
except:
    user = {}
    CLIENT_SECRET = ''

expected_token_resp_fields = [
    'access_token',
    'expires_in',
    'refresh_expires_in',
    'refresh_token',
    'token_type',
    'id_token',
    'not-before-policy',
    'session_state',
    'scope',
    ]

def test_get_valid_token():
    identity_service = IdentityService(pytest.env)
    user = get_user('adap_keycloak', env=pytest.env)
    resp = identity_service.get_token(
        username=user.get('user_name'),
        password=user.get('password'),
        token=CLIENT_SECRET,
        client_id='appen-connect'
     )
    resp.assert_response_status(200)
    for expected_field_name in expected_token_resp_fields:
        assert expected_field_name in resp.json_response, resp.json_response

@pytest.mark.parametrize('username, password',
                         [(user.get('user_name'), 'invalid'),
                          (user.get('user_name'), ''),
                          (user.get('user_name'), None),
                          (user.get('user_name'), ' '),
                          ('invalid','invalid'),
                          ])
def test_get_token_invalid_credentials(username, password):
    identity_service = IdentityService(pytest.env)
    resp = identity_service.get_token(
        username=user.get('user_name'),
        password=password,
        token=CLIENT_SECRET,
        client_id='appen-connect'
    )
    resp.assert_response_status(401)
    assert resp.json_response == {
        'error': 'invalid_grant',
        'error_description': 'Invalid user credentials'
        }, resp.json_response

@pytest.mark.parametrize('username, password',
                         [(None, ''),
                          (None, None),
                          ])
def test_get_token_missing_username(username, password):
    identity_service = IdentityService(pytest.env)
    resp = identity_service.get_token(
        username=username,
        password=password,
        token=CLIENT_SECRET,
        client_id='appen-connect'
    )
    resp.assert_response_status(401)
    assert resp.json_response == {
        'error': 'invalid_request',
        'error_description': 'Missing parameter: username'
        }, resp.json_response


def test_get_adap_sid_by_ac_login():
    identity_service = IdentityService(pytest.env)
    user = get_user('adap_keycloak', env=pytest.env)
    sid = identity_service.get_adap_sid_by_ac_login(user.get('user_name'), user.get('password'))
    assert sid is not None
