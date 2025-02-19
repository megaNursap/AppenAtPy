from appen_connect.api_automation.services_config.ac_sme import SME
from locust import TaskSet, task, between, events
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config

env = Config.ENV
log = get_logger(__name__, stdout=False)

events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.service = SME(env=env)

    def _healthcheck(self):
        resp = self.service.get_healthcheck()

    @task()
    def healthcheck(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "sme_find_projects",  # Requst name
            self._healthcheck,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
