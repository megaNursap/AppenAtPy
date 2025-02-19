from adap.perf_platform.test_scenarios import executor as se

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'

    kafka_topics = [
        'builder.aggregated.finalized.units.from.builder',
        'wfp.datalines.from.external.to.workflows',
        'wfp.builder.adapter.datalines.to.builder',
        'builder.units.from.external',
        'builder.units.creation.dead.letters',
        'raw.judgments.from.workerui',
        'db.builder.units',
    ]
    for i, topic in enumerate(kafka_topics):
        rs_config = {
              'name': f'kafka-consumers-{session_id}-{i}',
              'command': 'python',
              'args': ['adap/perf_platform/kafka_consumers_blank.py'],
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
