"""
1. Deploy replicaset of 3 Kafka consumers
2. Send message to kafka topic builder.aggregated.finalized.units.from.builder
"""

from adap.perf_platform.test_scenarios import executor as se
from adap.perf_platform.utils.logging import get_logger
import socket
log = get_logger(__name__)

with se.session(teardown=False) as session_id:

    # ------------------------- TASK I -------------------------
    TASK_ID = '1'
    se.init_task(TASK_ID)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('pkc-4nym6.us-east-1.aws.confluent.cloud', 9092))
    if result == 0:
        log.info({
            'message': 'Port is open'
        })
    else:
        log.info({
            'message': 'Port is not open'
        })
    sock.close()


    _consumerconfig = {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'KAFKA_BOOTSTRAP_SERVER': 'pkc-4nym6.us-east-1.aws.confluent.cloud:9092',
        'KAFKA_TEST_TOPICS': 'builder.aggregated.finalized.units.from.builder'
    }

    _producerconfig = {
        'SESSION_ID': session_id,
        'TASK_ID': TASK_ID,
        'CAPTURE_RESULTS': 'true',
        'KAFKA_BOOTSTRAP_SERVER': 'pkc-4nym6.us-east-1.aws.confluent.cloud:9092',
        'KAFKA_TEST_TOPICS': 'builder.raw.aggregated.finalized.units.from.builder'
    }

    rs_config = {
      'name': f'kafka-consumers-{session_id}-{TASK_ID}',
      'command': 'python',
      'args': ['adap/perf_platform/kafka_consumers.py'],
      'num_replicas': 3,
      'cmap_data': {
          **_consumerconfig
      }
    }

    se.deploy_replicaset(rs_config)
    se.wait(120)  # wait for the consumers to spin up

    kafka_producers = {
      'suffix': f'{session_id}-{TASK_ID}',
      'filename': 'adap/perf_platform/kafka_producers_locust.py',
      'num_slaves': 5,
      'num_clients': 20,
      'hatch_rate': 0.2,
      'run_time': '10m',
      'locust_config': {
          **_producerconfig
      }
    }

    se.run_locust(kafka_producers)
    se.wait_for_completion(kafka_producers, max_wait=60*60)
