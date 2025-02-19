from adap.perf_platform.test_scenarios import executor as se
import json

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
          'NUM_UNITS': '5000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '5',
          'MAX_JUDGMENTS_PER_WORKER': '25'
      }
    }

    se.run_job(job1)
    se.wait_for_completion(job1, max_wait=15*60)
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST
    workload = [
        {
            'start_at': '0:5:0',
            'target_count': 20,
            'finish_at': '0:6:0'
        },
        {
            'start_at': '0:9:0',
            'target_count': 5,
            'finish_at': '0:9:30'
        },
        {
            'start_at': '0:12:0',
            'target_count': 20,
            'finish_at': '0:13:0'
        },
    ]
    locust1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 3,
      'num_clients': 10,
      'hatch_rate': 0.1,
      'run_time': '20m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WORKLOAD': json.dumps(workload)
      }
    }
    se.run_locust(locust1)
    se.wait_for_completion(locust1, max_wait=25*60)
