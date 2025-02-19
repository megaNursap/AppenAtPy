
from adap.settings import Config
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.kafka_helpers import Consumer

log = get_logger(__name__)

config = {
    'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVER,
    'group.id': Config.KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': Config.KAFKA_USERNAME,
    'sasl.password': Config.KAFKA_PASSWORD
}


with Consumer(config) as consumer:
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg:
                try:
                    msg_key = msg.key().decode('utf-8')
                    if msg.error():
                        log.error({
                            'message': "Consumer error",
                            'msg_key': msg_key,
                            'error': msg.error()
                            })
                    else:
                        log.debug({
                            'message': "Received message",
                            'msg_key': msg_key,
                            })
                except Exception as e:
                    log.error({
                        'message': 'Error consuming message',
                        'exception': e.__repr__()
                        })
        except KeyboardInterrupt:
            break
