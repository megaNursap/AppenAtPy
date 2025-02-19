import sys
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import HttpLocust, TaskSet, task, seq_task
import os

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']

sys.path.append(os.getcwd())

email = ""
url = "/authorization?userIdValue=" + email + "&userIdType=userEmail&resourceName=workflow&resourceAction=GET&resourceId=15"


class raas_api(TaskSet):

    @task
    @seq_task(1)
    def authorization(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 204:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = raas_api
    host = "https://raas.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
