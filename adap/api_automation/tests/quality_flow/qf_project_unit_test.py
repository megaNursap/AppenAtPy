"""
https://api-kepler.integration.cf3.us/project/swagger-ui/index.html#/Unit%20Controller
"""
import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject, QualityFlowApiWork, \
    get_unit_by_index, get_job_attribute, QualityFlowApiContributor
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_data_file
from adap.ui_automation.services_config.quality_flow.components import login_and_open_qf_page

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module",autouse=False)
def setup(app):
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    team_id = get_user_team_id('qf_user')

    project_name = f"automation project {_today} {faker.zipcode()}: unit controller"
    # project_name = 'automation project 2022_10_27 26504: unit controller'
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    # create job
    quiz_work_mode_cml = """
      <div class="html-element-wrapper">
        <p>Column1: {{column_1}}</p>
        <p>Column2: {{column_2}}</p>
        <p>marker: {{marker}}</p>
      </div>
      <cml:radios label="What is greater?" validates="required" name="what_is_greater" gold="true">
        <cml:radio label="Column1" value="col1" />
        <cml:radio label="Column2" value="col2" />
        <cml:radio label="Equals" value="equals" />
      </cml:radios>
    """

    job_api = QualityFlowApiWork()
    job_api.cookies=api.cookies
    payload = {"title": "New  WORK job",
               "teamId": team_id,
               "projectId": data['id'],
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "",
                       "css": "",
                       "cml": quiz_work_mode_cml,
                       "instructions": "Test what is greater"}
               }

    res = job_api.post_create_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200

    login_and_open_qf_page(app, 'qf_user')
    time.sleep(5)
    app.navigation.refresh_page()
    app.quality_flow.open_project(by='name', value=project_name)

    # upload data
    data_file = get_data_file("/quiz_work_mode_switch/whatisgreater.csv")
    app.quality_flow.data.all_data.upload_data(data_file)
    app.navigation.refresh_page()
    api.get_valid_sid(username,password)

    work_api = QualityFlowApiWork()
    contributor_api = QualityFlowApiContributor()

    work_api.cookies=api.cookies
    contributor_api.cookies=api.cookies

    return {
        "username": username,
        "password": password,
        "api": api,
        "work_api": work_api,
        "contributor_api": contributor_api,
        "default_project": default_project,
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version'],
        "jobs": [res.json_response['data']['id']]
    }


@pytest.fixture(scope="module")
def setup_segmented_project(setup):
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    team_id = get_user_team_id('qf_user')
    default_segmented_project = get_test_data('qf_user', 'default_segmented_project')
    api=setup["api"]

    return {
        "api": api,
        "username": username,
        "password": password,
        "default_segmented_project_id": default_segmented_project['id'],
        "team_id": team_id
    }

#  /project/units
def test_qf_post_units_invalid_cookies(setup):
    print(setup["api"].cookies)
    api = QualityFlowApiProject()
    project_id = setup['id']
    team_id = setup['team_id']

    payload = {"startRow": 0, "endRow": 19, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_units_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']
    print(setup["api"].cookies)
    payload = {"startRow": 0, "endRow": 19, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_qf_post_units_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']
    print(setup["api"].cookies)
    payload = {"startRow": 0, "endRow": 19, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_qf_post_units_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']
    # project_id = 'de743440-78c6-43c2-a573-1ae9a25d10e4'
    print(setup["api"].cookies)
    payload = {"startRow": 0, "endRow": 19, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200

    result = res.json_response
    assert len(result['data']['units']) == 19 == result['data']['totalElements']

    unit_1 = result['data']['units'][0]
    assert unit_1['unitDisplayId'][0]['value'] == '1_1'
    assert unit_1['unitDisplayId'][0]['link']

    assert unit_1['projectId'][0]['value'] == project_id


# ----------------------------
#  /project/send-to-job
# ----------------------------

def test_qf_post_send_to_job_invalid_cookies(setup):
    api = QualityFlowApiProject()
    job_id = setup['jobs'][0]
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": [], "percentage": 100}
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_send_to_job_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    job_id = setup['jobs'][0]
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": [], "percentage": 100}
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.dependency()
def test_qf_post_send_to_job_valid(setup):
    """
    send 1st unit to job
    """
    api = setup['api']
    job_id = setup['jobs'][0]
    team_id = setup['team_id']
    project_id = setup['id']
    work_api = setup['work_api']

    # find unit id
    payload = {"startRow": 0, "endRow": 1, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200
    unit_1 = res.json_response['data']['units'][0]['unitId'][0]['value']

    # update LAUNCH -> Crowd Settings
    payload = {
        "id": job_id,
        "jobCrowd": {
            "crowdType": ["INTERNAL"]
        }
    }
    res = work_api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['data']['jobCrowd']['crowdType'] == ["INTERNAL"]

    # update launch config
    payload = {"id": job_id,
               "judgmentsPerRow": "1",
               "rowsPerPage": 1,
               "assignmentLeaseExpiry": 1800,
               "payRateType": "",
               "invoiceStatisticsType": None,
               "allowAbandonUnits": "false",
               "allowSelfQa": "false",
               "maxJudgmentPerContributor": 0,
               "maxJudgmentPerContributorEnabled": "false"}

    res = work_api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    # res = work_api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    # assert res.status_code == 200
    # time.sleep(5)

    # payload = {"projectId": project_id, "unitIds": [unit_id], "percentage": 100}
    # res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload)
    # assert res.status_code == 200
    # time.sleep(5)

    res = work_api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 200
    time.sleep(5)

    payload = {"projectId": project_id, "unitIds": [unit_1], "percentage": 100}
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']['total'] == 1
    assert res.json_response['data']['error'] == False
    time.sleep(20)
    # verification
    unit_1 = get_unit_by_index(api, project_id, team_id, 0)

    assert unit_1['jobStatus'][0]['value'] == 'JUDGEABLE'
    assert job_id in unit_1['jobAlias'][0]['link']
    assert unit_1['jobTitle'][0]['value'] == 'New  WORK job'
    assert unit_1['jobId'][0]['value'] == job_id


# -------------------------
# /project/remove-from-job
# -------------------------
def test_qf_post_remove_from_job_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": []}
    res = api.post_remove_from_job(team_id=team_id, payload=payload, ignore_conflict='true')

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_remove_from_job_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": []}
    res = api.post_remove_from_job(team_id=team_id, payload=payload, ignore_conflict='true')
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.dependency(depends=["test_qf_post_send_to_job_valid"])
def test_qf_post_remove_from_job_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['id']
    unit1_id = get_unit_by_index(api, project_id, team_id, 0)['unitId'][0]['value']
    payload = {"projectId": project_id, "unitIds": [unit1_id]}

    res = api.post_remove_from_job(team_id=team_id, payload=payload, ignore_conflict='true')
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']['total'] == 1
    time.sleep(10)
    unit_1 = get_unit_by_index(api, project_id, team_id, 0)

    assert unit_1['jobStatus'][0]['value'] != 'ASSIGNED'


# -------------------------
# /project/send-to-group
# -------------------------
def test_qf_post_send_to_group_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']
    group_name = 'test'

    payload = {"dataGroup": {"projectId": project_id,
                             "name": group_name},
               "units": {"projectId": project_id,
                         "unitIds": []}}

    res = api.post_send_to_group(team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_send_to_group_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']
    group_name = 'test'

    payload = {"dataGroup": {"projectId": project_id,
                             "name": group_name},
               "units": {"projectId": project_id,
                         "unitIds": []}}

    res = api.post_send_to_group(team_id=team_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.dependency()
def test_qf_post_send_to_group_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['id']

    group_name = 'test group data 1'

    #  find 1st unit
    payload = {"startRow": 0, "endRow": 1, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200

    unit_id = res.json_response['data']['units'][0]['unitId'][0]['value']

    # send unit to group
    payload = {"dataGroup": {"projectId": project_id,
                             "name": group_name},
               "units": {"projectId": project_id,
                         "unitIds": [unit_id]}}

    res = api.post_send_to_group(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']['name'] == group_name
    assert res.json_response['data']['totalUnits'] == 1
    assert res.json_response['data']['status'] == 'ACTIVE'

    time.sleep(10)
    unit_1 = get_unit_by_index(api, project_id, team_id, 0)

    assert unit_1['activeStatus'][0]['value'] == 'ACTIVE'
    assert unit_1['dataGroupName'][0]['value'] == group_name
    # assert unit_1['jobStatus'][0]['value'] == 'NEW'


def test_qf_post_remove_unit_group_to_data_group_valid(setup_segmented_project):
    '''
        1. query two unit groups in segmented project
        2. send two groups to a new data group
        3. remove all units from the data group
        4. delete the new created data group
    '''
    api = setup_segmented_project['api']
    team_id = setup_segmented_project['team_id']
    project_id = setup_segmented_project['default_segmented_project_id']
    group_name = 'test seg data group 1'

    # 1 query two units groups
    payload = {
        "pageSize": 50,
        "pageNum": 1,
        "query": "",
        "jobId": ""
    }
    res = api.post_segment_group_list(team_id=team_id, project_id=project_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response["data"]

    assert list(filter(lambda x: x['projectId'] != project_id, data['content'])) == []
    assert len(data['content']) == data['totalElements']

    unit_group_id_1 = res.json_response['data']['content'][0]['segmentGroupId']
    unit_group_id_2 = res.json_response['data']['content'][1]['segmentGroupId']

    # 2 send two units groups to a new data group
    payload = {"dataGroup": {"projectId": project_id,
                             "name": group_name},
               "units": {
                   "projectId": project_id,
                   "queryString": "",
                   "filterModel": {
                       "segmentGroupId": {
                           "values": [
                               unit_group_id_1,
                               unit_group_id_2
                           ],
                           "filterType": "SET"
                       }
                   }
               }
               }

    res = api.post_send_to_group(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']['name'] == group_name
    assert res.json_response['data']['totalUnits'] == 0
    assert res.json_response['data']['status'] == 'ACTIVE'
    data_group_id = res.json_response['data']['id']
    assert data_group_id is not None
    time.sleep(10)

    # 3 remove all units from the above data group
    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_remove_from_group(team_id=team_id, group_id=data_group_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    time.sleep(10)

    payload = {"startRow": 0,
               "endRow": 29,
               "filterModel": {
                   "segmentGroupId": {
                       "values": [
                           unit_group_id_1
                       ],
                       "filterType": "SET"
                   }
               },
               "sortModel": [],
               "queryString": ""}

    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    units = res.json_response['data']['units']
    assert units is not None
    for unitDataGroupId in units[0]['dataGroupId']:
        print("data group name list ==" + unitDataGroupId['value'])
        print("data group name list ==" + data_group_id)
        assert unitDataGroupId['value'] is not data_group_id
    time.sleep(5)

    # delete data group
    res = api.delete_data_group(project_id=project_id, team_id=team_id, group_id=data_group_id)
    assert res.status_code == 200



# -------------------------
# /project/data-group-list
# -------------------------

def test_qf_post_data_group_list_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    res = api.post_data_group_list(team_id=team_id, project_id=project_id, payload={})

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_data_group_list_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    res = api.post_data_group_list(team_id=team_id, project_id=project_id, payload={})
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.dependency(depends=["test_qf_post_send_to_group_valid"])
def test_qf_post_data_group_list_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    res = api.post_data_group_list(team_id=team_id, project_id=project_id, payload={})
    assert res.status_code == 200
    assert res.json_response['data']['content'][0]['name'] == 'test group data 1'
    assert res.json_response['data']['content'][0]['totalUnits'] == 1
    assert res.json_response['data']['content'][0]['status'] == 'ACTIVE'


# -------------------------
# /project/remove-from-group
# -------------------------
def test_qf_post_remove_to_group_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']
    group_id = 'kfehjklfklerjvf;eklr'

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_remove_from_group(team_id=team_id, group_id=group_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_remove_from_group_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']
    group_id = 'kfehjklfklerjvf;eklr'

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_remove_from_group(team_id=team_id, group_id=group_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.dependency(depends=["test_qf_post_send_to_group_valid"])
def test_qf_remove_to_group_valid(setup):
    # Bug?
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['id']

    #  find group id
    payload = {"startRow": 0, "endRow": 1, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200

    group_id = res.json_response['data']['units'][0]['dataGroupId'][0]['value']
    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}

    res = api.post_remove_from_group(team_id=team_id, group_id=group_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    payload = {"startRow": 0, "endRow": 1, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200


#     TODO add verification


# -------------------------
# /project/send-to-contributor
# -------------------------

def test_qf_post_sent_to_contributor_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": []}
    res = api.post_send_to_contributor(contributor_id="", job_id="", team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_send_to_contributor_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": []}
    res = api.post_send_to_contributor(contributor_id="", job_id="", team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == message


# def test_qf_post_sent_to_contributor_job_not_launched(setup):
#     api = setup['api']
#     project_id = setup['id']
#     team_id = setup['team_id']
#     unit_id = '95ead39e-bd21-45d5-8d3d-f98a53ae949e'
#     job_id = setup['jobs'][0]
#     contributor = setup['default_project']['curatedCrowd']['contributors'][0]['contributorId']
#
#     payload = {"projectId": project_id, "unitIds": [unit_id]}
#     res = api.post_send_to_contributor(contributor_id=contributor, job_id=job_id, team_id=team_id, payload=payload)
#     assert res.status_code == 200
#     assert res.json_response['message'] == 'Job should launch before send units to contributor.'


def test_qf_post_sent_to_contributor_job_valid(setup):
    api = setup['api']
    work_api = setup['work_api']
    project_id = setup['id']
    team_id = setup['team_id']
    job_id = setup['jobs'][0]

    contributor_id = setup['default_project']['curatedCrowd']['contributors'][0]['contributorId']
    contributor_name = setup['default_project']['curatedCrowd']['contributors'][0]['emailAddress']
    unit_id = get_unit_by_index(api, project_id, team_id, 1)['unitId'][0]['value']
    #
    # # update LAUNCH -> Crowd Settings
    # payload = {
    #     "id": job_id,
    #     "jobCrowd": {
    #         "crowdType": ["INTERNAL"]
    #     }
    # }
    # res = work_api.put_update_job_v2(team_id=team_id, payload=payload)
    # assert res.status_code == 200
    # assert res.json_response['data']['jobCrowd']['crowdType'] == ["INTERNAL"]
    #
    # # update launch config
    # payload = {"id": job_id,
    #            "judgmentsPerRow": "1",
    #            "rowsPerPage": 1,
    #            "assignmentLeaseExpiry": 1800,
    #            "payRateType": "",
    #            "invoiceStatisticsType": None,
    #            "allowAbandonUnits": "false",
    #            "allowSelfQa": "false",
    #            "maxJudgmentPerContributor": 0,
    #            "maxJudgmentPerContributorEnabled": "false"}
    #
    # res = work_api.put_update_job_v2(team_id=team_id, payload=payload)
    # assert res.status_code == 200
    # assert res.json_response['message'] == 'success'
    #
    # res = work_api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    # assert res.status_code == 200
    # time.sleep(5)
    #
    # payload = {"projectId": project_id, "unitIds": [unit_id], "percentage": 100}
    # res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload)
    # assert res.status_code == 200
    # time.sleep(5)
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')

    api_contributor = QualityFlowApiContributor()
    api_contributor.get_valid_sid(username, password)

    payload = {
        "projectId": project_id,
        "contributorIds": [contributor_id],
        "jobId": job_id
    }
    res = api_contributor.post_contributor_crowd_assign_job(team_id, payload)
    assert  res.status_code == 200

    # check contributors assigned to job
    payload = {
        "projectId": project_id,
        "contributorIds": [contributor_id]
    }
    res = api_contributor.post_contributor_crowd_batch_detail(team_id, payload)
    rsp = res.json_response

    assert rsp['code'] == 200
    payload = {"projectId": project_id, "unitIds": [unit_id]}

    res = api.post_send_to_contributor(contributor_id=contributor_id, job_id=job_id, team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert not res.json_response['data']['error']
    time.sleep(10)

    unit_data = get_unit_by_index(api, project_id, team_id, 1)
    assert unit_data["latest.workerEmail"][0]['value'] == contributor_name
    assert unit_data["latest.workerId"][0]['value'] == contributor_id


# -------------------------
# project/unit
# -------------------------

def test_qf_get_unit_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']
    units = setup['default_project']['units']

    res = api.get_unit(team_id=team_id, project_id=project_id, unit_id=units[0])

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_get_unit_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']
    units = setup['default_project']['units']

    res = api.get_unit(team_id=team_id, project_id=project_id, unit_id=units[0])
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Unauthorized'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Unauthorized')
])
def test_qf_get_unit_invalid_project_id(setup, name, project_id, message):
    api = setup['api']
    units = setup['default_project']['units']
    team_id = setup['team_id']

    res = api.get_unit(team_id=team_id, project_id=project_id, unit_id=units[0])
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_qf_get_unit_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']
    unit_id = setup['default_project']['units']

    res = api.get_unit(team_id=team_id, project_id=project_id, unit_id=unit_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'


# -------------------------
# /project/unit-commit-history
# -------------------------

def test_qf_get_unit_commit_history_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']
    units = setup['default_project']['units']

    res = api.get_unit_commit_history(team_id=team_id, project_id=project_id, unit_segment_id=units[0])

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_get_unit_commit_history_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']
    units = setup['default_project']['units']

    res = api.get_unit_commit_history(team_id=team_id, project_id=project_id, unit_segment_id=units[0])
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Unauthorized'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Unauthorized')
])
def test_qf_get_unit_commit_history_invalid_project_id(setup, name, project_id, message):
    api = setup['api']
    units = setup['default_project']['units']
    team_id = setup['team_id']

    res = api.get_unit_commit_history(team_id=team_id, project_id=project_id, unit_segment_id=units[0])
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_qf_get_unit_commit_history_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    # get units
    payload = {}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.status_code == 200

    units = [x['unitId'][0]['value'] for x in res.json_response['data']['units']]
    assert units, 'Units have not been found'

    for unit in units:
        res = api.get_unit_commit_history(team_id=team_id, project_id=project_id, unit_segment_id=unit)
        assert res.status_code == 200
        assert res.json_response['message'] == 'success'

        data = res.json_response['data']['unit']
        assert data['id'] == unit
        assert data['source']['what_is_greater_gold_reason'] == ""
        assert data['content']


# -------------------------
# /project/units-header
# -------------------------

def test_qf_get_units_header_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    res = api.get_units_header(team_id=team_id, project_id=project_id)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_get_units_header_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    res = api.get_units_header(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Unauthorized'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Unauthorized')
])
def test_qf_get_units_header_invalid_project_id(setup, name, project_id, message):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_units_header(team_id=team_id, project_id=project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_qf_get_units_header_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    res = api.get_units_header(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response["data"]
    assert data["columnDefs"][0]["headerName"] == "unit"
    assert list(filter(lambda x: x['group'] != 'unit', data["columnDefs"][0]['children'])) == []
    assert data["columnDefs"][0]['children'][0]['displayName'] == 'Unit ID'
    assert data["columnDefs"][0]['children'][0]['searchKey'] == 'unitDisplayId'
    assert data["columnDefs"][0]['children'][0]['filterType'] == 'text'

    assert data["columnDefs"][1]["headerName"] == "source"
    assert list(filter(lambda x: x['group'] != 'source', data["columnDefs"][1]['children'])) == []


# -------------------------
# /project/segment-group-list
# -------------------------
def test_qf_post_segment_group_list_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']
    payload = {}
    res = api.post_segment_group_list(team_id=team_id, project_id=project_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_segment_group_list_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {}
    res = api.post_segment_group_list(team_id=team_id, project_id=project_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Unauthorized'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Unauthorized')
])
def test_qf_post_segment_group_list_invalid_project_id(setup, name, project_id, message):
    api = setup['api']
    team_id = setup['team_id']

    payload = {}
    res = api.post_segment_group_list(team_id=team_id, project_id=project_id, payload=payload)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_qf_post_segment_group_list_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    payload = {
        "pageSize": 30,
        "pageNum": 1,
        "filterModel": {},
        "query": ""
    }
    res = api.post_segment_group_list(team_id=team_id, project_id=project_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response["data"]

    assert list(filter(lambda x: x['projectId'] != project_id, data['content'])) == []
    assert len(data['content']) == data['totalElements']


# -------------------------
# /project/delete-units
# -------------------------
def test_qf_post_delete_units_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": [""]}
    res = api.post_delete_units(team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_delete_units_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": [""]}
    res = api.post_delete_units(team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_qf_post_delete_units_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    payload = {"projectId": project_id, "unitIds": [""]}
    res = api.post_delete_units(team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


@pytest.mark.dependency()
def test_qf_post_delete_units_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    global unit1_id
    unit1_id = get_unit_by_index(api, project_id, team_id, 0)['unitId'][0]['value']

    payload = {"projectId": project_id, "unitIds": [unit1_id]}
    res = api.post_delete_units(team_id=team_id, payload=payload)

    assert res.status_code == 200
    assert res.json_response['message'] == 'success'


# -------------------------
# /project/inactive-units
# -------------------------
def test_qf_post_inactive_units_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {}
    res = api.post_inactive_units(project_id=project_id, team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_inactive_units_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {}
    res = api.post_inactive_units(project_id=project_id, team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_qf_post_inactive_units_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    payload = {}
    res = api.post_inactive_units(project_id=project_id, team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


@pytest.mark.dependency(depends=["test_qf_post_delete_units_valid"])
def test_qf_post_inactive_units_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    payload = {}
    res = api.post_inactive_units(project_id=project_id, team_id=team_id, payload=payload)

    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert len(res.json_response['data']['units']) == 1
    assert res.json_response['data']['units'][0]['activeStatus'][0]['value'] == 'INACTIVE'
    assert res.json_response['data']['units'][0]['unitId'][0]['value'] == unit1_id


# -------------------------
# /project/recover-units
# -------------------------

def test_qf_post_recover_units_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_recover_units(team_id=team_id, payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_recover_units_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_recover_units(team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_qf_post_recover_units_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_recover_units(team_id=team_id, payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


@pytest.mark.dependency(depends=["test_qf_post_delete_units_valid"])
def test_qf_post_recover_units_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    payload = {}
    res_inactive_units = api.post_inactive_units(project_id=project_id, team_id=team_id, payload=payload)
    inactive_units = res_inactive_units.json_response['data']['units']
    assert len(inactive_units) == 1

    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_recover_units(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    time.sleep(3)
    new_inactive_units = api.post_inactive_units(project_id=project_id, team_id=team_id, payload=payload)
    new_inactive_units = new_inactive_units.json_response['data']['units']
    assert new_inactive_units == []


# -------------------------
# /project/data-group
# -------------------------

def test_qf_delete_data_group_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']
    group_id = "ofije9fi89we8i"

    res = api.delete_data_group(team_id=team_id, project_id=project_id, group_id=group_id)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_delete_data_group_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']
    group_id = "ofije9fi89we8i"

    res = api.delete_data_group(team_id=team_id, project_id=project_id, group_id=group_id)

    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_qf_delete_data_group_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']
    group_id = "ofije9fi89we8i"

    res = api.delete_data_group(team_id=team_id, project_id=project_id, group_id=group_id)

    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_qf_delete_data_group_valid(setup):
    api = setup['api']
    project_id = setup['id']
    team_id = setup['team_id']

    # create data group
    unit_id = get_unit_by_index(api, project_id, team_id, 0)['unitId'][0]['value']

    current_group_res = api.post_data_group_list(team_id=team_id, project_id=project_id, payload={})
    assert current_group_res.status_code == 200
    count_current_groups = len(current_group_res.json_response['data']['content'])

    payload = {"dataGroup": {"projectId": project_id,
                             "name": "test group to delete"},
               "units": {"projectId": project_id,
                         "unitIds": [unit_id]}}

    res = api.post_send_to_group(team_id=team_id, payload=payload)
    assert res.status_code == 200
    group_id = res.json_response['data']['id']

    time.sleep(3)
    res = api.post_data_group_list(team_id=team_id, project_id=project_id, payload={})
    assert res.status_code == 200
    assert len(res.json_response['data']['content']) == count_current_groups + 1

    #  delete data group
    res = api.delete_data_group(team_id=team_id, project_id=project_id, group_id=group_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    time.sleep(3)

    res = api.post_data_group_list(team_id=team_id, project_id=project_id, payload={})
    assert res.status_code == 200
    assert len(res.json_response['data']['content']) == count_current_groups


# --------------------------------
# /project/remove-from-contributor
# --------------------------------

def test_qf_post_remove_from_contributor_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": []}
    res = api.post_remove_from_contributor(team_id=team_id, job_id="", payload=payload)

    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_qf_post_remove_from_contributor_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['id']

    payload = {"projectId": project_id, "unitIds": []}
    res = api.post_remove_from_contributor(team_id=team_id, job_id="", payload=payload)

    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_qf_post_unassign_unit_from_contributor_job_valid(setup):
    """
    Test un-assign unit from contributor in job
    Prepare steps:
        1. config and syncing settings with job
        2. set curated crowd in job and launch job
        3. send all units to job and assign all units to contributor
    Test steps:
        4. verify un-assign unit from contributor by unit_id success
        5. verify un-assign unit from contributor by filter and query success
    """
    api = setup['api']
    work_api = setup['work_api']
    contributor_api = setup['contributor_api']
    project_id = setup['id']
    team_id = setup['team_id']
    job_id = setup['jobs'][0]

    contributor_id = setup['default_project']['curatedCrowd']['contributors'][0]['contributorId']
    contributor_name = setup['default_project']['curatedCrowd']['contributors'][0]['emailAddress']
    unit_id = get_unit_by_index(api, project_id, team_id, 1)['unitId'][0]['value']
    ac_id = setup['default_project']['curatedCrowd']['ac_project_info']['AC_Project_2']['AC_Project_ID_2']
    job_filter = setup['default_project']['jobs']['filter']

    # 1. Config the job luanch settings
    payload = {"id": job_id,
               "jobCrowd": {
                   "crowdType": ["INTERNAL", "EXTERNAL"],
                   "crowdSubType": "APPEN_CONNECT"
               },
               "judgmentsPerRow": 1,
               "rowsPerPage": 5,
               "assignmentLeaseExpiry": 1800,
               "payRateType": "DEFAULT",
               "invoiceStatisticsType": "UNIT_COUNT",
               "allowAbandonUnits": "false",
               "allowSelfQa": "false",
               "maxJudgmentPerContributor": 0,
               "maxJudgmentPerContributorEnabled": "false"}

    res = work_api.put_update_job_v2(team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert res.status_code == 200
    assert res.json_response['data']['jobCrowd']['crowdType'] == ["INTERNAL", "EXTERNAL"]

    # 2. create AC syncing settings
    payload = {
        "projectId": project_id,
        "externalName": "APPEN_CONNECT",
        "externalProjectId": ac_id,
    }
    res = contributor_api.post_contributor_sync_setting_create(team_id, payload)
    rsp = res.json_response
    assert rsp.get('code') == 200
    data = rsp.get('data')
    res = contributor_api.put_contributor_sync_setting_update_effect(team_id, data)
    time.sleep(5)

    # 3. assign contributors to job
    res = contributor_api.post_contributor_crowd_assign_job(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "contributorIds": [contributor_id]
    })
    assert res.status_code == 200

    # 4. launch job
    res = work_api.post_launch_job_v2(team_id=team_id, job_id=job_id)
    assert res.status_code == 200
    data = rsp.get('data')
    assert data is not None
    time.sleep(5)

    # 5. send all units to job
    payload = {"projectId": project_id,
               "percentage": 100,
               "filterModel": {},
               "queryString": ""}
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['data']['total'] != 0
    time.sleep(10)

    # 6. assign all units to contributor
    payload = {"projectId": project_id, "filterModel": {}, "queryString": ""}
    res = api.post_send_to_contributor(contributor_id=contributor_id, job_id=job_id, team_id=team_id, payload=payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    assert not res.json_response['data']['error']
    time.sleep(10)

    # 7. verify unit's assign to contributor success
    res = api.post_units(project_id=project_id, team_id=team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {
            "jobId": {
                "filter": job_id,
                "filterType": "text",
                "type": "equals"
            }
        },
        "queryString": "",
        "sortModel": []
    })
    assert res.status_code == 200
    units_data = res.json_response.get('data').get('units')
    for unit in units_data:
        assert unit["latest.workerEmail"][0]['value'] == contributor_name
        assert unit["latest.workerId"][0]['value'] == contributor_id

    # 8. un-assign unit from contributor by unit_id and verify it execute success
    payload = {"projectId": project_id, "unitIds": [unit_id]}
    res = api.post_remove_from_contributor(team_id=team_id, job_id=job_id, payload=payload)
    assert res.status_code == 200
    time.sleep(5)

    worker_key = ["latest.workerEmail", "latest.workerId", "latest.workerExternalId"]
    unit_data = get_unit_by_index(api, project_id, team_id, 1)
    for key in worker_key:
        assert key not in unit_data

    # 9. un-assign unit from contributor by filter and query and verify it execute success
    res = api.post_remove_from_contributor(team_id=team_id, job_id=job_id, payload={
        "projectId": project_id,
        "filterModel": job_filter['filterModel_1'],
        "queryString": job_filter['queryString_1']
    })
    assert res.status_code == 200
    time.sleep(5)

    res = api.post_units(project_id=project_id, team_id=team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": job_filter['filterModel_1'],
        "queryString": job_filter['queryString_1'],
        "sortModel": []
    })
    assert res.status_code == 200
    units_data = res.json_response.get('data').get('units')
    for unit in units_data:
        for key in worker_key:
            assert key not in unit

# # TODO  /project/field-values
