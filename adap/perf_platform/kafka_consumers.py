
from adap.settings import Config
from adap.perf_platform.utils.results_handler import send_kafka_out
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.kafka_helpers import Consumer
from datetime import datetime
import json

log = get_logger(__name__)

client_config = {
    'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVER,
    'group.id': Config.KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    # replace with kafka user name and password here, or add config
    'sasl.username': Config.KAFKA_USERNAME,
    'sasl.password': Config.KAFKA_PASSWORD
}

topics = Config.KAFKA_CONSUMER_TOPICS
with Consumer(client_config, topics=topics) as consumer:
    while True:
        msg = consumer.poll(1.0)
        if msg:
            try:
                log.info({
                    'consume message': "start consume message",
                    'msg_key': msg.key().decode('utf-8'),
                    'msg_value': msg.value().decode('utf-8')
                })
                msg_key = msg.key().decode('utf-8') if msg.key() else ''
                # # msg_value = json.loads(msg.value().decode('utf-8')) if msg.value() else ''
                msg_value = msg.value().decode('utf-8') if msg.value() else ''
                # msg_key = msg.key() if msg.key() else ''
                # msg_value = msg.value() if msg.value() else ''
                details = {
                    'consumed_at': str(datetime.now()),
                    'topics': str(topics),
                    'partition': msg.partition()
                }
                if msg.error():
                    log.error({
                        'message': "Consumer error",
                        'msg_key': msg_key,
                        'msg_value': msg_value,
                        'error': msg.error(),
                        'details': details
                        })
                else:
                    log.debug({
                        'message': "Received message",
                        'msg_key': msg_key,
                        'msg_value': msg_value,
                        'details': details
                        })
                send_kafka_out(
                    msg_key,
                    value=msg_value,
                    error=msg.error(),
                    details=details)
            except Exception as e:
                log.error({
                    'message': 'Error consuming message',
                    'exception': e.__repr__()
                    })
