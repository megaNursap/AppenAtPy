import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from bs4 import BeautifulSoup

from appen_connect.api_automation.services_config.endpoints.keycloak import *


class Keycloak:
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
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache"
            }
        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def retrieve_token(self, payload):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res = self.service.post(TOKEN, headers=headers, data=payload)
        return res

    @allure.step
    def get_user_info(self, headers):
        res = self.service.get(USER, headers=headers)
        return res
