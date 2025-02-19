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

default_password = get_user('default', env=env).get('password')
BASE_URL = f"https://connect-{env}.appen.com"
SERVICE_URL = BASE_URL + "/qrp/api/v2/services/user-service"
USER_PROFILE = "/users/{user_id}/profile"
DEMOGRAPHICS_COMPLEXIONS = '/demographics/complexions'
DEMOGRAPHICS_DISABILITY_TYPES = '/demographics/disability-types'
DEMOGRAPHICS_ETHNICITIES = '/demographics/ethnicities'
DEMOGRAPHICS_GENDERS = '/demographics/genders'
EDUCATION_LEVELS = '/education-levels'
LINGUISTICS_QUALIFICATION = '/linguistics-qualification'


class LocustUserBehavior(TaskSet):

    def setup(self):
        self.user = random.choice(globals()['workers'])
        core = Core(env=env)
        assert core.sign_in(
            username=self.user.get('worker_email'),
            password=default_password
        ).status_code == 200, "Unable to sign in"
        self.service = core.service
        self.service.base_url = SERVICE_URL

    def on_start(self):
        self.setup()

    def _get_user_profile(self):
        self.service.get(
            USER_PROFILE.format(
                user_id=self.user.get('id')),
            ep_name=USER_PROFILE
        )

    def _random_request(self):
        ep = random.choice([
            USER_PROFILE,
            DEMOGRAPHICS_COMPLEXIONS,
            DEMOGRAPHICS_DISABILITY_TYPES,
            DEMOGRAPHICS_ETHNICITIES,
            DEMOGRAPHICS_GENDERS,
            EDUCATION_LEVELS,
            LINGUISTICS_QUALIFICATION,
        ])
        if ep == USER_PROFILE:
            self._get_user_profile()
        else:
            self.service.get(
                ep,
                ep_name=ep
            )

        if random.random() > 0.99:
            self.setup()


    @task()
    def get_user_profile(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "sme_find_projects",  # Requst name
            self._get_user_profile,
            )

class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        # part_id = request_feed('part_id')
        # log.debug(f'data part_id: {part_id}')
        # df = pandas.read_csv(f'appen_connect/data/test_users_stage/{part_id}')
        data_source_path = 'appen_connect/data/ac_accounts_stage.csv'  # 100
        df = pandas.read_csv(data_source_path)
        globals()['workers'] =  df.to_dict('records')
