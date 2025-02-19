import json
import os
import time
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import HttpLocust, TaskSet, task

# ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']


ENV = "integration"
api_key = ""
akon_id = ""
team_id = ""

# api_key = DataTricks(ENV).users['test_ui_account']['api_key']
# akon_id = DataTricks(ENV).users['test_ui_account']['akon_id']
# team_id = DataTricks(ENV).users['test_ui_account']['team_id']

job1_data = {
    "title": "Determine If Youtube/Vimeo Videos Are About A Research Paper ",
    "instructions": "<h1>Overview</h1><p>We are looking for YouTube or Vimeo Videos that discuss biomedical or computer science research papers. Ideally, these videos would show a professor or graduate student presenting their paper. You will be given a paper title and video and will determine if the video is specifically discussing that paper.&nbsp;</p><hr><h1>Steps</h1><ol><li>Read the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube or Vimeo video.</li><li>Select 'Yes' if the video is a<strong>&nbsp;presentation</strong> that describes the paper in detail.</li></ol><hr><h1>Rules &amp; Tips</h1><p>You are assessing YouTube or Vimeo videos to determine if the video is about a research paper.&nbsp;</p><p><strong>How to Decide:</strong></p><ul><li><strong>YES, the video is about the research paper&nbsp;</strong>if:<ul><li>The video discusses &nbsp;the paper in detail&nbsp;<ul><li>&nbsp;This means that there is a person presenting the concepts/methods/conclusion of the paper in an academic setting &nbsp;</li></ul></li><li>The video is <strong>professional and&nbsp;</strong><strong>academic&nbsp;</strong><ul><li>ex: scientific conference presentation</li></ul></li><li><strong>Over 1 minute</strong>&nbsp;</li><li><strong>The sounds works</strong></li><li><strong>A person is talking about the paper</strong></li></ul></li><li><strong>NO, the video is not about the research paper</strong> if:<ul><li>The video is not about that specific paper</li><li>The video is too general to be about one paper</li><li>From a non-academic source&nbsp;<ul><li><strong>no</strong>\n<strong>loud music</strong></li><li><strong>no advertisements</strong><ul><li>no videos that show the paper, but don't discuss what the paper is about&nbsp;</li><li>no to paid services ('helping with IEEE projects' or 'helping with final year projects')</li></ul></li><li><strong>no movie clips</strong></li><li><strong>no religious services</strong></li><li><strong>no personal opinions</strong></li></ul></li><li>Under or near 1 minute long</li><li><strong>The sound doesn't work</strong></li><li>The video is <strong>unprofessional</strong></li></ul></li></ul><p><strong>Tips:&nbsp;</strong></p><ol><li>The video title may be similar to the paper title.</li><li>Look for the paper author's name in the video description.</li></ol><hr><h1>Examples</h1><table style=\"width: 100%;\"><tbody><tr><td style=\"width: 33.8368%; text-align: center; vertical-align: middle; background-color: rgb(143, 158, 178);\"><br><span style=\"color: rgb(255, 255, 255);\"><strong>Paper Title</strong></span><br><br></td><td style=\"width: 33.2078%; text-align: center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: rgb(255, 255, 255);\">Video</span></strong><br></td><td style=\"width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, 255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td style=\"width: 33.8368%; text-align: center;\"><h2>Deep Residual Learning for Image Recognition</h2></td><td style=\"width: 33.2078%;\"><br><strong>Title:</strong><br>Deep Residual Learning for Image Recognition<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=C6tLw-rPQ2o<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709313387-Screen+Shot+2018-07-27+at+9.35.02+AM.png\" style=\"width: 268px; height: 211.575px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top;\"><br><strong>Yes:</strong><br><ul><li>Video is about the paper</li><li>Video title and paper title are the same</li><li>Video has audio</li><li>Video is over 1 minute</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; text-align: center; background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms in Search, Optimization, and Machine Learning</h2><br></td><td style=\"width: 33.2078%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>Title:</strong><br>Genetic Algorithms in Search, Optimization, and Machine Learning<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=Xt2dujBPnTw<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>No:</strong><br><ul><li>Video is under 1 minute long</li><li>Not a presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br></td></tr><tr><td style=\"width: 33.8368%;\"><h2 style=\"text-align: center;\">Refactoring improving the design of existing code</h2><br></td><td style=\"width: 33.2078%;\"><strong>Title:</strong><br>Refactoring Book(Martin Fowler) Review<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=jRRmkyNuKNo<br><br><strong>Screenshot:</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896118948-Screen+Shot+2019-03-06+at+10.15.10+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td><strong>No:</strong><br><ul><li>This is a book review, not a presentation of the material</li><li>unprofessional</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; vertical-align: middle;\"><h2 style=\"text-align: center;\">\"If you can't stand the heat, get out of the kitchen\"</h2></td><td style=\"width: 33.2078%; vertical-align: top;\"><br><strong>Title:</strong><br>Your Kid Doesn't Need an iPhone 5<br><br><strong>Link:</strong>&nbsp;<br>https://vimeo.com/87196383<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896339890-Screen+Shot+2019-03-06+at+10.18.46+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top;\"><br><strong>No:</strong><br><ul><li>Completely unrelated video</li><li>Not about the paper</li><li>No personal opinions</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; background-color: rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">When all else fails, read the instructions</h2></td><td style=\"width: 33.2078%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>Title:</strong><br>WHEN ALL ELSE FAILS READ THE INSTRUCTIONS Part 1<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=WyC16y34-6E<br><br><strong>Screenshot:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896529675-Screen+Shot+2019-03-06+at+10.22.00+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>No:</strong><br><ul><li>This video is not about the paper</li><li>The video is about an unrelated topic</li><li>This is not a scientific video</li></ul><br></td></tr></tbody></table>",
    "cml": "  \n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Read Title and Watch Video</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n          <td>\n            <b>Paper Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n        <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n            <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n          <td>\n            <b>Video Link:</b>\n          </td>\n          <td>\n            <a target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        </tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Answer Question</h2>\n    <hr />\n    <cml:radios label=\"Does the video discuss the paper?\" validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br />\n  </div>\n</div>",
    "judgments_per_unit": 1,
    "max_judgments_per_worker": 100,
    "project_number": "PN000113"
}

job2_data = {
    "title": "Match Youtube Demonstrations To Academic Research Papers ",
    "instructions": "<h1>Overview</h1>\n<p>Help us determine if Computer Science YouTube Videos are demonstrations of Computer Science Papers.&nbsp;</p>\n<hr />\n<h1>Steps</h1>\n<ol><li>Read the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube video.</li><li>Select 'Yes' if the video is a <strong>demonstration</strong> of the paper.</li></ol>\n<hr />\n<h1>Rules &amp; Tips</h1>\n<p>You are assessing YouTube videos to determine if the video is about an academic research paper.&nbsp;</p>\n<p>We are especially looking for <strong>demonstrations of the paper</strong>.&nbsp;</p>\n<p>Such as:&nbsp;</p>\n<ol><li>A program from the paper running on a computer</li><li>Code from the paper</li></ol>\n<p><strong>How to Decide:&nbsp;</strong></p>\n<ul><li>Choose <strong>yes&nbsp;</strong>if:<ul><li>The video is about the paper <strong>AND</strong><ul><li>From an professional, <strong>academic source</strong>: ex(conferences, talks, and presentations)</li><li><strong>Over 1 minute</strong> long</li><li><strong>A demonstration of the research</strong></li><li><strong>SILENT VIDEOS ARE OK</strong></li></ul></li></ul></li><li>Choose <strong>no</strong> if:<ul><li>The video is not about the paper</li><li>From a non-academic source (ex <strong>no</strong>\n<strong>loud music</strong>, <strong>large graphics/advertisement</strong> [phone number, company name])</li><li>Under or near 1 minute long</li><li>The video is very unprofessional</li></ul></li></ul>\n<p><strong>Tips:&nbsp;</strong></p>\n<ol><li>The video name may be similar to the paper title. &nbsp;</li><li>The paper title may be in the video description.&nbsp;</li></ol>\n<hr />\n<h1>Examples</h1>\n<table style=\"width: 100%;\"><tbody><tr><td style=\"width: 33.3333%; text-align: center; vertical-align: middle; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, 255);\"><strong>Paper Title</strong></span></td><td style=\"width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: rgb(255, 255, 255);\">Video</span></strong></td><td style=\"width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, 255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td style=\"width: 33.3333%; text-align: center;\"><h2>Real-time 3D reconstruction at scale using voxel hashing</h2></td><td style=\"width: 33.3333%;\"><br /><strong>Title:</strong>Real-time 3D Reconstruction at Scale using Voxel Hashing<strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365384427-Screen+Shot+2018-08-15+at+1.36.11+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\"><span data-sheets-userformat=\"{&quot;2&quot;:8403841,&quot;3&quot;:[null,0],&quot;10&quot;:2,&quot;11&quot;:0,&quot;12&quot;:0,&quot;14&quot;:[null,2,0],&quot;15&quot;:&quot;Calibri, sans-serif&quot;,&quot;16&quot;:12,&quot;26&quot;:400}\" data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;Real-time visual-inertial mapping re-localization and planning onboard MAVs in unknown environments&quot;}\">Real-time visual-inertial mapping re-localization and planning onboard MAVs in unknown environments</span></h2><br /></td><td><strong>Title:&nbsp;</strong>Real-Time Visual-Inertial Mapping, Re-localization and Planning Onboard MAVs in Unknown Environments<strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535567908185-Screen+Shot+2018-08-29+at+11.38.11+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\">Playing hard exploration games by watching YouTube</h2><br /></td><td><strong>Title:&nbsp;</strong>Learnt agent - Private Eye<br /><strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535568194488-Screen+Shot+2018-08-29+at+11.41.23+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>paper title is found in the description</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; text-align: center; background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms in Search, Optimization, and Machine Learning</h2><br /></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>Title:</strong>Genetic Algorithms in Search, Optimization, and Machine Learning<strong>Screenshot</strong><strong>:&nbsp;</strong><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic fr-dib\" /></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>No:</strong><ul><li>Video is under 1 minute long</li><li>Not a presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\">Object Removal by Exemplar-Based Inpainting</h2><br /></td><td><strong>Title:</strong>Object removal by Exemplar based Inpainting<strong>Screenshot:<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365582122-Screen+Shot+2018-08-15+at+1.39.31+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td><strong>No:</strong><ul><li>under 1 minute</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; vertical-align: middle;\"><h2 style=\"text-align: center;\">Recent Advances in Augmented Reality</h2></td><td style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>Title:&nbsp;</strong>Medical Imaging in AR - Laboratory of Pharmacometabolomics and Companion Diagnostics<strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455413455-Screen+Shot+2018-08-16+at+2.34.00+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>No:</strong><ul><li>Video is not a demonstration of the paper</li><li>Video is not about the paper</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; background-color: rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">Playing hard exploration games by watching YouTube</h2></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>Title:</strong>Learnt agent - &nbsp;Pitfall!<strong>Screenshot:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455637964-Screen+Shot+2018-08-16+at+2.40.25+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>Yes:</strong><ul><li>Over 1 minute</li><li>Demonstration of the paper</li></ul><br /></td></tr></tbody></table>\n",
    "cml": "  \n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Review the Title and list of Authors</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n          <td>\n            <b>Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n        <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n            <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n          <td>\n            <b>YouTube Video Link:</b>\n          </td>\n          <td>\n            <a target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        </tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Collect Information</h2>\n    <hr />\n    <cml:radios label=\"Is the video about the paper?\" validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br />\n  </div>\n</div>",
    "judgments_per_unit": 1,
    "max_judgments_per_worker": 100,
    "project_number": "PN000113"
}

JOB_URL = "https://api.{}.cf3.us/v1".format(ENV)
WF_URL = 'https://workflows-service.internal.{}.cf3.us/v1/workflows'.format(ENV)


class CreateWorkflow(TaskSet):

    def on_start(self):
        print("======== start ===== %s" %self.locust.__str__())
        self.new_wf_list = []


    @task
    def create_wf(self):
        self.JOBS = []
        self.create_job(job1_data)
        self.create_job(job2_data)

        self.create_new_wf()

        self.determine_steps()

        self.create_route()

        self.filter_rules()


        file_name = 'customer_01_sample_22.csv'
        storage_key = 'shared-test-data-sets/customer_01_sample_22.csv'
        self.upload_data(file_name, storage_key)
        time.sleep(20)

        self.get_data_uplod()

        self.launch_wf()


    def launch_wf(self):
        url = "/%s/launch" % self.WF_ID
        querystring = {"user_id": akon_id, "rows": "22"}
        payload = ""
        headers = {
            'cache-control': "no-cache",
        }
        with self.client.post(WF_URL + url, name="/[]/launch", data=payload, headers=headers, params=querystring,
                              catch_response=True) as response:
            if response.status_code == 202:
                response.success()

            if response.json()['status'] == 'launching':
                response.success()

    def get_data_uplod(self):
        status = None
        max_try = 20
        current_try = 0
        while status != 'completed' and status != 'failed' and current_try < max_try:
            url = "/%s/data_uploads/%s" % (self.WF_ID, self.WF_DATA_ID)

            querystring = {"team_id": team_id}

            payload = ""
            headers = {
                'Content-Type': "application/json",
                'X-Request-TeamID': team_id,
                'cache-control': "no-cache",
            }

            # response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
            with self.client.get(WF_URL + url, name="/[]/data_uploads/[]", data=payload, headers=headers, params=querystring,
                                 catch_response=True) as response:
                status = response.json()['state']
                print(status)
                time.sleep(1)
                current_try += 1

    def upload_data(self, file_name, storage_key):

        print("data upload =================================")
        url = "/%s/data_uploads" % self.WF_ID
        payload = {
            'original_filename': file_name,
            'content_type': 'text/csv',
            'storage_key': storage_key,
            'user_id': akon_id,
            'team_id': team_id
        }
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",

        }
        with self.client.post(WF_URL + url, name="/[]/data_uploads", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()

            self.WF_DATA_ID = response.json()['id']


    def filter_rules(self):
        rules_url = "https://workflows-service.internal.%s.cf3.us/v1/step_routes/%s/filter_rules" % (ENV, self.ROUTE_ID)
        payload = {"filter_rule": {
            "comparison_field": "video_found_yn",
            "comparison_operation": "==",
            "comparison_value": "Yes",
            "rule_connector": "and"}
        }
        headers = {
            'Content-Type': "application/json",
            'X-Request-TeamID': team_id,
            'cache-control': "no-cache",
        }
        with self.client.post(rules_url, name="/v1/step_routes/[]/filter_rules", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()

    def create_route(self):
        url = "/%s/steps/%s/routes" % (self.WF_ID, self.steps_info[0]['id'])
        payload = {'destination_step_id': '%s' % self.steps_info[1]['id']}
        headers = {
            'Content-Type': 'application/json',
            'X-Request-TeamID': team_id,
        }
        with self.client.post(WF_URL + url, name="/[]/steps/[]/routes", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            self.ROUTE_ID = response.json()['id']


    def determine_steps(self):
        url = "/%s/steps" % self.WF_ID
        self.steps_info = []
        for job in (self.JOBS[0], self.JOBS[1]):
            payload = {'job_id': '%s' % job}
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }
            with self.client.post(WF_URL + url, name="/[]/steps",  data=json.dumps(payload), headers=headers,
                                  catch_response=True) as response:
                if response.status_code == 201:
                    response.success()

                self.steps_info.append({'id': response.json()['id'],
                                   'data_processor_id': response.json()['data_processor_id']})


    def create_new_wf(self):
        print("Create WF for jobs - %s and %s" % (self.JOBS[0], self.JOBS[1]))
        # WF_URL = 'https://workflows-service.internal.%s.cf3.us/v1/workflows' % ENV
        payload = {
            'name': "Teas WF for jobs %s and %s" % (self.JOBS[0], self.JOBS[1]),
            'description': '2 Job demo workflow, example of using filter_rule to route data between related jobs.',
            'user_id': akon_id,
            'team_id': team_id
        }
        data = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json'
        }
        with self.client.post(WF_URL, data=data, headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            print(response.json())
            self.WF_ID = response.json()['id']
            self.new_wf_list.append(self.WF_ID )
            print("WF %s was created" % self.WF_ID)


    def create_job(self, job_data):
        payload = {
            'key': api_key,
            'job': job_data
        }
        url = '/jobs.json'
        response = self.client.post(JOB_URL + url, json=payload)
        self.JOBS.append(response.json()['id'])
        print("Job with id - %s was created" % self.JOBS[-1])

    def on_stop(self):
        print("======== stop ===== %s" % self.locust.__str__())
        print(self.new_wf_list)
        # for wf in self.new_wf_list:
        #     url = 'https://workflows-service.internal.%s.cf3.us/v1/workflows/%s' % (ENV, wf)
        #     with self.client.delete(url, catch_response=True) as response:
        #         print(response.status_code)
        #         print(response.text)



class WebsiteUser(HttpLocust):

    task_set = CreateWorkflow
    host = "https://tags.internal.integration.cf3.us"
    global user_num
    # sock = None

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
