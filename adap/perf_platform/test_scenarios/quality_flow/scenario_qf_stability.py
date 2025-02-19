# -*- coding: utf-8 -*-
"""
@Desc:
"""
import decouple
from adap.perf_platform.test_scenarios import executor as se

env = decouple.config('ENV', default='integration', cast=str)
with se.session(teardown=False) as session_id:
    TASK_ID = '1'
    se.init_task(TASK_ID)

    # LOCUST
    locust1 = {
        'suffix': f'{session_id}-{TASK_ID}-pm',
        'filename': 'adap/perf_platform/test_scenarios/quality_flow/locust_qf_stability_pm.py',
        'num_slaves': 1,  # decouple.config('NUM_SLAVES', default=10, cast=int),  # num_clients / num_slaves clients per pod
        'num_clients': decouple.config('QF_NUM_CLIENTS_PM', default=1, cast=int),  # num_clients * N tasks/m = M tasks/m
        'hatch_rate': decouple.config('QF_NUM_CLIENTS_PM', default=1, cast=int),  # num_clients / hatch_rate = Ramp up time
        'run_time': decouple.config('RUN_TIME', default='60m', cast=str),
        'locust_config': {
            'ENV': env,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            # 'DATA_SOURCE_FILE': f'{env}_contributor_IDs.py',
            'QA_KEY': decouple.config('QA_KEY', default='None', cast=str),
            'QF_PROJECT_ID': decouple.config('QF_PROJECT_ID', default='None', cast=str),
            'QF_UNIT_TYPE': decouple.config('QF_UNIT_TYPE', default='None', cast=str),
            'QF_WORK_JOB_ID': decouple.config('QF_WORK_JOB_ID', default='None', cast=str),
            'QF_MAX_LOOP': decouple.config('QF_MAX_LOOP', default='None', cast=str),
            'QF_UPLOAD_UNIT_NUM_PER_ROUND': decouple.config('QF_UPLOAD_UNIT_NUM_PER_ROUND', default='None', cast=str),
            'QF_SEGMENTED_GROUP_NUM': decouple.config('QF_SEGMENTED_GROUP_NUM', default='None', cast=str),
        }
    }
    se.run_locust(locust1)

    locust2 = {
        'suffix': f'{session_id}-{TASK_ID}-worker',
        'filename': 'adap/perf_platform/test_scenarios/quality_flow/locust_qf_stability_worker.py',
        'num_slaves': 1,
        'num_clients': decouple.config('QF_NUM_CLIENTS_WORKER', default=1, cast=int),
        'hatch_rate': decouple.config('QF_NUM_CLIENTS_WORKER', default=1, cast=int),
        'run_time': decouple.config('RUN_TIME', default='60m', cast=str),
        'locust_config': {
            'ENV': env,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            # 'DATA_SOURCE_FILE': f'{env}_contributor_IDs.py',
            'QF_PROJECT_ID': decouple.config('QF_PROJECT_ID', default='None', cast=str),
            'QF_UNIT_TYPE': decouple.config('QF_UNIT_TYPE', default='None', cast=str),
            'QF_UNIT_GROUP_OPTION': decouple.config('QF_UNIT_GROUP_OPTION', default='None', cast=str),
            'QF_WORK_JOB_ID': decouple.config('QF_WORK_JOB_ID', default='None', cast=str),
            'QF_WORKING_SECONDS_PER_TASK_PAGE': decouple.config('QF_WORKING_SECONDS_PER_TASK_PAGE', default='None', cast=str),
            'QF_WORKER_FEEDBACK_RESULT_LIST': decouple.config('QF_WORKER_FEEDBACK_RESULT_LIST', default='None', cast=str),
            'QF_WORKER_ABANDON_PERCENTAGE': decouple.config('QF_WORKER_ABANDON_PERCENTAGE', default='None', cast=str),
            'QF_DATA_TYPE': decouple.config('QF_DATA_TYPE', default='None', cast=str)
        }
    }
    se.run_locust(locust2)

    locust3 = {
        'suffix': f'{session_id}-{TASK_ID}-qa',
        'filename': 'adap/perf_platform/test_scenarios/quality_flow/locust_qf_stability_qa.py',
        'num_slaves': 1,
        'num_clients': decouple.config('QF_NUM_CLIENTS_QA', default=1, cast=int),
        'hatch_rate': decouple.config('QF_NUM_CLIENTS_QA', default=1, cast=int),
        'run_time': decouple.config('RUN_TIME', default='60m', cast=str),
        'locust_config': {
            'ENV': env,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            # 'DATA_SOURCE_FILE': f'{env}_contributor_IDs.py',
            'QF_PROJECT_ID': decouple.config('QF_PROJECT_ID', default='None', cast=str),
            'QF_UNIT_TYPE': decouple.config('QF_UNIT_TYPE', default='None', cast=str),
            'QF_UNIT_GROUP_OPTION': decouple.config('QF_UNIT_GROUP_OPTION', default='None', cast=str),
            'QF_QA_JOB_ID': decouple.config('QF_QA_JOB_ID', default='None', cast=str),
            'QF_QA_WORKING_SECONDS_PER_TASK_PAGE': decouple.config('QF_QA_WORKING_SECONDS_PER_TASK_PAGE', default='None', cast=str),
            'QF_QA_REVIEW_RESULT_LIST': decouple.config('QF_QA_REVIEW_RESULT_LIST', default='None', cast=str),
            'QF_QA_ABANDON_PERCENTAGE': decouple.config('QF_QA_ABANDON_PERCENTAGE', default='None', cast=str),
            'QF_DATA_TYPE': decouple.config('QF_DATA_TYPE', default='None', cast=str)
        }
    }
    se.run_locust(locust3)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust1, max_wait=25 * 60)
    se.wait_for_completion(locust2, max_wait=25 * 60)
    se.wait_for_completion(locust3, max_wait=25 * 60)
