"""
10 min load test with 30 workers => ~750 j/m
"""

from adap.perf_platform.test_scenarios import executor as se

ENV = 'integration'
scenario = f"[{ENV}] test small case"

# These contributors can be used on ADAP integration env.
data_source_env_paths = {
    'integration': 'appen_connect/data/adap_integration_users.csv'
}

with se.session() as session_id:

    TASK_ID = '1'
    # locust1 = {
    #     'suffix': f'{session_id}-{TASK_ID}',
    #     'filename': 'adap/perf_platform/locust_ipa.py',
    #     'num_slaves': 1,
    #     'num_clients': 1,  # 20 * 25j/m ~ 500j/m
    #     'hatch_rate': 1,
    #     'run_time': '3m',
    #     'locust_config': {
    #         'SESSION_ID': session_id,
    #         'TASK_ID': TASK_ID,
    #         'CAPTURE_RESULTS': 'true',
    #         'LOCUST_TASK': 'generate_aggregation'
    #     }
    # }
    #
    # se.run_locust(locust1)
    # se.wait(5)

    # LOCUST II
    locust2 = {
        'suffix': f'{session_id}-{TASK_ID}-2',
        'filename': 'adap/perf_platform/locust_ipa.py',
        'num_slaves': 1,
        'num_clients': 300,  # 20 * 25j/m ~ 500j/m
        'hatch_rate': 1,
        'run_time': '5m',
        'locust_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'LOCUST_TASK': 'get_job_status_info'
        }
    }
    se.run_locust(locust2)
    se.wait_for_completion(locust2, max_wait=15 * 60)
