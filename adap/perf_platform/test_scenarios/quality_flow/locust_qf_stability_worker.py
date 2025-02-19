import threading, queue, decouple, traceback, time
from adap.api_automation.utils.data_util import *
from locust import TaskSet, task, between, events
os.environ.setdefault("LOGGER_PERF", "True")
# from adap.api_automation.services_config.qf_api_logic import *
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from gevent._semaphore import Semaphore
from adap.api_automation.utils.data_util import get_test_account_data_generally, get_user_team_id
from adap.api_automation.services_config.qf_api_logic import TestType, EnvType, JobType, DataType, \
    QualityFlowApiSingletonManager, CommitPayloadType, UnitGroupOption
from faker import Faker
faker = Faker()

# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching

audio_tx_judgment = {
    "9b3a820d-d389-48ab-a03c-b968f26da5b7": {  # X-ER ADD
        "WORK": {
            "storageType": "CDS",
            "teamId": "acdac212-8e03-49a9-99cb-dd157ccabe29",
            "value": '{\"type\":\"audio_transcription\",\"valueRef\":\"jobs/13fad504-2991-4e4f-9e04-7e2e9e0db6de/annotations/9b3a820d-d389-48ab-a03c-b968f26da5b7.json\"}'
        },
        "QA": {
            "storageType": "CDS",
            "teamId": "acdac212-8e03-49a9-99cb-dd157ccabe29",
            "value": '{\"type\":\"audio_transcription\",\"valueRef\":\"jobs/13fad504-2991-4e4f-9e04-7e2e9e0db6de/annotations/9d8fbb9b-d8e4-4b1f-ae55-0ee20d6264f6.json\",\"metadata\":{\"qaResult\":\"modified\"}}'
        }
    },
    "fdb2ebf6-30df-4a93-b607-44e249fedbe4": {  # X-ER DEL
        "WORK": {
            "storageType": "CDS",
            "teamId": "acdac212-8e03-49a9-99cb-dd157ccabe29",
            "value": '{\"type\":\"audio_transcription\",\"valueRef\":\"jobs/13fad504-2991-4e4f-9e04-7e2e9e0db6de/annotations/fdb2ebf6-30df-4a93-b607-44e249fedbe4.json\"}'
        },
        "QA": {
            "storageType": "CDS",
            "teamId": "acdac212-8e03-49a9-99cb-dd157ccabe29",
            "value": '{\"type\":\"audio_transcription\",\"valueRef\":\"jobs/13fad504-2991-4e4f-9e04-7e2e9e0db6de/annotations/da829df3-dd0c-40c2-a1e1-d35a5e116bd6.json\",\"metadata\":{\"qaResult\":\"modified\"}}'
        }
    },
    "40071332-03d4-4c9f-b683-a86806c4776c": {  # X-ER CHANGE
        "WORK": {
            "storageType": "CDS",
            "teamId": "acdac212-8e03-49a9-99cb-dd157ccabe29",
            "value": '{\"type\":\"audio_transcription\",\"valueRef\":\"jobs/13fad504-2991-4e4f-9e04-7e2e9e0db6de/annotations/40071332-03d4-4c9f-b683-a86806c4776c.json\"}'
        },
        "QA": {
            "storageType": "CDS",
            "teamId": "acdac212-8e03-49a9-99cb-dd157ccabe29",
            "value": '{\"type\":\"audio_transcription\",\"valueRef\":\"jobs/13fad504-2991-4e4f-9e04-7e2e9e0db6de/annotations/70f792d0-4b73-497e-b967-7abf80daba48.json\",\"metadata\":{\"qaResult\":\"modified\"}}'
        }
    }
}

env = decouple.config('ENV', default='integration', cast=str)  # 'sandbox'
PM_USERNAME = get_test_account_data_generally('qf_stability', 'user_name', env=env)
PM_PASSWORD = get_test_account_data_generally('qf_stability', 'password', env=env)
PM_TEAM_ID = get_test_account_data_generally('qf_stability', 'teams', env=env)[0]['id']
CONTRIBUTOR = get_test_account_data_generally('qf_stability', 'contributor', env=env)
WORKER_ID_LIST = [x['contributor_id'] for x in CONTRIBUTOR['workers']]

qfm = QualityFlowApiSingletonManager
qfm.set_env(env, PM_TEAM_ID)
qfm.get_singleton_instance()
qfm.set_perf()
qfm.logic_qf_login(PM_USERNAME, PM_PASSWORD)

project_id = decouple.config('QF_PROJECT_ID', default='None', cast=str)
work_job_id = decouple.config('QF_WORK_JOB_ID', default='None', cast=str)
qa_job_id = decouple.config('QF_QA_JOB_ID', default='None', cast=str)
QF_WORKING_SECONDS_PER_TASK_PAGE = int(decouple.config('QF_WORKING_SECONDS_PER_TASK_PAGE', default='1', cast=str))
QF_WORKER_FEEDBACK_RESULT_LIST = decouple.config('QF_WORKER_FEEDBACK_RESULT_LIST', default='ACCEPTED', cast=str)
QF_WORKER_ABANDON_PERCENTAGE = int(decouple.config('QF_WORKER_ABANDON_PERCENTAGE', default='0', cast=str))
QF_DATA_TYPE = decouple.config('QF_DATA_TYPE', default=DataType.AudioTX, cast=str)
QF_UNIT_TYPE = decouple.config('QF_UNIT_TYPE', default='UNIT_ONLY', cast=str)
QF_UNIT_GROUP_OPTION = decouple.config('QF_UNIT_GROUP_OPTION', default='RETAIN', cast=str)

JUDGMENT_KEYS = ["audio_transcription"] if QF_DATA_TYPE == DataType.AudioTX else ["sample_text_area"]
AUTO_JUDGMENT = True if QF_DATA_TYPE == DataType.AudioTX else False

PROJECT_ID = project_id
WORK_JOB_ID = work_job_id

user_counter = 0


class LocustUserBehavior(TaskSet):
    def on_start(self):
        global user_counter

        log.info({
            "msg": "on start"
        })

        user_counter += 1
        self.locust.worker_id = self.parent.queue_data.get()
        self.locust.page_num = 1 if QF_UNIT_TYPE == 'SEGMENTED' and QF_UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
        self.locust.penalty, self.locust.last_penalty = 1, 1

    @task()
    def simulate_worker_action(self):
        log.info(f'Thread {threading.currentThread().getName()} Start')

        try:
            _, fetch_info = qfm.logic_distribution_fetch_and_submit(
                job_id=WORK_JOB_ID,
                worker_id=self.locust.worker_id,
                working_seconds_per_task_page=QF_WORKING_SECONDS_PER_TASK_PAGE,
                job_type=JobType.WORK,
                auto_judgment_source_col_name="audio_name",
                auto_judgment=AUTO_JUDGMENT,
                judgment_keys=JUDGMENT_KEYS,
                audio_tx_judgment=audio_tx_judgment,
                judgment={"sample_text_area": f"J - {faker.zipcode()} - {faker.city()}"},
                feedback_result_list=list(map(str.strip, QF_WORKER_FEEDBACK_RESULT_LIST.split(','))),
                abandon_percentage=QF_WORKER_ABANDON_PERCENTAGE,
                commit_payload_type=CommitPayloadType.AGG,
                data_type=QF_DATA_TYPE,
                fetch_page_num=self.locust.page_num
            )
            if fetch_info is not None:
                if self.locust.page_num is not None:
                    if fetch_info.get("abandon_flag"):
                        self.locust.page_num = 1 if QF_UNIT_TYPE == 'SEGMENTED' and QF_UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
                    else:
                        total = fetch_info.get("fetch_total_pages")
                        self.locust.page_num = self.locust.page_num + 1 if type(total) == int and self.locust.page_num < total else 1
                if fetch_info.get("fetch_dist_num") == 0:
                    log.info(f'Wait for {self.locust.penalty} seconds for nothing to be fetched.')
                    time.sleep(self.locust.penalty)
                    self.locust.penalty, self.locust.last_penalty = (self.locust.penalty + self.locust.last_penalty) % 60, self.locust.penalty
                else:
                    self.locust.penalty, self.locust.last_penalty = 1, 1
            else:
                log.error(f"Fetch info is None.")
        except Exception as r:
            traceback.print_exc()
            if r.__class__.__name__ == "AssertionError" and\
                    'code[5006], msg[There are unfinished units in some pages. You need to finish them all before submission. Please check again!]' in r.args[0]:
                self.locust.page_num = 1
            pass

        log.info(f'Thread {threading.currentThread().getName()} End')


class LocustUser(CustomLocust):
    wait_time = between(0, 0)
    task_set = LocustUserBehavior
    queue_data = queue.Queue()
    for item in WORKER_ID_LIST:
        queue_data.put_nowait(item)

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
