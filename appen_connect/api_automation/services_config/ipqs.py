import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.ipqs import *


class AC_IPQS_API:

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
    def get_healthcheck(self,  cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(HEALTHCHECK, headers=self.headers, cookies=cookies)
        return res

    @allure.step
    def get_check_ip(self, ip, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(CHECK_IP.format(ip=ip), headers=self.headers, cookies=cookies)
        return res


