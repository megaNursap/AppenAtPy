from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'integration'

with se.session() as session_id:
    TASK_ID = '1'

    JOB_TYPE = 'what_is_greater'

    se.init_task(TASK_ID)

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

    job1 = {
        'name': f'create-job-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/create_job.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'JOB_TYPE': JOB_TYPE,
            'MAX_WAIT_TIME': '5400',
            'CAPTURE_RESULTS': 'true',
            'LOG_HTTP': 'false',
            'NUM_UNITS': '30000',
            'UNITS_PER_ASSIGNMENT': '5',
            'GOLD_PER_ASSIGNMENT': '0',
            'JUDGMENTS_PER_UNIT': '5',
            'MAX_JUDGMENTS_PER_WORKER': '100',
            'DYNAMIC_JUDGMENT_COLLECTION': 'true',
            'MAX_JUDGMENTS_PER_UNIT': '100',
            'MIN_UNIT_CONFIDENCE': '0.9'
        }
    }

    se.run_job(job1)
    se.wait_for_completion(job1, max_wait=15 * 60)
    se.wait(3 * 60)  # wait for the job to become available in channels

    job_judgments_monitor = {
        'name': f'monitor-job-judgments-{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/judgments_monitor.py',
        'job_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'CAPTURE_RESULTS': 'true',
            'MAX_WAIT_TIME': '5400',
            'RUN_TIME': '10800',  # 3 hours
            'INTERVAL': '5'  # take a measurement once every 5 seconds
        }
    }
    se.run_job(job_judgments_monitor)

    workload = [
        {
            'start_at': '0:0:1',
            'target_count': 100,
            'finish_at': '0:20:0'
        }
    ]
    # LOCUST
    locust1 = {
        'suffix': f'{session_id}-{TASK_ID}',
        'filename': 'adap/perf_platform/locust_judge.py',
        'num_slaves': 1,
        'num_clients': 1,
        'hatch_rate': 1,  # 5 min ramp up
        'run_time': '20m',
        'locust_config': {
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '3600',
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'RANDOM_JUDGMENT': 'true',
            'EXTERNAL': 'false',
            'WORKLOAD': json.dumps(workload)
        }
    }
    se.run_locust(locust1)
    se.wait_for_completion(locust1, max_wait=120 * 60)
