"""
1 hour load test at 5000j/m (target) after 13.3m ramp-up.
"""

from adap.perf_platform.test_scenarios import executor as se

with se.session() as session_id:

    # ------------------------- TASK #1 -------------------------
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
          'NUM_UNITS': '100000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '100'
      }
    }

    se.run_job(job1)
    se.wait_for_completion(job1, max_wait=15*60)
    se.wait(3*60)

    # LOCUST
    locust1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 10,  # 20 clients per pod
      'num_clients': 200,  # 200 * 25j/m = 5000j/m
      'hatch_rate': 0.25,  # 200 / 0.25 = 800s => 13.3m
      'run_time': '60m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WORKER_RANDOM_EXIT': '0.03'
      }
    }
    se.run_locust(locust1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust1, max_wait=65*60)
