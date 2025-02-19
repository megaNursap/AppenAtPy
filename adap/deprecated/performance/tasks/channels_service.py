import sys
from random import randint
from locust import HttpLocust, TaskSet, task, seq_task
import os

from adap.api_automation.utils.data_util import read_data_from_file
from adap.deprecated.performance.utils.locust_support import setup_wait_time

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
sys.path.append(os.getcwd())

profile_id = None
filepath = "/" + ENV + "/channels-service.csv"
sample_file = os.path.abspath(
    os.path.dirname(__file__) + "/../../data/locust") + filepath
data = read_data_from_file(sample_file)
profile_id = data.values.flatten()
num = randint(0, len(profile_id) - 1)
url = "v1/profiles/" + str(profile_id[num]) + "/channel_workers"


class channels_service(TaskSet):

    @task
    @seq_task(1)
    def channels(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
                print(response.text)
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = channels_service
    host = "https://contributor-profiles.internal."+ ENV +".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)