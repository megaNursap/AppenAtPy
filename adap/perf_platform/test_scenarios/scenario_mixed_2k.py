"""
0: create job_1
5: start locust_1 (for 45 min @ 500 j/m)
15: create workflow (3 jobs)
20: start locust_2_1 (for 20 min @ 1250 j/m)
30: start locust_2_2 and locust_2_3 (for 15 min @ 500 j/m each)
40: locust_2_1 finish
45: locust_2_1 and locust_2_2 finish
50: locust_1 finishes
"""

from adap.perf_platform.test_scenarios import executor as se

env = 'qa'

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    job_1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'ENV': env,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '600',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '6000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '100'
      }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=15*60)
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 2,
      'num_clients': 20,  # 20 * 25j/m ~ 500j/m
      'hatch_rate': 0.5,
      'run_time': '45m',
      'locust_config': {
        'ENV': env,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'DATA_SOURCE_FILE': 'qa_contributor_emails.py',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust_1)

    se.wait(10*60)

    # ------------------------- TASK II -------------------------
    TASK_ID = '2'
    wf = {
      'name': f'create-workflow-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_workflow.py',
      'job_config': {
          'ENV': env,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '600',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '6000'
      }
    }

    se.run_job(wf)
    se.wait_for_completion(wf, max_wait=15*60)
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST I
    locust_2_1 = {
      'suffix': f'{session_id}-{TASK_ID}-1',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 2,
      'num_clients': 50,  # 50 * 25j/m ~ 1250j/m
      'hatch_rate': 1,
      'run_time': '20m',
      'locust_config': {
        'ENV': env,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'MAX_WAIT_TIME': '600',
        'WORKFLOW_STEP': '1',
        'CAPTURE_RESULTS': 'true',
        'DATA_SOURCE_FILE': 'qa_contributor_emails.py',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust_2_1)

    se.wait(10*60)  # wait for jobs 2 and 3 of the workflow to get launched

    # LOCUST II
    locust_2_2 = {
      'suffix': f'{session_id}-{TASK_ID}-2',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 2,
      'num_clients': 20,  # 20 * 25j/m ~ 500j/m
      'hatch_rate': 0.5,
      'run_time': '15m',
      'locust_config': {
        'ENV': env,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'MAX_WAIT_TIME': '600',
        'WORKFLOW_STEP': '2',
        'CAPTURE_RESULTS': 'true',
        'DATA_SOURCE_FILE': 'qa_contributor_emails.py',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust_2_2)

    # LOCUST III
    locust_2_3 = {
      'suffix': f'{session_id}-{TASK_ID}-3',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 2,
      'num_clients': 20,  # 20 * 25j/m ~ 500j/m
      'hatch_rate': 0.5,
      'run_time': '15m',
      'locust_config': {
        'ENV': env,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'MAX_WAIT_TIME': '600',
        'WORKFLOW_STEP': '3',
        'CAPTURE_RESULTS': 'true',
        'DATA_SOURCE_FILE': 'qa_contributor_emails.py',
        'WAIT_ON_ASSIGNMENT': '11'
      }
    }
    se.run_locust(locust_2_3)

    # ------------------------- END -------------------------

    se.wait_for_completion(locust_2_1, max_wait=15*60)
    se.wait_for_completion(locust_2_2, max_wait=10*60)
    se.wait_for_completion(locust_2_3, max_wait=10*60)
    se.wait_for_completion(locust_1, max_wait=10*60)
