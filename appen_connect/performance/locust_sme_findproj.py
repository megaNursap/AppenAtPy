from appen_connect.api_automation.services_config.ac_sme import SME

from locust import TaskSet, task, between, events
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config
import requests
import random
import pandas
import os

env = Config.ENV
log = get_logger(__name__, stdout=False)

events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.service = SME(env=env)

    def _findproj(self):
        if not globals().get('worker_ids'):
            globals()['worker_ids'] = globals()['worker_ids_src'].copy()
        worker_id = globals()['worker_ids'].pop()
        data = {
            "workerId": worker_id,
            "rankFactor": "bestMatch",
            "maxReturnCount": 20,
            "hireGapThreshold": 0.0001,
            "useCase": "allWorkers",
            "is_QA_mode": True
        }
        resp = self.service.find_projects(data)
        # resultCount = resp.json_response.get('resultCount')
        # if not resultCount and resp.json_response.get('status') != 'NO_PROJECT_MATCH':
        #     log.error({
        #         'message': 'Invalid response',
        #         'resp.json_response': resp.json_response
        #     })

    def _healthcheck(self):
        resp = self.service.get_healthcheck()


    @task()
    def find_projects(self):
        if os.environ.get("SME_TASK") == 'healthcheck':
            task_func = self._healthcheck
        else:
            task_func = self._findproj
        self.client.locust_event(
            "Execute task",  # Requst type
            "sme_find_projects",  # Requst name
            task_func,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
    
    def setup(self):
        part_id = request_feed('part_id')
        log.debug(f'data part_id: {part_id}')
        df = pandas.read_csv(f'appen_connect/data/sme_data/parts/{part_id}.csv')
        if LIMIT_WORKER_IDS := os.environ.get('LIMIT_WORKER_IDS'):
            df =  df[:int(LIMIT_WORKER_IDS)]
        globals()['worker_ids_src'] = df.to_dict('records')
        globals()['worker_ids'] = globals()['worker_ids_src'].copy()
