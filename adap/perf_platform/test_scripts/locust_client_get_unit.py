"""
DOESNT WORK AS EXPECTED
"""
from locust import TaskSet, task, between, events
from adap.api_automation.services_config.client import Client
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.utils.results_handler import get_task_info
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.helpers import (
    get_job_id_from_tasks_info, get_job_unit_ids
)
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config
import random

log = get_logger(__name__, stdout=False)

env = Config.ENV

user_password = get_user('perf_platform').get('password')

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.adap_client = Client(env=env)
        self.user_email = request_feed('user_email')
        self.adap_client.sign_in(self.user_email, user_password)
        self.adap_client.service.get(
            f'https://client.integration.cf3.us/jobs/{job_id}'
        )

    def get_unit(self):
        global job_id, unit_ids
        self.adap_client.get_unit(
            job_id=job_id,
            unit_id=random.choice(unit_ids)
        )

    @task()
    def work(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "GetUnit",  # Requst name
            self.get_unit
        )


class LocustUser(CustomLocust):
    wait_time = between(0.1, 1.0)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        """ Locust setup """
        try:
            global job_id, unit_ids
            job_id = get_job_id_from_tasks_info()
            log.info({
                'message': 'Assigned job_id',
                'job_id': job_id
                })
            unit_ids = get_job_unit_ids(job_id)
        except Exception as e:
            log.error(e.__repr__())
            raise

    def teardown(self):
        """ Locust teardown """
        # log.info(f"Locust Teardown: TBD")
