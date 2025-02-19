from adap.perf_platform.test_scenarios import executor as se

with se.session() as session_id:

    # ------------------------- TASK I -------------------------
    tasks = [str(x) for x in range(1, 11)]
    jobs_monitors = []
    for TASK_ID in tasks:
        job_units_monitor = {
            'name': f'monitor-job-units-{session_id}-{TASK_ID}',
            'filename': 'adap/perf_platform/units_state_monitor.py',
            'job_config': {
                'SESSION_ID': session_id,
                'TASK_ID': TASK_ID,
                'CAPTURE_RESULTS': 'true',
                'MAX_WAIT_TIME': '1200',
                'RUN_TIME': '600'
            }
        }
        se.run_job(job_units_monitor)
        jobs_monitors.append(job_units_monitor)

    se.wait(10)  # wait for the units monitor pod to be created

    JOB_TYPE = 'image_annotation'
    jobs = []
    for TASK_ID in tasks:
        job_1 = {
            'name': f'create-job-{session_id}-{TASK_ID}',
            'filename': 'adap/perf_platform/create_job.py',
            'job_config': {
                'JOB_TYPE': JOB_TYPE,
                'SESSION_ID': session_id,
                'TASK_ID': TASK_ID,
                'MAX_WAIT_TIME': '600',
                'CAPTURE_RESULTS': 'true',
                'LOG_HTTP': 'false',
                'NUM_UNITS': '15000',
                'NUM_TEST_QUESTION': '0',
                'UNITS_PER_ASSIGNMENT': '3',
                'GOLD_PER_ASSIGNMENT': '0',
            }
        }
        se.run_job(job_1)
        jobs.append(job_1)

    for job in jobs:
        se.wait_for_completion(job, max_wait=20 * 60)

    for job in jobs_monitors:
        se.wait_for_completion(job, max_wait=20 * 60)
