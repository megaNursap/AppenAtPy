import time
from datetime import date

import allure
import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, get_data_file
from adap.api_automation.services_config.workflow import Workflow
from adap.perf_platform.utils.logging import get_logger
from adap.settings import Config

pytestmark = [pytest.mark.regression_wf, pytest.mark.adap_api_uat,  pytest.mark.adap_wf_api]

api_key = get_user_api_key('test_account')
team_id = get_user_team_id('test_account')

LOGGER = get_logger(__name__)
if not Config.LOG_HTTP:
    LOGGER.disabled = True


def get_wf_with_status_from_cash(status=None):
    if cash_wfs.get(status) is None:
        cash_wfs[status] = []
        return None
    elif len(cash_wfs[status]) == 0:
        return None
    return cash_wfs[status][0]


def update_wf_cash(status, wf_id):
    if cash_wfs.get(status) is None:
        _jobs = [wf_id]
        cash_wfs[status] = _jobs

    _jobs = cash_wfs[status]
    _jobs.append(wf_id)
    cash_wfs[status] = list(set(_jobs))

    # delete job with previous status
    for k in cash_wfs:
        if k != status:
            if wf_id in cash_wfs[k]:
                _jobs = cash_wfs[k]
                _jobs.remove(wf_id)
                cash_wfs[k] = _jobs

    return cash_wfs


cash_wfs = {}

payload1 = {
    "key": api_key,
    "job": {
        "title": "Determine If Youtube/Vimeo Videos Are About A Research Paper {SERVICE_SHORTNAME}  {timestamp}".format(
            SERVICE_SHORTNAME=pytest.env, timestamp=date.today()),
        "instructions": "<h1>Overview</h1><p>We are looking for YouTube or Vimeo Videos that discuss biomedical or computer science research papers. Ideally, these videos would show a professor or graduate student presenting their paper. You will be given a paper title and video and will determine if the video is specifically discussing that paper.&nbsp;</p><hr><h1>Steps</h1><ol><li>Read the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube or Vimeo video.</li><li>Select 'Yes' if the video is a<strong>&nbsp;presentation</strong> that describes the paper in detail.</li></ol><hr><h1>Rules &amp; Tips</h1><p>You are assessing YouTube or Vimeo videos to determine if the video is about a research paper.&nbsp;</p><p><strong>How to Decide:</strong></p><ul><li><strong>YES, the video is about the research paper&nbsp;</strong>if:<ul><li>The video discusses &nbsp;the paper in detail&nbsp;<ul><li>&nbsp;This means that there is a person presenting the concepts/methods/conclusion of the paper in an academic setting &nbsp;</li></ul></li><li>The video is <strong>professional and&nbsp;</strong><strong>academic&nbsp;</strong><ul><li>ex: scientific conference presentation</li></ul></li><li><strong>Over 1 minute</strong>&nbsp;</li><li><strong>The sounds works</strong></li><li><strong>A person is talking about the paper</strong></li></ul></li><li><strong>NO, the video is not about the research paper</strong> if:<ul><li>The video is not about that specific paper</li><li>The video is too general to be about one paper</li><li>From a non-academic source&nbsp;<ul><li><strong>no</strong>\n<strong>loud music</strong></li><li><strong>no advertisements</strong><ul><li>no videos that show the paper, but don't discuss what the paper is about&nbsp;</li><li>no to paid services ('helping with IEEE projects' or 'helping with final year projects')</li></ul></li><li><strong>no movie clips</strong></li><li><strong>no religious services</strong></li><li><strong>no personal opinions</strong></li></ul></li><li>Under or near 1 minute long</li><li><strong>The sound doesn't work</strong></li><li>The video is <strong>unprofessional</strong></li></ul></li></ul><p><strong>Tips:&nbsp;</strong></p><ol><li>The video title may be similar to the paper title.</li><li>Look for the paper author's name in the video description.</li></ol><hr><h1>Examples</h1><table style=\"width: 100%;\"><tbody><tr><td style=\"width: 33.8368%; text-align: center; vertical-align: middle; background-color: rgb(143, 158, 178);\"><br><span style=\"color: rgb(255, 255, 255);\"><strong>Paper Title</strong></span><br><br></td><td style=\"width: 33.2078%; text-align: center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: rgb(255, 255, 255);\">Video</span></strong><br></td><td style=\"width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, 255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td style=\"width: 33.8368%; text-align: center;\"><h2>Deep Residual Learning for Image Recognition</h2></td><td style=\"width: 33.2078%;\"><br><strong>Title:</strong><br>Deep Residual Learning for Image Recognition<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=C6tLw-rPQ2o<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709313387-Screen+Shot+2018-07-27+at+9.35.02+AM.png\" style=\"width: 268px; height: 211.575px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top;\"><br><strong>Yes:</strong><br><ul><li>Video is about the paper</li><li>Video title and paper title are the same</li><li>Video has audio</li><li>Video is over 1 minute</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; text-align: center; background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms in Search, Optimization, and Machine Learning</h2><br></td><td style=\"width: 33.2078%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>Title:</strong><br>Genetic Algorithms in Search, Optimization, and Machine Learning<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=Xt2dujBPnTw<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>No:</strong><br><ul><li>Video is under 1 minute long</li><li>Not a presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br></td></tr><tr><td style=\"width: 33.8368%;\"><h2 style=\"text-align: center;\">Refactoring improving the design of existing code</h2><br></td><td style=\"width: 33.2078%;\"><strong>Title:</strong><br>Refactoring Book(Martin Fowler) Review<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=jRRmkyNuKNo<br><br><strong>Screenshot:</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896118948-Screen+Shot+2019-03-06+at+10.15.10+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td><strong>No:</strong><br><ul><li>This is a book review, not a presentation of the material</li><li>unprofessional</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; vertical-align: middle;\"><h2 style=\"text-align: center;\">\"If you can't stand the heat, get out of the kitchen\"</h2></td><td style=\"width: 33.2078%; vertical-align: top;\"><br><strong>Title:</strong><br>Your Kid Doesn't Need an iPhone 5<br><br><strong>Link:</strong>&nbsp;<br>https://vimeo.com/87196383<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896339890-Screen+Shot+2019-03-06+at+10.18.46+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top;\"><br><strong>No:</strong><br><ul><li>Completely unrelated video</li><li>Not about the paper</li><li>No personal opinions</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; background-color: rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">When all else fails, read the instructions</h2></td><td style=\"width: 33.2078%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>Title:</strong><br>WHEN ALL ELSE FAILS READ THE INSTRUCTIONS Part 1<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=WyC16y34-6E<br><br><strong>Screenshot:&nbsp;</strong><br><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896529675-Screen+Shot+2019-03-06+at+10.22.00+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br><strong>No:</strong><br><ul><li>This video is not about the paper</li><li>The video is about an unrelated topic</li><li>This is not a scientific video</li></ul><br></td></tr></tbody></table>",
        "cml": "  \n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Read Title and Watch Video</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n          <td>\n            <b>Paper Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n        <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n            <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n          <td>\n            <b>Video Link:</b>\n          </td>\n          <td>\n            <a target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        </tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Answer Question</h2>\n    <hr />\n    <cml:radios label=\"Does the video discuss the paper?\" validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br />\n  </div>\n</div>",
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

payload2 = {
    "key": api_key,
    "job": {
        "title": "Match Youtube Demonstrations To Academic Research Papers {SERVICE_SHORTNAME}  {timestamp}".format(
            SERVICE_SHORTNAME=pytest.env, timestamp=date.today()),
        "instructions": "<h1>Overview</h1>\n<p>Help us determine if Computer Science YouTube Videos are demonstrations of Computer Science Papers.&nbsp;</p>\n<hr />\n<h1>Steps</h1>\n<ol><li>Read the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube video.</li><li>Select 'Yes' if the video is a <strong>demonstration</strong> of the paper.</li></ol>\n<hr />\n<h1>Rules &amp; Tips</h1>\n<p>You are assessing YouTube videos to determine if the video is about an academic research paper.&nbsp;</p>\n<p>We are especially looking for <strong>demonstrations of the paper</strong>.&nbsp;</p>\n<p>Such as:&nbsp;</p>\n<ol><li>A program from the paper running on a computer</li><li>Code from the paper</li></ol>\n<p><strong>How to Decide:&nbsp;</strong></p>\n<ul><li>Choose <strong>yes&nbsp;</strong>if:<ul><li>The video is about the paper <strong>AND</strong><ul><li>From an professional, <strong>academic source</strong>: ex(conferences, talks, and presentations)</li><li><strong>Over 1 minute</strong> long</li><li><strong>A demonstration of the research</strong></li><li><strong>SILENT VIDEOS ARE OK</strong></li></ul></li></ul></li><li>Choose <strong>no</strong> if:<ul><li>The video is not about the paper</li><li>From a non-academic source (ex <strong>no</strong>\n<strong>loud music</strong>, <strong>large graphics/advertisement</strong> [phone number, company name])</li><li>Under or near 1 minute long</li><li>The video is very unprofessional</li></ul></li></ul>\n<p><strong>Tips:&nbsp;</strong></p>\n<ol><li>The video name may be similar to the paper title. &nbsp;</li><li>The paper title may be in the video description.&nbsp;</li></ol>\n<hr />\n<h1>Examples</h1>\n<table style=\"width: 100%;\"><tbody><tr><td style=\"width: 33.3333%; text-align: center; vertical-align: middle; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, 255);\"><strong>Paper Title</strong></span></td><td style=\"width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: rgb(255, 255, 255);\">Video</span></strong></td><td style=\"width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, 255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td style=\"width: 33.3333%; text-align: center;\"><h2>Real-time 3D reconstruction at scale using voxel hashing</h2></td><td style=\"width: 33.3333%;\"><br /><strong>Title:</strong>Real-time 3D Reconstruction at Scale using Voxel Hashing<strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365384427-Screen+Shot+2018-08-15+at+1.36.11+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\"><span data-sheets-userformat=\"{&quot;2&quot;:8403841,&quot;3&quot;:[null,0],&quot;10&quot;:2,&quot;11&quot;:0,&quot;12&quot;:0,&quot;14&quot;:[null,2,0],&quot;15&quot;:&quot;Calibri, sans-serif&quot;,&quot;16&quot;:12,&quot;26&quot;:400}\" data-sheets-value=\"{&quot;1&quot;:2,&quot;2&quot;:&quot;Real-time visual-inertial mapping re-localization and planning onboard MAVs in unknown environments&quot;}\">Real-time visual-inertial mapping re-localization and planning onboard MAVs in unknown environments</span></h2><br /></td><td><strong>Title:&nbsp;</strong>Real-Time Visual-Inertial Mapping, Re-localization and Planning Onboard MAVs in Unknown Environments<strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535567908185-Screen+Shot+2018-08-29+at+11.38.11+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\">Playing hard exploration games by watching YouTube</h2><br /></td><td><strong>Title:&nbsp;</strong>Learnt agent - Private Eye<br /><strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535568194488-Screen+Shot+2018-08-29+at+11.41.23+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>paper title is found in the description</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; text-align: center; background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms in Search, Optimization, and Machine Learning</h2><br /></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>Title:</strong>Genetic Algorithms in Search, Optimization, and Machine Learning<strong>Screenshot</strong><strong>:&nbsp;</strong><img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic fr-dib\" /></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>No:</strong><ul><li>Video is under 1 minute long</li><li>Not a presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\">Object Removal by Exemplar-Based Inpainting</h2><br /></td><td><strong>Title:</strong>Object removal by Exemplar based Inpainting<strong>Screenshot:<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365582122-Screen+Shot+2018-08-15+at+1.39.31+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td><strong>No:</strong><ul><li>under 1 minute</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; vertical-align: middle;\"><h2 style=\"text-align: center;\">Recent Advances in Augmented Reality</h2></td><td style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>Title:&nbsp;</strong>Medical Imaging in AR - Laboratory of Pharmacometabolomics and Companion Diagnostics<strong>Screenshot</strong><strong>:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455413455-Screen+Shot+2018-08-16+at+2.34.00+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>No:</strong><ul><li>Video is not a demonstration of the paper</li><li>Video is not about the paper</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; background-color: rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">Playing hard exploration games by watching YouTube</h2></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>Title:</strong>Learnt agent - &nbsp;Pitfall!<strong>Screenshot:&nbsp;<img src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455637964-Screen+Shot+2018-08-16+at+2.40.25+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" /></strong></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);\"><br /><strong>Yes:</strong><ul><li>Over 1 minute</li><li>Demonstration of the paper</li></ul><br /></td></tr></tbody></table>\n",
        "cml": "  \n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Review the Title and list of Authors</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n          <td>\n            <b>Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n        <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n            <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n          <td>\n            <b>YouTube Video Link:</b>\n          </td>\n          <td>\n            <a target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        </tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Collect Information</h2>\n    <hr />\n    <cml:radios label=\"Is the video about the paper?\" validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br />\n  </div>\n</div>",
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

wf_payload = {
    "name": "Cust01-01 - 2xJobs 22xRows  {SERVICE_SHORTNAME} {timestamp}".format(SERVICE_SHORTNAME=pytest.env,
                                                                                 timestamp=date.today()),
    "description": "2 Job demo workflow, example of using filter_rule to route data between related jobs."
}

filter_payload = {
    "filter_rule": {
        "comparison_field": "video_found_yn",
        "comparison_operation": "==",
        "comparison_value": "Yes",
        "rule_connector": "and"}
}


@allure.parent_suite('/v2/workflows/launch:post')
@pytest.mark.workflow
@pytest.mark.workflow_deploy
@pytest.mark.skip_hipaa
def test_launch_wf_route_rows_to_first_job(tmpdir):
    # create jobs
    job_1 = Builder(api_key, payload=payload1, api_version='v2')
    res = job_1.create_job()

    job_2 = Builder(api_key, payload=payload2, api_version='v2')
    res = job_2.create_job()

    _jobs = [job_1.job_id, job_2.job_id]

    # create WF
    _wf = Workflow(api_key)
    res = _wf.create_wf(payload=wf_payload)

    #  create steps
    _steps = _wf.create_job_step(_jobs, _wf.wf_id)

    step_id = _steps[0]['step_id']
    destination_step_id = _steps[1]['step_id']

    # create route
    route_id = _wf.create_route(step_id, destination_step_id, _wf.wf_id).json_response['id']

    # create filter
    res = _wf.create_filter_rule(step_id, route_id, filter_payload, _wf.wf_id)

    # data upload
    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    res = _wf.upload_data(sample_file, wf_id=_wf.wf_id)
    data_upload_id = res.json_response['id']
    # storage_key = res.json_response['storage_key']

    # ---------- CHECKS FOR LAUNCHED WF ----------- #
    status = None
    max_try = 60
    current_try = 0
    while status != 'completed' and status != 'failed' and current_try < max_try:
        res = _wf.get_data_upload_info(data_upload_id, sample_file, _wf.wf_id)
        status = res.json_response['state']
        print(status)
        time.sleep(1)
        current_try += 1

    res = _wf.launch(22)
    res.assert_response_status(202)
    assert res.json_response['id'] == _wf.wf_id
    assert res.json_response['name'] == wf_payload['name']

    # ---------- CHECKS FOR LAUNCHED FIRST JOB INCLUDING ROUTING OF ROWS ----------- #

    status = None
    max_try = 60
    current_try = 0
    while status != 'running' and status != 'failed' and current_try < max_try:
        res = _wf.get_info(_wf.wf_id)
        status = res.json_response['status']
        time.sleep(1)
        current_try += 1

    assert status == 'running'
    assert res.json_response['ordered_rows'] == 22

    update_wf_cash("running", _wf.wf_id)
    LOGGER.info("workflow has been launched")

    job = Builder(api_key=api_key, job_id=_jobs[0])

    max_try = 15
    current_try = 1
    status_job_1 = None

    while status_job_1 != 'running' and current_try < max_try:
        try:
            time.sleep(30)
            LOGGER.info("current try: %s" % current_try)
            resp_first_job_info = job.get_json_job_status()
            status_job_1 = resp_first_job_info.json_response['state']
            LOGGER.info("status of job: %s" % status_job_1)
            if status_job_1 == 'running':
                resp = job.get_job_status()

                # Auto launch is enabled for jobs once a WF is launched
                assert resp_first_job_info.json_response['auto_order'] is True
                assert status_job_1 == 'running', "Units are not routing to the first job"
                if resp.json_response['ordered_units'] == 22:
                    break
                else:
                    status_job_1 = None
            current_try += 1
            LOGGER.info("tries: %s" % current_try)
        except ValueError:
            LOGGER.info("Units haven't routed to the first job in under 5 minutes. Exiting test...")

    if status_job_1 != 'running':
        _wf.pause()
        pytest.fail("job status is {state}. job failed to launch! setting wf to paused and exiting test".format(
            state=status_job_1))

    resp = job.get_job_status()
    assert resp.json_response['ordered_units'] == 22, "Units haven't routed to the first job in under 5 minutes."




@allure.parent_suite('/v2/workflows/{id}:delete')
@pytest.mark.workflow
@pytest.mark.skip_hipaa
def test_delete_running_wf():
    _wf = Workflow(api_key)
    reuse_wf = get_wf_with_status_from_cash('running')

    if not reuse_wf:
        _wf.wf_id = reuse_wf
    else:
        pass
        #  create and launch WF

    res = _wf.delete_wf(wf_id=reuse_wf)
    res.assert_response_status(403)
    assert res.json_response['errors'] == "Workflows cannot be deleted once they have been launched"


@allure.parent_suite('/v2/workflows/pause:post')
@pytest.mark.workflow
@pytest.mark.skip_hipaa
def test_pause_wf_api():
    _wf = Workflow(api_key)
    reuse_wf = get_wf_with_status_from_cash('running')

    if reuse_wf is not None:
        _wf.wf_id = reuse_wf
    else:
        pass
        #  create and launch WF

    res = _wf.pause(wf_id=reuse_wf)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'paused'
    update_wf_cash("paused", _wf.wf_id)


@allure.parent_suite('/v2/workflows/resume:post')
@pytest.mark.workflow
@pytest.mark.skip_hipaa
def test_resume_wf_api():
    _wf = Workflow(api_key)
    reuse_wf = get_wf_with_status_from_cash('paused')

    if reuse_wf is not None:
        _wf.wf_id = reuse_wf
    else:
        pass
        #  create and launch WF

    res = _wf.resume(wf_id=reuse_wf)
    res.assert_response_status(202)
    assert res.json_response['status'] == 'running'
    update_wf_cash("paused", _wf.wf_id)


@allure.parent_suite('/v2/workflows/{id}:delete')
@pytest.mark.workflow
@pytest.mark.skip_hipaa
def test_delete_paused_wf():
    _wf = Workflow(api_key)
    reuse_wf = get_wf_with_status_from_cash('paused')

    if reuse_wf is not None:
        _wf.wf_id = reuse_wf
    else:
        pass
        #  create and launch WF

    res = _wf.delete_wf(wf_id=reuse_wf)
    res.assert_response_status(403)
    assert res.json_response['errors'] == "Workflows cannot be deleted once they have been launched"



