"""
1. Deploy replicaset of 3 Kafka consumers
2. Start units count monitoring
3. Create and launch a job
4. Start judgments count monitoring
5. Deploy locusts to run for 60 min at 10 workers max after 30m ramp-up
6. Validate units data consumed from Kafka stream
"""

from adap.perf_platform.test_scenarios import executor as se
from adap.perf_platform.utils import results
import json

scenario = 'Internal judgment submission, 25 workers, 20 min'

with se.session(scenario=scenario, teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'

    JOB_TYPE = 'what_is_greater'

    job_units_monitor = {
      'name': f'monitor-job-units-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/units_state_monitor.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '2700',
          'RUN_TIME': '10800'  # 3 hours
      }
    }
    se.run_job(job_units_monitor)
    se.wait(15)  # wait for the units monitor pod to be created

    # creating and launnching a job
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
          'NUM_UNITS': '10000',
          'NUM_TEST_QUESTION': '300',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '100'
      }
    }
    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=30*60)

    job_judgments_monitor = {
      'name': f'monitor-job-judgments-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/judgments_monitor.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '2700',
          'RUN_TIME': '10800',  # 3 hours
          'INTERVAL': '5'  # take a measurement once every 5 seconds
      }
    }
    se.run_job(job_judgments_monitor)
    se.wait(15)  # wait for the judgments monitor pod to be created
    se.wait(3*60)  # wait for the job to become available in channels

    # LOCUST
    workload = [
        {
            'start_at': '0:1:0',
            'target_count': 25,
            'finish_at': '0:5:0'
        },
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 3,
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '20m',
      'locust_config': {
        'JOB_TYPE': JOB_TYPE,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'EXTERNAL': 'false',
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.05'
      }
    }

    # starting locust deployment
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=65*60)
    # wait for lagging messages to be consumed
    # wait for queued jobs in builder resque
    se.wait(5*60)

    def check(grade):
        if grade > 1:
            return ':white_check_mark:'
        else:
            return ':x:'

    # Compare aggregated results to the golden results

    # session_grade = results.compare_session_summary(
    #     current_session_id=session_id,
    #     golden_session_id=341)
    api_grade = results.compare_session_apis(
        current_session_id=session_id,
        golden_session_id=341)
    api_results_df = results.fetch_session_api_summary_df(session_id)
    se.post_performance_results(f"""
    API Performance Score: {api_grade} {check(api_grade)}
    ```{api_results_df.__str__()}```
    """)
    failed_requests_df = results.get_agg_failed_api_requests_df(session_id)
    if not failed_requests_df.empty:
        se.post_performance_results(f"""
    Failed API requests:
    ```{failed_requests_df.__str__()}```
    """)
