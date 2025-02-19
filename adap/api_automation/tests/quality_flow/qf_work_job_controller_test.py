"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/job-controller
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
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    flow_id = default_project['work_jobs'][0]
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project['id'],
        "work_jobs": default_project['work_jobs'],
        "qa_jobs": default_project['qa_jobs'],
        "flow_id":  flow_id
    }


@pytest.fixture(scope="module")
def new_project(setup):
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    team_id = get_user_team_id('qf_user')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_name = f"automation project {_today} {faker.zipcode()}: work controller "
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200
    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"
    project_id = data['id']

    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)
    title1 = f"New QF leading work job {_today} {faker.zipcode()}"
    job_payload = {"title": title1,
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "WORK",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "",
                           "css": "",
                           "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                           "instructions": "Test CML API update"},
                   "jobFilter": {
                       "projectId": project_id,
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

    # prepare step: create a leading work job in new flow
    res = job_api.post_create_job_v2(team_id=team_id, payload=job_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    job_id = data['id']
    assert job_id is not None
    return {
        "job_api": job_api,
        "id": project_id,
        "job_id": job_id,
        "team_id": data['teamId'],
        "version": data['version']
    }


# get "/work/job/summary"
def test_get_job_summary_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project_id = setup['default_project']
    # project_id = project['id']
    job_id = setup['work_jobs'][0]

    res = api.get_job_summary(team_id=team_id, project_id=project_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_summary_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']
    # project_id = project['id']
    job_id = setup['work_jobs'][0]

    res = api.get_job_summary(team_id=team_id, project_id=project_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_summary_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']
    # project_id = project['id']
    job_id = setup['work_jobs'][0]

    res = api.get_job_summary(team_id=team_id, project_id=project_id, job_id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Job's data has not been found"


def test_get_job_summary_empty_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']
    # project_id = project['id']

    res = api.get_job_summary(team_id=team_id, project_id=project_id, job_id="")
    assert res.status_code == 400
    assert res.json_response['message'] == 'must not be empty'


# ---------------   "/work/job/list-as-flow"  ---------------------
def test_get_job_list_as_flow_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project_id = setup['default_project']
    # project_id = project['id']

    res = api.get_job_list_as_flow(team_id=team_id, project_id=project_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_list_as_flow_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']
    # project_id = project['id']

    res = api.get_job_list_as_flow(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_list_as_flow_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']

    # 0d78ddb2-4bd0-4d93-b87f-4d12d7759615
    flow_id = setup['flow_id']


    res = api.get_job_list_as_flow(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Job's data has not been found"
    work_qa_jobs_flow = [job for job in data if job['value']['id'] == flow_id][0]
    assert work_qa_jobs_flow.get('value', False), "Value data has not been found"
    assert work_qa_jobs_flow.get('next', False), "next data has not been found"

    assert work_qa_jobs_flow['value']['type'] == 'WORK'
    assert work_qa_jobs_flow['next']['value']['type'] == 'QA'


# -------------- "/work/job/job-with-cml"  --------------------
def test_get_job_with_cml_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    # project = setup['default_project']
    job_id = setup['work_jobs'][0]

    res = api.get_job_with_cml(team_id=team_id, id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_with_cml_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    # project = setup['default_project']
    job_id = setup['work_jobs'][0]

    res = api.get_job_with_cml(team_id=team_id, id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_with_cml_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    # project = setup['default_project']
    job_id = setup['work_jobs'][-1]

    res = api.get_job_with_cml(team_id=team_id, id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert data.get('instructions', False) == ('<h1>Overview</h1>\n'
                                                 '<hr/>\n'
                                                 '\n'
                                                 '<h1>Steps</h1>\n'
                                                 '<hr/>\n'
                                                 '\n'
                                                 '<h1>Rules &amp; Tips</h1>\n'
                                                 '<hr/>\n'
                                                 '\n'
                                                 '<h1>Examples</h1>\n'
                                                 '<hr/>\n'
                                                 '\n') != ('<h1>Overview</h1><hr>\n'
                                                 '<h1>Steps</h1><hr>\n'
                                                 '<h1>Rules & Tips</h1><hr>\n'
                                                 '<h1>Examples</h1><hr>')

    assert data.get('cml', False) == ('<div class="html-element-wrapper">Show data to contributors '
                                     'here</div><cml:radios label="Ask question here: test invoice test job with '
                                     'retry api" validates="required" gold="true"><cml:radio label="First option" '
                                     'value="first_option" /><cml:radio label="Second option" '
                                     'value="second_option" /></cml:radios>')

    assert data.get('id', False) == job_id
    assert data.get('teamId', False) == team_id
    assert data.get('projectId', False) == setup['default_project']
    assert data.get('type', False) == "WORK"
    assert data.get('title', False) == "invoice test job with retry api"


def test_get_job_with_cml_invalid_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_job_with_cml(team_id=team_id, id="test 1234")
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'

    data = res.json_response.get('data')
    assert not data, "Data has been found"


# -------------"/work/job/by" -------------------
def test_get_job_by_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    # project = setup['default_project']
    job_id = setup['work_jobs'][0]

    res = api.get_job_by(team_id=team_id, id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_by_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    # project = setup['default_project']
    job_id = setup['work_jobs'][0]

    res = api.get_job_by(team_id=team_id, id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_by_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    # project = setup['default_project']
    job_id = setup['work_jobs'][-1]

    res = api.get_job_by(team_id=team_id, id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert data.get('id', False) == job_id
    assert data.get('teamId', False) == team_id
    assert data.get('projectId', False) == setup['default_project']
    assert data.get('type', False) == "WORK"
    assert data.get('title', False) == "invoice test job with retry api"
    assert data.get('displayId', False)


def test_get_job_by_invalid_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_job_by(team_id=team_id, id="test 1234")
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'

    data = res.json_response.get('data')
    assert not data, "Data has been found"


# --------------  "/work/job/appendable-as-collection" -------------
def test_get_job_appendable_collection_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']

    res = api.get_job_appendable_as_collection(team_id=team_id, project_id=project)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_appendable_collection_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']

    res = api.get_job_appendable_as_collection(team_id=team_id, project_id=project)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_appendable_collection_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    job_id = setup['qa_jobs'][0]

    res = api.get_job_appendable_as_collection(team_id=team_id, project_id=project)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert data[0].get('id', False) == job_id
    assert data[0].get('teamId', False) == team_id
    assert data[0].get('projectId', False) == project
    assert data[0].get('type', False) == "QA"
    assert data[0].get('title', False) == "qa test"


def test_get_job_appendable_collection_invalid_project_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_job_appendable_as_collection(team_id=team_id, project_id="test 1233")
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'

    data = res.json_response.get('data')
    assert not data, "Data has been found"


# ----------- "/work/job/all" ---------------
def test_get_job_all_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']

    res = api.get_job_all(team_id=team_id, project_id=project)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_all_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']

    res = api.get_job_all(team_id=team_id, project_id=project)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_all_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    work_job_id = setup['work_jobs'][-1]
    qa_job_id = setup['qa_jobs'][0]

    res = api.get_job_all(team_id=team_id, project_id=project)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert data.get('totalElements', False) == len(setup['work_jobs']) + len(setup['qa_jobs'])

    content = data.get('content')
    assert content, "content has not been found"
    assert len(content) == len(setup['work_jobs']) + len(setup['qa_jobs'])
    jobIdList = [jobId['id'] for jobId in content]

    assert qa_job_id in jobIdList
    qa_job_index= jobIdList.index(qa_job_id)

    assert content[qa_job_index]['type'] == 'QA'
    assert content[qa_job_index]['teamId'] == team_id
    assert content[qa_job_index]['projectId'] == project

    work_job_index = jobIdList.index(work_job_id)
    assert work_job_id in jobIdList
    assert content[work_job_index]['type'] == 'WORK'
    assert content[work_job_index]['teamId'] == team_id
    assert content[work_job_index]['projectId'] == project


def test_get_job_all_invalid_project_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_job_all(team_id=team_id, project_id="test1233")
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'



# TODO expend test coverage for get_job_all

# ------------   "/work/job/all-as-collection" ----------
def test_get_job_all_as_collection_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project = setup['default_project']

    res = api.get_job_all_as_collection(team_id=team_id, project_id=project)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_job_all_as_collection_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project = setup['default_project']

    res = api.get_job_all_as_collection(team_id=team_id, project_id=project)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_job_all_as_collection_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project = setup['default_project']
    work_job_id = setup['work_jobs']
    qa_job_id = setup['qa_jobs'][0]

    res = api.get_job_all_as_collection(team_id=team_id, project_id=project)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"
    assert len(data) == len(work_job_id) + len(setup['qa_jobs'])

    actual_qa_job = find_dict_in_array_by_value(data, 'type', 'QA')
    assert actual_qa_job['id'] == qa_job_id
    assert actual_qa_job['type'] == 'QA'
    assert actual_qa_job['teamId'] == team_id
    assert actual_qa_job['projectId'] == project

    actual_work_job = find_dict_in_array_by_value(data, 'type', 'WORK')
    assert actual_work_job['id'] in work_job_id
    assert actual_work_job['type'] == 'WORK'
    assert actual_work_job['teamId'] == team_id
    assert actual_work_job['projectId'] == project

# todo check QF
def test_get_job_all_as_collection_invalid_project_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_job_all_as_collection(team_id=team_id, project_id="test1233")
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


# TODO expend test coverage for get_job_all_as_collection

# -------- POST "/work/job"  -----------
def test_post_create_job_invalid_cookies(setup, new_project):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project_id = new_project['id']

    payload = {"title": "test 1",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": 'null',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_create_job_invalid_team_id(setup, new_project, name, team_id, message):
    api = setup['api']
    project_id = new_project['id']

    payload = {"title": "test 1",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": 'null',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_post_create_job_invalid_project_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    payload = {"title": "test 1",
               "teamId": team_id,
               "projectId": "8fb3aaf-f3f1-437a",
               "type": "WORK",
               "flowId": 'null',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_post_create_job_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_create_job_v2(team_id=team_id, payload={})
    assert res.status_code == 400

    required_fields = {'type': 'job type should not be null or empty',
                       # 'templateType': 'must not be null',
                       # 'templateDisplayNm': 'must not be empty',
                       # 'cml': 'must not be null',
                       'projectId': 'project id should not be null or empty',
                       'title': 'must not be empty'}

    for k, v in required_fields.items():
        assert f"{k}: {v}" in res.json_response['message']


def test_post_create_job_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']

    payload = {"title": "New  WORK job - api",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"

    assert data.get('id'), 'id has not been found'
    assert data.get('teamId') == team_id
    assert data.get('projectId') == project_id
    assert data.get('flowId'), 'flowId has not been found'
    assert data.get('type') == 'WORK'
    assert data.get('state') == 'DRAFT'
    assert data.get('title') == "New  WORK job - api"

    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    assert data, "Data has not been found"

    assert data['content'][0]['title'] == "New  WORK job - api"


# TODO expend test coverage for post_create_job

# ------- PUT "/work/job"  ---------
def test_put_update_job_invalid_cookies(setup, new_project):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    project_id = new_project['id']

    payload = {"title": "test 1",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": 'null',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_put_update_job_invalid_team_id(setup, new_project, name, team_id, message):
    api = setup['api']
    project_id = new_project['id']

    payload = {"title": "test 1",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": 'null',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_put_update_job_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.put_update_job_v2(team_id=team_id, payload={})
    assert res.status_code == 403

    # required_fields = {
    #     'id': 'must not be empty',
    #     'version': 'must not be null',
    #     'title': 'must not be empty'
    # }
    #
    # for k, v in required_fields.items():
    #     assert f"{k}: {v}" in res.json_response['message']

    assert 'Unauthorized' == res.json_response['message']


def test_put_update_job_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']

    payload = {"title": "New  WORK job - to update",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    job_id = res.json_response['data']['id']
    version = res.json_response['data']['version']

    update_payload = {
        "id": job_id,
        "version": version,
        "teamId": team_id,
        "projectId": project_id,
        "cycleNumber": 0,
        "flowId": job_id,
        "type": "WORK",
        "state": "DRAFT",
        "copiedFrom": "",
        "title": "Job title was updated",
        "Template type": "UNDEFINED",
        "Allow to modify judgment": True,
        "Send back options": "SEND_BACK_TO_POOL"
    }

    res = api.put_update_job_v2(team_id=team_id, payload=update_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']

    assert data.get('id'), 'id has not been found'
    assert data.get('teamId') == team_id
    assert data.get('projectId') == project_id
    assert data.get('flowId'), 'flowId has not been found'
    assert data.get('type') == 'WORK'
    assert data.get('state') == 'DRAFT'
    assert data.get('title') == "Job title was updated"


# TODO expend test coverage for put_update_job


# -------- "/work/job/launch-config" ------
def test_post_launch_config_invalid_cookies(setup, new_project):
    api = QualityFlowApiWork()
    team_id = setup['team_id']

    payload = {}

    res = api.post_job_launch_config(team_id=team_id, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message, status', [
    ('empty', '', 'jobId: must not be empty; version: must not be null; ', 400),
    ('not exist', 'fkreek0mvml', 'Access Denied', 203),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied', 203)
])
def test_post_launch_config_invalid_team_id(setup, new_project, name, team_id, message, status):
    api = setup['api']
    payload = {}

    res = api.post_job_launch_config(team_id=team_id, payload=payload)
    assert res.status_code == status
    assert sorted(res.json_response['message'].split('; ')) == sorted(message.split('; '))


def test_post_launch_config_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_job_launch_config(team_id=team_id, payload={})
    assert res.status_code == 400

    required_fields = {'jobId': 'must not be empty',
                       'version': 'must not be null'}

    for k, v in required_fields.items():
        assert f"{k}: {v}" in res.json_response['message']


# feature is deprecated, user is not able to change config for running job
# def test_post_launch_config_valid(setup, new_project):
#     api = setup['api']
#     team_id = setup['team_id']
#
#     # create new job
#     project_id = new_project['id']
#
#     payload = {"title": "New  WORK job - test launch config",
#                "teamId": team_id,
#                "projectId": project_id,
#                "type": "WORK",
#                "flowId": '',
#                "templateDisplayNm": "No use template",
#                "templateType": {"index": 1},
#                "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
#                }
#
#     res = api.post_create_job_v2(team_id=team_id, payload=payload)
#     assert res.status_code == 200
#     assert res.json_response['message'] == 'success'
#
#     job_id = res.json_response['data']['id']
#     version = res.json_response['data']['version']
#
#     payload = {"jobId": job_id,
#                "teamId": team_id,
#                "version": version,
#                "judgmentsPerRow": 5,
#                "rowsPerPage": 5,
#                "assignmentLeaseExpiry": 1800,
#                "displayContributorName": False,
#                "strictTiming": False}
#
#     res = api.post_job_launch_config(team_id=team_id, payload=payload)
#     assert res.status_code == 200
#     assert res.json_response['message'] == 'success'
#
#     data = res.json_response.get('data', False)
#     assert data, "Data has not been found"
#
#     assert data['jobId'] == job_id
#     assert data['teamId'] == team_id
#     assert data['version'] == version + 1
#     assert data['judgmentsPerRow'] == 5
#     assert data['rowsPerPage'] == 5
#     assert data['pricePerJudgement'] == None


# TODO expend test coverage for post_job_launch_config
# -------- PUT "/work/job/launch"
def test_put_launch_job_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    job_id = setup['work_jobs'][0]

    res = api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_put_launch_job_invalid_team_id(setup, new_project, name, team_id, message):
    api = setup['api']
    job_id = setup['work_jobs'][0]

    res = api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_put_launch_job_invalid_job_id(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_launch_job_v2(team_id=team_id, job_id="wrhfiu88hjfewlknf")
    assert res.status_code == 403
    assert res.json_response['message'] == 'Unauthorized'


# todo check QF
@pytest.mark.dependency()
def test_post_launch_job_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']

    # create new job
    project_id = new_project['id']

    payload = {"title": "New  WORK job - test launch job",
               "teamId": team_id,
               "projectId": project_id,
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
               }

    res = api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    job_id = res.json_response['data']['id']
    version = res.json_response['data']['version']

    # res = api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    # assert res.status_code == 200
    # assert res.json_response['message'] == 'Pay rate type missing or invalid.'  # 'Need to update job config before launch'

    # update LAUNCH -> Crowd Settings
    payload = {
        "id": job_id,
        "jobCrowd": {
            "crowdType": ["INTERNAL"]
        }
    }
    res = api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['data']['jobCrowd']['crowdType'] == ["INTERNAL"]

    # update launch config
    payload = {"id": job_id,
               # "teamId": team_id,
               # "version": version,
               "judgmentsPerRow": "5",
               "rowsPerPage": 5,
               "assignmentLeaseExpiry": 1800,
               # "displayContributorName": False,
               "payRateType": "",
               "invoiceStatisticsType": None,
               # "strictTiming": False,
               "allowAbandonUnits": "false",
               "allowSelfQa": "false",
               "maxJudgmentPerContributor": 0,
               "maxJudgmentPerContributorEnabled": "false"}

    # res = api.post_job_launch_config(team_id=team_id, payload=payload)
    res = api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    # version = res.json_response['data']['version']

    # launch job
    res = api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']
    assert data['id'] == job_id
    assert data['teamId'] == team_id
    # assert data['version'] == version + 1
    assert data['state'] == 'RUNNING'
    assert data['judgmentsPerRow'] == 5
    assert data['rowsPerPage'] == 5

    new_project['running_job'] = job_id


# TODO expend test coverage for put_launch_job

# ----------  "/work/job/clone"  --------
def test_post_clone_job_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']

    res = api.post_clone_job(team_id=team_id, payload={})
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message, status', [
    ('empty', '', 'Unauthorized', 203),
    # ('empty', '',
    #  'appendTo: must not be empty; copiedFrom: must not be empty; title: must not be empty; projectId: must not be empty; ',
    #  403),

    ('not exist', 'fkreek0mvml', 'Access Denied', 203),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied', 203)
])
def test_post_clone_job_invalid_team_id(setup, name, team_id, message, status):
    api = setup['api']

    res = api.post_clone_job(team_id=team_id, payload={})

    assert res.status_code == status

    # if name == 'empty':
    #     required_fields = {
    #         'appendTo': 'must not be empty',
    #         'copiedFrom': 'must not be empty',
    #         'title': 'must not be empty',
    #         'projectId': 'must not be empty'
    #     }
    #
    #     for k, v in required_fields.items():
    #         assert f"{k}: {v}" in res.json_response['message']
    # else:
    assert res.json_response['message'] == message


def test_post_clone_job_invalid_payload(setup):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_clone_job(team_id=team_id, payload={})
    assert res.status_code == 203

    # required_fields = {'projectId': 'must not be empty',
    #                    'copiedFrom': 'must not be empty',
    #                    'appendTo': 'must not be empty',
    #                    'title': 'must not be empty'}
    #
    # for k, v in required_fields.items():
    #     assert f"{k}: {v}" in res.json_response['message']
    assert res.json_response['message'] == 'Unauthorized'


def test_post_clone_job_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']

    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    jobs = data['content']
    if not jobs:
        payload = {"title": "New  WORK job - copy test",
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "WORK",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "", "css": "", "cml": "", "instructions": ""}
                   }

        res = api.post_create_job_v2(team_id=team_id, payload=payload)
        assert res.status_code == 200
        assert res.json_response['message'] == 'success'

        job_to_copy = res.json_response['data']['id']
    else:
        job_to_copy = data['content'][0]['id']

    # Get jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    jobs = data['content']

    copy_payload = {
        "copiedFrom": job_to_copy,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": "Job was copied",
        "types": []
    }

    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']

    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)

# TODO expend test coverage for post_clone_job


def test_post_job_review_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    job_id = setup['work_jobs'][0]

    res = api.post_job_preview_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_job_review_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    job_id = setup['work_jobs'][0]

    res = api.post_job_preview_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, job_id, message', [
    ('empty', '', 'Job not found. Please check again.'),
    ('not exist', 'fkreek0mvm9809809l', 'Unauthorized')
])
def test_post_job_review_invalid_job_id(setup, name, job_id, message):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_job_preview_v2(team_id=team_id, job_id=job_id)
    assert res.status_code in [403, 400]
    assert res.json_response['message'] == message


def test_post_job_pause_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    job_id = setup['work_jobs'][0]

    res = api.post_job_pause_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_job_pause_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    job_id = setup['work_jobs'][0]

    res = api.post_job_pause_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, job_id, message', [
    ('empty', '', 'Job not found. Please check again.'),
    ('not exist', 'fkreek0mvm9809809l', 'Unauthorized')
])
def test_post_job_pause_invalid_job_id(setup, name, job_id, message):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_job_pause_v2(team_id=team_id, job_id=job_id)
    assert res.status_code in [203, 400]
    assert res.json_response['message'] == message


def test_post_job_resume_invalid_cookies(setup):
    api = QualityFlowApiWork()
    team_id = setup['team_id']
    job_id = setup['work_jobs'][0]

    res = api.post_job_resume_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_post_job_resume_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    job_id = setup['work_jobs'][0]

    res = api.post_job_resume_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, job_id, message', [
    ('empty', '', 'Job not found. Please check again.'),
    ('not exist', 'fkreek0mvm9809809l', 'Unauthorized')
])
def test_post_job_resume_invalid_job_id(setup, name, job_id, message):
    api = setup['api']
    team_id = setup['team_id']

    res = api.post_job_resume_v2(team_id=team_id, job_id=job_id)
    assert res.status_code in [403, 400]
    assert res.json_response['message'] == message


@pytest.mark.dependency(depends=["test_post_launch_job_valid"])
def test_post_job_pause_valid(setup, new_project):
    print(new_project)
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['running_job']

    res = api.post_job_pause_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 200

    data = res.json_response.get('data')
    assert data
    assert data['projectId'] == new_project['id']
    assert data['id'] == job_id
    assert data['state'] == 'PAUSED'


@pytest.mark.dependency(depends=["test_post_job_pause_valid"])
def test_post_job_resume_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['running_job']

    res = api.post_job_resume_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 200

    data = res.json_response.get('data')
    assert data
    assert data['projectId'] == new_project['id']
    assert data['id'] == job_id
    assert data['state'] == 'RUNNING'


@pytest.mark.dependency(depends=["test_post_job_resume_valid"])
def test_post_job_preview_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['running_job']

    res = api.post_job_preview_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 200

    data = res.json_response.get('data')
    assert data
    assert data['projectId'] == new_project['id']
    assert data['id'] == job_id
    assert data['state'] == 'PAUSED'


#----- DELETE API -----
def test_delete_job_valid(new_project):
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']

    title1 = f"New QF leading work job {_today} {faker.zipcode()}"
    job_payload = {"title": title1,
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "WORK",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "",
                           "css": "",
                           "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                           "instructions": "Test CML API update"},
                   "jobFilter": {
                       "projectId": project_id,
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

    # prepare step: create a leading work job in new flow
    res = api.post_create_job_v2(team_id=team_id, payload=job_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    job_id = data['id']
    assert job_id is not None
    assert data['projectId'] == project_id
    assert data['cycleNumber'] == 0
    assert data['type'] == 'WORK'
    assert data['flowId'] == job_id
    assert data['state'] == 'DRAFT'
    assert data['activeStatus'] == 'ACTIVE'

    # test step: delete the job
    res = api.post_delete_job_v2(team_id=team_id, project_id=project_id, job_id=job_id)
    assert res.status_code == 200
    assert len(res.json_response['data']['deletedJobIds']) == 1
    assert res.json_response['data']['deletedJobIds'][0] == job_id

    # check delete success
    job_by_id_payload = {"queryContents": ["jobFilter"]}
    job_by_id_res = api.post_job_by_id_v2(team_id=team_id, job_id=job_id, payload=job_by_id_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = job_by_id_res.json_response['data']
    assert data['id'] == job_id
    assert data['activeStatus'] == "INACTIVE"


def test_delete_job_invalid_cookies(setup, new_project):
    job_api = QualityFlowApiWork()
    team_id = setup['team_id']
    project_id = new_project['id']
    job_id = new_project['job_id']

    res = job_api.post_delete_job_v2(team_id=team_id, job_id=job_id, project_id=project_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_delete_job_invalid_team_id(setup, new_project, name, team_id, message):
    api = setup['api']
    project_id = new_project['id']
    job_id = new_project['job_id']

    res = api.post_delete_job_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


# @pytest.mark.parametrize('name, job_id, message', [
#     ('empty', '', 'Unauthorized'),
#     ('not exist', 'fkreek0mvm9809809l', 'Unauthorized')
# ])
# ## bug ticket is https://appen.atlassian.net/browse/KEP-3959
# def test_delete_job_invalid_job_id(setup, new_project, name, job_id, message):
#     api = setup['api']
#     team_id = setup['team_id']
#     project_id = new_project['id']
#
#     res = api.post_delete_job_v2(team_id=team_id, job_id=job_id, project_id=project_id)
#     assert res.status_code == 403 ## Failed caused by bug https://appen.atlassian.net/browse/KEP-3959
#     assert res.json_response['message'] == message ## Failed caused by bug https://appen.atlassian.net/browse/KEP-3959

#
@pytest.mark.parametrize('name, project_id, message', [
    # ('empty', '', 'Unauthorized'), ## bug ticket is https://appen.atlassian.net/browse/KEP-3959
    ('not exist', 'fkreek0mvm9809809l', 'Unauthorized')
])
def test_delete_job_invalid_project_id(setup, new_project, name, project_id, message):
    api = setup['api']
    team_id = setup['team_id']
    job_id = new_project['job_id']

    res = api.post_delete_job_v2(team_id=team_id, job_id=job_id, project_id=project_id)
    assert res.status_code == 203 ## Failed caused by bug https://appen.atlassian.net/browse/KEP-3959
    assert res.json_response['message'] == message ## Failed caused by bug https://appen.atlassian.net/browse/KEP-3959

