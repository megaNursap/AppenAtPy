import pytest
import allure
import json
from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.sme import *
from adap.perf_platform.utils.http_client import HTTPClient

class SME:

    def __init__(self, env=None, cookies=None, payload=None, custom_url=None, headers=None):
        self.payload = payload
        self.cookies = cookies

        if env is None:
            env = getattr(pytest, 'env', None)

        self.env = env

        if custom_url is not None:
            self.url = custom_url
        elif env == "prod":
            self.url = PROD
        else:
            self.url = URL.format(env)

        if not headers:
            self.headers = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
        }

        # self.service = HttpMethod(self.url, self.payload, session=True)
        self.service = HTTPClient(self.url)

    @allure.step
    def find_projects(self, payload):
        return self.service.post(
            FIND_PROJECT,
            headers=self.headers,
            data=json.dumps(payload),
            ep_name=FIND_PROJECT)

    @allure.step
    def get_worker_details(self, payload):
        return self.service.post(
            WORKER_DETAILS,
            headers={'Content-Type': 'text/plain'},
            data=json.dumps(payload),
            ep_name=WORKER_DETAILS
        )

    @allure.step
    def get_healthcheck(self):
        return self.service.get('/', ep_name=self.url)
