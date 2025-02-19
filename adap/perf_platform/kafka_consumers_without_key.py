"""
https://appen.atlassian.net/browse/QED-2586#icft=QED-2586
"""
from adap.settings import Config
from adap.perf_platform.utils.results_handler import send_kafka_out
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.kafka_helpers import Consumer
from datetime import datetime
from adap.api_automation.utils.data_util import get_user
import json

log = get_logger(__name__)

env = Config.ENV

kafka_user = get_user('kafka_user')
kafka_password = kafka_user['password']
kafka_user = f'{kafka_user["user_name"]}'

client_config = {
    'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVER,
    'group.id': Config.KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    # replace with kafka user name and password here, or add config
    'sasl.username': kafka_user,
    'sasl.password': kafka_password
}

print(client_config)

topics = Config.KAFKA_CONSUMER_TOPICS
with Consumer(client_config, topics=topics) as consumer:
    while True:
        msg = consumer.poll(1.0)
        if msg:
            try:
                log.info({
                    'kafka user name is': "sasl.username",
                    'kafka user psw is': "sasl.password",
                    'consume message': "start consume message",
                    'msg_value': msg.value()
                })
                msg_value = msg.value().decode('utf-8') if msg.value() else ''
                details = {
                    'consumed_at': str(datetime.now()),
                    'topics': str(topics),
                    'partition': msg.partition()
                }
                if msg.error():
                    log.error({
                        'message': "Consumer error",
                        'msg_value': msg_value,
                        'error': msg.error(),
                        'details': details
                        })
                else:
                    log.debug({
                        'message': "Received message",
                        'msg_value': msg_value,
                        'details': details
                        })
                send_kafka_out(
                    "thirdtopic",
                    value=msg_value,
                    error=msg.error(),
                    details=details)
            except Exception as e:
                log.error({
                    'message': 'Error consuming message',
                    'exception': e.__repr__()
                    })
