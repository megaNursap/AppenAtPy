from locust import HttpLocust, TaskSet, task, seq_task
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.deprecated.performance.utils.locust_support import setup_wait_time
import urllib3
import sys

urllib3.disable_warnings()

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
sys.path.append(os.getcwd())

api_key = ""

header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }


class jobs_api(TaskSet):

    def on_start(self):

        # create a new Job with cml
        cml_sample = '''<cml:text label="Please enter the correct ZIP in 2-letter format." validates="required maxLength:2 clean:['uppercase']" />'''

        payload = {
            'key': api_key,
            'job': {
                'title': "Job for Performance Testing",
                'instructions': "Test job Instructions",
                'cml': cml_sample

            }
        }
        self.new_job = Builder(api_key=api_key, payload=payload, env=ENV)
        self.new_job.create_job()
        self.job_id = self.new_job.job_id

    @task
    @seq_task(1)
    def channels(self):
        url = "v1/jobs/" + str(self.job_id) + "/channels"
        with self.client.get(url, headers=header, catch_response=True) as response:
            if "cf_internal" not in response.text:
                response.failure("Incorrect response")
                print(response.text)
            else:
                response.success()

    @task
    @seq_task(2)
    def validate(self):
        url = "v1/jobs/" + str(self.job_id) + "/validate?job_id=" + str(self.job_id)
        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 204:
                response.failure("Incorrect response")
                print(response.text)
            else:
                response.success()

    # TODO https://appen.atlassian.net/browse/ADAP-3613
    def on_stop(self):
        resp = Builder(api_key,env=ENV, api_version='v2').delete_job(self.new_job.job_id)
        resp.assert_response_status(200)
        assert resp.json_response == {"action": "requested"}
    #     resp.assert_job_message({'success': 'Job %s has been deleted.' % self.new_job.job_id})


class WebsiteUser(HttpLocust):
    task_set = jobs_api
    host = "https://jobs-api.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
