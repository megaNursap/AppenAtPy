"""
3000 workers, 50s per assignment => ~3600 assignment/m
5 units/page => ~18000 judgments/m (3600 golds) => 1.08M j/m

Jobs are created and launched first in the following order:
job1 - 200k units, 1500 workers
job2 - 100k units, 750 workers
job3 - 60k units, 450 workers
job4 - 40k units, 300 workers

Once jobs are launched, there is 10 minute delay before starting locusts
to make sure units are processed into judgmable state.
All 4 are deployed at the same time and have similar workloads:
  Ramp up to full capacity in 30 minutes
  Steady at full capacity for 1 hour
  Ramp down to 0 in 30 minutes
Worker submits assignment every 50 sec.
With 4% chance of random worker exit, 70% workers will complete
all 10 assignments.

"""

from adap.perf_platform.test_scenarios import executor as se
import json

with se.session(teardown=True) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'

    job_1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '200000',
          'NUM_TEST_QUESTION': '1000',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '50'
      }
    }

    # LOCUST
    workload = [
        {
            'start_at': '0:1:0',
            'target_count': 1500,
            'finish_at': '0:30:0'
        },
        {
            'start_at': '1:30:0',
            'target_count': 0,
            'finish_at': '1:59:00'
        },
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 30,  # 1500/50
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '130m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '50',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.04'
      }
    }

    # ------------------------- TASK II -------------------------
    TASK_ID = '2'

    job_2 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '100000',
          'NUM_TEST_QUESTION': '500',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '50'
      }
    }

    # LOCUST
    workload = [
        {
            'start_at': '0:1:0',
            'target_count': 750,
            'finish_at': '0:30:0'
        },
        {
            'start_at': '1:30:0',
            'target_count': 0,
            'finish_at': '1:59:00'
        },
    ]
    locust_2 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 15,  # 750/50
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '130m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '50',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.04'
      }
    }

    # ------------------------- TASK III -------------------------
    TASK_ID = '3'

    job_3 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '60000',
          'NUM_TEST_QUESTION': '500',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '50'
      }
    }

    # LOCUST
    workload = [
        {
            'start_at': '0:1:0',
            'target_count': 450,
            'finish_at': '0:30:0'
        },
        {
            'start_at': '1:30:0',
            'target_count': 0,
            'finish_at': '1:59:00'
        },
    ]
    locust_3 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 9,  # 450/50
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '130m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '50',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.04'
      }
    }

    # ------------------------- TASK IV -------------------------
    TASK_ID = '4'

    job_4 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '40000',
          'NUM_TEST_QUESTION': '500',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '50'
      }
    }

    # LOCUST
    workload = [
        {
            'start_at': '0:1:0',
            'target_count': 300,
            'finish_at': '0:30:0'
        },
        {
            'start_at': '1:30:0',
            'target_count': 0,
            'finish_at': '1:59:00'
        },
    ]
    locust_4 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 6,  # 300/50
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '130m',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '50',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.04'
      }
    }

    # ------------------------- START EXECUTION -------------------------

    # creating and launnching all 4 jobs
    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=30*60)
    se.run_job(job_2)
    se.wait_for_completion(job_2, max_wait=30*60)
    se.run_job(job_3)
    se.wait_for_completion(job_3, max_wait=30*60)
    se.run_job(job_4)
    se.wait_for_completion(job_4, max_wait=30*60)
    se.wait(10*60)  # wait for the job to become available in channels
    # starting 4 locust deployments
    se.run_locust(locust_1)
    se.run_locust(locust_2)
    se.run_locust(locust_3)
    se.run_locust(locust_4)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=130*60)
    se.wait_for_completion(locust_2, max_wait=5*60)
    se.wait_for_completion(locust_3, max_wait=5*60)
    se.wait_for_completion(locust_4, max_wait=5*60)
