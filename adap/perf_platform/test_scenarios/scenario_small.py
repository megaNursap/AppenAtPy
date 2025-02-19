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
    job1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '600',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '1000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '25'
      }
    }

    se.run_job(job1)
    se.wait_for_completion(job1, max_wait=15*60)
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST
    locust1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 3,
      'num_clients': 30,
      'hatch_rate': 0.5,
      'run_time': '10m',
      'locust_config': {
            'ENV': ENV,
            'EXTERNAL': 'false',
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'MAX_WAIT_TIME': '4000',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV]
        }
    }
    se.run_locust(locust1)
    se.wait_for_completion(locust1, max_wait=15*60)
