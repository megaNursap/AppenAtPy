from locust import HttpLocust, task, seq_task, TaskSequence
import os
import calendar
import time
from adap.deprecated.performance.utils.locust_support import setup_wait_time


ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']


class taskListing(TaskSequence):

    def on_start(self):
        self.uidNumber = "1234567"

    @task
    @seq_task(1)
    def tasklistingpage(self):
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "channels/memolink/tasks"

        uid = calendar.timegm(time.gmtime())
        print(uid)

        with self.client.get(url, data={"uid": uid}, headers=header, catch_response=True) as response:
            if "Figure Eight" not in response.text:
                response.failure("Incorrect response")
                print(response.text)
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = taskListing
    host = "https://tasks." + ENV + ".cf3.work"

    def __init__(self):
       super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)