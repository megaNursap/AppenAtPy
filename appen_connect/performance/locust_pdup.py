# import faulthandler; faulthandler.enable()
import json
import os
from urllib.parse import urlencode

from locust import TaskSet, task, between, events

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
import random
import pytest


pytest.appen = 'true'

log = get_logger(__name__, stdout=False)

env  = os.environ['ENV']

base_urls = {
    'stage': 'https://maas-ts-pdup-stage.appen.io'
}

endpoint = "/duplicates/check/worker/"

events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


if Config.DATA_SOURCE_PATH:
    log.debug("Reading input data...")
    sdr = SourceDataReader(Config.DATA_SOURCE_PATH)
    INPUT_DATA = sdr.read()
    random.shuffle(INPUT_DATA)
    log.debug(f"{len(INPUT_DATA)} records read")


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.base_url = base_urls[env]
        self.service = HttpMethod()

    def get_user_id(self):
        row = random.choice(INPUT_DATA)
        _id = row.get('user_id')
        assert _id, 'user_id not found in data source'
        return str(_id)

    def _potential_duplicates(self):
        user_id = self.get_user_id()
        payload = {
          "worker_id": user_id,
          "max_user_count": 10,
          "sort": "desc",
          "exclude": [],
          "include_false_positives": 'false'
        }
        resp = self.service.post(
            self.base_url+endpoint,
            headers={'Content-Type': 'application/json',
                     'accept': 'application/json'},
            data=json.dumps(payload),
            ep_name='/duplicates/check/worker'
            )

        if resp.status_code == 404:
            if resp.json_response.get('message') and \
                    (f'Worker {user_id} not found!'.format(user_id=user_id) != resp.json_response['message']):

                log.error({
                    'message': f'Error response: "Worker {user_id} not found!"'.format(user_id=user_id),
                    'resp.status_code': resp.status_code,
                    'resp.status_message': getattr(resp, 'status_message', ''),
                    'resp.text': getattr(resp, 'text', ''),
                    'resp.url': getattr(resp, 'url', ''),
                    'user_id': user_id,
                    'endpoint': (self.base_url + endpoint)
                })
                return

        if resp.status_code not in [200, 404]:
            log.error({
                'message': 'Error response',
                'resp.status_code': resp.status_code,
                'resp.status_message': getattr(resp, 'status_message', ''),
                'resp.text': getattr(resp, 'text', ''),
                'resp.url': getattr(resp, 'url', ''),
                'user_id': user_id,
                'endpoint': (self.base_url + endpoint)
                })
            return


    @task(20)
    def pdup(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "pdup",  # Requst name
            self._potential_duplicates,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

