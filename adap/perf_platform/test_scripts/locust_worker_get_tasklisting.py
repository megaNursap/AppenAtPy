from locust import TaskSet, task, between, events
from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.custom_locust import (
    CustomLocust,
    on_master_start_hatching,
    on_worker_listener,
    )
from adap.settings import Config
import random

log = get_logger(__name__, stdout=False)

env = Config.ENV

# Start ZMQ data feeder on master
events.master_start_hatching += on_master_start_hatching
# Start ZMQ listener on workers for workload changes
if Config.WORKLOAD:
    events.locust_start_hatching += on_worker_listener

channels = [
    'bitcoinget','clickworker','clickworker_en','clixsense','content_runner',
    'csedit','crowdguru','crowdworks','digitalcampusconnect','earnably','eup_slw',
    'elite','fusioncash','fusioncashsafe','gifthunterclub','gifthulk','grabpoints',
    'hiving','humanintheloop','kaycaptions','keeprewarding','kinetic','listia',
    'memolink','neodev','pactera','points2shop','prizerebel','proximo','redial_bpo',
    'superrewards','prodege','sykes','taqadam_cf','timebucks','vivatic',
    'wannads','vcare',
]

class LocustUserBehavior(TaskSet):
    def on_start(self):
        self.service = HttpMethod()


    def get_task_listing(self):
        base_url = f'https://account.{env}.cf3.us'
        _id = random.randint(1,10**6)
        channel = random.choice(channels)
        tasks_page_url = f'{base_url}/channels/{channel}/tasks?uid={_id}'
        resp = self.service.get(
            tasks_page_url,
            headers={},
            ep_name='tasks_page_url'
        )

    @task()
    def work(self):
        self.client.locust_event(
            "Execute task",  # Requst type
            "GetUnit",  # Requst name
            self.get_task_listing
        )


class LocustUser(CustomLocust):
    wait_time = between(0.1, 1.0)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
