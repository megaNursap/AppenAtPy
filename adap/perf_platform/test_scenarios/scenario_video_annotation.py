from adap.perf_platform.test_scenarios import executor as se

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    JOB_TYPE = 'video_annotation'
    job_1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'JOB_TYPE': JOB_TYPE,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '900',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '1000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '3',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '10'
      }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=15*60)
    se.wait(5*60)  # wait for the job to become available in channels

    # LOCUST
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 5,
      'num_clients': 10,  # 10 * 25j/m ~ 250/m
      'hatch_rate': 0.033,  # 0 to 10 in 300 s
      'run_time': '30m',
      'locust_config': {
        'JOB_TYPE': JOB_TYPE,
        'EXTERNAL': 'true',
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'PREDICT_BOX_RATE': '0.8'
      }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=35*60)
