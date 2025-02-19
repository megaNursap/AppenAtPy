"""
https://appen.atlassian.net/browse/QED-1987
Three step workflow:
1. Audio Annotation job
2. Audio Transcription job
3. Audio Transcription review job
"""
import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.workflow import Workflow
from adap.data.audio_transcription import data
from adap.e2e_automation.services_config.workflow_api_support import api_create_wf_from_config
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_annotation/audio_data.csv")
JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

payload1 = {
    "key": API_KEY,
    "job": {
        "title": "testing workflow job",
        "instructions": "Updated",
        "cml": data.workflow_audio_annotation_cml,
        "units_per_assignment": 5,
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

payload2 = {
    "key": API_KEY,
    "job": {
        "title": "testing workflow job",
        "instructions": "Updated",
        "cml": data.workflow_audio_transcription_cml,
        "units_per_assignment": 5,
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

payload3 = {
    "key": API_KEY,
    "job": {
        "title": "testing workflow job",
        "instructions": "Updated",
        "cml": data.workflow_audio_transcription_peerreview_cml,
        "units_per_assignment": 5,
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

filter_payload = {
        "filter_rule": {
            "rule_connector": "all"
        }
    }

wf_config_3 = {
    "env": pytest.env,
    "user": {
        "api_key": API_KEY
    },
    "jobs": {
        "count": 3,
        "payloads": [payload1, payload2, payload3]
    },
    "workflow": {
        "payload": {
          'name': 'Audio Transcription WF', 'description': 'API create new wf'
        }
    },
    "routes": {
        "1": {"connect": (1, 2), "filter": filter_payload},
        "2": {"connect": (2, 3), "filter": filter_payload}
    },
    "data_upload": [DATA_FILE],
    "launch": True,
    "row_order": 5,
    "ontology": data.ontology,
    "jwt_token": JWT_TOKEN
}


def test_workflow_for_audio_transcription(app):
    wf_info = api_create_wf_from_config(wf_config_3, username=USER_EMAIL, password=PASSWORD)
    wf = Workflow(API_KEY)
    wf.wf_id = wf_info['id']
    _jobs = wf_info['jobs']

    """
    annotate first audio annotation job, will auto trigger second audio transcription job go to running status and use the result from first job,
    then annotate second audio transcription job will trigger third audio transcription peer review job go to running status
    """
    for i in range(3):
        job = JobAPI(API_KEY, job_id=_jobs[i])
        job.wait_until_status('running', 200)
        res = job.get_json_job_status()
        res.assert_response_status(200)
        assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
            res.json_response['state'], "running")

        job_link = generate_job_link(_jobs[i], API_KEY, pytest.env)
        app.navigation.open_page(job_link)
        if i == 0:
            app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
        app.user.close_guide()
        time.sleep(2)
        app.user.task.wait_until_job_available_for_contributor(job_link)
        if i == 0:
            for j in range(0, 5):
                app.audio_annotation.activate_iframe_by_index(j)
                app.audio_annotation.begin_annotate(0)
                app.navigation.click_link('Nothing to Annotate')
                app.audio_annotation.save_for_nothing_annotate()
                app.audio_annotation.deactivate_iframe()

        app.audio_annotation.submit_page()
        time.sleep(2)
        app.verification.text_present_on_page('There is no work currently available in this task.')
