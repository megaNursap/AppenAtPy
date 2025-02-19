from adap.perf_platform.test_scenarios import executor as se
import json

desc = "Client: Get units"

with se.session(desc, teardown=False) as session_id:
    TASK_ID = '1'
    se.init_task(
        task_id=TASK_ID, 
        info={"job_id": 1577512}
    )
    locust = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/test_scripts/locust_client_get_unit.py',
      'num_slaves': 2,
      'num_clients': 10,
      'hatch_rate': 0.1,
      'run_time': '5m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'CAPTURE_RESPONSE': 'false',
        'DATA_SOURCE_FILE': 'integration_requestor_emails.py'
        # 'WORKLOAD': json.dumps(workload),
      }
    }
    se.run_locust(locust)
    se.wait_for_completion(locust, max_wait=90*60)
