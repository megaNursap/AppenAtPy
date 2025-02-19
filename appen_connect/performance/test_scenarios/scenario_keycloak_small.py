from adap.perf_platform.test_scenarios import executor as se
import json
import os

ENV         = os.environ['ENV']
TEST_TIME   = os.environ['RUN_TIME']
NUM_SLAVES  = os.environ['NUM_SLAVES']
NUM_CLIENTS = os.environ['NUM_CLIENTS']
HATCH_RATE  = os.environ['HATCH_RATE']

with se.session(f"Keycloak internal [{ENV}]", teardown=False) as session_id:
    
    data_source_env_paths = {
      'qa': 'appen_connect/data/ac_accounts_qa.csv',
      'stage': 'appen_connect/data/test_users_stage_example.com.csv',
    }
    
    TASK_ID = '1'
    se.init_task(TASK_ID)
    workload = [
        {
            'start_at': '0:0:01',
            'target_count': 10,
            'finish_at': '0:0:30'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_keycloak_internal.py',
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
    se.wait_for_completion(locust_1, max_wait=60*60)
