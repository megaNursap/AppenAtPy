import allure, requests, time

import appen_connect.api_automation.services_config.endpoints.identity_service as endpoints
from adap.api_automation.utils.data_util import get_user, get_test_data
from adap.api_automation.utils.http_util import HttpMethod
from bs4 import BeautifulSoup

form_headers = {
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded',
}


class IdentityService:
    def __init__(self, env, service=None, session=True):
        self.url = endpoints.URL(env=env)
        self.endpoints = endpoints
        self.service = HttpMethod(base_url=self.url, session=session)

    @allure.step
    def get_token(self, username, password, token=None, client_id='appen-connect'):
        return self.service.post(
            endpoints.TOKEN,
            headers=form_headers,
            data={
                'client_id': client_id,
                'grant_type': 'password',
                'client_secret': token,
                'scope': 'openid',
                'username': username,
                'password': password,
            },
            ep_name=endpoints.TOKEN
            )

    @allure.step
    def get_auth(self, params, **kwargs):
        return self.service.get(
            endpoints.AUTH,
            params=params,
            ep_name=endpoints.AUTH,
            **kwargs
        )

    @allure.step
    def post_authenticate(self, payload):
        return self.service.post(
            endpoints.AUTHENTICATE,
            headers=form_headers,
            data=payload,
            ep_name=endpoints.AUTHENTICATE
        )

    @allure.step
    def get_adap_sid_by_ac_login(self, username, password):
        params = {
            "response_type": "code",
            "client_id": "appen-connect",
            "redirect_uri": "https://connect-stage.integration.cf3.us/qrp/core/login",
            "state": "0",
            "login": "true",
            "scope": "openid"
        }
        login_page = self.get_auth(params)
        soup = BeautifulSoup(login_page.text, features='html.parser')
        authenticate_url = soup.find("form", {"id": "kc-form-login"})['action']

        bypass = get_test_data('adap_keycloak', 'bypass')
        headers_bypass_fraud_check = {
            "Appen-Kasada-Postman-Bypass": bypass
        }
        authenticate_payload = {
            "username": username,
            "password": password
        }
        base_url_backup, self.service.base_url = self.service.base_url, ""
        self.service.post(authenticate_url, data=authenticate_payload, headers=headers_bypass_fraud_check)
        self.service.base_url = base_url_backup
        keycloak_identity_cookie_value = None

        for k, v in requests.utils.dict_from_cookiejar(self.service.request.cookies).items():
            if k == 'KEYCLOAK_IDENTITY':
                keycloak_identity_cookie_value = v

        if keycloak_identity_cookie_value is None:
            raise Exception("Keycloak identity cookie not found")

        cookies = {
            'KEYCLOAK_IDENTITY': keycloak_identity_cookie_value
        }
        params = {
            "client_id": "akon",
            "redirect_uri": "https://account.integration.cf3.us/auth/keycloak/callback",
            "response_type": "code",
            "state": "0"
        }

        self.get_auth(params, cookies=cookies, allow_redirects=True)
        for k, v in requests.utils.dict_from_cookiejar(self.service.request.cookies).items():
            if k == '_sid':
                return {k: v}

        return None
