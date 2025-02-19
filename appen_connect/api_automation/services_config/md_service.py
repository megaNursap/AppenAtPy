import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.md_service import *


class AC_MD_API:

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
    def get_check_md_level_by_worker_id(self, worker_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(CHECK_WORKER_BY_ID.format(worker_id=worker_id), headers=self.headers, cookies=cookies)
        return res

    @allure.step
    def get_check_md_level_with_ip_by_worker(self, worker_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(CHECK_WORKER_IP.format(worker_id=worker_id), headers=self.headers, cookies=cookies)
        return res

    @allure.step
    def post_check_md_level_by_worker_list(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.post(CHECK_WORKER_LIST, headers=self.headers, cookies=cookies, data=json.dumps(payload))
        return res

    @allure.step
    def get_md_healthcheck(self, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(HEALTHCHECK, headers=self.headers, cookies=cookies)
        return res
