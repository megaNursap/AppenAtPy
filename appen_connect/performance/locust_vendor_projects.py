from locust import TaskSet, task, between, events
from appen_connect.api_automation.services_config.identity_service import IdentityService
from appen_connect.api_automation.services_config.ac_project_service import ProjectServiceAPI
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
# this is needed for data_util
import pytest
pytest.appen = 'true'

env = Config.ENV
log = get_logger(__name__, stdout=False)

# Start ZMQ data feeder on master
if CustomLocust.is_master():
    username = get_user('performance_user').get('user_name')
    password = get_user('performance_user').get('password')
    token = IdentityService(env)\
        .get_token(
            username=username,
            password=password)\
        .json_response.get('access_token')
    custom_locust.INPUT_DATA = [{'token': token} for i in range(1000)]
    events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if CustomLocust.is_slave():
    if Config.WORKLOAD:
        events.locust_start_hatching += on_worker_listener

# data_source_path = 'appen_connect/data/test_users_stage_example.com.csv'
# data_source_path = 'appen_connect/data/proj_5375_vendors.csv'
data_source_path = 'appen_connect/data/proj_5375_vendors_2.csv'

# data_source_path = 'appen_connect/data/proj_no_5375_vendors.csv'
# data_source_path = 'appen_connect/data/ac_accounts_stage.csv'  # 100


class LocustUserBehavior(TaskSet):

    def on_start(self):
        token = request_feed('token')
        self.service = ProjectServiceAPI(token, env=env)

    def _get_projects(self):
        vendor_id = random.choice(globals()['workers']).get('id')
        res = self.service.get_vendor_project_all(vendor_id)

    @task()
    def get_projects(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "sme_find_projects",  # Requst name
            self._get_projects,
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
