"""
1. Deploy replicaset of 3 Kafka consumers
2. Create and launch a job
3. Deploy locusts to run for 60 min at 60 workers max
"""

from adap.perf_platform.test_scenarios import executor as se

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    JOB_TYPE = 'video_annotation'
    rs_config = {
      'name': f'kafka-consumers-{session_id}-{TASK_ID}',
      'command': 'python',
      'args': ['adap/perf_platform/kafka_consumers_judgments.py'],
      'num_replicas': 3,
      'cmap_data': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'KAFKA_SERVER': '1.kafka.integration.cf3.us:9092',
          'KAFKA_CONSUMER_TOPICS': 'global.judgments.from.workerui',
          'CAPTURE_RESULTS': 'true',
      }
    }

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
          'NUM_UNITS': '1000',
          'NUM_TEST_QUESTION': '0',
          'UNITS_PER_ASSIGNMENT': '5',
          'GOLD_PER_ASSIGNMENT': '0',
          'JUDGMENTS_PER_UNIT': '3',
          'MAX_JUDGMENTS_PER_WORKER': '10'
      }
    }

    locust_1 = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/locust_judge.py',
      'num_slaves': 5,
      'num_clients': 10,
      'hatch_rate': 0.3,
      'run_time': '5m',
      'locust_config': {
        'JOB_TYPE': JOB_TYPE,
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'WAIT_ON_ASSIGNMENT': '10',
        'WORKER_RANDOM_EXIT': '0.05',
        'PREDICT_BOX_RATE': '0.8'
      }
    }

    compare_judgments = {
      'name': f'compare-judgments-{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/compare_judgments.py',
      'job_config': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'MAX_WAIT_TIME': '1800',
          'CAPTURE_RESULTS': 'true',
          'LOG_HTTP': 'false',
      }
    }
    # creating replicaset of consumers
    se.deploy_replicaset(rs_config)
    # se.wait(2*60)  # wait for the consumers to spin up
    # creating and launnching a job
    se.run_job(job_1)
    se.wait_for_completion(job_1, max_wait=30*60)
    se.wait(3*60)  # wait for the job to become available in channels
    # starting locust deployment
    se.run_locust(locust_1)

    # ------------------------- END -------------------------
    se.wait_for_completion(locust_1, max_wait=60*60)
    # wait for lagging messages to be consumed
    se.wait(2*60)
    se.run_job(compare_judgments)
    se.wait_for_completion(compare_judgments, max_wait=30*60)
