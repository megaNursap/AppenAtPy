import os

from adap.perf_platform.test_scenarios import executor as se
import json

# ENV         = os.environ['ENV']
TEST_TIME   = os.environ['RUN_TIME']
NUM_SLAVES  = os.environ['NUM_SLAVES']
NUM_CLIENTS = os.environ['NUM_CLIENTS']
# HATCH_RATE  = os.environ['HATCH_RATE']
# WORKLOAD    = os.environ['WORKLOAD']

ENV         = 'integration'
# TEST_TIME   = 10
# NUM_SLAVES  = 1
# NUM_CLIENTS = 1
HATCH_RATE  = 1
WORKLOAD  = ''


with se.session(f"API gateway [{ENV}]", teardown=True) as session_id:
    if int(NUM_CLIENTS) > 10:
        NUM_CLIENTS = '10'

    data_source_env_paths = {
        # 'integration': 'adap/data/performance/integration_gateway_accounts.csv'
        'integration': 'adap/perf_platform/test_data/integration_contributor_emails_new.csv'
    }

    TASK_ID = '1'
    se.init_task(TASK_ID)

    if WORKLOAD != '':
        print("-= custom WORKLOAD =-", WORKLOAD)
        workload = json.loads(WORKLOAD)
        print("-= WORKLOAD =-", workload)
    else:
        workload = [
            {
                'start_at': '0:0:01',
                'target_count': int(NUM_CLIENTS),
                'finish_at': '0:05:0'
            }
        ]
    print("-= default WORKLOAD =-", workload)

    locust_1 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/locust_adap_contributor_login_single_call_idle_random_call_test.py',
        'num_slaves': int(NUM_SLAVES),
        'num_clients': int(NUM_CLIENTS),
        'hatch_rate': int(HATCH_RATE),  # 0-10 in 2.5 minutes
        'run_time': f'{TEST_TIME}m',
        'locust_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'CAPTURE_PAYLOAD': 'true',
            'CAPTURE_RESPONSE': 'true',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV],
            'ENV': ENV,
            'WORKLOAD': json.dumps(workload),
        }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=180 * 60)
