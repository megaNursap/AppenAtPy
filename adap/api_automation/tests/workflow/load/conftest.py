"""`conftest.py` pytest fixtures loaded from a Postman env variable template.
auto-generate using a utility function.
"""
import pytest
import os
import json

POSTMAN_VARS = {}


### Utility functions


def load_postman_file():
    try:
        if POSTMAN_VARS:
            return
        with open(
            os.path.expanduser(
                os.environ.get("POSTMAN_FILE", "template.postman_environment.json")
            )
        ) as fin:
            data = json.load(fin)
            for data_dict in data["values"]:
                POSTMAN_VARS[data_dict["key"]] = data_dict["value"]
                # currently all entries in there are considered true and enabled, why not?

        # Overwrite with QA specific env params
        if os.environ.get("SERVICE_DOMAIN", "") == "qa":
            with open(
                os.path.expanduser(
                    os.environ.get("POSTMAN_FILE", "qa.cf3.us.postman_environment.json")
                )
            ) as fin:
                data = json.load(fin)
                for data_dict in data["values"]:
                    POSTMAN_VARS[data_dict["key"]] = data_dict["value"]
        # if Sandbox testing, overwrite with sandbox params
        if os.environ.get("SERVICE_DOMAIN", "") == "sandbox":
            with open(
                os.path.expanduser(
                    os.environ.get(
                        "POSTMAN_FILE", "sandbox.cf3.us.postman_environment.json"
                    )
                )
            ) as fin:
                data = json.load(fin)
                for data_dict in data["values"]:
                    POSTMAN_VARS[data_dict["key"]] = data_dict["value"]

        if os.environ.get("akon_id"):
            POSTMAN_VARS["MY_AKON_UUID"] = os.environ.get("akon_id")
        if os.environ.get("api_key"):
            POSTMAN_VARS["MY_API_KEY"] = os.environ.get("api_key")
        if os.environ.get("proj_num"):
            POSTMAN_VARS["MY_PROJECT_NUM"] = os.environ.get("proj_num")
        if os.environ.get("team_id"):
            POSTMAN_VARS["MY_TEAM_ID"] = os.environ.get("team_id")
    except Exception:
        print("problem loading postman config")


def generate_fixture_code():
    template = (
        """@pytest.fixture\ndef $_VARNAME ():\n\treturn POSTMAN_VARS['$_VARNAME']\n"""
    )
    for name in POSTMAN_VARS.keys():
        print(template.replace("$_VARNAME", name))


def push_fixture_val(key, val):
    POSTMAN_VARS[key] = val


####
load_postman_file()

# generate_fixture_code()

### Missing fixture variables, these were added manually, they will likely be refactored


@pytest.fixture
def WORKFLOWS_KAFKA_FLAG():
    return POSTMAN_VARS.get("WORKFLOWS_KAFKA_FLAG", True)


@pytest.fixture
def CUST01_WF01():
    return POSTMAN_VARS.get("CUST01_WF01", 12986)


@pytest.fixture
def CUST01_WF01_JOB1():
    return POSTMAN_VARS.get("CUST01_WF01_JOB1", 1423335)


@pytest.fixture
def CUST01_WF01_JOB2():
    return POSTMAN_VARS.get("CUST01_WF01_JOB2", 1423336)


@pytest.fixture
def CUST01_WF01_STEP_1():
    return POSTMAN_VARS.get("CUST01_WF01_STEP_1", 23796)


@pytest.fixture
def STEP_ROUTE_ID():
    return POSTMAN_VARS.get("STEP_ROUTE_ID", 11827)


@pytest.fixture
def CUST01_WF01_JOB1():
    return POSTMAN_VARS.get("CUST01_WF01_JOB1", 1423335)


@pytest.fixture
def CONTRIB_AUTH_TOKEN():
    return POSTMAN_VARS.get("CONTRIB_AUTH_TOKEN", "")


@pytest.fixture
def CONTRIB_AKON_ID():
    return POSTMAN_VARS.get("CONTRIB_AKON_ID", "")


@pytest.fixture
def CONTRIB_AUTH_TOKEN():
    return POSTMAN_VARS.get("CONTRIB_AUTH_TOKEN", "")


@pytest.fixture
def STARTED_AT_NEXT():
    return POSTMAN_VARS.get("STARTED_AT_NEXT", "")


@pytest.fixture
def TOKEN():
    return POSTMAN_VARS.get("TOKEN", "")


@pytest.fixture
def ASSIGNMENT_ID():
    return POSTMAN_VARS.get("ASSIGNMENT_ID", True)


@pytest.fixture
def CUST01_WF01_STEP_2():
    return POSTMAN_VARS.get("CUST01_WF01_STEP_2", True)


@pytest.fixture
def CUST01_WF01_DATA():
    return POSTMAN_VARS.get("CUST01_WF01_DATA", True)


@pytest.fixture
def CUST01_WF01_JOB1_SECRET():
    return POSTMAN_VARS.get("CUST01_WF01_JOB1_SECRET", True)


@pytest.fixture
def CONTRIB_ASSIGNMENT_ID():
    return POSTMAN_VARS.get("CONTRIB_ASSIGNMENT_ID", True)


@pytest.fixture
def STARTED_AT():
    return POSTMAN_VARS.get("STARTED_AT", True)


@pytest.fixture
def JOB_JSON():
    # this was copied manually from the Postman body section; auto-convert had some hiccups
    return {
        "job": {
            "title": "Determine If Youtube/Vimeo Videos Are About A Research Paper [{{SERVICE_SHORTNAME}}] {{$TIMESTAMP}}",
            "instructions": '<h1>Overview</h1><p>We are looking for YouTube or Vimeo Videos that discuss biomedical or computer science research papers. Ideally, these videos would show a professor or graduate student presenting their paper. You will be given a paper title and video and will determine if the video is specifically discussing that paper.&nbsp;</p><hr><h1>Steps</h1><ol><li>Read the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube or Vimeo video.</li><li>Select \'Yes\' if the video is a<strong>&nbsp;presentation</strong> that describes the paper in detail.</li></ol><hr><h1>Rules &amp; Tips</h1><p>You are assessing YouTube or Vimeo videos to determine if the video is about a research paper.&nbsp;</p><p><strong>How to Decide:</strong></p><ul><li><strong>YES, the video is about the research paper&nbsp;</strong>if:<ul><li>The video discusses &nbsp;the paper in detail&nbsp;<ul><li>&nbsp;This means that there is a person presenting the concepts/methods/conclusion of the paper in an academic setting &nbsp;</li></ul></li><li>The video is <strong>professional and&nbsp;</strong><strong>academic&nbsp;</strong><ul><li>ex: scientific conference presentation</li></ul></li><li><strong>Over 1 minute</strong>&nbsp;</li><li><strong>The sounds works</strong></li><li><strong>A person is talking about the paper</strong></li></ul></li><li><strong>NO, the video is not about the research paper</strong> if:<ul><li>The video is not about that specific paper</li><li>The video is too general to be about one paper</li><li>From a non-academic source&nbsp;<ul><li><strong>no</strong>\n<strong>loud music</strong></li><li><strong>no advertisements</strong><ul><li>no videos that show the paper, but don\'t discuss what the paper is about&nbsp;</li><li>no to paid services (\'helping with IEEE projects\' or \'helping with final year projects\')</li></ul></li><li><strong>no movie clips</strong></li><li><strong>no religious services</strong></li><li><strong>no personal opinions</strong></li></ul></li><li>Under or near 1 minute long</li><li><strong>The sound doesn\'t work</strong></li><li>The video is <strong>unprofessional</strong></li></ul></li></ul><p><strong>Tips:&nbsp;</strong></p><ol><li>The video title may be similar to the paper title.</li><li>Look for the paper author\'s name in the video description.</li></ol><hr><h1>Examples</h1><table style="width: 100%;"><tbody><tr><td style="width: 33.8368%; text-align: center; vertical-align: middle; background-color: rgb(143, 158, 178);"><br><span style="color: rgb(255, 255, 255);"><strong>Paper Title</strong></span><br><br></td><td style="width: 33.2078%; text-align: center; background-color: rgb(143, 158, 178);"><strong><span style="color: rgb(255, 255, 255);">Video</span></strong><br></td><td style="width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);"><span style="color: rgb(255, 255, 255);"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td style="width: 33.8368%; text-align: center;"><h2>Deep Residual Learning for Image Recognition</h2></td><td style="width: 33.2078%;"><br><strong>Title:</strong><br>Deep Residual Learning for Image Recognition<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=C6tLw-rPQ2o<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709313387-Screen+Shot+2018-07-27+at+9.35.02+AM.png" style="width: 268px; height: 211.575px;" class="fr-fic fr-dib"></td><td style="width: 33.3333%; vertical-align: top;"><br><strong>Yes:</strong><br><ul><li>Video is about the paper</li><li>Video title and paper title are the same</li><li>Video has audio</li><li>Video is over 1 minute</li></ul><br></td></tr><tr><td style="width: 33.8368%; text-align: center; background-color: rgb(245, 246, 249);"><h2>Genetic Algorithms in Search, Optimization, and Machine Learning</h2><br></td><td style="width: 33.2078%; vertical-align: top; background-color: rgb(245, 246, 249);"><br><strong>Title:</strong><br>Genetic Algorithms in Search, Optimization, and Machine Learning<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=Xt2dujBPnTw<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot+2018-07-27+at+9.36.30+AM.png" style="width: 265px; height: 303.621px;" class="fr-fic fr-dib"></td><td style="width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);"><br><strong>No:</strong><br><ul><li>Video is under 1 minute long</li><li>Not a presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br></td></tr><tr><td style="width: 33.8368%;"><h2 style="text-align: center;">Refactoring improving the design of existing code</h2><br></td><td style="width: 33.2078%;"><strong>Title:</strong><br>Refactoring Book(Martin Fowler) Review<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=jRRmkyNuKNo<br><br><strong>Screenshot:</strong><br><img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896118948-Screen+Shot+2019-03-06+at+10.15.10+AM.png" style="width: 300px;" class="fr-fic fr-dib"></td><td><strong>No:</strong><br><ul><li>This is a book review, not a presentation of the material</li><li>unprofessional</li></ul><br></td></tr><tr><td style="width: 33.8368%; vertical-align: middle;"><h2 style="text-align: center;">"If you can\'t stand the heat, get out of the kitchen"</h2></td><td style="width: 33.2078%; vertical-align: top;"><br><strong>Title:</strong><br>Your Kid Doesn\'t Need an iPhone 5<br><br><strong>Link:</strong>&nbsp;<br>https://vimeo.com/87196383<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896339890-Screen+Shot+2019-03-06+at+10.18.46+AM.png" style="width: 300px;" class="fr-fic fr-dib"></td><td style="width: 33.3333%; vertical-align: top;"><br><strong>No:</strong><br><ul><li>Completely unrelated video</li><li>Not about the paper</li><li>No personal opinions</li></ul><br></td></tr><tr><td style="width: 33.8368%; background-color: rgb(245, 246, 249);"><h2 style="text-align: center;">When all else fails, read the instructions</h2></td><td style="width: 33.2078%; vertical-align: top; background-color: rgb(245, 246, 249);"><br><strong>Title:</strong><br>WHEN ALL ELSE FAILS READ THE INSTRUCTIONS Part 1<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=WyC16y34-6E<br><br><strong>Screenshot:&nbsp;</strong><br><img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896529675-Screen+Shot+2019-03-06+at+10.22.00+AM.png" style="width: 300px;" class="fr-fic fr-dib"></td><td style="width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);"><br><strong>No:</strong><br><ul><li>This video is not about the paper</li><li>The video is about an unrelated topic</li><li>This is not a scientific video</li></ul><br></td></tr></tbody></table>',
            "cml": '  \n<div class="row-fluid">\n  <div class="span5">\n    <h2>Step 1: Read Title and Watch Video</h2>\n    <hr />\n    <div class="well">\n      <table class="table">\n        <tr>\n          <td>\n            <b>Paper Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n        <tr>\n        {% assign domain = {{title}} | split: \'@\' %}\n          <td>\n            <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n          <td>\n            <b>Video Link:</b>\n          </td>\n          <td>\n            <a target="_blank" href="{{url}}" class="btn">Click here for Video</a>\n          </td>\n        </tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class="span7">\n    <h2>Step 2: Answer Question</h2>\n    <hr />\n    <cml:radios label="Does the video discuss the paper?" validates="required" name="video_found_yn" gold="true"> \n      <cml:radio label="Yes"></cml:radio> \n      <cml:radio label="No"></cml:radio> \n    </cml:radios>\n    <br />\n  </div>\n</div>',
            "judgments_per_unit": 1,
            "copied_from": 1356404,
            "max_judgments_per_worker": 100,
            "project_number": "{{MY_PROJ_NUM}}",
        }
    }


@pytest.fixture
def JOB2_JSON():
    # this was copied manually from the Postman body section; auto-convert had some hiccups
    return {
        "job": {
            "title": "Match Youtube Demonstrations To Academic Research Papers [{{SERVICE_SHORTNAME}}] {{$timestamp}}",
            "instructions": '<h1>Overview</h1>\n<p>Help us determine if Computer Science YouTube Videos are demonstrations of Computer Science Papers.&nbsp;</p>\n<hr />\n<h1>Steps</h1>\n<ol><li>Read the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube video.</li><li>Select \'Yes\' if the video is a <strong>demonstration</strong> of the paper.</li></ol>\n<hr />\n<h1>Rules &amp; Tips</h1>\n<p>You are assessing YouTube videos to determine if the video is about an academic research paper.&nbsp;</p>\n<p>We are especially looking for <strong>demonstrations of the paper</strong>.&nbsp;</p>\n<p>Such as:&nbsp;</p>\n<ol><li>A program from the paper running on a computer</li><li>Code from the paper</li></ol>\n<p><strong>How to Decide:&nbsp;</strong></p>\n<ul><li>Choose <strong>yes&nbsp;</strong>if:<ul><li>The video is about the paper <strong>AND</strong><ul><li>From an professional, <strong>academic source</strong>: ex(conferences, talks, and presentations)</li><li><strong>Over 1 minute</strong> long</li><li><strong>A demonstration of the research</strong></li><li><strong>SILENT VIDEOS ARE OK</strong></li></ul></li></ul></li><li>Choose <strong>no</strong> if:<ul><li>The video is not about the paper</li><li>From a non-academic source (ex <strong>no</strong>\n<strong>loud music</strong>, <strong>large graphics/advertisement</strong> [phone number, company name])</li><li>Under or near 1 minute long</li><li>The video is very unprofessional</li></ul></li></ul>\n<p><strong>Tips:&nbsp;</strong></p>\n<ol><li>The video name may be similar to the paper title. &nbsp;</li><li>The paper title may be in the video description.&nbsp;</li></ol>\n<hr />\n<h1>Examples</h1>\n<table style="width: 100%;"><tbody><tr><td style="width: 33.3333%; text-align: center; vertical-align: middle; background-color: rgb(143, 158, 178);"><span style="color: rgb(255, 255, 255);"><strong>Paper Title</strong></span></td><td style="width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);"><strong><span style="color: rgb(255, 255, 255);">Video</span></strong></td><td style="width: 33.3333%; text-align: center; background-color: rgb(143, 158, 178);"><span style="color: rgb(255, 255, 255);"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td style="width: 33.3333%; text-align: center;"><h2>Real-time 3D reconstruction at scale using voxel hashing</h2></td><td style="width: 33.3333%;"><br /><strong>Title:</strong>Real-time 3D Reconstruction at Scale using Voxel Hashing<strong>Screenshot</strong><strong>:&nbsp;<img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365384427-Screen+Shot+2018-08-15+at+1.36.11+PM.png" style="width: 300px;" class="fr-fic fr-dib" /></strong></td><td style="width: 33.3333%; vertical-align: top;"><br /><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style="text-align: center;"><span data-sheets-userformat="{&quot;2&quot;:8403841,&quot;3&quot;:[null,0],&quot;10&quot;:2,&quot;11&quot;:0,&quot;12&quot;:0,&quot;14&quot;:[null,2,0],&quot;15&quot;:&quot;Calibri, sans-serif&quot;,&quot;16&quot;:12,&quot;26&quot;:400}" data-sheets-value="{&quot;1&quot;:2,&quot;2&quot;:&quot;Real-time visual-inertial mapping re-localization and planning onboard MAVs in unknown environments&quot;}">Real-time visual-inertial mapping re-localization and planning onboard MAVs in unknown environments</span></h2><br /></td><td><strong>Title:&nbsp;</strong>Real-Time Visual-Inertial Mapping, Re-localization and Planning Onboard MAVs in Unknown Environments<strong>Screenshot</strong><strong>:&nbsp;<img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535567908185-Screen+Shot+2018-08-29+at+11.38.11+AM.png" style="width: 300px;" class="fr-fic fr-dib" /></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style="text-align: center;">Playing hard exploration games by watching YouTube</h2><br /></td><td><strong>Title:&nbsp;</strong>Learnt agent - Private Eye<br /><strong>Screenshot</strong><strong>:&nbsp;<img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535568194488-Screen+Shot+2018-08-29+at+11.41.23+AM.png" style="width: 300px;" class="fr-fic fr-dib" /></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>paper title is found in the description</li><li>Video is over 1 minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td style="width: 33.3333%; text-align: center; background-color: rgb(245, 246, 249);"><h2>Genetic Algorithms in Search, Optimization, and Machine Learning</h2><br /></td><td style="width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);"><br /><strong>Title:</strong>Genetic Algorithms in Search, Optimization, and Machine Learning<strong>Screenshot</strong><strong>:&nbsp;</strong><img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot+2018-07-27+at+9.36.30+AM.png" style="width: 265px; height: 303.621px;" class="fr-fic fr-dib" /></td><td style="width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);"><br /><strong>No:</strong><ul><li>Video is under 1 minute long</li><li>Not a presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br /></td></tr><tr><td><h2 style="text-align: center;">Object Removal by Exemplar-Based Inpainting</h2><br /></td><td><strong>Title:</strong>Object removal by Exemplar based Inpainting<strong>Screenshot:<img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365582122-Screen+Shot+2018-08-15+at+1.39.31+PM.png" style="width: 300px;" class="fr-fic fr-dib" /></strong></td><td><strong>No:</strong><ul><li>under 1 minute</li></ul><br /></td></tr><tr><td style="width: 33.3333%; vertical-align: middle;"><h2 style="text-align: center;">Recent Advances in Augmented Reality</h2></td><td style="width: 33.3333%; vertical-align: top;"><br /><strong>Title:&nbsp;</strong>Medical Imaging in AR - Laboratory of Pharmacometabolomics and Companion Diagnostics<strong>Screenshot</strong><strong>:&nbsp;<img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455413455-Screen+Shot+2018-08-16+at+2.34.00+PM.png" style="width: 300px;" class="fr-fic fr-dib" /></strong></td><td style="width: 33.3333%; vertical-align: top;"><br /><strong>No:</strong><ul><li>Video is not a demonstration of the paper</li><li>Video is not about the paper</li></ul><br /></td></tr><tr><td style="width: 33.3333%; background-color: rgb(245, 246, 249);"><h2 style="text-align: center;">Playing hard exploration games by watching YouTube</h2></td><td style="width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);"><br /><strong>Title:</strong>Learnt agent - &nbsp;Pitfall!<strong>Screenshot:&nbsp;<img src="https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455637964-Screen+Shot+2018-08-16+at+2.40.25+PM.png" style="width: 300px;" class="fr-fic fr-dib" /></strong></td><td style="width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, 249);"><br /><strong>Yes:</strong><ul><li>Over 1 minute</li><li>Demonstration of the paper</li></ul><br /></td></tr></tbody></table>\n',
            "cml": '  \n<div class="row-fluid">\n  <div class="span5">\n    <h2>Step 1: Review the Title and list of Authors</h2>\n    <hr />\n    <div class="well">\n      <table class="table">\n        <tr>\n          <td>\n            <b>Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n        <tr>\n        {% assign domain = {{title}} | split: \'@\' %}\n          <td>\n            <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n          <td>\n            <b>YouTube Video Link:</b>\n          </td>\n          <td>\n            <a target="_blank" href="{{url}}" class="btn">Click here for Video</a>\n          </td>\n        </tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class="span7">\n    <h2>Step 2: Collect Information</h2>\n    <hr />\n    <cml:radios label="Is the video about the paper?" validates="required" name="video_found_yn" gold="true"> \n      <cml:radio label="Yes"></cml:radio> \n      <cml:radio label="No"></cml:radio> \n    </cml:radios>\n    <br />\n  </div>\n</div>',
            "judgments_per_unit": 1,
            "max_judgments_per_worker": 100,
            "copied_from": 1357617,
            "project_number": "{{MY_PROJ_NUM}}",
        }
    }


@pytest.fixture
def WORKFLOW_JSON():
    return {
        "name": "Cust01-01 - 2xJobs 22xRows [kafka={{WORKFLOWS_KAFKA_FLAG}}] {{SERVICE_SHORTNAME}} {{$timestamp}}",
        "description": "2 Job demo workflow, example of using filter_rule to route data between related jobs.",
        "user_id": "{{MY_AKON_UUID}}",
        "team_id": "{{MY_TEAM_ID}}",
        "kafka": "{{WORKFLOWS_KAFKA_FLAG}}",
    }


@pytest.fixture
def STEP_01_JSON():
    return {"job_id": "{{CUST01_WF01_JOB1}}"}


@pytest.fixture
def STEP_02_JSON():
    return {"job_id": "{{CUST01_WF01_JOB2}}"}


@pytest.fixture
def ROUTE_STEP_01_TO_02_JSON():
    return {"destination_step_id": "{{CUST01_WF01_STEP_2}}"}


@pytest.fixture
def FILTER_RULE_JSON():
    return {
        "filter_rule": {
            "comparison_field": "video_found_yn",
            "comparison_operation": "==",
            "comparison_value": "Yes",
            "rule_connector": "and",
        }
    }


@pytest.fixture
def DATA_UPLOAD_JSON():
    return {
        "original_filename": "customer_01_sample_643.csv",
        "content_type": "text/csv",
        "storage_key": "{{CUST01_WF01_DATA_STORAGE_KEY}}",
        "team_id": "{{MY_TEAM_ID}}",
        "user_id": "{{MY_AKON_UUID}}",
    }


@pytest.fixture
def AKON_API_REQUEST_JSON():
    return {"user": {"email_verified_at": "2018-07-02 15:43:24 -0700"}}


@pytest.fixture
def CONTRIB_SIGNUP_JSON():
    return {
        "user[password_confirmation]": "{{USER_SIGNUP_PASSWORD}}",
        "user[name]": "{{USER_SIGNUP_EMAIL}}",
        "terms": "on",
        "user[email]": "{{USER_SIGNUP_EMAIL}}",
        "utf8": "true",
        "user[password]": "{{USER_SIGNUP_PASSWORD}}",
        "commit": "Create My Free Account",
        "user[force_disposable_email_check]": "false",
        "authenticity_token": "{{CONTRIB_AUTH_TOKEN}}",
    }


@pytest.fixture
def CONTRIB_LOGIN_JSON():
    return {
        "session[email]": "{{USER_SIGNUP_EMAIL}}",
        "session[password]": "{{USER_SIGNUP_PASSWORD}}",
        "authenticity_token": "{{CONTRIB_AUTH_TOKEN}}",
    }


#### Auto generated code, from above: do not edit manually
#######################################################################################################################
@pytest.fixture
def PROTOCOL():
    return POSTMAN_VARS["PROTOCOL"]


@pytest.fixture
def SERVICE_DOMAIN():
    return POSTMAN_VARS["SERVICE_DOMAIN"]


@pytest.fixture
def SERVICE_SHORTNAME():
    return POSTMAN_VARS["SERVICE_SHORTNAME"]


@pytest.fixture
def INTERNAL_SERVICE_DOMAIN():
    return POSTMAN_VARS["INTERNAL_SERVICE_DOMAIN"]


@pytest.fixture
def BUILDER_INTERNAL_API_TOKEN():
    return POSTMAN_VARS["BUILDER_INTERNAL_API_TOKEN"]


@pytest.fixture
def MY_API_KEY():
    return POSTMAN_VARS["MY_API_KEY"]


@pytest.fixture
def MY_AKON_UUID():
    return POSTMAN_VARS["MY_AKON_UUID"]


@pytest.fixture
def MY_TEAM_ID():
    return POSTMAN_VARS["MY_TEAM_ID"]


@pytest.fixture
def MY_PROJ_NUM():
    return POSTMAN_VARS["MY_PROJ_NUM"]


@pytest.fixture
def SERVICE_API_TOKEN():
    return POSTMAN_VARS["SERVICE_API_TOKEN"]


@pytest.fixture
def CUST01_WF01_DATA_STORAGE_KEY():
    return POSTMAN_VARS["CUST01_WF01_DATA_STORAGE_KEY"]


@pytest.fixture
def CUST01_WF02_DATA_STORAGE_KEY():
    return POSTMAN_VARS["CUST01_WF02_DATA_STORAGE_KEY"]


@pytest.fixture
def CUST02_WF01_DATA_STORAGE_KEY():
    return POSTMAN_VARS["CUST02_WF01_DATA_STORAGE_KEY"]


@pytest.fixture
def CUST03_WF01_DATA_STORAGE_KEY():
    return POSTMAN_VARS["CUST03_WF01_DATA_STORAGE_KEY"]


@pytest.fixture
def LAUNCH_ROWS():
    return POSTMAN_VARS["LAUNCH_ROWS"]


@pytest.fixture
def INTERNAL_TASKS_DOMAIN():
    return POSTMAN_VARS["INTERNAL_TASKS_DOMAIN"]


@pytest.fixture
def USER_SIGNUP_EMAIL():
    return POSTMAN_VARS["USER_SIGNUP_EMAIL"]


@pytest.fixture
def USER_SIGNUP_PASSWORD():
    return POSTMAN_VARS["USER_SIGNUP_PASSWORD"]

