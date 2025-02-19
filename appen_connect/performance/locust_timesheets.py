# import faulthandler; faulthandler.enable()
import traceback, sys
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
import random
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
project_id = 733


class LocustUserBehavior(TaskSet):

    def on_start(self):
        # executed once per client
        self.core = Core(env=env)
        self.worker_email = self.get_worker_email()
        self.core.sign_in(self.worker_email, password)

    def get_worker_email(self):
        """ Request a new worker email from locust master """
        email = request_feed('worker_email')
        log.debug({
            'worker_email': email
            })
        return email

    def _get_timesheets(self):
        acan_timesheets = self.core.get_timesheets(project_id=project_id)
        if 'acan_timesheets' not in acan_timesheets.url:
            log.error({
                'message': 'Invalid get_timesheets response',
                'resp.url': acan_timesheets.url,
                'resp.text': acan_timesheets.text,
                'worker_email': self.worker_email
                })

    def _update_timesheets(self):
        _id = random.choice([1, 3, 13, 17, 20])
        update_timesheets = self.core.update_timesheets(_id=_id, project_id=project_id)
        if update_timesheets.status_code != 200:
            log.error({
                'message': 'Error update_timesheets response',
                'resp.status_code': update_timesheets.status_code,
                'resp.text': update_timesheets.text,
                'worker_email': self.worker_email
                })
        if not update_timesheets.json_response.get('tasks'):
            log.error({
                'message': 'Invalid update_timesheets response',
                'resp.json_response': update_timesheets.json_response,
                'worker_email': self.worker_email
                })

    def _stop_timesheets(self):
        try:
            stop_timesheets = self.core.full_stop_timesheets(project_id=project_id)
            if stop_timesheets.status_code != 200:
                log.error({
                    'message': 'Error full_stop_timesheets response',
                    'resp.status_code': stop_timesheets.status_code,
                    'resp.text': stop_timesheets.text,

                    })
            if stop_timesheets.json_response.get('name') != 'Finished your Day':
                log.error({
                    'message': 'Invalid full_stop_timesheets response',
                    'resp.json_response': stop_timesheets.json_response,
                    'worker_email': self.worker_email
                    })
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            log.error({
                'message': 'full_stop_timesheets failed',
                })


    @task(10)
    def get_timesheets(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "get_timesheets",  # Requst name
            self._get_timesheets,
            )

    @task(10)
    def update_timesheets(self):
        self.client.locust_event(
            "Execute task",
            "update_timesheets",
            self._update_timesheets,
            )

    @task(1)
    def stop_timesheets(self):
        # ensure timesheets get before finalize
        self.get_timesheets()
        self.update_timesheets()
        self.client.locust_event(
            "Execute task",
            "stop_timesheets",
            self._stop_timesheets,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
