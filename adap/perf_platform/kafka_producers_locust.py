
from locust import TaskSet, task, between, events
from confluent_kafka import Producer
from adap.settings import Config
from utils.logging import get_logger
from utils.results_handler import send_kafka_in, send_kafka_in_batch
from utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener
    )
from datetime import datetime
from adap.api_automation.utils.data_util import get_user
import json
import warnings
import uuid
import gevent
import time
import random

env = Config.ENV

kafka_user = get_user('kafka_user')
kafka_password = kafka_user['password']
kafka_user = f'{kafka_user["user_name"]}'

warnings.filterwarnings("ignore")

log = get_logger(__name__, stdout=False)

config = {'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVER,
          'group.id': Config.KAFKA_GROUP_ID,
          'session.timeout.ms': 6000,
          'auto.offset.reset': 'earliest',
          'enable.auto.commit': True,
          'sasl.mechanism': 'PLAIN',
          'security.protocol': 'SASL_SSL',
          # replace with kafka user name and password here, or add config
          'sasl.username': kafka_user,
          'sasl.password': kafka_password,
          # check https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html
          'acks': 0
          }

print(config)

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.producer = Producer(config)
        log.info({
          'message': 'confluent_kafka.Producer created',
        })

    def callback_delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """

        msg_key = msg.key().decode('utf-8')
        if err is not None:
            log.error({
              'message': 'Message delivery failed',
              'msg_key': msg_key,
              'error': err
            })
        else:
            log.debug({
              'message': 'Message delivered',
              'msg_key': msg_key,
              'topic': msg.topic(),
              'partition': msg.partition()
            })

    def throttle(self, t0):
        """
        Waits until required time passes
        to ensure that each task takes at least 1 second
        """
        t1 = time.time()
        td = t1 - t0
        if 1 - td > 0.1:
            gevent.sleep(1 - td)

    def produce(self):
        # Trigger any available delivery report callbacks from previous produce() calls
        log.info({
            'start sending time': str(datetime.now())
        })
        self.producer.poll(1.0)

        t0 = time.time()
        message_body = json.dumps({
            'uid': uuid.uuid4().__str__(),
            'session_id': Config.SESSION_ID,
            'task_id': Config.TASK_ID,
            'created_at': str(datetime.now())
          })
        message_key = uuid.uuid4().__str__()

        # Insert a row into kafka_in table in ResultsDB
        Config.produced_messages_list.append(
          (str(datetime.now()), Config.SESSION_ID, message_key, message_body)
          )

        log.info({
            'Producer data_line_id:': "96364c2a-09cd-11ec-8289-1ab017faae5w"
        })
        value_to_be_sent = "{\"id\":2209430552,\"data\":{\"query\":\"b\",\"title\":\"toy trucks\",\"image_url\":\"http://www.overstock.com/search?keywords=toy+trucks&taxonomy=sto5&ralt=sto1,sto3,sto35&TID=AR:TRUE&searchtype=Header\",\"data_line_id\":\"96364c2a-09cd-11ec-8289-1ab017faae5w\",\"workflow_id\":45238,\"step_id\":53269,\"data_upload_id\":16530,\"launch_order_id\":null,\"row_number\":1,\"row_launched_at\":1629477890873,\"_kafka_agg_units_enabled\":-1},\"judgments_count\":1,\"state\":\"finalized\",\"agreement\":1,\"missed_count\":0,\"gold_pool\":null,\"created_at\":\"2021-08-20T16:49:18+00:00\",\"updated_at\":\"2021-08-20T16:56:43+00:00\",\"job_id\":1655470,\"workflow_id\":45238,\"results\":{\"judgments\":[{\"id\":4606645972,\"created_at\":\"2021-08-20T16:56:32+00:00\",\"started_at\":\"2021-08-20T16:54:47+00:00\",\"acknowledged_at\":null,\"external_type\":\"cf_internal\",\"golden\":false,\"missed\":null,\"rejected\":null,\"tainted\":false,\"country\":\"US\",\"region\":\"Missouri\",\"city\":\"Clayton\",\"unit_id\":2209430552,\"job_id\":1655470,\"worker_id\":45189726,\"trust\":1,\"worker_trust\":1,\"unit_state\":\"finalized\",\"data\":{\"how_well_does_this_result_match_the_query\":\"acceptable\"},\"unit_data\":{\"query\":\"b\",\"title\":\"toy trucks\",\"image_url\":\"http://www.overstock.com/search?keywords=toy+trucks&taxonomy=sto5&ralt=sto1,sto3,sto35&TID=AR:TRUE&searchtype=Header\",\"data_line_id\":\"96364c2a-09cd-11ec-8289-1ab017faae5w\",\"workflow_id\":45238,\"step_id\":53269,\"data_upload_id\":16530,\"launch_order_id\":null,\"row_number\":1,\"row_launched_at\":1629477890873,\"_kafka_agg_units_enabled\":-1}}],\"how_well_does_this_result_match_the_query\":{\"agg\":\"acceptable\",\"confidence\":1}}}"

        # values for other scenarios
        # value_to_be_sent = "{\"value\":{\"id\":2205465611,\"data\":{\"column_1\":\"717\",\"column_2\":\"177\",\"marker\":\"36040cb4-1713-4bbd-88a8-a9d633120b40\",\"_kafka_agg_units_enabled\":1,\"what_is_greater\":\"col1\",\"what_is_greater:confidence\":1,\"all_judgments\":[{\"id\":4603972135,\"created_at\":\"2021-07-07T10:07:48+00:00\",\"started_at\":\"2021-07-07T10:07:35+00:00\",\"acknowledged_at\":null,\"external_type\":\"cf_internal\",\"golden\":false,\"missed\":null,\"rejected\":null,\"tainted\":false,\"country\":null,\"region\":null,\"city\":\"\",\"unit_id\":2205465577,\"job_id\":1635541,\"worker_id\":45158250,\"trust\":1,\"worker_trust\":1,\"unit_state\":\"finalized\",\"data\":{\"what_is_greater\":\"col1\"}}],\"worker_id\":45158250,\"data_line_id\":\"b06dd177-7737-4980-af6a-2c69c42b7d1e\",\"workflow_id\":39322,\"step_id\":49319,\"data_upload_id\":12422,\"launch_order_id\":null,\"row_number\":29,\"row_launched_at\":1625652341584},\"judgments_count\":1,\"state\":\"finalized\",\"agreement\":1,\"missed_count\":0,\"gold_pool\":null,\"created_at\":\"2021-07-07T10:08:17+00:00\",\"updated_at\":\"2021-07-07T10:14:48+00:00\",\"job_id\":1635543,\"workflow_id\":39322,\"results\":{\"judgments\":[{\"id\":4603972232,\"created_at\":\"2021-07-07T10:14:38+00:00\",\"started_at\":\"2021-07-07T10:14:26+00:00\",\"acknowledged_at\":null,\"external_type\":\"cf_internal\",\"golden\":false,\"missed\":null,\"rejected\":null,\"tainted\":false,\"country\":null,\"region\":null,\"city\":\"\",\"unit_id\":2205465611,\"job_id\":1635543,\"worker_id\":45158250,\"trust\":1,\"worker_trust\":1,\"unit_state\":\"finalized\",\"data\":{\"what_is_greater\":\"col1\"},\"unit_data\":{\"column_1\":\"717\",\"column_2\":\"177\",\"marker\":\"36040cb4-1713-4bbd-88a8-a9d633120b40\",\"_kafka_agg_units_enabled\":1,\"what_is_greater\":\"col1\",\"what_is_greater:confidence\":1,\"all_judgments\":[{\"id\":4603972135,\"created_at\":\"2021-07-07T10:07:48+00:00\",\"started_at\":\"2021-07-07T10:07:35+00:00\",\"acknowledged_at\":null,\"external_type\":\"cf_internal\",\"golden\":false,\"missed\":null,\"rejected\":null,\"tainted\":false,\"country\":null,\"region\":null,\"city\":\"\",\"unit_id\":2205465577,\"job_id\":1635541,\"worker_id\":45158250,\"trust\":1,\"worker_trust\":1,\"unit_state\":\"finalized\",\"data\":{\"what_is_greater\":\"col1\"}}],\"worker_id\":45158250,\"data_line_id\":\"b06dd177-7737-4980-af6a-2c69c42b7d1e\",\"workflow_id\":39322,\"step_id\":49319,\"data_upload_id\":12422,\"launch_order_id\":null,\"row_number\":29,\"row_launched_at\":1625652341584}}],\"what_is_greater\":{\"agg\":\"col1\",\"confidence\":1}}}}"
        # value_to_be_sent = "{\"job_id\":1643129,\"data\":{\"image_url\":\"34999\",\"data_line_id\":\"5107ae3f-fe27-4e19-af3d-ce8187221f55\",\"workflow_id\":40336,\"step_id\":49968,\"data_upload_id\":14079,\"launch_order_id\":null,\"row_number\":34999,\"row_launched_at\":1627389157769}}"
        # we send key with random one from this set
        keys_to_be_sent = {'testkey21', 'testkey22', 'testkey23', 'testkey24', 'testkey25', 'testkey26', 'testkey27', 'testkey28'}

        key_to_be_sent = random.choice(tuple(keys_to_be_sent))
        log.info({
            'value to be sent': value_to_be_sent,
            'key to be sent': key_to_be_sent
        })
        self.producer.produce(
          topic=Config.KAFKA_TEST_TOPICS,
          value=value_to_be_sent.encode('utf-8'),
          key=key_to_be_sent.encode('utf-8'),
          callback=self.callback_delivery_report)

        log.info({
            'finish sending time': str(datetime.now())
        })
        # Commented out for open throttle test
        # self.throttle(t0)

    @task()
    def produce_msg(self):
        self.client.locust_event(
            "Publish",  # Requst type
            "Message 1",  # Requst name
            self.produce
            )

    def on_stop(self):
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        log.info(f"producer before flushs")
        self.producer.flush()


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.002)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        """ Locust setup """
        log.info(f"Locust Setup: TBD")

    def teardown(self):
        """ Locust teardown """
        delay = random.randrange(1, 300)
        log.info(f"Locust Teardown after {delay} seconds")
        time.sleep(delay)
        messages = Config.produced_messages_list
        log.info(f"send_kafka_in_batch {len(messages)} messages")
        send_kafka_in_batch(messages)
