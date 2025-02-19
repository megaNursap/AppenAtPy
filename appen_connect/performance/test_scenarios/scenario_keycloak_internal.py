from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'stage'

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
            'target_count': 50,
            'finish_at': '0:10:0'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_keycloak_internal.py',
      'num_slaves': 5,
      'num_clients': 1,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '20m',
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
