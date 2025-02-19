"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/prompt-controller
"""

import time

import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiWork, QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, find_dict_in_array_by_value

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              pytest.mark.qf_dc_api,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    # User Credentials
    username = get_test_data('qf_user_dc', 'email')
    password = get_test_data('qf_user_dc', 'password')
    team_id = get_test_data('qf_user_dc', 'teams')[0]['id']
    default_dc_project = get_test_data('qf_user_dc', 'dc_project')[0]['id']
    default_dc_job = get_test_data('qf_user_dc', 'dc_project')[0]['dc_jobs'][0]

    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)

    # create project
    api_project = QualityFlowApiProject()
    api_project.get_valid_sid(username, password)
    project_name = f"automation project {_today} {faker.zipcode()}: work controller "
    payload_project = {"name": project_name,
                       "description": project_name,
                       "unitSegmentType": "UNIT_ONLY"}

    res = api_project.post_create_project(team_id=team_id, payload=payload_project)
    assert res.status_code == 200
    response = res.json_response
    project_data = response.get('data')
    project_id = project_data['id']

    # create Data Collection job
    job_title = f"automation job {_today} {faker.zipcode()}"
    dc_job_payload = {"title": job_title,
                      "teamId": team_id,
                      "projectId": project_id,
                      "type": "DATA_COLLECTION"}

    res = api.post_create_dc_job_v2(team_id=team_id, payload=dc_job_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_data = res.json_response.get('data')
    assert job_data.get('type') == 'DATA_COLLECTION'
    job_id = job_data['id']

    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "project_id": project_id,
        "job_id": job_id,
        "default_dc_project": default_dc_project,
        "default_dc_job": default_dc_job
    }


@pytest.fixture
def create_dc_job(setup):
    api = setup['api']
    job_title = f"DATA_COLLECTION automation job {_today} {faker.zipcode()}"
    dc_job_payload = {"title": job_title,
                      "teamId": setup['team_id'],
                      "projectId": setup['project_id'],
                      "type": "DATA_COLLECTION"}

    res = api.post_create_dc_job_v2(team_id=setup['team_id'], payload=dc_job_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_data = res.json_response.get('data')
    assert job_data.get('type') == 'DATA_COLLECTION'
    dc_job_id = job_data['id']

    return {'dc_job_id': dc_job_id}


# post /work/prompt/add
def test_post_dc_prompt_add(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_element_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pageSize": 10,
        "pageNum": 1
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'],
                                                                  payload=payload_prompt_element_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    assert prompt_list_data['totalElements'] == 1
    assert len(prompt_list_data['content']) == 1


# post /work/prompt/delete
def test_post_dc_prompt_delete(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_element_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pageSize": 10,
        "pageNum": 1
    }

    response_prompt_list_before = api.post_dc_prompt_element_list(team_id=setup['team_id'],
                                                                  payload=payload_prompt_element_list)

    assert response_prompt_list_before.status_code == 200
    assert response_prompt_list_before.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list_before.json_response['data']
    prompt_id = prompt_list_data['content'][0]['promptId']

    payload_delete_prompt = {
        "promptId": prompt_id,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptIds": [
            prompt_id
        ],
        "promptGroupIds": []
    }

    response_delete_prompt = api.post_dc_prompt_delete(team_id=setup['team_id'], payload=payload_delete_prompt)
    assert response_delete_prompt.status_code == 200
    assert response_delete_prompt.json_response['message'] == 'success'

    response_prompt_list_after = api.post_dc_prompt_element_list(team_id=setup['team_id'],
                                                                 payload=payload_prompt_element_list)

    assert response_prompt_list_after.status_code == 200
    assert response_prompt_list_after.json_response['message'] == 'success'

    prompt_list_data_after = response_prompt_list_after.json_response['data']
    assert prompt_list_data_after['totalElements'] == 0
    assert len(prompt_list_data_after['content']) == 0


# post /work/prompt/edit
def test_post_dc_prompt_edit(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": False,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": False,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_element_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pageSize": 10,
        "pageNum": 1
    }

    response_prompt_list_before = api.post_dc_prompt_element_list(team_id=setup['team_id'],
                                                                  payload=payload_prompt_element_list)

    assert response_prompt_list_before.status_code == 200
    assert response_prompt_list_before.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list_before.json_response['data']
    prompt_id = prompt_list_data['content'][0]['promptId']

    payload_edit_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptId": prompt_id,
        "corpusCode": "image_prompt",
        "promptDisplayId": 20013,
        "inputQuestions": [
            {
                "isHidden": "false",
                "corpusCode": "prompt_checkbox",
                "resultsHeader": "prompt_checkbox",
                "id": "01a3a0d2-1131-4ac3-84e4-fa4e17332637",
                "optionType": "CHECK_BOX",
                "content": "prompt_checkbox",
                "hint": "",
                "options": [
                    {
                        "answerId": "",
                        "content": "Check",
                        "label": "Check"
                    },
                    {
                        "answerId": "",
                        "content": "NotCheck",
                        "label": "NotCheck"
                    }
                ],
                "source": "CUSTOM",
                "position": -1
            }
        ],
        "prompt": "<p></p>",
        "numberOfRecordings": 5,
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        }
    }

    response_edit_prompt = api.post_dc_prompt_edit(team_id=setup['team_id'], payload=payload_edit_prompt)

    assert response_edit_prompt.status_code == 200
    assert response_edit_prompt.json_response['message'] == 'success'

    response_prompt_list_after = api.post_dc_prompt_element_list(team_id=setup['team_id'],
                                                                 payload=payload_prompt_element_list)

    assert response_prompt_list_after.status_code == 200
    assert response_prompt_list_after.json_response['message'] == 'success'

    prompt_list_data_validation = response_prompt_list_after.json_response['data']
    assert prompt_list_data_validation['content'][0]['remains'] == 5
    assert prompt_list_data_validation['content'][0]['attributes']['accessMediaLibrary'] == True
    assert prompt_list_data_validation['content'][0]['attributes']['locationRequired'] == True
    assert len(prompt_list_data_validation['content'][0]['inputQuestions']) == 1


# post /work/prompt/element/list
# reorder the prompt which is out of the group
def test_post_dc_prompt_element_list(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_element_list = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "pageSize": 10,
        "pageNum": 1
    }

    response_prompt_list_before = api.post_dc_prompt_element_list(team_id=setup['team_id'],
                                                                  payload=payload_prompt_element_list)

    assert response_prompt_list_before.status_code == 200
    assert response_prompt_list_before.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list_before.json_response['data']
    assert len(prompt_list_data['content']) == 1
    assert prompt_list_data['totalElements'] == 1

# post /work/prompt/element/list
# reorder the prompt which is in the group
def test_post_reorder_dc_prompt_group_in_element_list(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt_1 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    payload_add_prompt_2 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "RECORDING",
        "corpusCode": "audio_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "audio_prompt"
    }

    response_add_prompt_add_first = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_1)
    assert response_add_prompt_add_first.status_code == 200
    assert response_add_prompt_add_first.json_response['message'] == 'success'

    response_add_prompt_add_second = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_2)
    assert response_add_prompt_add_second.status_code == 200
    assert response_add_prompt_add_second.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id_audio = prompt_list_data['content'][0]['promptId']
    prompt_display_id_audio = prompt_list_data['content'][0]['promptDisplayId']

    prompt_id_image = prompt_list_data['content'][1]['promptId']
    prompt_display_id_image = prompt_list_data['content'][1]['promptDisplayId']

    payload_group_organize = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "groupName": "prompt_group",
        "promptDisplayIds": [
            prompt_display_id_audio,
            prompt_display_id_image
        ],
        "promptIds": [
            prompt_id_audio,
            prompt_id_image
        ],
        "numberOfRecordings": 10,
        "promptsPerSession": 1,
        "promptLaunchMode": "IN_SEQUENCE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_organize = api.post_dc_prompt_group_organize(team_id=setup['team_id'],
                                                                       payload=payload_group_organize)

    assert response_prompt_group_organize.status_code == 200
    assert response_prompt_group_organize.json_response['message'] == 'success'

    payload_add_prompt_1 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt2",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt2"
    }
    response_add_prompt_add_third = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_1)
    assert response_add_prompt_add_third.status_code == 200
    assert response_add_prompt_add_third.json_response['message'] == 'success'

    response_prompt_list_group = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list_group.status_code == 200
    assert response_prompt_list_group.json_response['message'] == 'success'
    prompt_list_data_validation = response_prompt_list_group.json_response['data']
    group_id = prompt_list_data_validation['content'][1]['promptGroupId']
    group_display_id = prompt_list_data_validation['content'][1]['promptGroupDisplayId']

    payload_group_reorder = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptGroupId": group_id,
        "promptGroupDisplayId": group_display_id,
        "position": 0,
        "originalPosition": 2
    }

    response_prompt_group_reorder = api.post_dc_prompt_element_reorder(team_id=setup['team_id'],
                                                                     payload=payload_group_reorder)

    assert response_prompt_group_reorder.status_code == 200
    assert response_prompt_group_reorder.json_response['message'] == 'success'


def test_post_dc_prompt_element_reorder(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt_1 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    payload_add_prompt_2 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "RECORDING",
        "corpusCode": "audio_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "audio_prompt"
    }

    response_add_prompt_add_first = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_1)
    assert response_add_prompt_add_first.status_code == 200
    assert response_add_prompt_add_first.json_response['message'] == 'success'

    response_add_prompt_add_second = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_2)
    assert response_add_prompt_add_second.status_code == 200
    assert response_add_prompt_add_second.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id_audio = prompt_list_data['content'][0]['promptId']
    prompt_id_image = prompt_list_data['content'][1]['promptId']
    prompt_display_id_image = prompt_list_data['content'][1]['promptDisplayId']

    payload_prompt_reorder = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptId": prompt_id_image,
        "promptDisplayId": prompt_display_id_image,
        "originalPosition": 2,
        "position": 0
    }

    response_prompt_reorder = api.post_dc_prompt_element_reorder(team_id=setup['team_id'], payload=payload_prompt_reorder)
    assert response_prompt_reorder.status_code == 200
    assert response_prompt_reorder.json_response['message'] == 'success'

    response_prompt_list_validation = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)
    assert response_prompt_list_validation.status_code == 200
    assert response_prompt_list_validation.json_response['message'] == 'success'
    prompt_list_validation = response_prompt_list_validation.json_response['data']
    assert prompt_list_validation['content'][0]['promptType'] == "IMAGE"
    assert prompt_list_validation['content'][1]['promptType'] == "RECORDING"


# post /work/prompt/group/organize
def test_post_dc_prompt_group_organize(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id = prompt_list_data['content'][0]['promptId']
    prompt_display_id = prompt_list_data['content'][0]['promptDisplayId']

    payload_group_organize = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "groupName": "prompt_group",
        "promptDisplayIds": [
            prompt_display_id
        ],
        "promptIds": [
            prompt_id
        ],
        "numberOfRecordings": 10,
        "promptsPerSession": 1,
        "promptLaunchMode": "IN_SEQUENCE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_organize = api.post_dc_prompt_group_organize(team_id=setup['team_id'],
                                                                       payload=payload_group_organize)

    assert response_prompt_group_organize.status_code == 200
    assert response_prompt_group_organize.json_response['message'] == 'success'

    response_prompt_list_validation = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list_validation.status_code == 200
    assert response_prompt_list_validation.json_response['message'] == 'success'
    prompt_list_data_validation = response_prompt_list_validation.json_response['data']
    assert prompt_list_data_validation['content'][0]['itemType'] == "PROMPT_GROUP"
    assert prompt_list_data_validation['totalElements'] == 1


# post /work/prompt/group/edit
def test_post_dc_prompt_group_edit(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id = prompt_list_data['content'][0]['promptId']
    prompt_display_id = prompt_list_data['content'][0]['promptDisplayId']

    payload_group_organize = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "groupName": "prompt_group",
        "promptDisplayIds": [
            prompt_display_id
        ],
        "promptIds": [
            prompt_id
        ],
        "numberOfRecordings": 5,
        "promptsPerSession": 1,
        "promptLaunchMode": "IN_SEQUENCE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_organize = api.post_dc_prompt_group_organize(team_id=setup['team_id'],
                                                                       payload=payload_group_organize)

    assert response_prompt_group_organize.status_code == 200
    assert response_prompt_group_organize.json_response['message'] == 'success'

    response_group_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_group_list.status_code == 200
    assert response_group_list.json_response['message'] == 'success'
    prompt_group_list_data = response_group_list.json_response['data']
    group_id = prompt_group_list_data['content'][0]['promptGroupId']
    group_display_id = prompt_group_list_data['content'][0]['promptGroupDisplayId']

    payload_group_edit = {
        "itemType": "PROMPT_GROUP",
        "promptGroupId": group_id,
        "promptGroupDisplayId": group_display_id,
        "name": "group",
        "numberOfRecordings": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptsPerSession": 2,
        "promptLaunchMode": "RANDOMIZE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_edit = api.post_dc_prompt_group_edit(team_id=setup['team_id'], payload=payload_group_edit)
    assert response_prompt_group_edit.status_code == 200
    assert response_prompt_group_edit.json_response['message'] == 'success'

    response_group_list_validation = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_group_list_validation.status_code == 200
    assert response_group_list_validation.json_response['message'] == 'success'
    prompt_group_list_data_validation = response_group_list_validation.json_response['data']
    assert prompt_group_list_data_validation['content'][0]['promptLaunchMode'] == "RANDOMIZE"
    assert prompt_group_list_data_validation['content'][0]['promptsPerSession'] == 2
    assert prompt_group_list_data_validation['content'][0]['numberOfRecordings'] == 10


# post /work/prompt/group/release
def test_post_dc_prompt_group_release(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    response_add_prompt = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt)
    assert response_add_prompt.status_code == 200
    assert response_add_prompt.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id = prompt_list_data['content'][0]['promptId']
    prompt_display_id = prompt_list_data['content'][0]['promptDisplayId']

    payload_group_organize = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "groupName": "prompt_group",
        "promptDisplayIds": [
            prompt_display_id
        ],
        "promptIds": [
            prompt_id
        ],
        "numberOfRecordings": 10,
        "promptsPerSession": 1,
        "promptLaunchMode": "IN_SEQUENCE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_organize = api.post_dc_prompt_group_organize(team_id=setup['team_id'],
                                                                       payload=payload_group_organize)

    assert response_prompt_group_organize.status_code == 200
    assert response_prompt_group_organize.json_response['message'] == 'success'

    response_prompt_list_group = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list_group.status_code == 200
    assert response_prompt_list_group.json_response['message'] == 'success'
    prompt_list_data_validation = response_prompt_list_group.json_response['data']
    group_id = prompt_list_data_validation['content'][0]['promptGroupId']
    group_display_id = prompt_list_data_validation['content'][0]['promptGroupDisplayId']

    payload_group_release = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptGroupId": group_id,
        "promptGroupDisplayId": group_display_id,
        "groupName": "prompt_group"
    }

    response_prompt_group_release = api.post_dc_prompt_group_release(team_id=setup['team_id'],
                                                                     payload=payload_group_release)
    assert response_prompt_group_release.status_code == 200
    assert response_prompt_group_release.json_response['message'] == 'success'

    response_prompt_list_validation = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list_validation.status_code == 200
    assert response_prompt_list_validation.json_response['message'] == 'success'
    prompt_list_data_validation = response_prompt_list_validation.json_response['data']
    assert prompt_list_data_validation['content'][0]['itemType'] == "PROMPT"
    assert prompt_list_data_validation['totalElements'] == 1


# post /work/prompt/group/reorder
# thie api is to reorder the prompt in group
def test_post_reorder_dc_prompt_in_group(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt_1 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    payload_add_prompt_2 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "RECORDING",
        "corpusCode": "audio_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "audio_prompt"
    }

    response_add_prompt_add_first = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_1)
    assert response_add_prompt_add_first.status_code == 200
    assert response_add_prompt_add_first.json_response['message'] == 'success'

    response_add_prompt_add_second = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_2)
    assert response_add_prompt_add_second.status_code == 200
    assert response_add_prompt_add_second.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id_audio = prompt_list_data['content'][0]['promptId']
    prompt_display_id_audio = prompt_list_data['content'][0]['promptDisplayId']

    prompt_id_image = prompt_list_data['content'][1]['promptId']
    prompt_display_id_image = prompt_list_data['content'][1]['promptDisplayId']

    payload_group_organize = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "groupName": "prompt_group",
        "promptDisplayIds": [
            prompt_display_id_audio,
            prompt_display_id_image
        ],
        "promptIds": [
            prompt_id_audio,
            prompt_id_image
        ],
        "numberOfRecordings": 10,
        "promptsPerSession": 1,
        "promptLaunchMode": "IN_SEQUENCE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_organize = api.post_dc_prompt_group_organize(team_id=setup['team_id'],
                                                                       payload=payload_group_organize)

    assert response_prompt_group_organize.status_code == 200
    assert response_prompt_group_organize.json_response['message'] == 'success'

    response_prompt_list_group = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list_group.status_code == 200
    assert response_prompt_list_group.json_response['message'] == 'success'
    prompt_list_data_validation = response_prompt_list_group.json_response['data']
    group_id = prompt_list_data_validation['content'][0]['promptGroupId']
    group_display_id = prompt_list_data_validation['content'][0]['promptGroupDisplayId']

    payload_group_reorder = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptId": prompt_id_audio,
        "promptDisplayId": prompt_display_id_audio,
        "promptGroupId": group_id,
        "promptGroupDisplayId": group_display_id,
        "position": 0,
        "originalPosition": 2
    }

    response_prompt_group_reorder = api.post_dc_prompt_group_reorder(team_id=setup['team_id'],
                                                                     payload=payload_group_reorder)

    assert response_prompt_group_reorder.status_code == 200
    assert response_prompt_group_reorder.json_response['message'] == 'success'


# post /work/prompt/group/prompt-shuffle
def test_post_dc_prompt_group_prompt_shuffle(setup, create_dc_job):
    api = setup['api']

    payload_add_prompt_1 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "IMAGE",
        "corpusCode": "image_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "image_prompt"
    }

    payload_add_prompt_2 = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "prompt": "<p></p>",
        "promptType": "RECORDING",
        "corpusCode": "audio_prompt",
        "attributes": {
            "defaultCameraFacing": "back",
            "flashMode": "auto",
            "accessMediaLibrary": True,
            "cameraEnabled": True,
            "videoQuality": None,
            "customResolution": "1080",
            "resolutionCheckMode": "gte",
            "frameRateCheckMode": "eq",
            "customFrameRate": 30,
            "videoMinDuration": "1",
            "videoMaxDuration": "600",
            "locationRequired": True,
            "minUploadFileSize": 1,
            "skippable": False
        },
        "numberOfRecordings": 1,
        "resultsHeader": "audio_prompt"
    }

    response_add_prompt_add_first = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_1)
    assert response_add_prompt_add_first.status_code == 200
    assert response_add_prompt_add_first.json_response['message'] == 'success'

    response_add_prompt_add_second = api.post_dc_prompt_add(team_id=setup['team_id'], payload=payload_add_prompt_2)
    assert response_add_prompt_add_second.status_code == 200
    assert response_add_prompt_add_second.json_response['message'] == 'success'

    payload_prompt_list = {
        "pageNum": 1,
        "pageSize": 10,
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id']
    }

    response_prompt_list = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list.status_code == 200
    assert response_prompt_list.json_response['message'] == 'success'

    prompt_list_data = response_prompt_list.json_response['data']
    prompt_id_audio = prompt_list_data['content'][0]['promptId']
    prompt_display_id_audio = prompt_list_data['content'][0]['promptDisplayId']

    prompt_id_image = prompt_list_data['content'][1]['promptId']
    prompt_display_id_image = prompt_list_data['content'][1]['promptDisplayId']

    payload_group_organize = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "groupName": "prompt_group",
        "promptDisplayIds": [
            prompt_display_id_audio,
            prompt_display_id_image
        ],
        "promptIds": [
            prompt_id_audio,
            prompt_id_image
        ],
        "numberOfRecordings": 10,
        "promptsPerSession": 1,
        "promptLaunchMode": "IN_SEQUENCE",
        "conditionalLogic": {
            "predicate": "AND",
            "questions": []
        }
    }

    response_prompt_group_organize = api.post_dc_prompt_group_organize(team_id=setup['team_id'],
                                                                       payload=payload_group_organize)

    assert response_prompt_group_organize.status_code == 200
    assert response_prompt_group_organize.json_response['message'] == 'success'

    response_prompt_list_group = api.post_dc_prompt_element_list(team_id=setup['team_id'], payload=payload_prompt_list)

    assert response_prompt_list_group.status_code == 200
    assert response_prompt_list_group.json_response['message'] == 'success'
    prompt_list_data_validation = response_prompt_list_group.json_response['data']
    group_id = prompt_list_data_validation['content'][0]['promptGroupId']
    group_display_id = prompt_list_data_validation['content'][0]['promptGroupDisplayId']

    payload_group_prompt_shuffle = {
        "projectId": setup['project_id'],
        "jobId": create_dc_job['dc_job_id'],
        "promptGroupId": group_id,
        "promptGroupDisplayId": group_display_id,
    }

    response_prompt_group_prompt_shuffle = api.post_dc_prompt_group_prompt_shuffle(team_id=setup['team_id'],
                                                                                   payload=payload_group_prompt_shuffle)

    assert response_prompt_group_prompt_shuffle.status_code == 200
    assert response_prompt_group_prompt_shuffle.json_response['message'] == 'success'



# TO DO: "/work/prompt/send-to-group" "/work/prompt/out-of-group" "/work/prompt/enable" "/work/prompt/disable"



