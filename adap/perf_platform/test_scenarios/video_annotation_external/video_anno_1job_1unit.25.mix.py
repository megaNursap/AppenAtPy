"""
https://appen.atlassian.net/browse/QED-1409
Load test: launching jobs/ordering new units while maintaining avg/high
load of judgments (Video Annotation)
"""
from adap.perf_platform.test_scenarios import executor as se

with se.session(teardown=False) as session_id:

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
          'RUN_TIME': '36000'  # 10 hours
      }
    }
    se.run_job(job_units_monitor)
    se.wait(15)  # wait for the units monitor pod to be created

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
          'NUM_UNITS': '10000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '1',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '1',
          'MAX_JUDGMENTS_PER_WORKER': '100',
          'VIDEO_SIZE': '25',
          'AUTO_ORDER': 'true',
          'BYPASS_ESTIMATED_FUND_LIMIT': 'true',
          'UNITS_REMAIN_FINALIZED': 'true',
          'SCHEDULE_FIFO': 'true',
          'AUTO_ORDER_TIMEOUT': '5',
      }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=120*60)

    se.wait(60*60)  # wait units to become judgeable

    # ORDERING ADDITIONAL UNITS
    job_1_2 = {
      'name': f'add-units-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/upload_units.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'JOB_TYPE': JOB_TYPE,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '100',
          'NUM_UNIT_UPLOADS': '240',
          'WAIT': '10'
      }
    }
    se.run_job(job_1_2)
    se.wait(5*60)

    # LOCUST
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 10,
      'num_clients': 300,  # 10 * 25j/m ~ 250/m
      'hatch_rate': 0.15,
      'run_time': '30m',
      'locust_config': {
          'JOB_TYPE': JOB_TYPE,
          'EXTERNAL': 'true',
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'WAIT_ON_ASSIGNMENT': '20',
          'PREDICT_BOX_RATE': '0.1',
          'WORKER_RANDOM_EXIT': '0.007'  # 50% complete 100 pages
      }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(job_1_2, max_wait=70*60)
    se.wait_for_completion(locust_1, max_wait=70*60)
