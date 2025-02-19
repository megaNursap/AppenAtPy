
from locust import TaskSet, task, between
from confluent_kafka import Producer
from adap.settings import Config
from utils.custom_locust import CustomLocust
from utils.logging import get_logger
from utils.results_handler import send_kafka_in
import random
import json
import warnings
import uuid
import gevent
import time

warnings.filterwarnings("ignore")

log = get_logger(__name__, stdout=False)

model_id = Config.MLAPI_MODEL_ID

config = {'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVER,
          'group.id': Config.KAFKA_GROUP_ID,
          'session.timeout.ms': 6000,
          'auto.offset.reset': 'earliest',
          'enable.auto.commit': True,
          'sasl.mechanism': 'PLAIN',
          'security.protocol': 'SASL_SSL',
          'sasl.username': Config.KAFKA_USERNAME,
          'sasl.password': Config.KAFKA_PASSWORD
          }


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.producer = Producer(config)

    def create_message(self):
        _id = random.choice(range(1, 10))
        image_url = f"https://annotation-sandbox.s3.amazonaws.com/explicit/{_id}.jpeg"
        data = {
            'image_url': image_url,
            'cache_buster': random.random()}
        msg = json.dumps({
            "data_line_id": uuid.uuid4().__str__(),
            "workflow_id": 1,
            "step_id": 1,
            "data_processor_type": "MLAPI::Model",
            "data_processor_id": model_id,
            "team_id": "0ae05f1d-01d2-4d43-b50f-062af9d22b27",
            "data_in": data
          })
        log.debug(f"msg: {msg}")
        return msg

    def callback_delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """

        data_line_id = json.loads(msg.value().decode('utf-8')).get('data_line_id')
        if err is not None:
            log.error({
              'message': 'Message delivery failed',
              'data_line_id': data_line_id,
              'error': err
            })
        else:
            log.info({
              'message': 'Message delivered',
              'data_line_id': data_line_id,
              'topic': msg.topic(),
              'partition': msg.partition()
            })

    def save_to_results(self, msg):
        data_line_id = json.loads(msg).get('data_line_id')
        send_kafka_in(data_line_id)

    def produce(self):
        t0 = time.time()
        msg = self.create_message()

        # Trigger any available delivery report callbacks from previous produce() calls
        self.producer.poll(1.0)

        self.save_to_results(msg)
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        self.producer.produce(
            Config.KAFKA_TEST_TOPICS,
            msg.encode('utf-8'),
            callback=self.callback_delivery_report)

        # esure that each task takes at least 1 second
        t1 = time.time()
        td = t1 - t0
        if 1 - td > 0.1:
            gevent.sleep(1 - td)

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
        self.producer.flush()


class LocustUser(CustomLocust):
    wait_time = between(0.1, 0.2)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        """ Locust setup """
        log.info(f"Locust Setup: TBD")

    def teardown(self):
        """ Locust teardown """
        log.info(f"Locust Teardown: TBD")
