
from locust import TaskSet, task, between, events
from adap.ui_automation.services_config.application import Application
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.e2e_automation.services_config.judgments import Judgments
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user
from utils.results_handler import get_task_info
from utils.logging import get_logger
from utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config


# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)

env = Config.ENV

user = get_user('perf_platform')
api_key = user['api_key']
worker_password = user['worker_password']

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


class LocustUserBehavior(TaskSet):

    def get_worker_email(self):
        """ Request a new worker email from locust master """
        email = request_feed('worker_email')
        return email

    def start_browser(self):
        app = Application(env)
        app.driver.set_page_load_timeout(60)
        app.driver.implicitly_wait(30)
        return app

    def submit_judgments_internal(self, job_id, worker_email):
        log.info({
            'message': 'Start Submit Judgments (internal) task',
            'user_id': worker_email,
            'job_id': job_id
            })
        job_link = generate_job_link(job_id, api_key, env)
        app = self.start_browser()
        app.user.user_id = worker_email
        j = Judgments(app, worker_email, worker_password, env=env)
        j.sign_in()
        j.go_to_job(job_id, job_url=job_link)
        j.annotate(
            min_time_per_page=Config.WAIT_ON_ASSIGNMENT
            )
        log.info({
            'message': 'Finish Submit Judgments (internal) task',
            'user_id': worker_email,
            'job_id': job_id
            })

    def submit_judgments_external(self, job_id, worker_email):
        log.info({
            'message': 'Start Submit Judgments (external) task',
            'user_id': worker_email,
            'job_id': job_id
            })
        app = self.start_browser()
        app.user.user_id = worker_email
        j = Judgments(app, worker_email, worker_password, env=env)
        j.sign_in()
        j.go_to_job(job_id)
        j.annotate(
            min_time_per_page=Config.WAIT_ON_ASSIGNMENT
            )

    @task()
    def submit_judgments(self):
        global job_id
        worker_email = self.get_worker_email()
        if Config.EXTERNAL:
            task = self.submit_judgments_external
        else:
            task = self.submit_judgments_internal
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

        try:
            info = get_task_info()
            log.debug(f"Current task info: {info}")
            global job_id
            if step := Config.WORKFLOW_STEP:
                job_id = info[0]['workflow_job_ids'][step-1]
            else:
                job_id = info[0]['job_id']
            log.info({
                'message': 'Assigned job_id',
                'job_id': job_id
                })
            log.debug(f"Checking that job {job_id} is running...")
            Builder(api_key, env=env, job_id=job_id).wait_until_status2('running')
        except Exception as e:
            log.error(e.__repr__())
            raise

    def teardown(self):
        """ Locust teardown """

        # log.info(f"Locust Teardown: TBD")
