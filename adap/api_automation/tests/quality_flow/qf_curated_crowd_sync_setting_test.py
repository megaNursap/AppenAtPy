"""
swagger - https://api-kepler.sandbox.cf3.us/contributor/swagger-ui/index.html#/
"""
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.services_config.quality_flow import QualityFlowApiWork
from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
import pytest
import time
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
import logging

logger = logging.getLogger('faker')
logger.setLevel(logging.INFO)  # Quiet faker locale messages down in tests.

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
    pre_defined_data = get_test_data('qf_user', 'curated_crowd_subject_api_test')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiContributor()
    cookies = api.get_valid_sid(username, password)
    api_prj = QualityFlowApiProject()
    api_prj.cookies = cookies
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api_prj": api_prj,
        "api": api,
        "default_project": default_project,
        "pre_defined_data": pre_defined_data
    }


@pytest.fixture(scope="module")
def create_new_project(setup):
    api = setup['api_prj']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()} for contributor sync setting test"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    return {
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version']
    }


@pytest.mark.skip(reason="Deprecated after multiple-AC is released")
def test_get_contributor_sync_setting_external_user_group(setup):
    api = setup['api']
    project = setup["default_project"]
    project_id = project['id']
    team_id = setup['team_id']

    res = api.get_contributor_sync_setting_external_user_group(project_id, team_id)
    assert res.json_response["code"] == 200


@pytest.mark.skip(reason="Deprecated after multiple-AC is released")
def test_get_contributor_sync_setting_external_locale(setup):
    api = setup['api']
    project = setup["default_project"]
    project_id = project['id']
    team_id = setup['team_id']

    res = api.get_contributor_sync_setting_external_locale(project_id, team_id)
    assert res.json_response["code"] == 200


def test_get_contributor_sync_setting_detail(setup):
    api = setup['api']
    project = setup["default_project"]
    project_id = project['id']
    team_id = setup['team_id']

    # step 1. get setting list
    res = api.get_contributor_sync_setting_list(team_id, project_id)
    rsp = res.json_response
    assert rsp.get('code') == 200
    data = rsp.get('data')

    # step 2. get setting detail for each setting
    for setting in data:
        res = api.get_contributor_sync_setting_detail(team_id, setting.get("settingId"))
        assert res.json_response["code"] == 200


def test_get_contributor_sync_setting_pay_rate_list_valid(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    project_id = put["projectId"]
    job_id = put["flow_1"][0]["job_id"]
    ref_sync_setting = put["flow_1"][0]["ref_sync_setting"]
    ref_ac_project_info = put[ref_sync_setting]["ref_ac_project_info"]
    team_id = setup['team_id']
    pay_rate_list = pre_defined_data[ref_ac_project_info]["pay_rates_info"]
    res = api.get_contributor_sync_setting_pay_rate_list(project_id, team_id, job_id)
    assert res.json_response["code"] == 200
    for data in res.json_response["data"]["payRates"]:
        assert data["label"] in pay_rate_list
        assert data["value"] in pay_rate_list


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'xxxxxxx'),
    ('other project', '92a20408-3b47-4cd6-99d1-0e1e079bbb17')
])
def test_get_contributor_sync_setting_pay_rate_list_invalid_project_id(setup, name, project_id):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    job_id = put["flow_1"][0]["job_id"]
    team_id = setup['team_id']
    res = api.get_contributor_sync_setting_pay_rate_list(project_id, team_id, job_id)
    assert res.status_code == 203
    assert res.json_response["code"] == 9001
    assert res.json_response['message'] == 'Unauthorized'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'xxxxxxx', 'Access Denied'),
    ('other user', 'ba738f62-debe-43fd-adc9-507ce7f335d9', 'Access Denied')
])
def test_get_contributor_sync_setting_pay_rate_list_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    project_id = put["projectId"]
    job_id = put["flow_1"][0]["job_id"]
    res = api.get_contributor_sync_setting_pay_rate_list(project_id, team_id, job_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_contributor_sync_setting_pay_rate_list_invalid_cookies(setup):
    api = QualityFlowApiContributor()
    team_id = setup['team_id']
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    project_id = put["projectId"]
    job_id = put["flow_1"][0]["job_id"]
    res = api.get_contributor_sync_setting_pay_rate_list(project_id, team_id, job_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


def test_get_contributor_sync_setting_non_existing_external_project_check_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    res = api.get_contributor_sync_setting_external_project_check(team_id, 999999)
    assert res.json_response["code"] == 2103
    assert res.json_response["message"] == "[2103:Integration UNKNOWN ERROR]AC Project Not Found"


def test_get_contributor_sync_setting_external_project_check_invalid_cookies():
    api = QualityFlowApiContributor()
    res = api.get_contributor_sync_setting_external_project_check(None, 999999)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


def test_get_contributor_sync_setting_detail_by_job_valid(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    project_id = put["projectId"]
    job_id_1 = put["flow_1"][0]["job_id"]
    ref_sync_setting_1 = put["flow_1"][0]["ref_sync_setting"]
    setting_id_1 = put[ref_sync_setting_1]["settingId"]
    job_id_2 = put["flow_1"][1]["job_id"]
    ref_sync_setting_2 = put["flow_1"][1]["ref_sync_setting"]
    setting_id_2 = put[ref_sync_setting_2]["settingId"]
    team_id = setup['team_id']

    res = api.get_contributor_sync_setting_detail_by_job(team_id, project_id, job_id_1)
    rsp = res.json_response
    assert rsp.get('code') == 200
    assert rsp.get('data').get('settingId') == setting_id_1

    res = api.get_contributor_sync_setting_detail_by_job(team_id, project_id, job_id_2)
    rsp = res.json_response
    assert rsp.get('code') == 200
    assert rsp.get('data').get('settingId') == setting_id_2


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'xxxxxxx', 'Access Denied'),
    ('other user', 'ba738f62-debe-43fd-adc9-507ce7f335d9', 'Access Denied')
])
def test_get_contributor_sync_setting_detail_by_job_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    project_id = put["projectId"]
    job_id_1 = put["flow_1"][0]["job_id"]
    ref_sync_setting_1 = put["flow_1"][0]["ref_sync_setting"]
    setting_id_1 = put[ref_sync_setting_1]["settingId"]

    res = api.get_contributor_sync_setting_detail_by_job(team_id, project_id, job_id_1)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_get_contributor_sync_setting_detail_by_job_invalid_cookies(setup):
    api = QualityFlowApiContributor()
    pre_defined_data = setup['pre_defined_data']
    put = pre_defined_data["qf_project_1"]
    project_id = put["projectId"]
    job_id_1 = put["flow_1"][0]["job_id"]
    team_id = setup['team_id']

    res = api.get_contributor_sync_setting_detail_by_job(team_id, project_id, job_id_1)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('sync_type', [
    'ALL',
    'BY_LOCALE',
    'BY_GROUP'
])
def test_contributor_sync_setting_main_process(setup, create_new_project, sync_type):
    """
    step 1. Create a new QF project
    step 2. Check external AC project
    step 3. Create effect: Select sync type and Click 'Save And Add Project'
    step 4. Check setting list
    step 5. Polling until setting saved and ac users synced
    step 6. Expect the number of users are equivalent to AC project's
    step 7. Update setting after modification if sync_type is BY_LOCALE
    step 8. Refresh to sync
    step 9. Polling until setting saved and ac users synced
    step 10. Create a leading WORK job and link this job to above sync setting
    """
    api = setup['api']
    team_id = setup['team_id']
    pre_defined_data = setup['pre_defined_data']
    ac_project_info_1 = pre_defined_data['ac_project_info_1']
    ac_project_info_2 = pre_defined_data['ac_project_info_2']
    ac_id = ac_project_info_1['AC_Project_ID']
    ac_name = ac_project_info_1['AC_Project_Name']
    num_of_ac_users = ac_project_info_1['Number_of_Users_by_ALL']
    ac_id_1 = ac_project_info_2['AC_Project_ID']
    ac_name_1 = ac_project_info_2['AC_Project_Name']
    num_of_ac_users_1 = ac_project_info_2['Number_of_Users_by_ALL']
    if sync_type == 'BY_LOCALE':
        num_of_ac_users = ac_project_info_1['Number_of_Users_by_Locale']['number_of_users']
        num_of_ac_users_after_sync_setting_modified = \
            ac_project_info_1['Number_of_Users_by_Locale_Modified']['number_of_users']
    if sync_type == 'BY_GROUP':
        num_of_ac_users = ac_project_info_1['Number_of_Users_by_Group']['number_of_users']

    # step 1. Create a new QF project
    project_id = create_new_project['id']

    # step 2. Check external AC project
    res = api.get_contributor_sync_setting_external_project_check(team_id, ac_id, external_source=None)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]["externalProjectId"] == ac_id

    # step 3. Create effect: Select sync type and Click 'Save And Add Project'
    payload = {
        "projectId": project_id,
        "externalProjectId": ac_id,
        "syncType": sync_type
    }
    if sync_type == 'BY_LOCALE':
        payload['locales'] = ac_project_info_1['Number_of_Users_by_Locale']['locales']
    if sync_type == 'BY_GROUP':
        payload['userGroups'] = ac_project_info_1['Number_of_Users_by_Group']['groups']

    res = api.post_contributor_sync_setting_create_effect(team_id, payload)
    rsp = res.json_response

    assert rsp.get('code') == 200
    assert rsp.get('message') == "success"
    data = rsp.get('data')
    assert data.get('batchjobId') is not None
    assert data.get('extInfo') is not None
    assert data.get('externalName') == "APPEN_CONNECT"
    assert data.get('externalProjectId') == ac_id
    assert data.get('externalProjectName') == ac_name
    assert data.get('lastSynced') is None
    assert data.get('projectId') == project_id
    assert data.get('settingId') is not None
    setting_id = data.get('settingId')
    assert data.get('statsBatchjobId') is not None
    assert data.get('status') == "ACTIVE"
    assert data.get('syncType') == sync_type
    if sync_type == 'ALL':
        assert data.get('locales') == {}
        assert data.get('userGroups') == {}
    if sync_type == 'BY_LOCALE':
        assert data.get('locales') == ac_project_info_1['Number_of_Users_by_Locale']['locales']
        assert data.get('userGroups') == {}
    if sync_type == 'BY_GROUP':
        assert data.get('locales') == {}
        assert data.get('userGroups') == ac_project_info_1['Number_of_Users_by_Group']['groups']

    # step 4. Check setting list
    res = api.get_contributor_sync_setting_list(team_id, project_id)
    rsp = res.json_response
    assert rsp.get('code') == 200
    data = rsp.get('data')
    sync_settings = [x.get("settingId") for x in data]
    assert setting_id in sync_settings

    # step 5. Polling until ac users synced
    MAX_LOOP = 30
    count = 0
    while True:
        count += 1
        res = api.get_contributor_sync_setting_detail(team_id, setting_id)
        rsp = res.json_response

        last_synced = rsp.get('data').get('lastSynced')
        if count > MAX_LOOP or last_synced is not None:
            break
        else:
            time.sleep(3)

    assert last_synced is not None

    # step 6. Expect the number of users are equivalent to AC project's
    payload_criteria_search = {
        "pageSize": 30,
        "pageNum": 1,
        "projectId": project_id,
        "filterModel": {},
        "query": "",
        "settingId": setting_id
    }
    res = api.post_contributor_crowd_criteria_search(team_id, payload_criteria_search)
    rsp = res.json_response

    assert rsp.get('data').get('totalElements') == num_of_ac_users

    # step 7. Update setting after modification if sync_type is BY_LOCALE
    if sync_type == 'BY_LOCALE':
        payload['settingId'] = setting_id
        payload['locales'] = ac_project_info_1['Number_of_Users_by_Locale_Modified']['locales']
        res = api.put_contributor_sync_setting_update(team_id, payload)
        rsp = res.json_response

        assert rsp.get('code') == 200
        assert rsp.get('message') == "success"
        data = rsp.get('data')
        assert data.get('batchjobId') is not None
        assert data.get('extInfo') is not None
        assert data.get('externalName') == "APPEN_CONNECT"
        assert data.get('externalProjectId') == ac_id
        assert data.get('externalProjectName') == ac_name
        assert data.get('lastSynced') is not None
        assert data.get('locales') == ac_project_info_1['Number_of_Users_by_Locale_Modified']['locales']
        assert data.get('userGroups') == {}
        assert data.get('projectId') == project_id
        assert data.get('settingId') is not None
        assert data.get('statsBatchjobId') is not None
        assert data.get('status') == "ACTIVE"
        assert data.get('syncType') == sync_type

        # step 8. Refresh to sync
        res = api.post_contributor_sync_setting_refresh(project_id, team_id, setting_id)
        rsp = res.json_response

        assert rsp.get('code') == 200
        assert rsp.get('message') == "success"
        data = rsp.get('data')
        assert data.get('batchjobId') is not None
        assert data.get('extInfo') is not None
        assert data.get('externalName') == "APPEN_CONNECT"
        assert data.get('externalProjectId') == ac_id
        assert data.get('externalProjectName') == ac_name
        assert data.get('lastSynced') is not None
        assert data.get('locales') == ac_project_info_1['Number_of_Users_by_Locale_Modified']['locales']
        assert data.get('userGroups') == {}
        assert data.get('projectId') == project_id
        assert data.get('settingId') is not None
        assert data.get('statsBatchjobId') is not None
        assert data.get('status') == "ACTIVE"
        assert data.get('syncType') == sync_type

        # step 9. Polling until setting saved and ac users synced
        MAX_LOOP = 30
        count = 0
        while True:
            count += 1
            res = api.post_contributor_crowd_criteria_search(team_id, payload_criteria_search)
            rsp = res.json_response

            cur_num_of_users = rsp.get('data').get('totalElements')
            if count > MAX_LOOP or cur_num_of_users == num_of_ac_users_after_sync_setting_modified:
                break
            else:
                time.sleep(3)

        assert cur_num_of_users == num_of_ac_users_after_sync_setting_modified,\
            "More users are not synced after sync setting is modified"

    # step 10. Create a leading WORK job and link this job to above sync setting
    api_work = QualityFlowApiWork()
    api_work.set_cookies(api.cookies)
    res = api_work.post_create_job_v2(team_id=team_id, payload={
        "title": f"WORK JOB - {faker.zipcode()}",
        "teamId": team_id,
        "projectId": project_id,
        "type": "WORK"})
    assert res.json_response["code"] == 200
    job_id = res.json_response['data']['id']

    res = api.get_contributor_sync_setting_detail_by_job(team_id, project_id, job_id)
    rsp = res.json_response
    assert rsp.get('code') == 2001
    assert rsp.get('message') == "[2001:Entity Not Found]No Such Job-SyncSetting!"
    assert rsp.get('data') is None

    res = api.post_contributor_sync_setting_job_link(team_id, {
            "projectId": project_id,
            "jobId": job_id,
            "settingId": setting_id
        })
    assert res.json_response['code'] == 200

    res = api.get_contributor_sync_setting_detail_by_job(team_id, project_id, job_id)
    rsp = res.json_response
    assert rsp.get('code') == 200
    assert rsp.get('data').get('settingId') == setting_id
