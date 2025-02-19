from adap.perf_platform.test_scenarios import executor as se
import json

desc = "AC SSO sign in"
with se.session(desc, teardown=False) as session_id:

    TASK_ID = '1'
    se.init_task(TASK_ID)
    workload = [
        {
            'start_at': '0:0:01',
            'target_count': 100,
            'finish_at': '0:1:0'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_sso_login.py',
      'num_slaves': 5,
      'num_clients': 1,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '20m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'DATA_SOURCE_PATH': 'appen_connect/data/ac_accounts_qa.csv',
        'ENV': 'qa',
        'WORKLOAD': json.dumps(workload),
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=60*60)
