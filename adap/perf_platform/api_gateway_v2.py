import os

from locust import TaskSet, task, between, events

from adap.api_automation.services_config.customer_data_service import CDS
from adap.api_automation.utils.data_util import get_user, decrypt_user_new_password
from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.http_client import HTTPClient
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
)
from adap.perf_platform.utils.data_feed import SourceDataReader
from adap.settings import Config
from uuid import uuid4
import requests
import random
# this is needed for data_util
import pytest
import subprocess
import json
from urllib.parse import urlencode

log = get_logger(__name__, stdout=False)

env = os.environ['ENV']

URL = "https://api.{}.cf3.us".format(env)


events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


endpoints = [
    "/v1/account.json",
    # "/auth",
    # "/v1/redeem_token",
    "/v1/jobs.json",
    "/v2/jobs",
    "/v2/workflows"
]



if Config.DATA_SOURCE_PATH:
    log.debug("Reading input data...")
    sdr = SourceDataReader(Config.DATA_SOURCE_PATH)
    INPUT_DATA = sdr.read()
    random.shuffle(INPUT_DATA)
    log.debug(f"{len(INPUT_DATA)} records read")


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.base_url = URL
        self.service = HttpMethod()
        row = random.choice(INPUT_DATA)
        _api_key = row.get('api_key')
        assert _api_key, 'api_key not found in data source'
        self.team_id = row.get('team_id')
        self.account = row.get('account')
        self.api_key = decrypt_user_new_password(_api_key, key=Config.KEY)
        self.headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }

    def _ping_endpoint(self, _endpoint):
        resp = self.service.get(
            self.base_url + _endpoint,
            headers=self.headers,
            ep_name=_endpoint
        )

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': _endpoint
            })
            return


    def _get_account(self):
        self._ping_endpoint("/v1/account.json")

    def _get_jobs_v1(self):
        self._ping_endpoint("/v1/jobs.json")

    def _get_jobs_v2(self):
        self._ping_endpoint("/v2/jobs")

    def _get_wf(self):
        self._ping_endpoint( "/v2/workflows")

    def _get_redeem_token(self):
        cds = CDS(env=env)
        resp = cds.request_token(team_id=self.team_id, path='jobs/3/units/3.json', expires_in=60)

        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/request_token?team_id"
            })
            return

        token = resp.text
        assert token.startswith('token='), f"Invalid token: {token}"

        resp = cds.redeem_token(token=token)
        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'account': self.account,
                'endpoint': "/v1/redeem_token"
            })
            return

    #     locust tasks
    @task
    def get_account_gateway(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "gateway",  # Requst name
            self._get_account,
        )

    @task
    def get_jobs_v1_gateway(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "gateway",  # Requst name
            self._get_jobs_v1,
        )

    @task
    def get_jobs_v2_gateway(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "gateway",  # Requst name
            self._get_jobs_v2,
        )

    @task
    def get_wfs(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "gateway",  # Requst name
            self._get_wf,
        )

    # @task
    # def get_redeem_token(self):
    #     self.client.locust_event(
    #         "Execute task",  # Requst type
    #         "gateway",  # Requst name
    #         self._get_redeem_token,
    #     )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
