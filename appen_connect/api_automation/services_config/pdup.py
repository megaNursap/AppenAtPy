import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.pdup import *


class AC_PDUP_API:

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

#This is not a valid endpoint and returns 404 now.
    @allure.step
    def post_check_pdup(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.post(CHECK_WORKER, headers=self.headers, cookies=cookies, data=json.dumps(payload))

        return res

    @allure.step
    def get_check_pdup_by_worker_id(self, worker_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(CHECK_WORKER_BY_ID.format(worker_id=worker_id), headers=self.headers, cookies=cookies)
        return res


    @allure.step
    def get_check_pdup_attributes_by_worker_id(self, worker_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(CHECK_ATTRIBUTE.format(worker_id=worker_id), headers=self.headers, cookies=cookies)
        return res

    @allure.step
    def get_pdup_healthcheck(self, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(HEALTHCHECK, headers=self.headers, cookies=cookies)
        return res
