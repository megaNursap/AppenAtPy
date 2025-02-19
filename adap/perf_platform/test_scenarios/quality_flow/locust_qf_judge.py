import importlib
import threading
import os
import decouple
from adap.api_automation.utils.data_util import *
from locust import TaskSet, task, between, events
os.environ.setdefault("LOGGER_PERF", "True")
from adap.api_automation.services_config.qf_api_logic import *
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
from gevent._semaphore import Semaphore

# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener

START_ON_HATCH_COMPLETE = False
TRY_FETCH_BEFORE_HATCH_COMPLETE = False
STOP_LOCUST_IF_FAIL = False

if START_ON_HATCH_COMPLETE:
    all_locust_spawned = Semaphore()
    all_locust_spawned.acquire()


def on_hatch_complete(**kwargs):
    log.info("on hatch complete ***")
    all_locust_spawned.release()


if START_ON_HATCH_COMPLETE:
    events.hatch_complete += on_hatch_complete

faker = Faker()
_today = datetime.datetime.now().strftime("%Y_%m_%d")

perf_platform_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
g_contributor_list_path = os.path.join(perf_platform_dir, 'test_data/integration_contributor_IDs.csv')
Config.DATA_SOURCE_PATH = os.path.join(perf_platform_dir, 'test_data/integration_contributor_IDs.py')
qfm = QualityFlowApiSingletonManager
# env = EnvType.INTEGRATION
env = decouple.config('ENV', default='integration', cast=str)  # 'sandbox'
PM_USERNAME = get_test_account_data_generally('qf_perf', 'user_name', env=env)
PM_PASSWORD = get_test_account_data_generally('qf_perf', 'password', env=env)
PM_TEAM_ID = get_test_account_data_generally('qf_perf', 'teams', env=env)[0]['id']
qfm.set_env(env, PM_TEAM_ID)
qfm.get_singleton_instance()
qfm.set_perf()
qfm.logic_qf_login(PM_USERNAME, PM_PASSWORD)

project_id = decouple.config('QF_PROJECT_ID', default='None', cast=str)
work_job_id = decouple.config('QF_WORK_JOB_ID', default='None', cast=str)
qa_job_id = decouple.config('QF_QA_JOB_ID', default='None', cast=str)
worker_type = decouple.config('QF_WORKER_TYPE', default='WORK', cast=str)
dry_run = decouple.config('QF_DRY_RUN', default='False', cast=str)
QF_UNIT_TYPE = decouple.config('QF_UNIT_TYPE', default='UNIT_ONLY', cast=str)
QF_UNIT_GROUP_OPTION = decouple.config('QF_UNIT_GROUP_OPTION', default='RETAIN', cast=str)

slave_worker_counter = 0


def save_contributor_list_into_csv():
    csv_content = "worker_id,qa_1_worker_id\n"
    column_number = 2
    page_size = 50
    page_num = contributor_num // page_size if contributor_num % page_size == 0 else contributor_num // page_size + 1
    count = 0
    line = ""
    for i in range(1, page_num + 1):
        data = qfm.logic_curated_crowd_criteria_search_by_project_id(project_id, default_page_size=page_size, default_page_num=i)
        for item in data['content']:
            line += f"{item['contributorInfo']['contributorId']},"
            count += 1
            if count == column_number:
                csv_content += f"{line[:-1]}\n"
                line = ""
                count = 0
    if line != "":
        for j in range(count, column_number):
            line += ","
        csv_content += line

    with open(g_contributor_list_path, 'w') as f:
        f.write(csv_content)


def prepare_assign_contributor_list_to_job(project_id, job_id):
    page_size = 1000
    page_num = contributor_num // page_size if contributor_num % page_size == 0 else contributor_num // page_size + 1
    for i in range(1, page_num+1):
        contributor_list = []
        data = qfm.logic_curated_crowd_criteria_search_by_project_id(project_id, default_page_size=page_size, default_page_num=i)
        for item in data['content']:
            contributor_list.append(item['contributorInfo']['contributorId'])

        qfm.logic_curated_crowd_assign_contributor_to_job(project_id, contributor_list, job_id)


def fetch_task(job_id, worker_id, max_polling_times=200, interval=1, max_duration=30, page_num=None):
    if dry_run != 'True':
        try:
            fetch_result = qfm.logic_distribution_polling_fetch(job_id, worker_id, max_polling_times=max_polling_times,
                                                                interval=interval, max_duration=max_duration,
                                                                fetch_page_num=page_num)
            cost_time, data_dist = fetch_result.get("time"), fetch_result.get("dataDist")

            if data_dist is None:
                log.error(f"{worker_id} fetch result is None in limited time")
                assert data_dist is not None, "fetch result is None in limited time"
                assert data_dist, f'{data_dist}: distributions of fetched response is empty'
                for i in range(len(data_dist)):
                    assert data_dist[i]["segments"], f'{data_dist[i]["segments"]}: distribution segments of fetched response is empty'
            else:
                return {
                    "dataDist": data_dist,
                    "totalPages": fetch_result.get("totalPages")
                }
        except AssertionError as ae:
            raise AssertionError(str(ae)[:350])


def commit_task(worker_id, dist, commit_type='COMMIT'):
    if dry_run != 'True':
        try:
            data = qfm.logic_distribution_commit(worker_id, dist,
                                                 auto_judgment=False, auto_judgment_source_col_name="audio_name",
                                                 judgment_keys=["sample_text_area"],
                                                 judgment={
                                                     "sample_text_area": f"J - {faker.zipcode()} - {faker.city()}"},
                                                 audio_tx_judgment={}, commit_payload_type=CommitPayloadType.AGG,
                                                 commit_type=commit_type,
                                                 abandon_percentage=0, data_type=DataType.Textarea)
            data_dist = data["distributions"]
            assert data_dist, f'{data_dist}: distributions of committed response is empty'
            abandon_flag = False
            for i in range(len(data_dist)):
                assert data_dist[i]["segments"], f'{data_dist[i]["segments"]}: distribution segments of committed response is empty'
                for j in range(len(data_dist[i]["segments"])):
                    assert data_dist[i]["segments"][j]["distributionStatus"] == "COMMITTED", f'{data_dist[i]["segments"][j]["distributionStatus"]}: distributionStatus is not COMMITTED'
                    if data_dist[i]["segments"][j]["reviewResult"] == "ABANDONED":
                        abandon_flag = True
            return {
                "abandon_flag": abandon_flag
            }
        except AssertionError as ae:
            raise AssertionError(str(ae)[:350])


def review_task(worker_id, dist, review_result_list, feedback_result_list, job_type="QA", review_type="REVIEW"):
    if dry_run != 'True':
        try:
            data = qfm.logic_distribution_review(worker_id, dist, review_result_list=review_result_list,
                                                 job_type=job_type, feedback_result_list=feedback_result_list,
                                                 judgment_keys=["sample_text_area"], audio_tx_judgment={},
                                                 review_type=review_type,
                                                 abandon_percentage=0, data_type=DataType.Textarea)
            data_dist = data["distributions"]
            assert data_dist, f'{data_dist}: distributions of committed response is empty'
            for i in range(len(data_dist)):
                assert data_dist[i]["segments"], f'{data_dist[i]["segments"]}: distribution segments of committed response is empty'
                for j in range(len(data_dist[i]["segments"])):
                    assert data_dist[i]["segments"][j]["distributionStatus"] == "COMMITTED", f'{data_dist[i]["segments"][j]["distributionStatus"]}: distributionStatus is not COMMITTED'
                    if data_dist[i]["segments"][j]["reviewResult"] == "ABANDONED":
                        abandon_flag = True
                return {
                    "abandon_flag": abandon_flag
                }
        except AssertionError as ae:
            raise AssertionError(str(ae)[:350])


user_counter = 0


class LocustUserBehavior(TaskSet):
    def on_start(self):
        global user_counter

        log.info({
            "msg": "on start"
        })
        self.locust.page_num = 1 if QF_UNIT_TYPE == 'SEGMENTED' and QF_UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
        self.locust.penalty, self.locust.last_penalty = 1, 1
        user_counter += 1
        # Step 1. get worker id
        MAX_TRY = 10000
        count = 0
        worker_id, qa_1_worker_id = None, None
        while count < MAX_TRY:
            try:
                worker_id = request_feed('worker_id')
                qa_1_worker_id = request_feed('qa_1_worker_id')
            except AssertionError as ae:
                log.warning("Data queue is empty.")
                return
            if (worker_type == JobType.WORK and worker_id is not None) or (worker_type == JobType.QA and qa_1_worker_id is not None):
                log.info(f'Get worker_id successfully.')
                break
            else:
                log.error(f'Get worker_id None.')
                time.sleep(1)
                count += 1
        # worker_id = 'd01a01b5-aae4-4fb7-87c3-5c009a594b93'
        # qa_1_worker_id = 'd01a01b5-aae4-4fb7-87c3-5c009a594b93'
        log.info(f'request_feed: worker_id - {worker_id}, qa_1_worker_id - {qa_1_worker_id}')
        self.locust.worker_id = worker_id
        self.locust.qa_1_worker_id = qa_1_worker_id
        # Step 2. fetch tasks
        # worker_type = JobType.WORK
        if START_ON_HATCH_COMPLETE:
            if TRY_FETCH_BEFORE_HATCH_COMPLETE:
                if worker_type == JobType.WORK:
                    fetch_result = qfm.logic_distribution_polling_fetch(work_job_id, worker_id, max_polling_times=200,
                                                                        interval=5, max_duration=600,
                                                                        fetch_page_num=self.locust.page_num)
                    if fetch_result.get("dataDist") is not None:
                        log.info(f"The worker {self.locust.worker_id} fetch tasks complete.")
                    else:
                        log.error("Can't fetch units in limited time.")
                elif worker_type == JobType.QA:
                    fetch_result = qfm.logic_distribution_polling_fetch(qa_job_id, qa_1_worker_id, max_polling_times=200,
                                                                        interval=5, max_duration=600,
                                                                        fetch_page_num=self.locust.page_num)
                    if fetch_result.get("dataDist") is not None:
                        log.info(f"The worker {self.locust.qa_1_worker_id} fetch tasks complete.")
                    else:
                        log.error("Can't fetch units in limited time.")
            self.locust.user_no = user_counter
            log.info(f"The No. {user_counter} user get ready and wait for all locust spawned.")
            all_locust_spawned.wait()
        else:
            self.locust.user_no = user_counter
            log.info(f"The No. {user_counter} user get ready.")

    def worker_submit_judgment(self):
        log.info(f"Thread Name: {threading.currentThread().getName()}, USER_NO: {self.locust.user_no}, WORKER_ID: {self.locust.worker_id}")
        fetch_task_result = self.client.locust_event_enhanced(
            "Execute task",  # Request type
            "Dist Fetch",  # Request name
            fetch_task,
            work_job_id,
            self.locust.worker_id,
            max_polling_times=200,
            interval=1,
            max_duration=60,
            page_num=self.locust.page_num
        )
        log.info(f"Fetch task done. worker id: {self.locust.worker_id}")
        # gevent.sleep(random.randint(0, 1))  # working hours for each task page
        if fetch_task_result.get("dataDist") or dry_run:
            commit_tasks_result = self.client.locust_event_enhanced(
                "Execute task",  # Request type
                "Dist Commit",  # Request name
                commit_task,
                self.locust.worker_id,
                fetch_task_result.get("dataDist"),
                'COMMIT'
            )
            log.info(f"Worker commit task done. worker id: {self.locust.worker_id}")
            # Prepare for another fetch
            if fetch_task_result is not None:
                if self.locust.page_num is not None:
                    if commit_tasks_result is not None and commit_tasks_result.get("abandon_flag"):
                        self.locust.page_num = 1 if QF_UNIT_TYPE == 'SEGMENTED' and QF_UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
                    else:
                        total = fetch_task_result.get("totalPages")
                        self.locust.page_num = self.locust.page_num + 1 if type(
                            total) == int and self.locust.page_num < total else 1

                self.locust.penalty, self.locust.last_penalty = 1, 1
            else:
                log.error(f"Fetch info is None.")
        else:
            # gevent.sleep(1)  # If fetch nothing after submission, worker will wait for 1 second
            log.error('re-fetch')
            log.info(f'Wait for {self.locust.penalty} seconds for nothing to be fetched.')
            time.sleep(self.locust.penalty)
            self.locust.penalty, self.locust.last_penalty = (self.locust.penalty + self.locust.last_penalty) % 60, self.locust.penalty

    def qa_submit_judgment(self):
        log.info(f"Thread Name: {threading.currentThread().getName()}, USER_NO: {self.locust.user_no}, QA_WORKER_ID: {self.locust.qa_1_worker_id}")
        fetch_task_result = self.client.locust_event_enhanced(
            "Execute task",  # Request type
            "Dist Fetch",  # Request name
            fetch_task,
            qa_job_id,
            self.locust.qa_1_worker_id,
            max_polling_times=200,
            interval=1,
            max_duration=60,
            page_num=self.locust.page_num
        )
        total = fetch_task_result.get("totalPages")
        self.locust.page_num = self.locust.page_num + 1 if type(total) == int and self.locust.page_num < total else 1
        log.info(f"Fetch task done. QA worker id: {self.locust.qa_1_worker_id}")
        # gevent.sleep(random.randint(0, 1))  # working hours for each task page
        if fetch_task_result.get("dataDist") or dry_run:
            review_tasks_result = self.client.locust_event_enhanced(
                "Execute task",  # Request type
                "Dist Commit",  # Request name
                review_task,
                self.locust.qa_1_worker_id,
                fetch_task_result.get("dataDist"),
                ["ACCEPTED"],
                ["ACCEPTED"],
                "QA",
                "REVIEW"
            )
            log.info(f"QA worker review task done. worker id: {self.locust.qa_1_worker_id}")
            # Prepare for another fetch
            if fetch_task_result is not None:
                if self.locust.page_num is not None:
                    if review_tasks_result is not None and review_tasks_result.get("abandon_flag"):
                        self.locust.page_num = 1 if QF_UNIT_TYPE == 'SEGMENTED' and QF_UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
                    else:
                        total = fetch_task_result.get("totalPages")
                        self.locust.page_num = self.locust.page_num + 1 if type(
                            total) == int and self.locust.page_num < total else 1

                self.locust.penalty, self.locust.last_penalty = 1, 1
            else:
                log.error(f"Fetch info is None.")
        else:
            # gevent.sleep(1)  # If fetch nothing after submission, worker will wait for 1 second
            log.error('re-fetch')
            log.info(f'Wait for {self.locust.penalty} seconds for nothing to be fetched.')
            time.sleep(self.locust.penalty)
            self.locust.penalty, self.locust.last_penalty = (self.locust.penalty + self.locust.last_penalty) % 60, self.locust.penalty

    @task()
    def qf_submit_judgment(self):
        log.info(f"project_id: {project_id}, work_job_id: {work_job_id}"
                 f", qa_job_id: {qa_job_id}, worker_type: {worker_type}")
        if worker_type == JobType.WORK and self.locust.worker_id is not None:
            self.worker_submit_judgment()
        elif worker_type == JobType.QA and self.locust.qa_1_worker_id is not None:
            self.qa_submit_judgment()
        else:
            if worker_type == JobType.WORK:
                log.error(f"worker_type: {worker_type} or worker_id: {self.locust.worker_id} is not supported.")
            elif worker_type == JobType.QA:
                log.error(f"worker_type: {worker_type} or worker_id: {self.locust.qa_1_worker_id} is not supported.")
            else:
                log.error(f"worker_type: {worker_type} is not supported.")
            gevent.sleep(10)


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


if __name__ == '__main__':
    """ locust -f adap/perf_platform/test_scenarios/quality_flow/locust_qf_commit_fetch.py --slave --master-host=127.0.0.1"""
    contributor_num = 10000
    # Step 0. Create Quality flow and bind AC project - 15304
    # Step 0.1. Create QF project
    # project_name = f"QF Auto Project {_today} {faker.zipcode()} for Perf Test"
    # project = qfm.logic_create_qf_project(project_name, project_name)
    # # project = {"id": "3e53ae8b-537c-4a8f-98a4-14522edbd1fe",
    # #            "name": "QF AutoTest Project 2022_12_12 19277 for Stability Test"}
    # project_id = project.get("id")
    # project_name = project.get("name")
    #
    # # Step 0.2. Create quality flow (WORK job -> QA job)
    # project_id, job_id_list = qfm.logic_create_quality_flow(project_id=project_id, serial_label="A",
    #                                                         job_name_prefix=f"{project_name} ",
    #                                                         cml_setting='<cml:textarea label="Sample text area:" validates="required" />')
    # # Step 0.3. Sync the AC project
    # ac_id = 15304
    # qfm.logic_curated_crowd_ac_setting_and_syncing(project_id, ac_id, "ALL")
    #

    # Step 1. Create contributors of a project using - 15304 - Quality_Flow_007 - QF007
    # qfm.logic_curated_crowd_test_create_contributor(project_id, contributor_num-1)

    # Step 2. Assign all contributors of the project to a job
    # prepare_assign_contributor_list_to_job(project_id, work_job_id)
    # prepare_assign_contributor_list_to_job(project_id, qa_job_id)

    # Step 3. Save contributor list into csv
    # save_contributor_list_into_csv()

    os.environ['ENV'] = env
    os.environ['DATA_SOURCE_PATH'] = Config.DATA_SOURCE_PATH
    # os.system("""
    # export PATH=/Users/edzhu/Library/Python/3.8/bin:/opt/homebrew/opt/python@3.8/libexec/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin；
    # /Users/edzhu/Library/Python/3.8/bin/locust -f locust_qf_commit_fetch.py --master --csv=report --no-web -c2 -r 1 --run-time 10
    # """)
    # os.system("""
    # export PATH=/Users/edzhu/Library/Python/3.8/bin:/opt/homebrew/opt/python@3.8/libexec/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin；
    # locust -f locust_qf_judge.py --csv=report --no-web -c2 -r 2 --run-time 10
    # """)

    # os.system("locust -f locust_qf_judge.py --csv=report --no-web -c50 -r 50 --run-time 60")

    os.system("""
    export PATH=/Users/edzhu/Library/Python/3.8/bin:/opt/homebrew/opt/python@3.8/libexec/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
    export QF_PROJECT_ID=adfdd13e-2534-414b-bc3a-6d0b7ecc4556
    export QF_WORK_JOB_ID=bf7083c8-a444-4e45-8307-02c86ab83b79
    export QF_QA_JOB_ID=bf7083c8-a444-4e45-8307-02c86ab83b79
    export QF_WORKER_TYPE=WORK
    export QF_UNIT_TYPE=UNIT_ONLY
    export QF_UNIT_GROUP_OPTION=RETAIN
    export QF_DRY_RUN=False
    locust -f locust_qf_judge.py --master
    """)
