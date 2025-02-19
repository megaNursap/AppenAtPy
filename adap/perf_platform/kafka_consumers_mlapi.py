
from adap.settings import Config
from utils.results_handler import send_kafka_out
from utils.logging import get_logger
from utils.kafka_helpers import Consumer
import json

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
                msg_value = json.loads(msg.value().decode('utf-8'))
                data_line_id = msg_value.get('data_line_id')
                if msg.error():
                    log.error({
                        'message': "Consumer error",
                        'data_line_id': data_line_id,
                        'error': msg.error()
                        })
                else:
                    log.info({
                        'message': "Received message",
                        'data_line_id': data_line_id,
                        'msg_value': msg_value
                        })
                send_kafka_out(data_line_id, error=msg.error())
        except KeyboardInterrupt:
            break
