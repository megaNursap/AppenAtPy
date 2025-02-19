from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'stage'

with se.session(f"Project Service [{ENV}]", teardown=False) as session_id:

    TASK_ID = '1'
    se.init_task(TASK_ID)
    workload = [
        {
            'start_at': '0:0:01',
            'target_count': 400,
            'finish_at': '0:20:0'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_vendor_projects.py',
      'num_slaves': 10,
      'num_clients': 1,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '20m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'CAPTURE_PAYLOAD': 'true',
        'CAPTURE_RESPONSE': 'true',
        'ENV': ENV,
        'WORKLOAD': json.dumps(workload)
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=60*60)
