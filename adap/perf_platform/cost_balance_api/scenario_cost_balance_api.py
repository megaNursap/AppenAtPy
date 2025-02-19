from adap.perf_platform.test_scenarios import executor as se

TEST_TIME = 8
NUM_SLAVES = 1
NUM_CLIENTS = 20
HATCH_RATE = 20

with se.session("Cost balance API") as session_id:
    TASK_ID = '1'
    se.init_task(TASK_ID)

    locust_1 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/cost_balance_api/locust_cost_balance_api.py',
        'num_slaves': int(NUM_SLAVES),
        'num_clients': int(NUM_CLIENTS),
        'hatch_rate': int(HATCH_RATE),
        'run_time': f'{TEST_TIME}m',
        'locust_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'CAPTURE_PAYLOAD': 'true',
            'CAPTURE_RESPONSE': 'true',
        }
    }
    se.run_locust(locust_1)
    se.wait_for_completion(locust_1, max_wait=8 * 60)
