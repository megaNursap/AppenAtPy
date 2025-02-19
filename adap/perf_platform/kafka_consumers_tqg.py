
from adap.settings import Config
from adap.perf_platform.utils.results_handler import send_kafka_out
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.kafka_helpers import Consumer
from datetime import datetime
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


def get_step_name(m):
    if dpt := m.get('data_processor_type'):
        if dpt == 'Builder::Job':
            if not m.get('data_out'):
                res = 'tq_from_wf_to_builder_adapter'
            else:
                res = 'finalized_units_agg_from_tqg_job_to_wf'
        elif dpt == 'TQG':
            if m.get('data_in'):
                res = 'finalized_units_agg_from_wf_to_tqg_converter'
            elif m.get('data_out'):
                res = 'tq_from_tqg_converter_to_wf'
            else:
                log.error(f'unknown {m}')
    else:
        if m.get('data').get('_golden'):
            res = 'tq_from_wf_to_original_job'
        else:
            res = 'units_from_original_job_to_wf'
    return res


with Consumer(config) as consumer:
    while True:
        msg = consumer.poll(1.0)
        if msg:
            try:
                msg_key = msg.key().decode('utf-8') if msg.key() else ''
                msg_value = json.loads(msg.value().decode('utf-8')) if msg.value() else ''
                msg_value['kafka_consumed_at'] = str(datetime.now())
                msg_value['kafka_partition'] = msg.partition()
                # for TQG only
                msg_value['kafka_step'] = get_step_name(msg_value)
                if msg.error():
                    log.error({
                        'message': "Consumer error",
                        'msg_key': msg_key,
                        'msg_value': msg_value,
                        'error': msg.error()
                        })
                else:
                    log.debug({
                        'message': "Received message",
                        'msg_key': msg_key,
                        'msg_value': msg_value
                        })
                send_kafka_out(msg_key, value=msg_value, error=msg.error())
            except Exception as e:
                log.error({
                    'message': 'Error consuming message',
                    'exception': e.__repr__()
                    })
