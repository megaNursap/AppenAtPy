"""
One-off test for the ipqs lambda function
"""

from adap.settings import Config
from adap.perf_platform.utils.logging import get_logger
from adap.api_automation.utils.http_util import HttpMethod, ApiHeaders
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    )
from locust import TaskSet, task, between, events
from faker import Faker

log = get_logger(__name__, stdout=False)
# Start processes on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


auth_token = ''  # !!! add authorization token
headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {auth_token}'
}


class LocustUserBehavior(TaskSet):
    def on_start(self):
        self.service = HttpMethod()
        self.faker = Faker()
        self.ip_addr = self.faker.ipv4()
        log.info({
            'message': 'on_start',
            'ip_addr': self.ip_addr
            })

    def call_ipqs(self):
        url = 'https://ipcheck-qa.appen.io/qa/ipqs?ipaddr={ip}'
        if Config.IPQS_RANDOM_IP:
            ip = self.faker.ipv4()
        else:
            ip = self.ip_addr
        resp = self.service.get(
            url.format(ip=ip),
            headers=headers,
            ep_name='ipqs')
        if resp.status_code != 200:
            log.error({
                'message': f'{resp.status_code} response',
                'text': resp.text
                })

    @task()
    def caller(self):
        task = self.call_ipqs
        self.client.locust_event(
            "Request",  # Request type
            task.__name__,  # Request name
            task,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.002)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()

    def setup(self):
        """ Locust setup """
        pass
