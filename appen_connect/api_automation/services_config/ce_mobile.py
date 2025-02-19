import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.ce_mobile import *


class CE_MOBILE_API:
    def __init__(self, token=None, payload=None, custom_url=None, headers=None, cookies=None, env=None):
            self.payload = payload
            self.cookies = cookies

            if env is None and custom_url is None: env = pytest.env
            self.env = env

            if custom_url is not None:
                self.url = custom_url
            else:
                self.url = URL(env=pytest.env)

            if not headers:
                self.headers = {
                    "Content-Type": "application/json, text/plain, */*'",
                    "Cache-Control": "no-cache",
                    "Authorization": "Bearer {}".format(token)
                }

            self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_all_vendor_projects(self, vendor_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(GET_ALL_PROJECTS % vendor_id, headers=self.headers, cookies=cookies)
        return res


