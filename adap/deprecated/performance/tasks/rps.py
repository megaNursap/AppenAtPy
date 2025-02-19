import os
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import task, HttpLocust

from adap.deprecated.performance.utils.tasksets import TaskSetRPS

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']

class UserBehavior(TaskSetRPS):
    @task
    def my_task(self):
        self.rps_sleep(3)
        with self.client.get('/', catch_response=True) as response:
            try:
                res = response.json()
            except:
                res = []
            print(response)


class MyHttpLocust(HttpLocust):
    task_set = UserBehavior
    host = "https://api.integration.cf3.us/v1/jobs.json?key=8g1_Leoyf2dYMpW7nPCV&page=1"

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)