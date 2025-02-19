import sys
import urllib3
from bs4 import BeautifulSoup
from locust import HttpLocust, TaskSet, seq_task
from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.http_util import ApiResponse
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from adap.api_automation.services_config.builder import Builder

sys.path.append(os.getcwd())

urllib3.disable_warnings()

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
sys.path.append(os.getcwd())

api_key = ""
JOB_URL = "https://api.{}.cf3.us/v1".format(ENV)


class Akon(TaskSet):

    authenticity_token=''

    def on_start(self):

        self.user_id = "Not_exist"
        self.password = "Not_exist"
        if len(datasetup) > 0:
            self.user_id, self.password = datasetup.pop()

    # create a new job, add units and launch
        cml_sample = '''<cml:text label="sample label" validates="required maxLength:2 clean:['uppercase']" />'''

        payload = {
            'key': api_key,
            'job': {
                'title': "Job for Performance Testing",
                'instructions': "Test job Instructions",
                'cml': cml_sample,
                'project_number': "PN1101"
            }
        }
        self.new_job = Builder(api_key=api_key, env=ENV)
        self.new_job.create_job()
        self.job_id = self.new_job.job_id
        self.add_rows_and_launch()
        self.secret = self.auto_launch()

    @seq_task(1)
    def launch_worker_ui(self):
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Secret": self.secret
        }
        url = "channels/cf_internal/jobs/"+ str(self.job_id) + "/work"
        with self.client.get(url, headers=header, catch_response=True) as response:
            api_response = ApiResponse(response)
            print("launch worker ui: %s" % api_response.status_code)
            print("launch worker ui: %s" % api_response.json_response)
            soup = BeautifulSoup(api_response.content, 'html.parser')
            value = soup.find('input', {'name': 'authenticity_token'}).get('value')
            self.authenticity_token = value

    @seq_task(2)
    def login_as_contributor_new_session(self):
        post_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"
        }
        data = {
            'session[email]': self.user_id,
            'session[password]': self.password,
            'commit': 'Sign In',
            'authenticity_token': self.authenticity_token
        }
        url = "sessions"
        with self.client.post(url, headers=post_headers, data=data, catch_response=True) as response:
            api_response = ApiResponse(response)
            print("login status code = %s" % api_response.status_code)
            print("login json: %s" % api_response.json_response)

    @seq_task(3)
    def contributor_chanels(self):
        url = "channels/cf_internal/jobs/" + str(self.job_id)+ "/work"
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"
        }
        payload = {"secret": self.secret
                   }
        with self.client.get(url, data=payload, headers=header, catch_response=True) as response:
            api_response = ApiResponse(response)
            print("contributor_chanels = %s" % api_response.status_code)
            print("contributor_chanels: %s" % api_response.json_response)

    def add_rows_and_launch(self):
        i = 1
        payload2 = {'key': api_key,
                    'unit': {
                        'data': "https://s3.amazonaws.com/pichost/segmentor/us101/IMG_9045.JPG"
                    }
                    }
        while i <= 5:
            self.new_job.add_new_row(data=payload2)
            i += 1
        self.new_job.launch_job()

    def auto_launch(self):
        params = {
            "job[auto_order]": True
        }
        url = JOB_URL + "/jobs/" + str(self.job_id) + ".json?key=" + api_key
        with self.client.put(url, data=params, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Got wrong response")
                exit()
            else:
                return response.json()['secret']

    # TODO https://appen.atlassian.net/browse/ADAP-3613
    def on_stop(self):
        resp = Builder(api_key, env=ENV, api_version='v2').delete_job(self.new_job.job_id)
        resp.assert_response_status(200)
        assert resp.json_response == {"action":"requested"}
        # resp.assert_job_message({'success': 'Job %s has been deleted.' % self.new_job.job_id})


class WebsiteUser(HttpLocust):
    task_set = Akon
    sock = None
    host = "https:tasks.{}.cf3.us".format(ENV)

    def __init__(self):
        super(WebsiteUser, self).__init__()

    def setup(self):
        global datasetup
        sample_file = get_data_file("data/locust/contributors.csv")

        with open(sample_file, 'rt') as f:
            csv_reader = csv.reader(f)
            datasetup = list(csv_reader)

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)



