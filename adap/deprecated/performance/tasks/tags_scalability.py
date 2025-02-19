from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.deprecated.performance.utils.locust_support import setup_wait_time
import sys
from locust import HttpLocust, TaskSet, task
import urllib3

sys.path.append(os.getcwd())

urllib3.disable_warnings()

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']

api_key = ""
sample_file = get_data_file('/sample_data.json', env=ENV)


class Tags(TaskSet):

    def on_start(self):

        # create a new Job with JSON
        resp = Builder(api_key, env=ENV).create_job_with_json(sample_file)
        self.job_id = resp.json_response.get('id')

        # Adding tag association to Job
        self.post_tag_associations(self)

    @task
    def get_tag_associations(self):

        url = "/v1/tag_associations?resource_type=job&resource_id=" + str(self.job_id)
        with self.client.get(url,
                             name="/v1/tag_associations?resource_type=job&resource_id=[job_id]",
                             catch_response=True) as response:
            try:
                res = response.json()
            except:
                res = []

            if len(res) == 0:
                response.failure("Empty response")
            else:
                if 'tag_id' not in response.text:
                    response.failure("Got wrong response")

    def post_tag_associations(self):

        url = "/v1/tag_associations"
        payload = {
            "resource_type": "job",
            "resource_id": self.job_id,
            "tag_ids": [
                4
            ]
        }
        with self.client.post(url,
                              json=payload,
                              catch_response=True) as response:
            try:
                res = response.json()
            except:
                res = []

            if len(res) == 0:
                response.failure("Empty response")
            else:
                if 'tag_id' not in response.text:
                    print(response.text)
                    response.failure("Got wrong response")


class WebsiteUser(HttpLocust):
    task_set = Tags
    host = "https://tags.internal." + ENV + ".cf3.us"
    sock = None

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
