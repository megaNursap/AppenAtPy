import json

import allure
import pytest

from appen_connect.api_automation.services_config.endpoints.ac_api_v3 import *
from adap.api_automation.utils.http_util import HttpMethod


def get_valid_cookies(app, user_name, user_password):
    app.ac_user.login_as(user_name=user_name, password=user_password)
    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}
    return flat_cookie_dict


class AC_API_V3:

    def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(env=pytest.env)

        if not headers:
            self.headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

        self.service = HttpMethod(self.url, self.payload)



    @allure.step
    def post_reports_request_dpr_falcon_jobs(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(REPORTS, headers=headers, cookies=cookies, data=json.dumps(payload))

        return res

    @allure.step
    def get_all_reports(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REPORTS, headers=self.headers, cookies=cookies, params=payload)

        return res

    @allure.step
    def get_all_programs(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PROGRAMS, headers=self.headers, cookies=cookies, params=payload)

        return res

    @allure.step
    def get_metrics(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(METRICS, headers=self.headers, cookies=cookies, params=payload)
        return res

    @allure.step
    def get_wbr_metrics_mapping(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(WBR_METRIC_MAPPINGS, headers=self.headers, cookies=cookies, params=payload)
        return res