"""
Reproduce https://crowdflower.atlassian.net/wiki/spaces/ENGR/pages/1025016114/2020-01-17+Giphy+job+results+in+Builder+Postgresql+outage
Job 1473418 collected most of the judgments (87%) across all running jobs
during the hour when platform failed, so I'm only running one job.
Some contributors submitted ~1500 judgments on that job
Some units collected 14 judgments

1% chance of random worker exit:
tasks chance_of_completion
10    89.53%
20    80.97%
50    59.90%
100   36.24%
150   21.92%

This test should take ~2.5 hours including job launch.

750 workers => 900 tasks/m
10 units/page => 9000 j/m
9000j/m * 60m =540k j/h
540k + 540k/2 (ramp-up & ramp-down) = 810k judgments

TODO: check if jobs were launched or high volumes of units loaded/ordered
TODO: units for 1473418 were ordered continuously,
94k units were ordered the hour before failure
"""

from adap.perf_platform.test_scenarios import executor as se
import json

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    JOB_TYPE = 'image_annotation'
    job_1 = {
      'name': f'create-job-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/create_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'JOB_TYPE': JOB_TYPE,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
          'NUM_UNITS': '200000',
          'NUM_TEST_QUESTION': '1000',
          'UNITS_PER_ASSIGNMENT': '10',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '',  # NOT SET !!!
          # 'AUTO_ORDER': 'TRUE',  # TODO: Turn on automatic launching of rows
          # 'AUTO_ORDER_THRESHOLD': '9' - this wasn't set in UI
          # 'CONTRIBUTOR_LEVEL': '3',  # Can this affect performance?
          # 'CONTAINS_EXPLICIT_CONTENT': 'TRUE',  # Can this affect performance?
          # 'MINIMUM_TIME_PER_PAGE': '20',
          # 'DYNAMIC_JUDGMENT_COLLECTION': 'TRUE', # TODO
          # 'MAX_JUDGMENTS_PER_ROW': '10',  # TODO
          # 'MINIMUM_CONFIDENCE': '0.75',  # TODO
          # # TODO: this ^^ will require parametrised corretness on judgments (possibly on specific units)
          # 'WEBHOOK URL': 'http://someurl.com'  # Can this affect performance?
          # Admin -> Webhook -> Ensure that the Webhook is always sent, even after failures
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
        'JOB_TYPE': JOB_TYPE,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '50',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.01'
      }
    }

    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=30*60)
    se.wait(5*60)
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=135*60)
