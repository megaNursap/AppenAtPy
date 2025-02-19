"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/job-controller-2/cloneJob

Notes:
    /job/filter/clone endpoint is old, we don't use it now, currently we use API /work/v2/job/clone to clone filter(SAMPLING)
        DESIGN,
        SAMPLING,
        QUALITY_SETTINGS,
        CROWD_SETTINGS,
        PRICE_AND_ROW;
"""

import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiWork, QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def new_project():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    team_id = get_user_team_id('qf_user')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_name = f"automation project {_today} {faker.zipcode()}: job filter controller"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    # create job
    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)

    job_name1 = f"New WORK job 1 - filer job testt {faker.zipcode()}"
    job_name2 = f"New WORK job 2 - filer job testt {faker.zipcode()}"
    payload1 = {"title": job_name1,
               "teamId": team_id,
               "projectId": data['id'],
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "",
                       "css": "",
                       "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                       "instructions": "Test CML API update"},
               "jobFilter": {
                   "projectId": data['id'],
                   "origin": "project_data_source",
                   "schedulerDelay": 24,
                   "schedulerUnit": "HOURS",
                   "sampleRate": 10,
                   "segmental": False,
                   "segmentSampleRate": 100,
                   "filterCriteria": "{}",
                   "filterNum": 0,
                   "minimumSampleUnit": 0
                    }
               }
    payload2 = {"title": job_name2,
                "teamId": team_id,
                "projectId": data['id'],
                "type": "WORK",
                "flowId": '',
                "templateDisplayNm": "No use template",
                "templateType": {"index": 1},
                "cml": {"js": "",
                        "css": "",
                        "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                        "instructions": "Test CML API update"},
                "jobFilter": {
                    "projectId": data['id'],
                    "origin": "project_data_source",
                    "schedulerDelay": 24,
                    "schedulerUnit": "HOURS",
                    "sampleRate": 20,
                    "segmental": False,
                    "segmentSampleRate": 100,
                    "filterCriteria": "{}",
                    "filterNum": 0,
                    "minimumSampleUnit": 0
                }
                }

    res_job1 = job_api.post_create_job_v2(team_id=team_id, payload=payload1)
    assert res_job1.status_code == 200

    res_job2 = job_api.post_create_job_v2(team_id=team_id, payload=payload2)
    assert res_job2.status_code == 200

    return {
        "api": job_api,
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version'],
        "jobs": [res_job1.json_response['data']['id'], res_job2.json_response['data']['id']]
    }


def test_post_job_clone_invalid_cookies(new_project):
    api = QualityFlowApiWork()
    project_id = new_project['id']
    team_id = new_project['team_id']
    job1_id = new_project['jobs'][0]
    job2_id = new_project['jobs'][1]

    copy_payload = {
        "copiedFrom": job1_id,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Job was copied: from Job {job1_id}",
        "includeLaunchConfig": True,
        "types": [
            "CROWD_SETTINGS",
            "PRICE_AND_ROW",
            "DESIGN"
        ]
    }

    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_job_clone_invalid_team_id(new_project, name, team_id, message):
    api = new_project['api']
    project_id = new_project['id']
    job1_id = new_project['jobs'][0]

    copy_payload = {
        "copiedFrom": job1_id,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Job was copied: from Job {job1_id}",
        "includeLaunchConfig": True,
        "types": [
            "CROWD_SETTINGS",
            "PRICE_AND_ROW",
            "DESIGN"
        ]
    }
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_post_job_clone_empty_project_id(new_project):
    api = new_project['api']
    team_id = new_project['team_id']
    job1_id = new_project['jobs'][0]

    copy_payload = {
        "copiedFrom": job1_id,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": '',
        "title": f"Job was copied: from Job {job1_id}",
        "includeLaunchConfig": True,
        "types": [
            "CROWD_SETTINGS",
            "PRICE_AND_ROW",
            "DESIGN"
        ]
    }
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'Job not found. Please check again.'


def test_post_job_clone_invalid_project_id(new_project):
        api = new_project['api']
        team_id = new_project['team_id']
        job1_id = new_project['jobs'][0]

        copy_payload = {
            "copiedFrom": job1_id,
            "appendTo": "project_data_source",
            "teamId": team_id,
            "projectId": 'fkreek0mvm9809809l',
            "title": f"Job was copied: from Job {job1_id}",
            "includeLaunchConfig": True,
            "types": [
                "CROWD_SETTINGS",
                "PRICE_AND_ROW",
                "DESIGN"
            ]
        }
        res = api.post_clone_job(team_id=team_id, payload=copy_payload)
        assert res.status_code == 203
        assert res.json_response['message'] == 'Unauthorized'


def test_post_job_clone_invalid_copied_from(new_project):
    api = new_project['api']
    project_id = new_project['id']
    team_id = new_project['team_id']
    job1_id = new_project['jobs'][0]

    copy_payload = {
        "copiedFrom": "",
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Job was copied: from Job {job1_id}",
        "includeLaunchConfig": True,
        "types": [
            "CROWD_SETTINGS",
            "PRICE_AND_ROW",
            "DESIGN"
        ]
    }
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'Job not found. Please check again.'


def test_post_job_clone_invalid_append_to(new_project):
    api = new_project['api']
    project_id = new_project['id']
    team_id = new_project['team_id']
    job1_id = new_project['jobs'][0]

    copy_payload = {
        "copiedFrom": job1_id,
        "appendTo": "",
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Job was copied: from Job {job1_id}",
        "includeLaunchConfig": True,
        "types": [
            "CROWD_SETTINGS",
            "PRICE_AND_ROW",
            "DESIGN"
        ]
    }
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'Job not found. Please check again.'


def test_post_job_clone_sampling_configuration_valid(new_project):
    api = new_project['api']
    project_id = new_project['id']
    team_id = new_project['team_id']
    job1_id = new_project['jobs'][0]
    job2_id = new_project['jobs'][1]

    copy_payload = {
        "copiedFrom": job1_id,
        "appendTo": job2_id,
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Job was copied: from Job {job1_id}",
        "includeLaunchConfig": True,
        "types": [
            "CROWD_SETTINGS",
            "PRICE_AND_ROW",
            "DESIGN",
            "SAMPLING"
        ]
    }

    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']

    new_job_id = res.json_response['data']['id']

    # get the job details and check jobFilter is cloned success
    res = api.post_job_by_id_v2(team_id=team_id, job_id=new_job_id, payload={"queryContents" : ["jobFilter"]})
    assert res.status_code == 200
    assert res.json_response['data']['jobFilter'] is not None
    assert res.json_response['data']['jobFilter']['sampleRate'] == 10

