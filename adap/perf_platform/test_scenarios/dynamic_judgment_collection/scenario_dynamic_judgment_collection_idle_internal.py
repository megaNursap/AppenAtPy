from adap.perf_platform.test_scenarios import executor as se

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
          'NUM_UNITS': '15000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '100',
          'DYNAMIC_JUDGMENT_COLLECTION': 'true',
          'MAX_JUDGMENTS_PER_UNIT': '8',
          'MIN_UNIT_CONFIDENCE': '0.9'
      }
    }

    se.run_job(job1)
    se.wait_for_completion(job1, max_wait=15*60)
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST
    locust1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 1,
      'num_clients': 60,
      'hatch_rate': 0.2,  # 5 min ramp up
      'run_time': '40m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WAIT_IDLE_TIME':'1860',  #31 min idle timeout
        'RANDOM_JUDGMENT': 'true',
        'EXTERNAL': 'false'
      }
    }
    se.run_locust(locust1)
    se.wait_for_completion(locust1, max_wait=50*60)
