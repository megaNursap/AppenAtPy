from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'stage'

with se.session(f"User Service [{ENV}]", teardown=False) as session_id:
    
    data_source_env_paths = {
      'qa': 'appen_connect/data/ac_accounts_qa.csv',
      # 'stage': 'appen_connect/data/ac_accounts_stage.csv',
      # 'stage': 'appen_connect/data/test_users_stage_example.com.csv'
      'stage': 'appen_connect/data/test_users_stage/parts.csv'
    }

    TASK_ID = '1'
    se.init_task(TASK_ID)
    workload = [
        {
            'start_at': '0:0:01',
            'target_count': 200,
            'finish_at': '0:10:0'
        },
        {
            'start_at': '0:15:0',
            'target_count': 400,
            'finish_at': '0:30:0'
        },
    ]
    # workload = [
    #     {
    #         'start_at': '0:0:01',
    #         'target_count': 100,
    #         'finish_at': '0:10:0'
    #     },
    #     {
    #         'start_at': '0:15:0',
    #         'target_count': 200,
    #         'finish_at': '0:20:0'
    #     },
    #     {
    #         'start_at': '0:30:0',
    #         'target_count': 400,
    #         'finish_at': '0:40:0'
    #     },
    #     {
    #         'start_at': '1:0:0',
    #         'target_count': 50,
    #         'finish_at': '1:30:0'
    #     },
    # ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'appen_connect/performance/locust_user_service.py',
      'num_slaves': 10,
      'num_clients': 1,
      'hatch_rate': 1,  # 0-10 in 2.5 minutes
      'run_time': '40m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'CAPTURE_PAYLOAD': 'true',
        'CAPTURE_RESPONSE': 'true',
        # 'DATA_SOURCE_PATH': data_source_env_paths[ENV],
        'ENV': ENV,
        'WORKLOAD': json.dumps(workload),
        'BATCHED_SAVE_RESULTS_SIZE': '1000'
      }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=60*60)
