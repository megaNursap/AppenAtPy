"""
E2E performance testing of workflows, testing finalized units onwards (builder->dedup->workflows-builder-adapeter) to workflows.
1. Create a workflow with 3 jobs, set routers to job2 if judgment result is col1, router to job3 if judgment result is col2, upload 20000 units and launch the workflow
2. Start submitting judgments on the job1 (units get finalized and routed to job2 or job3 based on result)
3. After all assignments are completed from Step 2, start submitting judgments on the job2 and job3
​
Concurrently create another Job4 (not part of any workflow) and start submitting
judgments on that job.
​
Verify that all units from job1(WF) are finalized and routed to job2(WF) or job3(WF)
Verify that all units from job4(non-WF) are finalized and ignored by the Workflow Builder Adapter
"""

from adap.perf_platform.test_scenarios import executor as se
import json

ENV = 'integration'
scenario = f"[{ENV}] Workflows Builder Adapter functional test"

# These contributors can be used on ADAP integration env.
data_source_env_paths = {
    'integration': 'appen_connect/data/adap_integration_users.csv'
}

with se.session(scenario, teardown=False) as session_id:

    # Start Kafka consumers for each topic
    kafka_topics = [
        'builder.aggregated.finalized.units.from.builder',
        'wfp.datalines.from.external.to.workflows',
        'wfp.builder.adapter.datalines.to.builder',
        'builder.units.from.external',
        'builder.units.creation.dead.letters'
    ]
    rs_configs = []
    for i, topic in enumerate(kafka_topics):
        rs_config = {
              'name': f'kafka-consumers-{session_id}-{i}',
              'command': 'python',
              'args': ['adap/perf_platform/kafka_consumers.py'],
              'num_replicas': 1,
              'cmap_data': {
                'SESSION_ID': session_id,
                'TASK_ID': '0',
                'CAPTURE_RESULTS': 'true',
                'KAFKA_BOOTSTRAP_SERVER': '1.kafka.integration.cf3.us:9092,'
                                          '2.kafka.integration.cf3.us:9092,'
                                          '3.kafka.integration.cf3.us:9092',
                'KAFKA_TEST_TOPICS': topic,
              }
            }
        se.deploy_replicaset(rs_config)

    se.wait(10)

    def task1():
        TASK_ID = '1'
        # JOB_TYPE = 'what_is_greater'

        # Create and launch workflow
        wf = {
          'name': f'create-job-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/create_workflow.py',
          'job_config': {
              'ENV': ENV,
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              'MAX_WAIT_TIME': '600',
              'CAPTURE_RESULTS': 'true',
              'LOG_HTTP': 'false',
              'NUM_UNITS': '20000'  # 500u * 5j/ = 2500j
          }
        }
        se.run_job(wf)
        se.wait_for_completion(wf, max_wait=15*60)
        se.wait(3*60)  # wait for the job to become available in channels

        # Monitoring unit counts in Builder for each job in the WF
        for wf_step in ['1', '2', '3']:
            job_units_monitor = {
              'name': f'monitor-wf-job-units-{session_id}-{TASK_ID}-{wf_step}',
              'filename': 'adap/perf_platform/units_state_monitor.py',
              'job_config': {
                  'SESSION_ID': session_id,
                  'TASK_ID': TASK_ID,
                  'CAPTURE_RESULTS': 'true',
                  'MAX_WAIT_TIME': '2700',
                  'RUN_TIME': '3600',  # 1 hour
                  'UNITS_MONITOR_TYPE': 'counts',
                  'UNITS_MONITOR_SOURCE': 'task_info',
                  'WORKFLOW_STEP': wf_step
              }
            }
            se.run_job(job_units_monitor)

        # workload = [
        #     {
        #         'start_at': '0:0:1',
        #         'target_count': 10,
        #         'finish_at': '0:5:0'
        #     },
        #     {
        #         'start_at': '0:10:0',
        #         'target_count': 20,
        #         'finish_at': '0:11:0'
        #     },
        #     {
        #         'start_at': '0:15:0',
        #         'target_count': 30,
        #         'finish_at': '0:20:0'
        #     },
        #     {
        #         'start_at': '0:25:0',
        #         'target_count': 40,
        #         'finish_at': '0:30:0'
        #     }
        # ]

        # LOCUST I
        locust1 = {
          'suffix': f'{session_id}-{TASK_ID}-1',
          'filename': 'adap/perf_platform/locust_judge.py',
          'num_slaves': 5,
          'num_clients': 100,  # 50 * 25j/m = 1250j/m
          'hatch_rate': 0.1,
          'run_time': '45m',
          'locust_config': {
            'ENV': ENV,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '3000',
            'WORKFLOW_STEP': '1',
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'EXTERNAL': 'false',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV],
            #   see judgments.py, if config random_judgment, judgment result will be col1 or col2, if not configured, some units may not be routed to the job
            'RANDOM_JUDGMENT': 'true'
            # 'WORKLOAD': json.dumps(workload)
          }
        }
        se.run_locust(locust1)
        se.wait(5*60)  # wait for jobs 2 and 3 to become available in channels

        # LOCUST II
        locust2 = {
          'suffix': f'{session_id}-{TASK_ID}-2',
          'filename': 'adap/perf_platform/locust_judge.py',
          'num_slaves': 5,
          'num_clients': 100,  # 20 * 25j/m = 500j/m
          'hatch_rate': 0.1,
          'run_time': '45m',
          'locust_config': {
            'ENV': ENV,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '3000',
            'WORKFLOW_STEP': '2',
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'EXTERNAL': 'false',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV],
            'RANDOM_JUDGMENT': 'true'
            # 'WORKLOAD': json.dumps(workload)
          }
        }
        se.run_locust(locust2)

        # LOCUST III
        locust3 = {
          'suffix': f'{session_id}-{TASK_ID}-3',
          'filename': 'adap/perf_platform/locust_judge.py',
          'num_slaves': 5,
          'num_clients': 100,  # 20 * 25j/m = 500j/m
          'hatch_rate': 0.1,
          'run_time': '45m',
          'locust_config': {
            'ENV': ENV,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '3000',
            'WORKFLOW_STEP': '3',
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'EXTERNAL': 'false',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV],
            'RANDOM_JUDGMENT': 'true'
             # 'WORKLOAD': json.dumps(workload)
          }
        }
        se.run_locust(locust3)
        se.wait_for_completion(locust1, max_wait=65*60)
        se.wait_for_completion(locust2, max_wait=65*60)
        se.wait_for_completion(locust3, max_wait=65*60)

    def task2():
        TASK_ID = '2'
        # Create a regular job
        job = {
          'name': f'create-job-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/create_job.py',
          'job_config': {
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              'MAX_WAIT_TIME': '1800',
              'CAPTURE_RESULTS': 'true',
              'LOG_HTTP': 'false',
              'NUM_UNITS': '1000',
              'NUM_TEST_QUESTION': '100',
              'UNITS_PER_ASSIGNMENT': '5',
              'GOLD_PER_ASSIGNMENT': '1',
              'JUDGMENTS_PER_UNIT': '2',
              'MAX_JUDGMENTS_PER_WORKER': '100',
              'LAUNCH_JOB': 'true'
          }
        }
        se.run_job(job)
        se.wait_for_completion(job, max_wait=30*60)
        job_units_monitor = {
          'name': f'monitor-job-units-{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/units_state_monitor.py',
          'job_config': {
              'SESSION_ID': session_id,
              'TASK_ID': TASK_ID,
              'CAPTURE_RESULTS': 'true',
              'MAX_WAIT_TIME': '2700',
              'RUN_TIME': '3600',
              'UNITS_MONITOR_TYPE': 'counts',
              'UNITS_MONITOR_SOURCE': 'task_info',
          }
        }
        se.run_job(job_units_monitor)
        se.wait(5*60)  # wait for the job to become available in channels
        locust = {
          'suffix': f'{session_id}-{TASK_ID}',
          'filename': 'adap/perf_platform/locust_judge.py',
          'num_slaves': 2,
          'num_clients': 20,  # 20 * 25j/m = 500j/m
          'hatch_rate': 0.5,
          'run_time': '20m',
          'locust_config': {
            'ENV': ENV,
            'SESSION_ID': session_id,
            'TASK_ID': TASK_ID,
            'MAX_WAIT_TIME': '600',
            'CAPTURE_RESULTS': 'true',
            'WAIT_ON_ASSIGNMENT': '11',
            'EXTERNAL': 'false',
            'DATA_SOURCE_PATH': data_source_env_paths[ENV]
          }
        }
        se.run_locust(locust)
        se.wait_for_completion(locust, max_wait=65*60)

    se.execute_concurrent_func(task1, task2)
