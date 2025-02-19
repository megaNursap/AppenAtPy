"""
https://appen.atlassian.net/browse/QED-1422
Create 1 job, 5 images/page. ~25s to complete a page of work.
Deploy locust and increase number of workers load gradually
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
          'MAX_WAIT_TIME': '2700',
          'RUN_TIME': '36000'  # 10 hours
      }
    }
    se.run_job(job_units_monitor)
    se.wait(15)  # wait for the units monitor pod to be created
    job_1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'JOB_TYPE': 'image_annotation',
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '2700',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '100000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '100'
      }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=2700)
    se.wait(20*60)  # wait for the job to become available in channels

    workload = [
      {
          'start_at': '0:1:0',
          'target_count': 600,
          'finish_at': '0:45:0'
      },
    ]
    # LOCUST
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 15,
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '60m',
      'locust_config': {
        'JOB_TYPE': 'image_annotation',
        'EXTERNAL': 'false',
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '25',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.02',  # 13% complete 100 pages
        'NUM_ANNOTATIONS_PER_UNIT': '1'
      }
    }
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=90*60)
