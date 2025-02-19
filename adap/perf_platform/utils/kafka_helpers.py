from adap.settings import Config
from adap.perf_platform.utils.logging import get_logger
import confluent_kafka

log = get_logger(__name__)


class Consumer:
    """ Context class for confluent_kafka.Consumer """

    def __init__(self, config: dict, **kwargs):
        self.config = config
        self.topics = kwargs.get('topics') or Config.KAFKA_CONSUMER_TOPICS
        self._consumer = confluent_kafka.Consumer(self.config)

    def __enter__(self):
        log.info(f'subscribing to topics {self.topics}')
        self._consumer.subscribe(self.topics)
        return self._consumer

    def __exit__(self, *args, **kwargs):
        log.info('closing _consumer')
        self._consumer.close()
        return not(any([args, kwargs]))
