import sys
from locust import HttpLocust, TaskSet, task, seq_task
import os
from adap.deprecated.performance.utils.locust_support import setup_wait_time


ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']

sys.path.append(os.getcwd())


class imagine(TaskSet):

    @task
    @seq_task(1)
    def annotation(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = ""

        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = imagine
    host = "https://annotation." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)


