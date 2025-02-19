from adap.api_automation.utils.data_util import *
from locust import TaskSet, task, between, events
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.judgments import Judgments
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.utils.results_handler import get_task_info
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config
from adap.perf_platform.utils.data_feed import SourceDataReader
import random

# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)

env = Config.ENV
if env == 'integration':
    user = get_user('perf_platform2')
else:
    user = get_user('perf_platform')

api_key = user['api_key']
worker = get_user('adap_integration_users_for_performance')
worker_password = worker['password']

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


class LocustUserBehavior(TaskSet):
    def get_job_id(self):
        if Config.WF_JOB_ID:
            job_id = int(Config.WF_JOB_ID)
        else:
            info = get_task_info()
            if step := Config.WORKFLOW_STEP:
                job_id = info[0]['workflow_job_ids'][step - 1]
            elif Config.JOB_TYPE.startswith('TQG'):
                job_id = info[0]['tqg_job_id']
            else:
                job_id = info[0]['job_id']
        log.debug(f"Checking that job {job_id} is running...")
        Builder(api_key, env=env, job_id=job_id).wait_until_status2('running')
        return job_id

    def get_worker_email(self):
        """ Request a new worker email from locust master """
        # email = request_feed('worker_email')
        # return email
        log.info("Get worker email from csv")
        workers_list = SourceDataReader(Config.DATA_SOURCE_PATH).read()
        worker_email = random.choice(workers_list).get('worker_email')
        return worker_email

    def submit_judgments_internal(self, job_id, worker_email):
        log.info({
            'message': 'Start Submit Judgments (internal) task',
            'worker_email': worker_email,
            'job_id': job_id
            })

        j = Judgments(worker_email, worker_password, env=env, internal=True)
        job_link = generate_job_link(job_id, api_key, env)
        assignment_page = j.get_assignments(internal_job_url=job_link, job_id=job_id)
        j.contribute(assignment_page)

    def submit_judgments_external(self, job_id, worker_email):
        log.info({
            'message': 'Start Submit Judgments (external) task',
            'worker_email': worker_email,
            'job_id': job_id
            })

        j = Judgments(worker_email, worker_password, env=env)
        assignment_page = j.get_assignments(job_id)
        j.contribute(assignment_page)

    @task()
    def submit_judgments(self):
        job_id = self.get_job_id()
        log.info({
            'message': 'start submitting judgements',
            'job_id': job_id
        })
        worker_email = self.get_worker_email()
        if Config.EXTERNAL:
            task = self.submit_judgments_external
        else:
            task = self.submit_judgments_internal

        log.info(f"Submit judgements task: {task}")
        self.client.locust_event(
            "Execute task",  # Requst type
            "SubmitJudgments",  # Requst name
            task,
            job_id,
            worker_email
            )


class LocustUser(CustomLocust):
    wait_time = between(0.1, 1.0)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        """ Locust setup """
        log.info({
                'message': 'Locust setup'
                })

    def teardown(self):
        """ Locust teardown """

        # log.info(f"Locust Teardown: TBD")