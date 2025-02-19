"""
1. Deploy replicaset of 3 Kafka consumers
2. Create and launch a job
3. Deploy locusts to run Kafka producers
"""

from adap.perf_platform.test_scenarios import executor as se

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    _config = {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'KAFKA_BOOTSTRAP_SERVER': '1.kafka.integration.cf3.us:9092',
        'KAFKA_TEST_TOPICS': 'global.judgments.from.workerui',
    }

    rs_config = {
      'name': f'kafka-consumers-{session_id}-{TASK_ID}',
      'command': 'python',
      'args': ['adap/perf_platform/kafka_consumers.py'],
      #   'args': ['adap/perf_platform/kafka_consumers_judgments.py'],
      'num_replicas': 3,
      'cmap_data': {
          **_config
      }
    }

    se.deploy_replicaset(rs_config)
    se.wait(60)  # wait for the consumers to spin up

    kafka_producers = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/kafka_producers_locust.py',
      # 'filename': 'adap/perf_platform/kafka_producer_judgments_locust.py',
      'num_slaves': 2,
      'num_clients': 20,
      'hatch_rate': 0.3,
      'run_time': '5m',
      'locust_config': {
          **_config
      }
    }

    se.run_locust(kafka_producers)
    se.wait_for_completion(kafka_producers, max_wait=25*60)
