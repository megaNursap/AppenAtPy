"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/question-controller
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


@pytest.fixture(scope="module")
def create_dc_job(setup):
    api = setup['api']
    job_title = f"automation job {_today} {faker.zipcode()}"
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


# put /work/question
def test_put_dc_job_question_valid(setup, create_dc_job):
    api = setup['api']

    payload = {
        "resultsHeader": "Checkbox_question",
        "corpusCode": "Checkbox_question",
        "content": "Checkbox_question",
        "source": "CUSTOM",
        "optionType": "CHECK_BOX",
        "extInfo": {},
        "options": [
            {
                "answerId": "",
                "label": "Check",
                "content": "Check"
            },
            {
                "answerId": "",
                "label": "NotCheck",
                "content": "NotCheck"
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res_create_question = api.post_dc_job_question(team_id=setup['team_id'], payload=payload)
    assert res_create_question.status_code == 200
    assert res_create_question.json_response['message'] == 'success'
    data = res_create_question.json_response['data']
    question_id = data['id']
    check_answer_id = data['options'][0]['answerId']
    not_check_answer_id = data['options'][1]['answerId']

    payload_update_question = {
        "id": question_id,
        "resultsHeader": "Checkbox_question_updated",
        "corpusCode": "Checkbox_question_updated",
        "content": "Checkbox_question_updated",
        "source": "CUSTOM",
        "optionType": "CHECK_BOX",
        "extInfo": {},
        "options": [
            {
                "answerId": check_answer_id,
                "label": "Check",
                "content": "Check",
                'selected': False,
                'status': 'ENABLED'
            },
            {
                "answerId": not_check_answer_id,
                "label": "NotCheck",
                "content": "NotCheck",
                'selected': False,
                'status': 'ENABLED'
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res_update_question = api.put_dc_job_question(team_id=setup['team_id'], payload=payload_update_question)
    assert res_update_question.status_code == 200
    assert res_update_question.json_response['message'] == 'success'

    res_question_list = api.get_dc_job_question_custom_list(team_id=setup['team_id'], job_id=create_dc_job['dc_job_id'])
    data_res = res_question_list.json_response['data']
    assert data_res[0]['content'] == "Checkbox_question_updated"


def test_put_dc_job_question_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    payload_update_question = {
        "id": "41036b13-9a5e-46a8-b244-2253c6117c96",
        "resultsHeader": "Checkbox_question_updated",
        "corpusCode": "Checkbox_question_updated",
        "content": "Checkbox_question_updated",
        "source": "CUSTOM",
        "optionType": "CHECK_BOX",
        "extInfo": {},
        "options": [
            {
                "answerId": "",
                "label": "Check",
                "content": "Check"
            },
            {
                "answerId": "",
                "label": "NotCheck",
                "content": "NotCheck"
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res_update_question = api_invalid.put_dc_job_question(team_id=setup['team_id'], payload=payload_update_question)
    assert res_update_question.status_code == 401
    assert res_update_question.json_response['message'] == 'Please login'


# post /work/question
@pytest.mark.parametrize('question_type, question_name, option_content_1, option_content_2', [
    ('CHECK_BOX', 'QA_Test_CHECK_BOX_question', 'Check', 'NotCheck'),
    ('CHECK_BOX_GROUP', 'QA_Test_CHECK_BOX_GROUP_question', 'label_1', 'label_2'),
    ('MULTI_CHOICE', 'QA_Test_MULTI_CHOICE_question', 'label_1', 'label_2'),
    ('DROP_DOWN', 'QA_Test_DROP_DOWN_question', 'label_1', 'label_2')
])
def test_post_dc_job_question_valid(setup, create_dc_job, question_type, question_name, option_content_1,
                                    option_content_2):
    api = setup['api']

    payload = {
        "resultsHeader": question_name,
        "corpusCode": question_name,
        "content": question_name,
        "source": "CUSTOM",
        "optionType": question_type,
        "extInfo": {},
        "options": [
            {
                "answerId": "",
                "label": option_content_1,
                "content": option_content_1
            },
            {
                "answerId": "",
                "label": option_content_2,
                "content": option_content_2
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res = api.post_dc_job_question(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']
    assert data['jobId'] == create_dc_job['dc_job_id']
    assert data['resultsHeader'] == question_name
    assert data['corpusCode'] == question_name
    assert data['content'] == question_name
    assert data['status'] == "ENABLED"
    assert data['optionType'] == question_type
    assert data['source'] == "CUSTOM"
    assert data['isHidden'] is False


@pytest.mark.parametrize('question_type, question_name, ', [
    ('TEXT_PARAGRAPH', 'QA_Test_TEXT_PARAGRAPH_question'),
    ('TEXT_LINE', 'QA_Test_TEXT_LINE_question')
])
def test_post_dc_job_question_valid(setup, create_dc_job, question_type, question_name):
    api = setup['api']

    payload = {
        "resultsHeader": question_name,
        "corpusCode": question_name,
        "content": question_name,
        "source": "CUSTOM",
        "optionType": question_type,
        "extInfo": {},
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res = api.post_dc_job_question(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']
    assert data['jobId'] == create_dc_job['dc_job_id']
    assert data['resultsHeader'] == question_name
    assert data['corpusCode'] == question_name
    assert data['content'] == question_name
    assert data['status'] == "ENABLED"
    assert data['optionType'] == question_type
    assert data['source'] == "CUSTOM"
    assert data['isHidden'] is False


def test_post_dc_job_question_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    payload = {
        "resultsHeader": "QA_Test_CHECK_BOX_question",
        "corpusCode": "QA_Test_CHECK_BOX_question",
        "content": "QA_Test_CHECK_BOX_question",
        "source": "CUSTOM",
        "optionType": "CHECK_BOX",
        "extInfo": {},
        "options": [
            {
                "answerId": "",
                "label": "Check",
                "content": "Check"
            },
            {
                "answerId": "",
                "label": "NotCheck",
                "content": "NotCheck"
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res = api_invalid.post_dc_job_question(team_id=setup['team_id'], payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


# post /work/question/update-status
@pytest.mark.parametrize('operation_type, question_name, is_hidden', [
    ('ENABLE', 'QA_Test_CHECK_BOX_question_1', 'true'),
    ('DISABLE', 'QA_Test_CHECK_BOX_question_2', 'false')
])
def test_post_dc_job_update_status_question_valid(setup, create_dc_job, operation_type, question_name, is_hidden):
    api = setup['api']

    payload_create_question = {
        "resultsHeader": question_name,
        "corpusCode": question_name,
        "content": question_name,
        "source": "CUSTOM",
        "optionType": 'CHECK_BOX',
        "extInfo": {},
        "options": [
            {
                "answerId": "",
                "label": "Check",
                "content": 'Check'
            },
            {
                "answerId": "",
                "label": "NotCheck",
                "content": 'NotCheck'
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": is_hidden
    }

    res_create_question = api.post_dc_job_question(team_id=setup['team_id'], payload=payload_create_question)
    assert res_create_question.status_code == 200
    assert res_create_question.json_response['message'] == 'success'
    data = res_create_question.json_response['data']
    question_id = data['id']

    payload_enable_question = {
        "questionIds": [
            question_id
        ],
        "operationType": operation_type,
        "jobId": create_dc_job['dc_job_id']
    }
    res_update_question_status = api.post_dc_job_question_update_status(team_id=setup['team_id'],
                                                                        payload=payload_enable_question)
    assert res_update_question_status.status_code == 200
    assert res_update_question_status.json_response['message'] == 'success'


@pytest.mark.parametrize('operation_type, question_name, is_hidden', [
    ('ENABLE', 'QA_Test_CHECK_BOX_question_1', 'true'),
    ('DISABLE', 'QA_Test_CHECK_BOX_question_2', 'false')
])
def test_post_dc_job_update_status_question_invalid_cookies(setup, create_dc_job, operation_type, question_name, is_hidden):
    api_invalid = QualityFlowApiWork()
    payload_enable_question = {
        "questionIds": [
            "41036b13-9a5e-46a8-b244-2253c6117c96"
        ],
        "operationType": operation_type,
        "jobId": create_dc_job['dc_job_id']
    }
    res_update_question_status = api_invalid.post_dc_job_question_update_status(team_id=setup['team_id'],
                                                                                payload=payload_enable_question)
    assert res_update_question_status.status_code == 401
    assert res_update_question_status.json_response['message'] == 'Please login'


# post /work/question/reorder
def test_post_dc_job_reorder_questions_valid(setup):
    api = setup['api']

    res_custom_list_before = api.get_dc_job_question_custom_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    data = res_custom_list_before.json_response['data']
    question_id_1 = data[0]['id']
    question_id_2 = data[1]['id']

    payload_reorder_questions = {
        "questionId": question_id_1,
        "jobId": setup['default_dc_job'],
        "targetQuestionId": question_id_2
    }
    res_reorder_questions = api.post_dc_job_question_reorder(team_id=setup['team_id'],
                                                             payload=payload_reorder_questions)
    assert res_reorder_questions.status_code == 200
    assert res_reorder_questions.json_response['message'] == 'success'

    res_custom_list_after = api.get_dc_job_question_custom_list(team_id =setup['team_id'], job_id=setup['default_dc_job'])
    data_res = res_custom_list_after.json_response['data']

    assert data_res[0]['id'] == question_id_2
    assert data_res[1]['id'] == question_id_1


def test_post_dc_job_reorder_questions_invalid_cookies(setup):
    api = setup['api']
    api_invalid = QualityFlowApiWork()

    res_custom_list_before = api.get_dc_job_question_custom_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    data = res_custom_list_before.json_response['data']
    question_id_1 = data[0]['id']
    question_id_2 = data[1]['id']

    payload_reorder_questions = {
        "questionId": question_id_1,
        "jobId": setup['default_dc_job'],
        "targetQuestionId": question_id_2
    }
    res_reorder_questions = api_invalid.post_dc_job_question_reorder(team_id=setup['team_id'],
                                                                     payload=payload_reorder_questions)
    assert res_reorder_questions.status_code == 401
    assert res_reorder_questions.json_response['message'] == 'Please login'


# post /work/question/delete
def test_post_delete_dc_job_valid(setup, create_dc_job):
    api = setup['api']

    res_custom_list_before_delete = api.get_dc_job_question_custom_list(job_id=create_dc_job['dc_job_id'],
                                                                        team_id=setup['team_id'])
    assert res_custom_list_before_delete.status_code == 200
    data = res_custom_list_before_delete.json_response['data']
    init_question_number = len(data)

    payload_create_question = {
        "resultsHeader": 'QA_Test_CHECK_BOX_question_to_delete',
        "corpusCode": 'QA_Test_CHECK_BOX_question_to_delete',
        "content": 'QA_Test_CHECK_BOX_question_to_delete',
        "source": "CUSTOM",
        "optionType": 'CHECK_BOX',
        "extInfo": {},
        "options": [
            {
                "answerId": "",
                "label": "Check",
                "content": 'Check'
            },
            {
                "answerId": "",
                "label": "NotCheck",
                "content": 'NotCheck'
            }
        ],
        "jobId": create_dc_job['dc_job_id'],
        "isHidden": "false"
    }

    res_create_question = api.post_dc_job_question(team_id=setup['team_id'], payload=payload_create_question)
    assert res_create_question.status_code == 200
    assert res_create_question.json_response['message'] == 'success'
    data = res_create_question.json_response['data']
    question_id = data['id']

    res_custom_list_before_delete = api.get_dc_job_question_custom_list(job_id=create_dc_job['dc_job_id'],
                                                                        team_id=setup['team_id'])
    assert res_custom_list_before_delete.status_code == 200
    data = res_custom_list_before_delete.json_response['data']
    assert len(data) == init_question_number + 1

    payload_delete_question = {
        "questionIds": [
            question_id
        ],
        "jobId": create_dc_job['dc_job_id']
    }

    res_delete_question = api.post_dc_job_question_delete(team_id=setup['team_id'],
                                                          payload=payload_delete_question)
    assert res_delete_question.status_code == 200
    assert res_delete_question.json_response['message'] == 'success'

    res_custom_list_after_delete = api.get_dc_job_question_custom_list(team_id=setup['team_id'],
                                                                       job_id=create_dc_job['dc_job_id'])
    assert res_custom_list_after_delete.status_code == 200
    data = res_custom_list_after_delete.json_response['data']
    assert len(data) == init_question_number


def test_post_delete_dc_job_invalid_cookies(setup, create_dc_job):
    api_invalid = QualityFlowApiWork()

    payload_delete_question = {
        "questionIds": [
            "41036b13-9a5e-46a8-b244-2253c6117c96"
        ],
        "jobId": create_dc_job['dc_job_id']
    }

    res_delete_question = api_invalid.post_dc_job_question_delete(team_id=setup['team_id'],
                                                                  payload=payload_delete_question)
    assert res_delete_question.status_code == 401
    assert res_delete_question.json_response['message'] == 'Please login'


# get /work/question/simple-list
def test_get_simple_list_questions_valid(setup):
    api = setup['api']

    res = api.get_dc_job_question_simple_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']
    assert len(data) == 4


def test_get_simple_list_questions_invalid_cookies(setup):
    api = QualityFlowApiWork()

    res = api.get_dc_job_question_simple_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_get_simple_list_questions_invalid_team_id(setup, name, team_id, status_code, message):
    api = setup['api']

    res = api.get_dc_job_question_simple_list(team_id=team_id, job_id=setup['default_dc_job'])
    assert res.status_code == status_code
    assert res.json_response['message'] == message


# get /work/question/hidden-list

def test_get_hidden_list_questions_valid(setup):
    api = setup['api']

    res = api.get_dc_job_question_hidden_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']
    assert len(data) == 1


def test_get_hidden_list_questions_invalid_cookies(setup):
    api = QualityFlowApiWork()

    res = api.get_dc_job_question_hidden_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_get_hidden_list_questions_invalid_team_id(setup, name, team_id, status_code, message):
    api = setup['api']

    res = api.get_dc_job_question_hidden_list(team_id=team_id, job_id=setup['default_dc_job'])
    assert res.status_code == status_code
    assert res.json_response['message'] == message


# get /work/question/custom-list
def test_get_custom_list_questions_valid(setup):
    api = setup['api']

    res = api.get_dc_job_question_custom_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']
    assert len(data) == 3


def test_get_custom_list_questions_invalid_cookies(setup):
    api = QualityFlowApiWork()

    res = api.get_dc_job_question_custom_list(team_id=setup['team_id'], job_id=setup['default_dc_job'])
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'

@pytest.mark.skip(reason="Test scripts not valid because there is no checking mechanism for team_id on the BackEnd code")
@pytest.mark.parametrize('name, team_id, status_code, message', [
    ('not exist', 'fkreek0mvml', 203, 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 203, 'Access Denied')
])
def test_get_custom_list_questions_invalid_team_id(setup, name, team_id, status_code, message):
    api = setup['api']

    res = api.get_dc_job_question_custom_list(team_id=team_id, job_id=setup['default_dc_job'])
    assert res.status_code == status_code
    assert res.json_response['message'] == message

