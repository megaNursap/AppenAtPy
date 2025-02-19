from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'staging'
desc = "Load test"
with se.session(desc, env=ENV, teardown=False) as session_id:

    JOB_TYPE = 'what_is_greater'
    TASK_ID = '1'

    job_units_monitor = {
    'name': f'monitor-job-units-{session_id}-{TASK_ID}',
    'filename': 'adap/perf_platform/units_state_monitor.py',
    'job_config': {
        'ENV': ENV,
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
        'ENV': ENV,
        'JOB_TYPE': JOB_TYPE,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'MAX_WAIT_TIME': '2700',
        'CAPTURE_RESULTS': 'true',
        'LOG_HTTP': 'false',
        'NUM_UNITS': '20000',
        'NUM_TEST_QUESTION': '0',
        'UNITS_PER_ASSIGNMENT': '5',
        'GOLD_PER_ASSIGNMENT': '0',
        'JUDGMENTS_PER_UNIT': '3',
        'MAX_JUDGMENTS_PER_WORKER': '100'
    }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=2700)

    job_judgments_monitor = {
      'name': f'monitor-job-judgments-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/judgments_monitor.py',
      'job_config': {
          'ENV': ENV,
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '2700',
          'RUN_TIME': '10800',  # 3 hours
          'INTERVAL': '5'  # take a measurement once every 5 seconds
      }
    }
    se.run_job(job_judgments_monitor)

    workload = [
    {
        'start_at': '0:0:1',
        'target_count': 100,
        'finish_at': '0:10:0'
    },
    ]
    # LOCUST
    locust = {
    'suffix': f'{session_id}-{TASK_ID}',
    'filename': 'adap/perf_platform/locust_judge.py',
    'num_slaves': 1,
    'num_clients': 1,
    'hatch_rate': 1,
    'run_time': '20m',
    'locust_config': {
        'ENV': ENV,
        'JOB_TYPE': JOB_TYPE,
        'EXTERNAL': 'false',
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.02',  # 13% complete 100 pages
    }
    }
    se.run_locust(locust)
    se.wait_for_completion(locust, max_wait=2*60*60)