"""
https://appen.atlassian.net/browse/CW-7755 JOB_TYPE = 'server_side_validation_simple_case'
https://appen.atlassian.net/browse/CW-7756   JOB_TYPE = 'server_side_validation_complicated_case'
https://appen.atlassian.net/browse/CW-7757  JOB_TYPE = 'server_side_validation_liquid_case'
"""

from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'integration'
scenario = f"[{ENV}] Server side simple case"

# These contributors can be used on ADAP integration env.
data_source_env_paths = {
    'integration': 'appen_connect/data/adap_integration_users.csv'
}

with se.session(teardown=False) as session_id:
    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    # All cases shared the same code, just need to update JOBY_TYPE
    # JOB_TYPE = 'server_side_validation_simple_case'
    # JOB_TYPE = 'server_side_validation_complicated_case'
    JOB_TYPE = 'server_side_validation_liquid_case'

    job_1 = {
        'name': f'create-job-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/create_job.py',
        'job_config': {
            'JOB_TYPE': JOB_TYPE,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '2000',
            'CAPTURE_RESULTS': 'true',
            'LOG_HTTP': 'false',
            'NUM_UNITS': '50000',
            'UNITS_PER_ASSIGNMENT': '5',
            'GOLD_PER_ASSIGNMENT': '0',
            'JUDGMENTS_PER_UNIT': '5',
            'MAX_JUDGMENTS_PER_WORKER': '200'
        }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=2000)
    se.wait(3 * 60)  # wait for the job to become available in channels

    job_judgments_monitor = {
        'name': f'monitor-job-judgments-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/judgments_monitor.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'MAX_WAIT_TIME': '3500',
            'RUN_TIME': '3300',
            'INTERVAL': '5'  # take a measurement once every 5 seconds
        }
    }
    se.run_job(job_judgments_monitor)

    # LOCUST
    locust_1 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/locust_judge.py',
        'num_slaves': 10,
        'num_clients': 100,
        'hatch_rate': 0.5,
        'run_time': '60m',
        'locust_config': {
            'JOB_TYPE': JOB_TYPE,
            'ENV': ENV,
            'EXTERNAL': 'false',
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'MAX_WAIT_TIME': '4000',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV],
            # ANSWER_TYPE 0 mean all valid answers, ANSWER_TYPE 1 means mix valid and invalid answers, ANSWER_TYPE 2 means all invalid answers
            'ANSWER_TYPE': '2'
        }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=5 * 20 * 60)
