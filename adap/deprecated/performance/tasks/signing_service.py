from adap.deprecated.performance.utils.locust_support import setup_wait_time
from adap.api_automation.utils.data_util import *
from locust import HttpLocust, TaskSet, task, between
from adap.api_automation.services_config.builder import Builder

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']

api_key = ""


class SigningService(TaskSet):

    def on_start(self):
        # create a new job, add units and launch
        cml_sample = '''<cml:text label="sample label" validates="required maxLength:2 clean:['uppercase']" />
                         <strong>original link:</strong>
                             <p>
                                 <span>{{ image_url }}</span>
                             </p>

                         <strong>link encoded</strong>
                             <p>
                                 <span>{{ image_url | secure: 's3' }}</span>
                             </p>

                         <strong>proxy link with context:</strong>
                             <p>
                                 <span>
                                     <img src="{{%20image_url%20|%20secure:%20's3'%20}}"/>
                                 </span>
                             </p>
                         hello
                     '''

        payload = {
            'key': api_key,
            'job': {
                'title': "Job for Performance Testing",
                'instructions': "Test job Instructions",
                'cml': cml_sample,
                'project_number': "PN1101"
            }
        }
        unit_data = {'key': api_key,
                    'unit': {
                        'data': "https://s3.amazonaws.com/pichost/segmentor/us101/IMG_9045.JPG"
                    }
                    }

        self.new_job = Builder(api_key=api_key, payload=payload, env=ENV)
        self.new_job.create_job()
        res = self.new_job.add_new_row(data=unit_data)
        print(res.json_response)
        self.unit_id = str(res.json_response['id'])
        self.job_id = str(self.new_job.job_id)
        print("unit id:" + self.unit_id)

    @task
    def create_wf(self):

        url = "/jobs/" + self.job_id + "/units/" + self.unit_id + "?key=" + api_key
        self.client.get(url)

    # TODO https://appen.atlassian.net/browse/ADAP-3613
    def on_stop(self):
        resp = Builder(api_key, env=ENV, api_version='v2').delete_job(self.new_job.job_id)
        resp.assert_response_status(200)
        assert resp.json_response == {"action": "requested"}
        # resp.assert_job_message({'success': 'Job %s has been deleted.' % self.new_job.job_id})


class WebsiteUser(HttpLocust):
    task_set = SigningService
    host = "https://make."+ ENV + ".cf3.us"
    wait_time = between(5,10)

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)