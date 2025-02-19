# import faulthandler; faulthandler.enable()

from locust import TaskSet, task, between, events
from appen_connect.api_automation.services_config.core import Core
from adap.api_automation.utils.data_util import get_user
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    request_feed
    )
from adap.settings import Config
from uuid import uuid4
# this is needed for data_util
import pytest
pytest.appen = 'true'

env = Config.ENV
log = get_logger(__name__, stdout=False)

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener

password = get_user('default', env=env).get('password')


class LocustUserBehavior(TaskSet):

    def on_start(self):
        self.core = Core(env=env)
        # self.uid = f"locust_uid_{uuid4().__str__()[-10:]}"

    def get_worker_email(self):
        """ Request a new worker email from locust master """
        email = request_feed('worker_email')
        return email

    def _sso_sign_in(self):
        worker_email = self.get_worker_email()
        log.info({
            'message': '_sso_sign_in',
            'worker_email': worker_email
            })
        try:
            resp = self.core.sign_in_sso(worker_email, password)
            if resp.status_code != 200:
                log.error({
                    'message': 'Error sign_in_sso response',
                    'resp.status_code': resp.status_code,
                    'resp.text': resp.text,
                    'resp.url': resp.url,
                    'worker_email': worker_email
                    })
            elif not resp.url.startswith(f"{self.core.url}/vendors"):
                log.error({
                    'message': 'Invalid sign_in_sso redirect',
                    'resp.url': resp.url,
                    'resp.text': resp.text,
                    'worker_email': worker_email
                    })
        except AssertionError as e:
            log.error({
                'message': 'Error in Core.sign_in_sso',
                'error': e.__repr__(),
                'worker_email': worker_email
                })

    def _sign_out(self):
        resp = self.core.sign_out()
        if resp.status_code != 200:
            log.error({
                'message': 'Error sign_out response',
                'resp.status_code': resp.status_code,
                'resp.text': resp.text,
                })

    def _authentication(self):
        self._sso_sign_in()
        self._sign_out()

    @task()
    def user_authentication(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "sso_sign_in",  # Requst name
            self._authentication,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
