"""
0: create job 1
15: start locust 1 (for 1 hr)
195: locust 1 finishes
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
          'MAX_WAIT_TIME': '1200',  # 20m
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '100000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '100'
      }
    }

    se.run_job(job1)
    se.wait_for_completion(job1, max_wait=30*60)
    se.wait(5*60)

    # LOCUST
    locust1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 5,
      'num_clients': 100,  # 2500j/m
      'hatch_rate': 0.03,  # 100/0.03 = 3333s => 55.5m
      'run_time': '180m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust1, max_wait=200*60)
