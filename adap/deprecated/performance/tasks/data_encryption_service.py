import sys
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import HttpLocust, TaskSet, seq_task, task
from adap.api_automation.utils.data_util import *
import os

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
sys.path.append(os.getcwd())


class data_encryption(TaskSet):

    def on_start(self):
        self.document_id = "Not_exist"
        self.team_id = "Not_exist"
        if len(datasetup) > 0:
            self.document_id, self.team_id = datasetup.pop()


    @task
    @seq_task(1)
    def documents(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "v1/documents/"+ self.document_id + "?team_id=" + self.team_id
        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = data_encryption
    host = "https://data-encryption.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    def setup(self):
        global datasetup
        sample_file = get_data_file("DocumentID-data_encryption.csv")

        with open(sample_file, 'rt') as f:
            csv_reader = csv.reader(f)
            datasetup = list(csv_reader)

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
