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
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/test_scenarios/quality_flow/locust_qf_judge.py',
        'num_slaves': decouple.config('NUM_SLAVES', default=20, cast=int),  # num_clients / num_slaves clients per pod
        'num_clients': decouple.config('NUM_CLIENTS', default=1000, cast=int),  # num_clients * N tasks/m = M tasks/m
        'hatch_rate': decouple.config('HATCH_RATE', default=100, cast=int),  # num_clients / hatch_rate = Ramp up time
        'run_time': decouple.config('RUN_TIME', default='30m', cast=str),
        'locust_config': {
            'ENV': env,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': decouple.config('QF_CAPTURE_RESULTS', default='false', cast=str),
            'DATA_SOURCE_FILE': f'{env}_contributor_IDs.py',
            # 'NUM_CLIENTS': decouple.config('NUM_CLIENTS', default=1000, cast=int),
            'QF_PROJECT_ID': decouple.config('QF_PROJECT_ID', default='None', cast=str),
            'QF_UNIT_TYPE': decouple.config('QF_UNIT_TYPE', default='None', cast=str),
            'QF_UNIT_GROUP_OPTION': decouple.config('QF_UNIT_GROUP_OPTION', default='None', cast=str),
            'QF_WORK_JOB_ID': decouple.config('QF_WORK_JOB_ID', default='None', cast=str),
            'QF_QA_JOB_ID': decouple.config('QF_QA_JOB_ID', default='None', cast=str),
            'QF_WORKER_TYPE': decouple.config('QF_WORKER_TYPE', default='None', cast=str),
            'QF_DRY_RUN': decouple.config('QF_DRY_RUN', default='False', cast=str)
        }
    }
    se.run_locust(locust1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust1, max_wait=25*60)
