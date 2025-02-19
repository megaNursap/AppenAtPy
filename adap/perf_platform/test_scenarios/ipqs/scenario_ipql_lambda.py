from adap.perf_platform.test_scenarios import executor as se
import json

with se.session(teardown=False) as session_id:

    TASK_ID = '1'

    workload = [
        {
            'start_at': '0:0:10',
            'target_count': 200,
            'finish_at': '0:8:0'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_ipqs.py',
      'num_slaves': 10,
      'num_clients': 1,
      'hatch_rate': 1,  # 8 minutes
      'run_time': '10m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WORKLOAD': json.dumps(workload),
        'IPQS_RANDOM_IP': 'false'
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=60*60)
