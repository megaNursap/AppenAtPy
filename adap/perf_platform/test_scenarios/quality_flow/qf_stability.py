from gevent import monkey; monkey.patch_all()
import os, sys, time, gevent, random, datetime, logging, traceback
from logging import handlers
logging.getLogger('faker').setLevel(logging.ERROR)
from faker import Faker
from gevent.pool import Pool
from adap.api_automation.utils.data_util import get_test_account_data_generally, get_user_team_id
from adap.api_automation.services_config.qf_api_logic import TestType, EnvType, JobType, DataType, \
    QualityFlowApiSingletonManager, CommitPayloadType, InvoiceStatisticsType, UnitGroupOption, ReviewReasonOption

log = logging.getLogger(__name__)
log.setLevel(level=logging.INFO)
# -----------------------------log format and output to file----------------------------
fmt = logging.Formatter('%(asctime)s %(thread)d %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(fmt)
log_file = os.path.join(os.path.dirname(__file__), 'stability.log')
file_handler = handlers.TimedRotatingFileHandler(filename=log_file, when='D', backupCount=1, encoding='utf-8')
file_handler.setFormatter(fmt)
log.addHandler(console_handler)
log.addHandler(file_handler)

faker = Faker()
_today = datetime.datetime.now().strftime("%Y_%m_%d")

mc = Pool(100)

# AudioTX judgment setting
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


def start_spawn_users(user_type, num_client, task, **kwargs):
    coroutines = []
    for i in range(num_client):
        new_kwargs = kwargs.copy()
        new_kwargs.update({"thread_name": f"{user_type}_{i}"})
        new_kwargs.update({"thread_index": i})
        coroutines.append(mc.spawn(task, new_kwargs))

    return coroutines


def simulate_pm_action(kwargs):
    log.info(f'Coroutine {kwargs.get("thread_name")} Start')

    for i in TOTAL_PM_ROUND_LIST:
        log.info(f'Coroutine {kwargs.get("thread_name")} Start - Round {TOTAL_PM_ROUND_LIST[i]+1}')
        try:
            time.sleep(random.randint(20, 30))
            try:
                if UNIT_TYPE == "SEGMENTED":
                    gcc = {'num_rows': UPLOAD_UNIT_NUM_PER_ROUND[i], 'segmentation': True,
                           'num_group': UPLOAD_CSV_GRP_NUM,
                           'header_size': 3, 'save_path': None}
                elif UNIT_TYPE == "UNIT_ONLY":
                    gcc = {'num_rows': UPLOAD_UNIT_NUM_PER_ROUND[i], 'segmentation': False,
                           'num_group': UPLOAD_UNIT_NUM_PER_ROUND[i],
                           'header_size': 3, 'save_path': None}
                else:
                    log.error(f"Wrong UNIT_TYPE: {UNIT_TYPE}")
                    exit(1)
                unit_number = qfm.logic_pm_upload_units(kwargs.get("project_id"), env, TOTAL_PM_ROUND_LIST[i]+1, gcc=gcc)
            except Exception as r:
                traceback.print_exc()
                pass
            time.sleep(random.randint(20, 30))
            try:
                qfm.logic_pm_send_all_new_units_to_job(kwargs.get("project_id"), kwargs.get("leading_job_id"))
            except Exception as r:
                traceback.print_exc()
                pass
            time.sleep(random.randint(20, 30))
        except Exception as r:
            traceback.print_exc()
            pass
        log.info(f'Coroutine {kwargs.get("thread_name")} End - Round {TOTAL_PM_ROUND_LIST[i]+1}')
    log.info(f'Coroutine {kwargs.get("thread_name")} End')


def simulate_worker_action(kwargs):
    log.info(f'Coroutine {kwargs.get("thread_name")} - {kwargs.get("thread_index")} Start')
    page_num = 1 if UNIT_TYPE == 'SEGMENTED' and UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
    i = 0
    while True:
        i += 1
        log.info(f'Coroutine {kwargs.get("thread_name")} Start - Round {i}')
        try:
            _, fetch_info = qfm.logic_distribution_fetch_and_submit(
                job_id=kwargs.get("job_id"),
                worker_id=kwargs.get("worker_id_list")[kwargs.get("thread_index")],
                working_seconds_per_task_page=0,
                job_type=JobType.WORK,
                judgment_keys=JUDGMENT_KEYS,
                auto_judgment_source_col_name="audio_name",
                auto_judgment=WORKER_AUTO_JUDGMENT,
                audio_tx_judgment=audio_tx_judgment,
                judgment={"sample_text_area": f"J - {faker.zipcode()} - {faker.city()}"},
                feedback_result_list=WORKER_FEEDBACK_RESULTS,
                abandon_percentage=WORKER_ABANDON_PERCENTAGE,
                commit_payload_type=CommitPayloadType.RANDOMIZED,
                data_type=DATA_TYPE,
                fetch_page_num=page_num
            )
            if fetch_info is not None:
                if page_num is not None:
                    if fetch_info.get("abandon_flag"):
                        page_num = 1 if UNIT_TYPE == 'SEGMENTED' and UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
                    else:
                        total = fetch_info.get("fetch_total_pages")
                        page_num = page_num + 1 if type(total) == int and page_num < total else 1
                if fetch_info.get("fetch_dist_num") == 0:
                    log.info(f'Wait for {penalty} seconds for nothing to be fetched.')
                    time.sleep(penalty)
                    penalty, last_penalty = (penalty + last_penalty) % 60, penalty
                else:
                    penalty, last_penalty = 1, 1
            else:
                log.error(f"Fetch info is None.")
        except Exception as r:
            traceback.print_exc()
            if r.__class__.__name__ == "AssertionError" and\
                    'code[5006], msg[There are unfinished units in some pages. You need to finish them all before submission. Please check again!]' in r.args[0]:
                page_num = 1
        log.info(f'Coroutine {kwargs.get("thread_name")} End - Round {i}')
    log.info(f'Coroutine {kwargs.get("thread_name")} - {kwargs.get("thread_index")} End')


def simulate_qa_action(kwargs):
    log.info(f'Coroutine {kwargs.get("thread_name")} - {kwargs.get("thread_index")} Start')
    page_num = 1 if UNIT_TYPE == 'SEGMENTED' and UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
    i = 0
    while True:
        i += 1
        log.info(f'Coroutine {kwargs.get("thread_name")} Start - Round {i}')
        try:
            _, fetch_info = qfm.logic_distribution_fetch_and_submit(
                job_id=kwargs.get("job_id"),
                worker_id=kwargs.get("worker_id_list")[kwargs.get("thread_index")],
                working_seconds_per_task_page=QA_WORKING_SECONDS_PER_TASK_PAGE,
                job_type=JobType.QA,
                review_result_list=QA_REVIEW_RESULTS,
                judgment_keys=JUDGMENT_KEYS,
                auto_judgment=None,
                audio_tx_judgment=audio_tx_judgment,
                abandon_percentage=QA_ABANDON_PERCENTAGE,
                commit_payload_type=CommitPayloadType.RANDOMIZED,
                data_type=DATA_TYPE,
                fetch_page_num=page_num
            )
            if fetch_info is not None:
                if page_num is not None:
                    if fetch_info.get("abandon_flag"):
                        page_num = 1 if UNIT_TYPE == 'SEGMENTED' and UNIT_GROUP_OPTION == UnitGroupOption.RETAIN else None
                    else:
                        total = fetch_info.get("fetch_total_pages")
                        page_num = page_num + 1 if type(total) == int and page_num < total else 1
                if fetch_info.get("fetch_dist_num") == 0:
                    log.info(f'Wait for {penalty} seconds for nothing to be fetched.')
                    time.sleep(penalty)
                    penalty, last_penalty = (penalty + last_penalty) % 60, penalty
                else:
                    penalty, last_penalty = 1, 1
            else:
                log.error(f"Fetch info is None.")
        except Exception as r:
            traceback.print_exc()
            if r.__class__.__name__ == "AssertionError" and\
                    'code[5006], msg[There are unfinished units in some pages. You need to finish them all before submission. Please check again!]' in r.args[0]:
                page_num = 1
        log.info(f'Coroutine {kwargs.get("thread_name")} End - Round {i}')
    log.info(f'Coroutine {kwargs.get("thread_name")} - {kwargs.get("thread_index")} End')


if __name__ == '__main__':
    # Stability Test Params
    env = EnvType.INTEGRATION
    UNIT_TYPE = ["UNIT_ONLY", "SEGMENTED"][0]
    UNIT_GROUP_OPTION = UnitGroupOption.RETAIN
    PM_ROTATION_NUM = 100
    UPLOAD_CSV_ROW_NUM = 1000
    UPLOAD_CSV_GRP_NUM = 10
    DATA_TYPE = DataType.Textarea
    WORKER_AUTO_JUDGMENT = True if DATA_TYPE == DataType.AudioTX else False
    WORKER_ABANDON_PERCENTAGE = 1
    WORKER_WORKING_SECONDS_PER_TASK_PAGE = 0
    WORKER_FEEDBACK_RESULTS = ["ACCEPTED", "REJECTED"]
    QA_ABANDON_PERCENTAGE = 1
    QA_WORKING_SECONDS_PER_TASK_PAGE = 0
    QA_REVIEW_RESULTS = ["ACCEPTED", "MODIFIED"]

    USER_NUM_PM = 1
    USER_NUM_WORKER = 20
    USER_NUM_QA = 10
    TOTAL_PM_ROUND_LIST = list(range(0, PM_ROTATION_NUM))
    UPLOAD_UNIT_NUM_PER_ROUND = [UPLOAD_CSV_ROW_NUM] * len(TOTAL_PM_ROUND_LIST)
    PM_USERNAME = get_test_account_data_generally('qf_stability', 'user_name', env=env)
    PM_PASSWORD = get_test_account_data_generally('qf_stability', 'password', env=env)
    PM_TEAM_ID = get_test_account_data_generally('qf_stability', 'teams', env=env)[0]['id']
    CONTRIBUTOR = get_test_account_data_generally('qf_stability', 'contributor', env=env)
    WORKER_ID_LIST = [x['contributor_id'] for x in CONTRIBUTOR['workers']]
    QA_WORKER_ID_LIST = [x['contributor_id'] for x in CONTRIBUTOR['qa_workers']]
    JUDGMENT_KEYS = ["audio_transcription"] if DATA_TYPE == DataType.AudioTX else ["sample_text_area"]

    # Initial setting
    qfm = QualityFlowApiSingletonManager
    qfm.set_env(env, PM_TEAM_ID)
    qfm.get_singleton_instance()
    qfm.set_perf()
    qfm.logic_qf_login(PM_USERNAME, PM_PASSWORD)

    # Step 1. Create QF project
    if UNIT_TYPE == "UNIT_ONLY":
        project_name = f"QF Auto {UNIT_TYPE} Project {_today} {faker.zipcode()} for Stability Test ({DATA_TYPE})"
    elif UNIT_TYPE == "SEGMENTED":
        project_name = f"QF Auto {UNIT_TYPE} ({UNIT_GROUP_OPTION}) Project {_today} {faker.zipcode()} for Stability Test ({DATA_TYPE})"
    project = qfm.logic_create_qf_project(project_name, project_name)
    project_id = project.get("id")
    project_name = project.get("name")

    # Step 2. Sync the AC project
    ac_id = 17833
    res = qfm.logic_curated_crowd_ac_setting_and_syncing(project_id, ac_id, "ALL")
    setting_id = res["setting_id"]

    # Step 3. Create quality flow (WORK job -> QA job)
    flow_define = [
        ["WORK", {"judgments_per_row": '1', "rows_per_page": 5, "assignment_lease_expiry": 600,
                  "invoiceStatisticsType": InvoiceStatisticsType.UNIT_COUNT, "payRateType": "Work",
                  "maxJudgmentPerContributorEnabled": "false", "maxJudgmentPerContributor": 0,
                  "allowAbandonUnits": "true", "unitGroupOption": UNIT_GROUP_OPTION}],
        ["QA", {"judgments_per_row": '1', "rows_per_page": 5, "assignment_lease_expiry": 600,
                "invoiceStatisticsType": InvoiceStatisticsType.UNIT_COUNT, "payRateType": "QA",
                "maxJudgmentPerContributorEnabled": "false", "maxJudgmentPerContributor": 0, "allowSelfQa": "false",
                "allowAbandonUnits": "true",
                "judgment_modifiable": 'true', "send_back_op": 'NO_OP', "feedback": "ENABLED",
                "reviewReasonOption": ReviewReasonOption.SINGLE, "reviewReasons": "TER\\nWER\\nLER\\nTSER"}],
    ]
    segmental_flag = True if UNIT_TYPE == "SEGMENTED" else False
    sample_define = [
        {},
        # {
        #     "sampleRate": 100,
        #     "filterCriteria": "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}",
        #     "filterNum": 1,
        #     "frequencyPeriod": 2,
        #     "frequencyUnit": "HOURS"
        # },
        {"sampleRate": 80, "segmental": segmental_flag, "segmentSampleRate": 100},
        # {"sampleRate": 100, "filterCriteria": "{}", "filterNum": 0, "frequencyPeriod": 2, "frequencyUnit": "HOURS"},
    ]
    if DATA_TYPE == DataType.Textarea:
        cml_setting = '{{audio_name}}<cml:textarea label="Sample text area:" validates="required" />'
        ontology_setting = None
    elif DATA_TYPE == DataType.AudioTX:
        cml_setting = '{{audio_name}}<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription"  allow-timestamping="true" type="[\'transcription\',\'labeling\']" beta="true" listen-to="[[0, 1, 0]]"/>'
        ontology_setting = '{"labelGroups":[{"title":"Speaker","color":"#9A2517","labels":["Speaker A","Speaker B","Speaker C"],"allowMultipleSelection":true,"isForTranscribableSegment":true,"allowNoSelection":true}],"spans":[{"title":"Span A","description":"","color":"#A92D26"},{"title":"Span B","description":"","color":"#7D1F4E"},{"title":"Span C","description":"","color":"#7D1F4F"}],"events":[{"title":"Event A","description":"","color":"#431F87"},{"title":"Event B","description":"","color":"#2C238C"},{"title":"Event C","description":"","color":"#2C238D"}]}'
    else:
        log.error("Unsupported data type: {}".format(DATA_TYPE))
    project_id, job_id_list = qfm.logic_create_quality_flow(
        project_id=project_id, serial_label="A", job_name_prefix=f"{project_name} ", flow_define=flow_define,
        sample_define=sample_define, cml_setting=cml_setting, ontology_setting=ontology_setting)
    PROJECT_ID = project_id
    WORK_JOB_ID = job_id_list[0].get("id") if len(job_id_list) > 0 else None
    QA_JOB_ID = job_id_list[1].get("id") if len(job_id_list) > 1 else None

    # Step 4. Assign Contributors to jobs
    qfm.logic_curated_crowd_link_ac_sync_setting_to_job(project_id, WORK_JOB_ID, setting_id)
    qfm.logic_assign_contributor_to_job(project_id, WORKER_ID_LIST, WORK_JOB_ID)
    if len(job_id_list) > 1:
        qfm.logic_curated_crowd_link_ac_sync_setting_to_job(project_id, QA_JOB_ID, setting_id)
        qfm.logic_assign_contributor_to_job(project_id, QA_WORKER_ID_LIST, QA_JOB_ID)
    log.info(f"Project ID: {project_id}, Project Name: {project_name}\n"
             f"WORK_JOB_ID: {WORK_JOB_ID}, QA_JOB_ID: {QA_JOB_ID}")

    c1 = start_spawn_users("PM", USER_NUM_PM, simulate_pm_action,
                           project_id=project.get("id"), leading_job_id=WORK_JOB_ID, )
    c2 = start_spawn_users("WORKER", USER_NUM_WORKER, simulate_worker_action,
                           worker_id_list=WORKER_ID_LIST, job_id=WORK_JOB_ID)
    c3 = start_spawn_users("QA", USER_NUM_QA, simulate_qa_action,
                           worker_id_list=QA_WORKER_ID_LIST, job_id=QA_JOB_ID)

    log.info(len(c1 + c2 + c3))
    gevent.joinall(c1 + c2 + c3)
