from adap.settings import Config
from .logging import get_logger
import importlib.util
import gevent
import csv
import queue
import zmq
import os


log = get_logger(__name__, stdout=False)


##################
# Code related to reading csv files
#
class SourceDataReader:
    """
    Handles reading of source data (csv or py file) and converting it to desired dict form.
    In case of .py file, it should define `get` function
    which returns the data in format similar to:
    [{col_name: value1}, {col_name: value2} ... ]
    (might have multiple colunms in a dictionary)

    """

    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        if self.file_path.endswith('.csv'):
            with open(self.file_path, "r") as file:
                reader = csv.DictReader(file)

                data = []
                for element in reader:
                    data.append(element)

        elif self.file_path.endswith('.py'):
            module_name = os.path.basename(self.file_path).split('.')[0]
            spec = importlib.util.spec_from_file_location(module_name, self.file_path)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            data = foo.get()

        else:
            raise(Exception('Cannot handle file with this extensio: {self.file_path}'))
        return data


##################
# Code related to receiving messages
#
class ZMQRequester:
    def __init__(self, address=f"tcp://127.0.0.1:{Config.FEEDER_BIND_PORT}"):
        """
        :param address: the addres to connect to; defaults to "tcp://127.0.0.1:5555"
        """
        log.debug(f"ZMQRequester connecting to {address}")
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(address)
        log.debug("zmq consumer initialized")

    def await_data(self):
        # Inform, that you want some data
        log.debug("requesting from data feed")
        self.socket.send_json({"msg": "available"})

        # wait for the data to arrive and return the message
        return self.socket.recv_json()


##################
# Code related to sending messages
#
class ZMQFeeder:
    def __init__(self, data, address="tcp://127.0.0.1:5555"):
        """
        :param data: list of dict objects
        :param address: indicates interface and port to bind to (see: http://api.zeromq.org/2-1:zmq-tcp#toc6);
                        defaults to "tcp://127.0.0.1:5555"
        """
        self.data_queue = queue.Queue()
        [self.data_queue.put(i) for i in data]

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(address)
        log.debug("zmq feeder initialized")

    def run(self):
        log.debug("Start seeding...")
        while True:
            try:
                j = self.socket.recv_json(flags=zmq.NOBLOCK)
                if j["msg"] == "available":
                    try:
                        work = self.data_queue.get(block=False)
                        log.debug(f"Sending: {work}")
                        self.socket.send_json(work)
                        self.data_queue.task_done()
                    except queue.Empty:
                        log.error("Queue empty. We need to reply something...")
                        self.socket.send_json({})
            except zmq.Again:
                log.debug("No message received yet")
                gevent.sleep(3)
