from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'stage'
desc = f"AC SME Find Project [{ENV}]"
with se.session(desc, teardown=False) as session_id:

    TASK_ID = '1'
    se.init_task(TASK_ID)
    workload = [
        {
            'start_at': '0:0:01',
            'target_count': 50,
            'finish_at': '0:02:0'
        },
        {
            'start_at': '0:05:0',
            'target_count': 400,
            'finish_at': '0:30:0'
        }
    ]
    
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_sme_findproj.py',
      'num_slaves': 10,
      'num_clients': 1,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '30m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'CAPTURE_PAYLOAD': 'true',
        'CAPTURE_RESPONSE': 'true',
        'ENV': ENV,
        'WORKLOAD': json.dumps(workload),
        'BATCHED_SAVE_RESULTS_SIZE': '10000',
        'DATA_SOURCE_PATH': 'appen_connect/data/sme_data/parts/part_ids.csv',
        'LIMIT_WORKER_IDS': '10000'
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=60*60)
