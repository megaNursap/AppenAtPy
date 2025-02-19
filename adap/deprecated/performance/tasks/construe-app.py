import sys
import urllib3
from locust import HttpLocust, TaskSet, seq_task, task
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.deprecated.performance.utils.locust_support import setup_wait_time

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
print(os.environ)
sys.path.append(os.getcwd())
urllib3.disable_warnings()

header = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

api_key = ""
sample_job = ""


class construe(TaskSet):

    def on_start(self):

        # create a new Job with cml
        self.new_job = Builder(api_key=api_key, env=ENV)
        self.new_job.copy_job(job_id=sample_job)
        self.job_id = self.new_job.job_id

    @task
    @seq_task(1)
    def render(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        url = "channels/cf_internal/jobs/" + str(self.job_id) + "/editor_preview?token=" + api_key
        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
            else:
                response.success()

    # TODO https://appen.atlassian.net/browse/ADAP-3613
    def on_stop(self):
        resp = Builder(api_key, env=ENV, api_version='v2').delete_job(self.new_job.job_id)
        resp.assert_response_status(200)
        assert resp.json_response == {"action": "requested"}
    #     resp.assert_job_message({'success': 'Job %s has been deleted.' % self.new_job.job_id})


class WebsiteUser(HttpLocust):
    task_set = construe
    host = "https://view." + ENV + ".cf3.io"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
