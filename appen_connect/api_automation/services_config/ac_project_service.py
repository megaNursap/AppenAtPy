import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.project_service import *


class ProjectServiceAPI:

    def __init__(self, token=None, cookies=None, payload=None, custom_url=None, headers=None, env=None):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(self.env)

        if not headers:
            self.headers = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Authorization": "Bearer {}".format(token)
            }

        self.service = HttpMethod(self.url, self.payload)


    @allure.step
    def get_vendor_project_all(self, user_id, cookies=None, **kwargs):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(VENDOR_PROJECT_LIST.format(userId=user_id), headers=self.headers, cookies=cookies,
                               ep_name=VENDOR_PROJECT_LIST, **kwargs)
        return res

    @allure.step
    def get_countries_available_list(self, language_code, **kwargs):
        header = {
            "Content-Type": "application/json",
        }
        res = self.service.get(COUNTRIES_LIST.format(languageCode=language_code), headers=header,
                               ep_name=COUNTRIES_LIST, **kwargs)
        return res
