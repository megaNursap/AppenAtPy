from adap.perf_platform.test_scenarios import executor as se

with se.session() as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    job_units_monitor = {
      'name': f'monitor-job-units-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/units_state_monitor.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '1800',
          'RUN_TIME': '600'
      }
    }

    JOB_TYPE = 'video_annotation'
    job_1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'JOB_TYPE': JOB_TYPE,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '1000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '3',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '5',
          'AUTO_ORDER': 'true',
          'BYPASS_ESTIMATED_FUND_LIMIT': 'true',
          'UNITS_REMAIN_FINALIZED': 'true',
          'SCHEDULE_FIFO': 'true',
          'AUTO_ORDER_TIMEOUT': '5',
      }
    }
    job_1_2 = {
      'name': f'add-units-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/upload_units.py',
      'job_config': {
          'JOB_TYPE': JOB_TYPE,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '100',
          'NUM_UNIT_UPLOADS': '30',
          'WAIT': '10'
      }
    }

    se.run_job(job_units_monitor)
    se.wait(15)  # wait for the units monitor pod to be created

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=30*60)

    se.wait(60)
    se.run_job(job_1_2)
    se.wait_for_completion(job_1_2, max_wait=10*60)
    se.wait_for_completion(job_units_monitor, max_wait=10*60)
