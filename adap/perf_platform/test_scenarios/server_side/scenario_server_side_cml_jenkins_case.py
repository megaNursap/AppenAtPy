"""
https://appen.atlassian.net/browse/CW-7755
"""
import os
from adap.perf_platform.test_scenarios import executor as se
import json

ENV         = os.environ['ENV']
TEST_TIME   = os.environ['RUN_TIME']
NUM_SLAVES  = os.environ['NUM_SLAVES']
NUM_CLIENTS = os.environ['NUM_CLIENTS']
HATCH_RATE  = os.environ['HATCH_RATE']


with se.session(f"Server side simple case [{ENV}]", teardown=False) as session_id:
    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    JOB_TYPE = 'server_side_validation_simple_case'

    job_1 = {
        'name': f'create-job-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/create_job.py',
        'job_config': {
            'JOB_TYPE': JOB_TYPE,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '100',
            'CAPTURE_RESULTS': 'true',
            'LOG_HTTP': 'false',
            'NUM_UNITS': '30',
            'UNITS_PER_ASSIGNMENT': '5',
            'GOLD_PER_ASSIGNMENT': '0',
            'JUDGMENTS_PER_UNIT': '1',
            'MAX_JUDGMENTS_PER_WORKER': '100',
            'ENV': ENV
        }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=600)
    se.wait(2 * 60)  # wait for the job to become available in channels

    job_judgments_monitor = {
        'name': f'monitor-job-judgments-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/judgments_monitor.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'MAX_WAIT_TIME': '600',
            'RUN_TIME': '550',
            'INTERVAL': '5'  # take a measurement once every 5 seconds
        }
    }
    se.run_job(job_judgments_monitor)

    # LOCUST
    locust_1 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/locust_judge.py',
        'num_slaves': int(NUM_SLAVES),
        'num_clients': int(NUM_CLIENTS),
        'hatch_rate': int(HATCH_RATE),
        'run_time': f'{TEST_TIME}m',
        'locust_config': {
            'JOB_TYPE': JOB_TYPE,
            'EXTERNAL': 'false',
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'ENV': ENV
        }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=2 * 20 * 60)
