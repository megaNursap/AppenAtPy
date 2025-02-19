"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/interlocking-controller
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

username = "integration+alpaca01@figure-eight.com"
password = "Xzsaazi$Ca6E$JMJ"
team_id = "acdac212-8e03-49a9-99cb-dd157ccabe29"

@pytest.fixture(scope="module")
def setup():
    # username = get_test_data('qf_user_dc', 'email')
    # password = get_test_data('qf_user_dc', 'password')
    # team_id = get_test_data('qf_user_dc', 'teams')[0]['id']

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
    project_name = res.json_response['data']['name']
    project_id = res.json_response['data']['id']

    job_title = f"automation job {_today} {faker.zipcode()}"
    dc_job_payload = {"title": job_title,
                      "teamId": team_id,
                      "projectId": project_id,
                      "type": "DATA_COLLECTION"}

    res = api.post_create_dc_job_v2(team_id=team_id, payload=dc_job_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_data = res.json_response['data']
    assert job_data['type'] == 'DATA_COLLECTION'
    job_id = job_data['id']
    job_name = job_data['title']

    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "project_id": project_id,
        "job_id": job_id,
        "default_dc_project": project_name,
        "default_dc_job": job_name
    }


@pytest.fixture(autouse=True)
def create_dc_job_with_questions(setup):
    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)
    resultsHeader = "Question" + faker.zipcode()
    payload_create_question = {
        "resultsHeader": resultsHeader,
        "corpusCode": resultsHeader,
        "content": "test1",
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
        "jobId": setup['job_id'],
        "isHidden": "false"
    }

    print("setup response ", setup)
    res_created_question = api.post_dc_job_question(team_id=setup['team_id'], payload=payload_create_question)
    print("res_created_question response ", res_created_question.json_response)
    assert res_created_question.status_code == 200
    assert res_created_question.json_response['message'] == 'success'
    data = res_created_question.json_response['data']
    question_id = data['id']
    options = data['options']

    return {
        "dc_job_id": setup['job_id'],
        "question_id": question_id,
        "options": options
    }


# post /work/interlocking/generate-quotas
def test_post_dc_job_generate_quotas(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id'],
        "type": "CUSTOM_INTERLOCKING"
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'], payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'
    data = response_generate_quotas.json_response['data']
    assert data['totalQuota'] == 10
    assert data['type'] == "CUSTOM_INTERLOCKING"


# post /work/interlocking/update-status
def test_post_dc_job_update_status_quotas(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_create_question = {
        "resultsHeader": "question1",
        "corpusCode": "question1",
        "content": "test1",
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
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "isHidden": "false"
    }

    res_create_question = api.post_dc_job_question(team_id=setup['team_id'], payload=payload_create_question)
    assert res_create_question.status_code == 200
    assert res_create_question.json_response['message'] == 'success'
    data = res_create_question.json_response['data']

    question_id = data['id'],

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id'],
        "type": "CUSTOM_INTERLOCKING"
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'],
                                                                        payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'
    data = response_generate_quotas.json_response['data']
    assert data['totalQuota'] == 10
    assert data['type'] == "CUSTOM_INTERLOCKING"

    payload_quota_list = {
        "pageNum": 1,
        "pageSize": 10,
        "jobId": create_dc_job_with_questions['dc_job_id']
    }

    response_quota_list = api.post_dc_interlocking_list(team_id=setup['team_id'], payload=payload_quota_list)
    assert response_quota_list.status_code == 200
    assert response_quota_list.json_response['message'] == 'success'
    data_quota_list = response_quota_list.json_response['data']

    interlocking_id = data_quota_list['content'][0]['id']

    payload_quota_update_status = {
        "interlockingIds": [
            interlocking_id
        ],
        "status": "DISABLED",
        "jobId": create_dc_job_with_questions['dc_job_id']
    }

    response_quota_update_status = api.post_dc_interlocking_update_status(team_id=setup['team_id'],
                                                                          payload=payload_quota_update_status)
    assert response_quota_update_status.status_code == 200
    assert response_quota_update_status.json_response['message'] == 'success'

    response_quota_list_after_update = api.post_dc_interlocking_list(team_id=setup['team_id'],
                                                                     payload=payload_quota_list)
    assert response_quota_list_after_update.status_code == 200
    assert response_quota_list_after_update.json_response['message'] == 'success'
    data_quota_list_after_update = response_quota_list_after_update.json_response['data']
    assert data_quota_list_after_update['content'][0]['status'] == "DISABLED"


# post /work/interlocking/update-quota
def test_post_dc_job_update_quota(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id']
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'],
                                                                        payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'

    payload_quota_list = {
        "pageNum": 1,
        "pageSize": 10,
        "jobId": create_dc_job_with_questions['dc_job_id']
    }

    response_quota_list = api.post_dc_interlocking_list(team_id=setup['team_id'], payload=payload_quota_list)
    assert response_quota_list.status_code == 200
    assert response_quota_list.json_response['message'] == 'success'
    data_quota_list = response_quota_list.json_response['data']

    interlocking_id = data_quota_list['content'][0]['id']

    response_quota_update = api.post_dc_interlocking_update_quota(team_id=setup['team_id'],
                                                                  interlocking_id=interlocking_id, target_quota=3)

    assert response_quota_update.status_code == 200
    assert response_quota_update.json_response['message'] == 'success'
    data_update_quota = response_quota_update.json_response['data']

    assert data_update_quota['interlockingDTO']['targetNumber'] == 3


# post /work/interlocking/update-quota-config
def test_post_dc_job_update_quota_config(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id'],
        "type": "CUSTOM_INTERLOCKING"
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'],
                                                                        payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'

    payload_quota_list = {
        "pageNum": 1,
        "pageSize": 10,
        "jobId": create_dc_job_with_questions['dc_job_id']
    }

    response_quota_list = api.post_dc_interlocking_list(team_id=setup['team_id'], payload=payload_quota_list)
    assert response_quota_list.status_code == 200
    assert response_quota_list.json_response['message'] == 'success'
    data_generate_quota = response_generate_quotas.json_response['data']

    interlocking_id = data_generate_quota['id']

    payload_update_quota_config = {
        "id": interlocking_id,
        "version": 0,
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id'],
        "totalQuota": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 30,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 70,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "type": "CUSTOM_INTERLOCKING"
    }

    res_update_quota_config = api.post_dc_interlocking_update_quota_config(team_id=setup['team_id'],
                                                                           payload=payload_update_quota_config)
    assert res_update_quota_config.status_code == 200
    assert res_update_quota_config.json_response['message'] == 'success'
    data_quota_config = res_update_quota_config.json_response['data']
    assert data_quota_config['questionList'][0]['answerConfigList'][0]['percentage'] == 30
    assert data_quota_config['questionList'][0]['answerConfigList'][1]['percentage'] == 70


# post /work/interlocking/list
def test_post_dc_job_quota_list(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    }
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id']
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'],
                                                                        payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'

    payload_quota_list = {
        "pageNum": 1,
        "pageSize": 10,
        "jobId": create_dc_job_with_questions['dc_job_id']
    }

    response_quota_list = api.post_dc_interlocking_list(team_id=setup['team_id'], payload=payload_quota_list)
    assert response_quota_list.status_code == 200
    assert response_quota_list.json_response['message'] == 'success'
    data_quota_list = response_quota_list.json_response['data']
    # Using if condition to check if running 1 script it will be 2 because creating only 2 quota
    # and if running all should be 10 because other script creating quota too and the total become 10
    if (len(data_quota_list['content']) > 2):
        assert len(data_quota_list['content']) == 10
    else:
        assert len(data_quota_list['content']) == 2



# get /work/interlocking/statistics
def test_get_dc_job_quota_statistics(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id']
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'],
                                                                        payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'

    response_statistics = api.get_dc_interlocking_statistics(job_id=create_dc_job_with_questions['dc_job_id'],
                                                             team_id=setup['team_id'])

    assert response_statistics.status_code == 200
    assert response_statistics.json_response['message'] == 'success'
    data_statistics = response_statistics.json_response['data']
    assert data_statistics['completedSessionsRequired'] == 10
    # Using if condition to check if running 1 script it will be 2 because creating only 2 quota
    # and if running all should be 12 because other script creating quota too and the total become 12
    if (data_statistics['numberOfQuotas'] > 2):
        assert data_statistics['numberOfQuotas'] == 12
    else:
        assert data_statistics['numberOfQuotas'] == 2
    assert data_statistics['sessionsCompleted'] == 0
    assert data_statistics['sessionsInProgress'] == 0
    assert data_statistics['sessionsRemaining'] == 10


# get /work/interlocking/config-by-interlocking-id
def test_get_dc_job_quota_config_by_interlocking_id(setup, create_dc_job_with_questions):
    api = setup['api']

    payload_generate_quotas = {
        "questionTotalQuota": 10,
        "totalSessionNumber": 10,
        "questionList": [
            {
                "questionId": create_dc_job_with_questions['question_id'],
                "answerConfigList": [
                    {
                        "answerId": create_dc_job_with_questions['options'][0]['answerId'],
                        "answerContent": "label_1",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                    {
                        "answerId": create_dc_job_with_questions['options'][1]['answerId'],
                        "answerContent": "label_2",
                        "targetQuota": 0,
                        "percentage": 50,
                        "engaged": "true"
                    },
                ]
            }
        ],
        "jobId": create_dc_job_with_questions['dc_job_id'],
        "projectId": setup['project_id'],
        "type": "CUSTOM_INTERLOCKING"
    }

    response_generate_quotas = api.post_dc_interlocking_generate_quotas(team_id=setup['team_id'],
                                                                        payload=payload_generate_quotas)

    assert response_generate_quotas.status_code == 200
    assert response_generate_quotas.json_response['message'] == 'success'

    payload_quota_list = {
        "pageNum": 1,
        "pageSize": 10,
        "jobId": create_dc_job_with_questions['dc_job_id']
    }

    response_quota_list = api.post_dc_interlocking_list(team_id=setup['team_id'], payload=payload_quota_list)
    assert response_quota_list.status_code == 200
    assert response_quota_list.json_response['message'] == 'success'
    data_quota_list = response_quota_list.json_response['data']

    interlocking_id = data_quota_list['content'][0]['id']

    response_config_by_interlocking_id = api.get_dc_interlocking_config_by_interlocking_id(team_id=setup['team_id'],
                                                                                           interlocking_id=interlocking_id)
    assert response_config_by_interlocking_id.status_code == 200
    assert response_config_by_interlocking_id.json_response['message'] == 'success'
    data_interlocking_id = response_config_by_interlocking_id.json_response['data']

    assert data_interlocking_id['totalQuota'] == 10
    assert data_interlocking_id['type'] == "CUSTOM_INTERLOCKING"
    assert len(data_interlocking_id['questionList'][0]['answerConfigList']) == 2









