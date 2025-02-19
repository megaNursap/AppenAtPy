"""
1. Deploy replicaset of 3 Kafka consumers
2. Start units count monitoring (counts by state)
3. Create and launch a job
4. Start judgments count monitoring
5. Start units count monitoring (state changes per unit)
5. Deploy locusts to run for 20 min at 50 workers max after 10m ramp-up (Random answers)
6. After 5 finishes, update job settings to enable Dynamic Judgment Collection
7. Wait 10 min after 6, then Deploy locusts to run for 20 min at 50 workers max after 10m ramp-up (Correct answers only)
8. Validate units data consumed from Kafka stream against Builder
"""

from adap.perf_platform.test_scenarios import executor as se
import json

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'

    JOB_TYPE = 'what_is_greater'

    # creating replicaset of consumers
    rs_config = {
      'name': f'kafka-consumers-{session_id}-{TASK_ID}',
      'command': 'python',
      'args': ['adap/perf_platform/kafka_consumers_units.py'],
      'num_replicas': 3,
      'cmap_data': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'KAFKA_BOOTSTRAP_SERVER': '1.kafka.integration.cf3.us:9092,'
                                    '2.kafka.integration.cf3.us:9092,'
                                    '3.kafka.integration.cf3.us:9092',
          'KAFKA_CONSUMER_TOPICS': 'builder.aggregated.finalized.units.from.builder',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
      }
    }
    se.deploy_replicaset(rs_config)
    # se.wait(60)  # wait for the consumers to spin up

    job_units_monitor = {
      'name': f'monitor-job-units-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/units_state_monitor.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '2700',
          'RUN_TIME': '10800',  # 3 hours
          'UNITS_MONITOR_TYPE': 'counts'
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
          'NUM_UNITS': '30000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '2',
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

    # starting this after job launch since we focus on unit finalization here
    job_units_monitor2 = {
      'name': f'monitor-job-units2-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/units_state_monitor.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '2700',
          'RUN_TIME': '10800',  # 3 hours
          'UNITS_MONITOR_TYPE': 'state_changes',
          'INTERVAL': '5'  # fetch all units every 5s
      }
    }
    se.run_job(job_units_monitor2)

    # LOCUST
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}-1',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 5,
      'num_clients': 50,
      'hatch_rate': 0.083,
      'run_time': '20m',
      'locust_config': {
        'JOB_TYPE': JOB_TYPE,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'EXTERNAL': 'false',
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WORKER_RANDOM_EXIT': '0.07',  # 45% complete 10 assignments, 10% - 30
        'RANDOM_JUDGMENT': 'true'
      }
    }
    se.run_locust(locust_1)

    se.wait(20*60)

    new_job_settings = {
      'job[variable_judgments_mode]': 'auto_confidence',
      'job[max_judgments_per_unit]': 5,
      'job[min_unit_confidence]': 0.7,
      '_dynamic_judgment_fields': ['what_is_greater']
      }
    job_settings_update = {
      'name': f'update-job-settings-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/update_job.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'CAPTURE_RESULTS': 'true',
          'MAX_WAIT_TIME': '2700',
          'JOB_SETTINGS_UPDATE': json.dumps(new_job_settings)
      }
    }
    se.run_job(job_settings_update)

    se.wait(10*60)

    locust_2 = {
      'suffix': f'{session_id}-{TASK_ID}-2',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 5,
      'num_clients': 50,
      'hatch_rate': 0.083,
      'run_time': '20m',
      'locust_config': {
        'JOB_TYPE': JOB_TYPE,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'EXTERNAL': 'false',
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '11',
        'WORKER_RANDOM_EXIT': '0.07',  # 45% complete 10 assignments, 10% - 30
        'RANDOM_JUDGMENT': 'false'
      }
    }
    se.run_locust(locust_2)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_2, max_wait=65*60)
    # wait for lagging messages to be consumed
    # wait for queued jobs in builder resque
    se.wait(1*60*60)  # 1 hour

    validate_results = {
      'name': f'compare-judgments-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/compare_aggregated_units.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
      }
    }
    se.run_job(validate_results)
    se.wait_for_completion(validate_results, max_wait=60*60)
