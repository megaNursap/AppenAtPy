# import faulthandler; faulthandler.enable()

from locust import TaskSet, task, between, events
from adap.api_automation.utils.data_util import get_user
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
from adap.perf_platform.utils import results_handler
from adap.settings import Config
from uuid import uuid4
import requests
import random
# this is needed for data_util
import pytest
import subprocess
import json
from urllib.parse import urlencode

pytest.appen = 'true'

log = get_logger(__name__, stdout=False)

env = Config.ENV

base_urls = {
    'qa': 'https://identity-service-qa.sandbox.cf3.us',
    'stage': 'https://identity-stage.integration.cf3.us'
}
endpoint = "/auth/realms/QRP/protocol/openid-connect/token"

events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener

default_user = get_user('default', env=env)
password = default_user.get('password')
keycloak_client_secret = default_user.get('keycloak_client_secret')

expected_resp_fields = [
    'access_token',
    'expires_in',
    'refresh_expires_in',
    'refresh_token',
    'token_type',
    'id_token',
    'not-before-policy',
    'session_state',
    'scope',
    ]


if Config.DATA_SOURCE_PATH:
    log.debug("Reading input data...")
    sdr = SourceDataReader(Config.DATA_SOURCE_PATH)
    INPUT_DATA = sdr.read()
    random.shuffle(INPUT_DATA)
    log.debug(f"{len(INPUT_DATA)} records read")


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.base_url = base_urls[env]
        # self.service = HttpMethod(self.base_url)
        self.service = HTTPClient(self.base_url)

    def get_worker_email(self):
        row = random.choice(INPUT_DATA)
        email = row.get('worker_email')
        assert email, 'worker_email not found in data source'
        return email

    def _authentication(self):
        worker_email = self.get_worker_email()
        resp = self.service.post(
            self.base_url + endpoint,
            headers={'Content-Type':'application/x-www-form-urlencoded'},
            data=urlencode({
                'client_id': 'appen-mobile',
                'grant_type': 'password',
                'client_secret': keycloak_client_secret,
                'scope': 'openid',
                'username': worker_email,
                'password': password,
            }),
            ep_name='/token'
            )
        if resp.status_code != 200:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'worker_email': worker_email
                })
            return
        for ef in expected_resp_fields:
            if ef not in resp.json_response:
                log.error({
                    'message': f'Missing {ef} in response',
                    'resp.json': resp.json_response,
                    'worker_email': worker_email
                    })

    @task(20)
    def user_authentication(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "sso_sign_in",  # Requst name
            self._authentication,
            )

    def _curl(self):
        worker_email = self.get_worker_email()
        cmd = f"""
        curl -w "@scripts/one_offs/curl_format.txt" -o /dev/null -s  \
        -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
        -d "client_id=appen-mobile" \
        -d "grant_type=password" \
        -d "client_secret={keycloak_client_secret}" \
        -d "scope=openid" \
        -d "username={worker_email}" \
        -d "password={password}" \
        '{self.base_url}{endpoint}'
        """
        resp = subprocess.check_output(cmd, shell=1)
        res = json.loads(resp.decode('utf8'))
        for k, v in res.items():
            if k.startswith('time'):
                res[k] = round(float(v)*1000,2)
        info = {
            'endpoint_full': base_urls[env],
            'response': {
                'status_code': res['response_code']
            },
            'details': res
        }
        results_handler.save_to_db(
            rtype='post',
            ep_name='/token(extended)',
            duration=res['time_total'],
            info=info
            )


    # @task(1)
    # def curl(self):
    #     self.client.locust_event(
    #         "Execute task",  # Requst type
    #         "sso_sign_in",  # Requst name
    #         self._curl,
    #         )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
