"""
0: create job 1
5: start locust 1 (for 1 hr)
20: create job 2
25: start locust 2 (for 30 min)
55: locust 2 finishes
65: locust 1 finishes
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
          'NUM_UNITS': '30000',
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
      'num_slaves': 5,
      'num_clients': 100,
      'hatch_rate': 0.25,
      'run_time': '60m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust1)

    se.wait(15*60)  # wait for 15 min

    # ------------------------- TASK #2 -------------------------
    TASK_ID = '2'

    job2 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '600',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '30000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '100'
      }
    }

    se.run_job(job2)
    se.wait_for_completion(job2, max_wait=15*60)
    se.wait(3*60)

    # LOCUST
    locust2 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 5,
      'num_clients': 100,
      'hatch_rate': 0.25,
      'run_time': '30m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust2)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust2, max_wait=35*60)
    se.wait_for_completion(locust1, max_wait=15*60)
