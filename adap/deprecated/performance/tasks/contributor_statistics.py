from locust import HttpLocust, TaskSet, seq_task, task
import os
from adap.deprecated.performance.utils.locust_support import setup_wait_time

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']


class contributor_statistics(TaskSet):

    @task
    @seq_task(1)
    def get_contributor_stats(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Accept": "application/json"
        }
        url = "contributors/stats"

        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = contributor_statistics
    host = "https://contributor-analytics.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
