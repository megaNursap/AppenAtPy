from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'stage'

with se.session(f"User Sign In [{ENV}]", teardown=False) as session_id:

    TASK_ID = '1'
    se.init_task(TASK_ID)

    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_sign_in.py',
      'num_slaves': 1,
      'num_clients': 10,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '120m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'CAPTURE_PAYLOAD': 'true',
        'CAPTURE_RESPONSE': 'true',
        'ENV': ENV
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=120*60)
