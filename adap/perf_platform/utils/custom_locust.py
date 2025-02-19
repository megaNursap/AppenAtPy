import traceback
import gevent
import random
import json
import time
import sys
from adap.settings import Config
from locust import Locust, events, runners
from locust.exception import StopLocust
from locust.runners import (
    MasterLocustRunner,
    SlaveLocustRunner,
    LocalLocustRunner
    )
from locust.rpc import zmqrpc
from locust.rpc.protocol import Message
from .logging import get_logger
from .results_handler import send_locust_user_counts
from .data_feed import (
    SourceDataReader,
    ZMQRequester,
    ZMQFeeder
    )

# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)


class Client(object):
    """
    Client with Locust functionality
    """
    @staticmethod
    def locust_event(request_type, name, func, *args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
        except Exception as e:
            if e.args:
                try:
                    log.error(e.args[0]['message'])
                except Exception:
                    log.error(e.__repr__())
            else:
                log.error(e.__repr__())
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(
                request_type=request_type,
                name=name,
                response_time=total_time,
                exception=e,
                response_length=0
            )
            traceback.print_exc(file=sys.stdout)
            raise StopLocust()
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(
                request_type=request_type,
                name=name,
                response_time=total_time,
                response_length=0
            )
            return result

    @staticmethod
    def locust_event_enhanced(request_type, name, func, *args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
        except Exception as e:
            if e.args:
                try:
                    log.error(e.args[0]['message'])
                except Exception:
                    log.error(e.__repr__())
            else:
                log.error(e.__repr__())
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(
                request_type=request_type,
                name=name,
                response_time=total_time,
                exception=e,
                response_length=0
            )
            return None
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(
                request_type=request_type,
                name=name,
                response_time=total_time,
                response_length=0
            )
            return result


class CustomLocust(Locust):

    def __init__(self, *args, **kwargs):
        super(CustomLocust, self).__init__(*args, **kwargs)
        self.client = Client()

    ##################
    # Code for detecting run context
    #
    @staticmethod
    def is_test_ran_on_master():
        return isinstance(runners.locust_runner, MasterLocustRunner)

    @staticmethod
    def is_test_ran_on_slave():
        return isinstance(runners.locust_runner, SlaveLocustRunner)

    @staticmethod
    def is_test_ran_on_standalone():
        return isinstance(runners.locust_runner, LocalLocustRunner)

    @staticmethod
    def is_master():
        return '--master' in sys.argv

    @staticmethod
    def is_slave():
        return '--slave' in sys.argv

    @staticmethod
    def is_standalone():
        return not ('--slave' in sys.argv or '--master' in sys.argv)


##################
# Code to be run exactly once, at node startup
#
if CustomLocust.is_master() or CustomLocust.is_standalone():
    if Config.DATA_SOURCE_PATH:
        log.debug("Reading input data...")
        sdr = SourceDataReader(Config.DATA_SOURCE_PATH)
        INPUT_DATA = sdr.read()
        random.shuffle(INPUT_DATA)
        log.debug(f"{len(INPUT_DATA)} records read")


def init_feeder():
    sender = ZMQFeeder(INPUT_DATA, f"tcp://0.0.0.0:{Config.FEEDER_BIND_PORT}")
    sender.run()


def monitor_users_count():
    t0 = time.time()
    while True:
        _t = int(time.time()-t0)
        _count = runners.locust_runner.user_count
        log.debug(f"{_t} locust user_count = {_count}")
        send_locust_user_counts(_count)
        gevent.sleep(1)


def event_monitor_users_count():
    gevent.spawn(monitor_users_count)


def get_sec(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def dynamic_workload():
    """
    Changing number of workers during test execution in a distributed
    deployment.
    This function runs on a locust master.
    Workload definition is read from WORKLOAD environment variable.
    Expected worlkload formating:
    workload is a list of steps, each step is a dict
    '[{"start_at": "h:m:s", "target_count": int, "finish_at": "h:m:s"},{...}]'
    "start_at" - time interval after initial launch,
                 when this step should be started
    "target_count" - desired count of locust workers at the end of this step
    "finish_at" - time interval after initial launch,
                  when this step should be finished

    Increasing number of workers is handled using locust's built-in function:
    runners.locust_runner.start_hatching
    Decreasing is handled manually. Master sends a message to workers using zmqrpc.
    Message has a custom 'reduce' type. Message is instance of locust.rpc.protocol.Message.
    """

    log.debug('DYNAMIC_WORKLOAD')

    start_time = time.time()

    workload = json.loads(Config.WORKLOAD)

    server = zmqrpc.Server('*', Config.MASTER_PORT)

    for step in workload:
        _start_at = get_sec(step['start_at'])
        _finish_at = get_sec(step['finish_at'])
        target_count = step['target_count']

        # wait for the moment to start changing number of workers
        t_target = start_time + _start_at
        t_sleep = t_target - time.time()
        gevent.sleep(t_sleep)

        current_count = runners.locust_runner.user_count
        abs_change = abs(target_count - current_count)
        change_rate = abs_change / (_finish_at - _start_at)
        if target_count > current_count:
            # add workers
            log.debug(f'start_hatching {target_count}')
            runners.locust_runner.start_hatching(
                target_count,
                change_rate
                )
        else:
            # remove workers
            log.debug(f'remove {abs_change} workers')
            lr = runners.locust_runner
            clients = (lr.clients.ready + lr.clients.running + lr.clients.hatching)
            n_clients = lr.slave_count
            abs_change_p_client = abs_change / n_clients
            change_rate_p_client = abs_change_p_client / (_finish_at - _start_at)
            workers_count = int(change_rate_p_client)
            if workers_count == 0:
                workers_count = 1
            num_rounds = abs_change / (workers_count * n_clients)
            wait = (_finish_at - _start_at) / num_rounds
            while abs_change > 0:
                for client in clients:
                    if abs_change <= 0:
                        break
                    elif abs_change < workers_count:
                        workers_count = abs_change
                    data = {"workers_count": workers_count}
                    log.debug(f'server.send_to_client {data}')
                    server.send_to_client(
                        runners.Message("reduce", data, client.id)
                        )
                    abs_change -= workers_count
                gevent.sleep(wait)


def client_listener():
    """
    Additional listener for workers handling new message type.
    """

    log.debug('Starting zmqrpc.Client')
    client = zmqrpc.Client(
        Config.MASTER_HOST,
        Config.MASTER_PORT,
        runners.locust_runner.client_id)
    while True:
        msg = client.recv()
        job = msg.data
        if msg.type == "reduce":
            _count = job['workers_count']
            runners.locust_runner.kill_locusts(_count)


def on_worker_listener():
    log.debug("on_worker_listener")
    gevent.spawn(client_listener)


##################
# Code to be run before the tests
#
def on_master_start_hatching():
    log.debug("on_master_start_hatching")

    # start sending the messages (in a separate greenlet, so it doesn't block)
    gevent.spawn(init_feeder)
    gevent.spawn(monitor_users_count)
    if Config.WORKLOAD:
        gevent.spawn(dynamic_workload)


def request_feed(key=''):
    zmq_consumer = ZMQRequester(Config.FEEDER_ADDR)
    resp = zmq_consumer.await_data()
    if key:
        data = resp.get(key)
        assert data, f'Value for {key} key not found in {resp}'
        return data
    else:
        return resp
