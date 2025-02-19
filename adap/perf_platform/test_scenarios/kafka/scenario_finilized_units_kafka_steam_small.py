"""
1. Deploy replicaset of 3 Kafka consumers
2. Start units count monitoring
3. Create and launch a job
4. Start judgments count monitoring
5. Deploy locusts to run for 60 min at 200 workers max after 30m ramp-up
6. Validate units data consumed from Kafka stream
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
          'NUM_TEST_QUESTION': '300',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '1',
          'JUDGMENTS_PER_UNIT': '2',
          'MAX_JUDGMENTS_PER_WORKER': '200'
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
    workload = [
        {
            'start_at': '0:1:0',
            'target_count': 400,
            'finish_at': '0:60:0'
        }
    ]
    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 10,
      'num_clients': 1,
      'hatch_rate': 1,
      'run_time': '60m',
      'locust_config': {
        'JOB_TYPE': JOB_TYPE,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'EXTERNAL': 'false',
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '60',
        'WORKLOAD': json.dumps(workload),
        'WORKER_RANDOM_EXIT': '0.07'  # 45% complete 10 assignments, 10% - 30
      }
    }

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

    # starting locust deployment
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=65*60)
    # wait for lagging messages to be consumed
    # wait for queued jobs in builder resque
    se.wait(3*60*60)
    se.run_job(validate_results)
    se.wait_for_completion(validate_results, max_wait=30*60)
