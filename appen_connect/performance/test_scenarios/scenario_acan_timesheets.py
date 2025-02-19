from adap.perf_platform.test_scenarios import executor as se
import json

desc = "ACAN Timesheets"
with se.session(desc, teardown=False) as session_id:

    TASK_ID = '1'
    se.init_task(TASK_ID)
    workload = [
        {
            'start_at': '0:0:10',
            'target_count': 100,
            'finish_at': '0:06:00'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_timesheets.py',
      'num_slaves': 5,
      'num_clients': 1,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '15m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'DATA_SOURCE_PATH': 'appen_connect/data/ac_accounts_stage.csv',
        'ENV': 'stage',
        'WORKLOAD': json.dumps(workload),
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=60*60)
