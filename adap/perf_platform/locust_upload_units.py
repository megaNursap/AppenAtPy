from adap.settings import Config
from utils.custom_locust import CustomLocust, event_monitor_users_count
from utils.logging import get_logger
from locust import TaskSet, task, between, events
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.perf_platform.utils.results_handler import get_task_info
from adap.api_automation.services_config.builder import Builder

log = get_logger(__name__, stdout=False)
events.master_start_hatching += event_monitor_users_count

num_units = Config.NUM_UNITS
user = get_user('perf_platform')
job_data = jobs_data.get(Config.JOB_TYPE)
assert job_data, f'Config for JOB_TYPE {Config.JOB_TYPE}, ' \
                f'available types are: {jobs_data.keys()}'

data_generator = job_data['data_generator']

class LocustUserBehavior(TaskSet):
    def upload_units(self, job_id):
        builder = Builder(user['api_key'], env=Config.ENV, job_id=job_id)
        log.info(f"Adding {num_units} units to the job {job_id}")
        units_fp = data_generator(num_units, filename='/tmp/units.csv')
        res = builder.upload_data(units_fp, data_type='csv')
        assert res.status_code == 200, res.content

    @task()
    def caller(self):
        global job_id
        task = self.upload_units
        self.client.locust_event(
            "Request",  # Requst type
            task.__name__,  # Requst name
            task,
            job_id
            )

class LocustUser(CustomLocust):
    wait_time = between(0.1, 0.2)  # wait time between tasks, in seconds
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
        except Exception as e:
            log.error(e.__repr__())
            raise

