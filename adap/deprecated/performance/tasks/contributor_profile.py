import csv
import sys

from adap.api_automation.utils.data_util import get_data_file
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import HttpLocust, TaskSet, seq_task, task
import os

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
print(os.environ)
sys.path.append(os.getcwd())


class contributorProfile(TaskSet):

    def on_start(self):
        self.akon_id = "Not_exist"
        self.api_key = "Not_exist"
        if len(datasetup) > 0:
            self.akon_id, self.api_key = datasetup.pop()

    @task
    @seq_task(1)
    def search_profile_by_akonid(self):
        token = "Token " + self.api_key
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Authorization": token
        }
        url = "v1/profiles?search_type=akon_id&search_key=" + self.akon_id
        print(url)
        with self.client.get(url, headers=header, catch_response=True) as response:
            if "akon_id" not in response.text:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = contributorProfile
    host = "https://contributor-profiles.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    def setup(self):
        global datasetup
        sample_file = get_data_file("data/locust/AkonID-ContributorProfileService.csv")
        with open(sample_file, 'rt') as f:
            csv_reader = csv.reader(f)
            datasetup = list(csv_reader)

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)