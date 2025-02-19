"""
swagger - https://api-kepler.integration.cf3.us/batchjob/swagger-ui/index.html#/
"""
import time

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor, QualityFlowApiBatchjob, \
    QualityFlowExternalApiProject, QualityFlowApiProject
import pytest
import random
from faker import Faker
import datetime
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_data_file
import logging

logger = logging.getLogger('faker')
logger.setLevel(logging.INFO)  # Quiet faker locale messages down in tests.

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    team_id = get_user_team_id('qf_user')
    api_key = get_test_data('qf_user', 'api_key')

    api = QualityFlowApiBatchjob()
    api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project,
        "batchjobId": '8aa2d0c4-f7b8-4fa6-86dd-123bbcdd6a0d',
        "api_key": api_key
    }


def test_post_bachjob_progress_list_invalid_cookies(setup):
    api = QualityFlowApiBatchjob()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    payload = {"pageNumber":1,"pageSize":30,"sortModel":[],"filterModel":{}}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_bachjob_progress_list_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']

    payload = {"pageNumber": 1, "pageSize": 30, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_post_bachjob_progress_list_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    payload = {"pageNumber": 1, "pageSize": 30, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_post_bachjob_progress_list_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    payload = {}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)
    assert res.status_code == 200
   # assert res.json_response['error'] == 'Internal Server Error'


def test_post_bachjob_progress_list_valid_existing_project(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    payload = {"pageNumber": 1, "pageSize": 1, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)

    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']['list']
    assert len(data) == 1
    assert sorted(data[0].keys()) ==sorted(['id','version', 'projectId', 'input', 'output', 'batchjobType', 'status',
                                            'intervalTime', 'intervalUnit','nextExecuteTime',
                                             'retryRemain', 'timeout', 'timeoutUnit', 'activeUntil', 'activeStatus',
                                             'createdAt', 'createdBy', 'updatedAt', 'filePath', 'progress', 'job'])


def test_post_bachjob_progress_list_new_project(setup):
    """
    create new project
    upload data
    verify bachjob_progress_list
    verify bachjob_progress_history
    """
    api = setup['api']
    team_id = setup['team_id']
    api_key = setup['api_key']

    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    faker = Faker()
    project_name = f"automation project {_today} {faker.zipcode()}"
    new_project_payload = {"name": project_name}

    # create new project
    public_api = QualityFlowExternalApiProject(api_key=api_key)

    res = public_api.post_create_project(team_id=setup["team_id"], payload=new_project_payload, headers=public_api.headers)
    response = res.json_response
    assert res.status_code == 200

    data = response.get('data')
    project_id = data.get('id', False)

    # verify no data in progress list
    payload = {"pageNumber": 1, "pageSize": 10, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)

    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data'] == {
                                           "list": [],
                                           "pageSize": 10,
                                           "totalPages": 0,
                                           "pageNumber": 0,
                                           "totalElements": 0
                                      }

    # upload data
    file_name = get_data_file('/authors.csv')
    res = public_api.post_upload_data_project(team_id=setup['team_id'],
                                              project_id=project_id,
                                              file_name=file_name,
                                              api_key=api_key)
    assert res.status_code == 201
    time.sleep(10)

    # verify 1 proccess inn progress list
    payload = {"pageNumber": 1, "pageSize": 10, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_list(team_id=team_id,
                                       project_id=project_id,
                                       payload=payload)

    assert res.status_code == 200
    data = res.json_response['data']['list']
    assert len(data) == 1
    assert data[0]['projectId'] == project_id
    assert data[0]['batchjobType'] == "FILE_PUBLISH"
    assert data[0]['status'] == "DONE"
    assert data[0]['activeStatus'] == "ACTIVE"
    assert data[0]['id']

    # verify data in progress history
    batchjobId = data[0]['id']
    payload = {"pageNumber": 1, "pageSize": 10, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_history(team_id=team_id,
                                          project_id=project_id,
                                          batchjobId=batchjobId,
                                          payload=payload)

    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']['list']
    assert len(data) == 1
    assert data[0]['projectId'] == project_id
    assert data[0]['batchjobType'] == "FILE_PUBLISH"
    assert data[0]['status'] == "DONE"
    assert data[0]['id']

    # delete project
    api_delete = QualityFlowApiProject()
    api_delete.get_valid_sid(setup['username'], setup['password'])

    res = api_delete.delete_project(project_id=project_id, team_id=setup['team_id'], version_id=1)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'


# ------------------------------------
# ----------- process history --------
# ------------------------------------

def test_post_bachjob_progress_history_invalid_cookies(setup):
    api = QualityFlowApiBatchjob()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    batchjobId = setup['batchjobId']

    payload = {"pageNumber":1,"pageSize":30,"sortModel":[],"filterModel":{}}
    res = api.post_batch_progress_history(team_id=team_id,
                                          project_id=project_id,
                                          batchjobId=batchjobId,
                                          payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_bachjob_progress_history_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']
    batchjobId = setup['batchjobId']

    payload = {"pageNumber": 1, "pageSize": 30, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_history(team_id=team_id,
                                          project_id=project_id,
                                          batchjobId=batchjobId,
                                          payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message

@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_post_bachjob_progress_history_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']
    batchjobId = setup['batchjobId']

    payload = {"pageNumber": 1, "pageSize": 30, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_history(team_id=team_id,
                                          project_id=project_id,
                                          batchjobId=batchjobId,
                                          payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_post_bachjob_progress_history_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    batchjobId = setup['batchjobId']

    payload = {}
    res = api.post_batch_progress_history(team_id=team_id,
                                          project_id=project_id,
                                          batchjobId=batchjobId,
                                          payload=payload)
    assert res.status_code == 500
    assert res.json_response['error'] == 'Internal Server Error'


def test_post_bachjob_progress_hisory_valid_existing_project(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    batchjobId = setup['batchjobId']

    payload = {"pageNumber": 1, "pageSize": 10, "sortModel": [], "filterModel": {}}
    res = api.post_batch_progress_history(team_id=team_id,
                                          project_id=project_id,
                                          batchjobId=batchjobId,
                                          payload=payload)

    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']['list']
    assert len(data) == 10
    assert sorted(data[0].keys()) ==sorted(['id','version', 'batchjobId', 'scheduleTime', 'processorId',
                                            'projectId', 'input','output',
                                             'batchjobType', 'status','retryRemain', 'timeoutUntil', 'activeUntil',
                                             'errMsg', 'createdAt', 'createdBy', 'updatedAt'])
    assert data[0]['projectId'] == project_id


