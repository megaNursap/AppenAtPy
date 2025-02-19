from adap.perf_platform.test_scenarios import executor as se


with se.session(teardown=False) as session_id:

    TASK_ID = '1'

    rs_config = {
      'name': f'kafka-consumers-{session_id}-{TASK_ID}',
      'command': 'python',
      'args': ['adap/perf_platform/kafka_consumers_mlapi.py'],
      'num_replicas': 3,
      'cmap_data': {
          'SESSION_ID': session_id,
          'TASK_ID': TASK_ID,
          'KAFKA_BOOTSTRAP_SERVER': '1.kafka.integration.cf3.us:9092',
          'CAPTURE_RESULTS': 'true',
          'KAFKA_TEST_TOPICS': 'mlapi.models.predict.test.from.mlapi,'
                               'mlapi.models.predict.test.dead.letters'
      }
    }
    se.deploy_replicaset(rs_config)
    se.wait(2*60)  # wait for the consumers to spin up

    # PRODUCERS
    kafka_producers = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/kafka_producer_mlapi_locust.py',
      'num_slaves': 3,
      'num_clients': 25,
      'hatch_rate': 2.5,
      'run_time': '45s',
      'locust_config': {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'KAFKA_BOOTSTRAP_SERVER': '1.kafka.integration.cf3.us:9092',
        'KAFKA_TEST_TOPICS': 'mlapi.models.predict.test.to.mlapi'
      }
    }
    se.run_locust(kafka_producers)
    se.wait_for_completion(kafka_producers, max_wait=15*60)

    se.wait(10*60)  # wait for all messages to be consumeed
