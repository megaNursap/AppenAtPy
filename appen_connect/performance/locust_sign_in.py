from locust import TaskSet, task, between, events
from appen_connect.api_automation.services_config.core import Core
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils import custom_locust
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config
import pandas
import random
import pytest

pytest.appen = 'true'
env = Config.ENV
log = get_logger(__name__, stdout=False)

# Start ZMQ data feeder on master
if CustomLocust.is_master():
    events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if CustomLocust.is_slave():
    if Config.WORKLOAD:
        events.locust_start_hatching += on_worker_listener

data_source_path = 'appen_connect/data/test_users_stage_example.com.csv'
default_password = get_user('default', env=env).get('password')

class LocustUserBehavior(TaskSet):

    def _signin(self):
        # self.user = request_feed()
        self.user = globals()['workers'].pop()
        core = Core(env=env)
        core.sign_in(
            username=self.user.get('worker_email'),
            password=default_password
        )

    @task()
    def signin(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "sme_find_projects",  # Requst name
            self._signin,
            )

class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        df = pandas.read_csv(data_source_path)
        globals()['workers'] =  df.to_dict('records')
