from adap.perf_platform.test_scenarios import executor as se

env = 'integration'

with se.session() as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    wf = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_workflow_simple.py',
      'job_config': {
          'ENV': env,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '600',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '500',
          'JUDGMENTS_PER_UNIT': '1',
      }
    }

    se.run_job(wf)
    se.wait_for_completion(wf, max_wait=15*60)
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST I
    locust1 = {
      'suffix': f'{session_id}-{TASK_ID}-1',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 2,
      'num_clients': 50,  # 50 * 25j/m = 1250j/m
      'hatch_rate': 5,
      'run_time': '10m',
      'locust_config': {
        'ENV': env,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'MAX_WAIT_TIME': '600',
        'WORKFLOW_STEP': '1',
        'CAPTURE_RESULTS': 'true',
        'EXTERNAL': 'false',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust1)
    # se.wait_for_completion(locust1, max_wait=15*60)
    se.wait(3*60)

    # LOCUST II
    locust2 = {
      'suffix': f'{session_id}-{TASK_ID}-2',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 2,
      'num_clients': 50,  # 20 * 25j/m = 500j/m
      'hatch_rate': 5,
      'run_time': '10m',
      'locust_config': {
        'ENV': env,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'MAX_WAIT_TIME': '600',
        'WORKFLOW_STEP': '2',
        'CAPTURE_RESULTS': 'true',
        'EXTERNAL': 'false',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust2)
    se.wait_for_completion(locust2, max_wait=15*60)
