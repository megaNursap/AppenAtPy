"""
https://appen.atlassian.net/browse/QED-1404
Create 1 job, 1 unit/page (250 frames). ~20s to complete a page of work.
Deploy 20 workers and increase number of worker load gradually
and steadily until AUT becomes unstable or errors observed.
"""
from adap.perf_platform.test_scenarios import executor as se
import json

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
          'RUN_TIME': '25200'  # 7 hours
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
          'MAX_WAIT_TIME': '7200',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '15000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '1',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '1',
          'MAX_JUDGMENTS_PER_WORKER': '100',
          'VIDEO_SIZE': '246'
      }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=120*60)
    se.wait(5*60*60)  # wait units to become judgeable

    # LOCUST
    workload = [
      {
          'start_at': '0:1:0',
          'target_count': 500,
          'finish_at': '0:60:0'
      },
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 25,
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '65m',
      'locust_config': {
          'JOB_TYPE': JOB_TYPE,
          'EXTERNAL': 'true',
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'WAIT_ON_ASSIGNMENT': '20',
          'PREDICT_BOX_RATE': '0.1',
          'WORKLOAD': json.dumps(workload),
          'WORKER_RANDOM_EXIT': '0.05'  # 13% complete 100 pages
      }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=100*60)
