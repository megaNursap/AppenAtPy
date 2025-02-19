"""
Job Auto Throttling
Create Job: 100k units, no TQ, Internal
Job Judgments Monitor

AUTO_THROTTLING_ENABLED=true
AUTO_THROTTLING_TEST_MODE=false
AUTO_THROTTLING_MAX_JUDGMENTS_PER_MINUTE=250
AUTO_THROTTLING_MAX_THROTTLED_JOBS=2
AUTO_THROTTLING_EXEMPT_TEAM_IDS="67d5807c-b1a5-4806-a5e7-bd7b7e631b88,0dc65bb9-803b-4531-b4ae-bd1d5455c96c"

run 2 tasks: 2 jobs, same load
after 10 minutes, start adding more workers to job2
keep adding until threshold reached on job2
verify it starts throttling
workers should get "Task has been throttled!"
verify job1 is not affected
reduce load on job2 until below threshold for 5 minutes
verify job is not throttled
increase load above threshold for a short period of time (< 5 min)
verify job is not throttled

5 workers * 6 pages/min * 5 units/page = 150 J/min

"""

from adap.perf_platform.test_scenarios import executor as se
import json

desc = "Job auto throttling"
with se.session(desc, teardown=False) as session_id:

    TASK_IDS = ['1', '2']
    JOB_TYPE = 'what_is_greater'

    def create_jobs(TASK_ID):
        
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
            'JOB_TYPE': JOB_TYPE,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '2700',
            'CAPTURE_RESULTS': 'true',
            'LOG_HTTP': 'false',
            'NUM_UNITS': '50000',
            'NUM_TEST_QUESTION': '0',
            'UNITS_PER_ASSIGNMENT': '5',
            'GOLD_PER_ASSIGNMENT': '0',
            'JUDGMENTS_PER_UNIT': '3',
            'MAX_JUDGMENTS_PER_WORKER': '100'
        }
        }

        se.run_job(job_1)
        se.wait_for_completion(job_1, max_wait=2700)

    se.execute_concurrent(create_jobs, TASK_IDS)
    se.wait(10*60)


    def deploy_locust_1():
        TASK_ID = '1'
        
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

        workload = [{
            'start_at': '0:0:1',
            'target_count': 5,
            'finish_at': '0:1:0'
        }]
        # LOCUST
        locust_1 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/locust_judge.py',
        'num_slaves': 1,
        'num_clients': 1,
        'hatch_rate': 1,
        'run_time': '30m',
        'locust_config': {
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
        se.run_locust(locust_1)


    def deploy_locust_2():
        TASK_ID = '2'
        
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

        workload = [
        {
            'start_at': '0:0:1',
            'target_count': 5,
            'finish_at': '0:1:0'
        },
        {
            'start_at': '0:5:0',
            'target_count': 20,
            'finish_at': '0:10:0'
        },
        {
            'start_at': '0:15:0',
            'target_count': 5,
            'finish_at': '0:16:0'
        },
        {
            'start_at': '0:20:0',
            'target_count': 20,
            'finish_at': '0:25:0'
        },
        ]
        # LOCUST
        locust_2 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/locust_judge.py',
        'num_slaves': 1,
        'num_clients': 1,
        'hatch_rate': 1,
        'run_time': '40m',
        'locust_config': {
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
        se.run_locust(locust_2)

    se.execute_concurrent_func(deploy_locust_1, deploy_locust_2)
    se.wait(45*60)