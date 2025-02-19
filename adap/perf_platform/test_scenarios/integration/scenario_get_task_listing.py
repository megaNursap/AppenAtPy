from adap.perf_platform.test_scenarios import executor as se
import json

desc = "Worker: Get Task Listing"

with se.session(desc, teardown=False) as session_id:
    TASK_ID = '1'
    se.init_task(TASK_ID)
    locust = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/test_scripts/locust_worker_get_tasklisting.py',
      'num_slaves': 5,
      'num_clients': 100,
      'hatch_rate': 0.05,
      'run_time': '30m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'CAPTURE_RESPONSE': 'false',
        # 'WORKLOAD': json.dumps(workload),
      }
    }
    se.run_locust(locust)
    se.wait_for_completion(locust, max_wait=90*60)
