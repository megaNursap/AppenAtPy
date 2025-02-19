"""
Consumer for aggregated finalized units.
Calls Builder API for each unit consumed and des DeepDiff.
"""

from adap.settings import Config
from adap.perf_platform.utils.results_handler import send_kafka_out
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.kafka_helpers import Consumer
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user
from deepdiff import DeepDiff
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

api_key = get_user('perf_platform', env=Config.ENV).get('api_key')
api_service = Builder(
    env=Config.ENV,
    api_key=api_key)


def diff(a, b, exclude_paths=None):
    result = DeepDiff(a, b,
                      ignore_order=True,
                      exclude_paths=exclude_paths
                      )
    return result


def trav(val: dict):
    """
    Recursive traverse through val and replace all "type" objects
    with it's string representation so it can be jsonified later
    """
    if isinstance(val, dict):
        for k, v in val.items():
            val[k] = trav(v)
        return val
    elif isinstance(val, list):
        new_val = []
        for v in val:
            new_val.append(trav(v))
        return new_val
    elif isinstance(val, type):
        return repr(val)
    else:
        return val


def diff_unit_data(unit_data):
    unit_id = unit_data['id']
    job_id = unit_data['job_id']
    resp = api_service.get_unit(job_id=job_id, unit_id=unit_id)
    resp.assert_response_status(200)
    unit_expected = resp.json_response
    # exclude_paths = [
    #     "root['updated_at']",
    #     "root['results']"
    #     ]
    # mismatch = diff(unit_expected, unit_data, exclude_paths)
    mismatch = diff(unit_expected, unit_data)
    if mismatch:
        log.error({
            'message': 'Mismatch',
            'unit_id': unit_id,
            'diff': trav(mismatch)
            })


with Consumer(config) as consumer:
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg:
                try:
                    msg_key = msg.key().decode('utf-8')
                    msg_value = json.loads(msg.value().decode('utf-8'))
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
                    # diff_unit_data(msg_value)
                except Exception as e:
                    log.error({
                        'message': 'Error consuming message',
                        'exception': e.__repr__()
                        })
        except KeyboardInterrupt:
            break
