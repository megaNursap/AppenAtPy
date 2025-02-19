from adap.api_automation.services_config.endpoints.cds_endpoints import *
from adap.api_automation.utils.http_util import HttpMethod
import pytest
import allure
import logging
import json

LOGGER = logging.getLogger(__name__)


class CDS:
    def __init__(self, custom_url=None, env=None, jwt=None):
        if env is None and custom_url is None: env = pytest.env
        self.env = env
        self.url = custom_url if custom_url else URL.format(env=env)
        self.service = HttpMethod(self.url)
        self.headers = {
            'Accept':'*/*',
            'Content-Type':'application/json',
            'x-appen-jwt': jwt,
        }

    @allure.step
    def get_proxy(self, team_id, path):
        return self.service.get(
            PROXY.format(
                team_id=team_id,
                path=path
            ),
            headers=self.headers,
            ep_name=PROXY)

    @allure.step
    def put_proxy(self, team_id, path, data):
        return self.service.put(
            PROXY.format(
                team_id=team_id,
                path=path
            ),
            headers=self.headers,
            data=json.dumps(data),
            ep_name=PROXY)

    @allure.step
    def delete_proxy(self, team_id, path):
        return self.service.delete(
            PROXY.format(
                team_id=team_id,
                path=path
            ),
            headers=self.headers,
            ep_name=PROXY)

    @allure.step
    def get_link(self, team_id, path):
        return self.service.get(
            LINK.format(
                team_id=team_id,
                path=path
            ),
            headers=self.headers,
            ep_name=LINK)

    @allure.step
    def put_link(self, team_id, path):
        return self.service.put(
            LINK.format(
                team_id=team_id,
                path=path
            ),
            allow_redirects=False,
            headers=self.headers,
            ep_name=LINK)

    @allure.step
    def delete_link(self, team_id, path):
        return self.service.delete(
            LINK.format(
                team_id=team_id,
                path=path
            ),
            headers=self.headers,
            allow_redirects=False,
            ep_name=LINK)

    @allure.step
    def get_all_managed_buckets(self):
        return self.service.get(
            MANAGED_BUCKETS,
            headers=self.headers,
            ep_name=MANAGED_BUCKETS)

    @allure.step
    def get_team_managed_buckets(self, team_id=None):
        return self.service.get(
            TEAM_MANAGED_BUCKETS.format(
                team_id=team_id),
            headers=self.headers,
            ep_name=TEAM_MANAGED_BUCKETS)

    @allure.step
    def create_managed_bucket(self, data: dict):
        res = self.service.post(
            MANAGED_BUCKETS,
            data=json.dumps(data),
            headers=self.headers,
            ep_name=MANAGED_BUCKETS)
        return res

    @allure.step
    def update_managed_bucket(self, team_id, data: dict):
        res = self.service.put(
            TEAM_MANAGED_BUCKETS.format(
                team_id=team_id),
            data=json.dumps(data),
            headers=self.headers,
            ep_name=TEAM_MANAGED_BUCKETS)
        return res

    @allure.step
    def delete_managed_bucket(self, team_id=None):
        res = self.service.delete(
            TEAM_MANAGED_BUCKETS.format(
                team_id=team_id),
            headers=self.headers,
            ep_name=TEAM_MANAGED_BUCKETS)
        return res

    @allure.step
    def request_token(self, team_id, path, expires_in):
        res = self.service.get(
            REQUEST_TOKEN.format(
                team_id=team_id,
                path=path,
                expires_in=expires_in
                ),
            headers=self.headers,
            ep_name=REQUEST_TOKEN)
        return res

    @allure.step
    def redeem_token(self, token):
        res = self.service.get(
            REDEEM_TOKEN.format(
                token=token),
            headers=self.headers,
            ep_name=REDEEM_TOKEN)
        return res

    @allure.step
    def generate_url(self, params):
        res = self.service.get(
            GENERATE_URL,
            headers=self.headers,
            params=params,
            ep_name=GENERATE_URL)
        return res

    @allure.step
    def get_team_storage_providers(self, team_ids=[]) -> list:
        return self.service.get(
            STORAGE_PROVIDERS,
            headers=self.headers,
            params={'team_ids': team_ids},
            ep_name=STORAGE_PROVIDERS)

    @allure.step
    def get_all_storage_providers(self) -> list:
        return self.service.get(
            STORAGE_PROVIDERS,
            headers=self.headers,
            ep_name=STORAGE_PROVIDERS)

    @allure.step
    def update_storage_provider_status(self, storage_provider_id: str, status: str):
        """
        status: active/pending
        """
        res = self.service.put(
            STORAGE_PROVIDER_STATUS.format(sp_id=storage_provider_id),
            data={'status': status},
            headers={},
            ep_name=STORAGE_PROVIDER_STATUS)
        return res
