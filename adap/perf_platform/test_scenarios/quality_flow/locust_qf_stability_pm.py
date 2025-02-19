import threading, decouple, traceback
from adap.api_automation.utils.data_util import *
from locust import TaskSet, task, between, events
from locust.exception import StopLocust
os.environ.setdefault("LOGGER_PERF", "True")
from adap.api_automation.services_config.qf_api_logic import *
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from gevent._semaphore import Semaphore
from adap.api_automation.utils.data_util import get_test_account_data_generally, get_user_team_id
from adap.api_automation.services_config.qf_api_logic import TestType, EnvType, JobType, QualityFlowApiSingletonManager

# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching

env = decouple.config('ENV', default='integration', cast=str)  # 'sandbox'
qa_key = decouple.config('QA_KEY', default='None', cast=str)
PM_USERNAME = get_test_account_data_generally('qf_stability', 'user_name', env=env, key=qa_key)
PM_PASSWORD = get_test_account_data_generally('qf_stability', 'password', env=env, key=qa_key)
PM_TEAM_ID = get_test_account_data_generally('qf_stability', 'teams', env=env, key=qa_key)[0]['id']

project_id = decouple.config('QF_PROJECT_ID', default='None', cast=str)
unit_type = decouple.config('QF_UNIT_TYPE', default='None', cast=str)
work_job_id = decouple.config('QF_WORK_JOB_ID', default='None', cast=str)
qa_job_id = decouple.config('QF_QA_JOB_ID', default='None', cast=str)
QF_MAX_LOOP = int(decouple.config('QF_MAX_LOOP', default='10', cast=str))
QF_UPLOAD_UNIT_NUM_PER_ROUND = int(decouple.config('QF_UPLOAD_UNIT_NUM_PER_ROUND', default='10', cast=str))
QF_SEGMENTED_GROUP_NUM = int(decouple.config('QF_SEGMENTED_GROUP_NUM', default='10', cast=str))

PROJECT_ID = project_id
WORK_JOB_ID = work_job_id
TOTAL_PM_ROUND_LIST = list(range(0, QF_MAX_LOOP))
UPLOAD_UNIT_NUM_PER_ROUND = [QF_UPLOAD_UNIT_NUM_PER_ROUND] * len(TOTAL_PM_ROUND_LIST)

user_counter = 0
one_time_job_run_times = 0


class LocustUserBehavior(TaskSet):
    def on_start(self):
        global user_counter
        self.locust.qfm = QualityFlowApiSingletonManager
        self.locust.qfm.set_env(env, PM_TEAM_ID)
        self.locust.qfm.get_singleton_instance()
        self.locust.qfm.set_perf()
        self.locust.qfm.logic_qf_login(PM_USERNAME, PM_PASSWORD)

        log.info({
            "msg": "on start"
        })

        user_counter += 1

    @task()
    def simulate_pm_action(self):
        global one_time_job_run_times
        one_time_job_run_times += 1
        log.info(f'Thread {threading.currentThread().getName()} Start')

        if one_time_job_run_times == 1:
            for i in range(len(TOTAL_PM_ROUND_LIST)):
                log.info(f'Thread {threading.currentThread().getName()} Start - Round {TOTAL_PM_ROUND_LIST[i] + 1}')
                time.sleep(random.randint(20, 30))
                try:
                    if unit_type == "SEGMENTED":
                        gcc = {'num_rows': UPLOAD_UNIT_NUM_PER_ROUND[i], 'segmentation': True,
                               'num_group': QF_SEGMENTED_GROUP_NUM,
                               'header_size': 3, 'save_path': None}
                    elif unit_type == "UNIT_ONLY":
                        gcc = {'num_rows': UPLOAD_UNIT_NUM_PER_ROUND[i], 'segmentation': False,
                               'num_group': UPLOAD_UNIT_NUM_PER_ROUND[i],
                               'header_size': 3, 'save_path': None}
                    else:
                        log.error(f"Wrong UNIT_TYPE: {unit_type}")
                    unit_number = self.locust.qfm.logic_pm_upload_units(PROJECT_ID, env, TOTAL_PM_ROUND_LIST[i] + 1, gcc=gcc)
                except Exception as r:
                    log.error(f'pm_upload_units: {str(r)}')
                    traceback.print_exc()
                    time.sleep(60)
                time.sleep(random.randint(20, 30))
                try:
                    # self.locust.qfm.logic_pm_send_units_to_job(PROJECT_ID, WORK_JOB_ID, i + 1, unit_number=unit_number)
                    self.locust.qfm.logic_pm_send_all_new_units_to_job(PROJECT_ID, WORK_JOB_ID)
                except Exception as r:
                    log.error(f'pm_send_units_to_job: {str(r)}')
                    traceback.print_exc()
                    time.sleep(60)
                time.sleep(random.randint(20, 30))
                log.info(f'Thread {threading.currentThread().getName()} End - Round {TOTAL_PM_ROUND_LIST[i] + 1}')
            log.info(f'Thread {threading.currentThread().getName()} End')
            log.info(f'PM tasks finished.')
        else:
            log.info(f'Job Finished.')
            time.sleep(36000)
            # exit(0)


class LocustUser(CustomLocust):
    wait_time = between(0, 0)
    task_set = LocustUserBehavior
    worker_id = None

    def __init__(self):
        super(LocustUser, self).__init__()

    def setup(self):
        log.info({
            "msg": "setup"
        })

    def teardown(self):
        log.info({
            "msg": "teardown"
        })
