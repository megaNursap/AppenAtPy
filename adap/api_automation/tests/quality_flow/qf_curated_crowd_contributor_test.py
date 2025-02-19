"""
swagger - https://api-kepler.sandbox.cf3.us/contributor/swagger-ui/index.html#/
"""
from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
import pytest
import random
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
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
    pre_defined_data = get_test_data('qf_user', 'curated_crowd_subject_api_test')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project,
        "pre_defined_data": pre_defined_data
    }


def test_get_contributor_crowd_list_by_group(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data["qf_project_1"]['projectId']
    team_id = setup['team_id']
    contributor_groups = pre_defined_data["qf_project_1"]["sync_setting_3"]['contributorGroups']
    group_name = random.sample(contributor_groups.keys(), 1)[0]
    group_id = contributor_groups[group_name]

    res = api.get_contributor_crowd_list_by_group(project_id, team_id, group_id)
    rsp = res.json_response

    assert rsp['code'] == 200


def test_post_contributor_crowd_list_by_criteria_search(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data["qf_project_1"]['projectId']
    team_id = setup['team_id']

    # step 1. get setting list
    res = api.get_contributor_sync_setting_list(team_id, project_id)
    rsp = res.json_response
    assert rsp.get('code') == 200
    data = rsp.get('data')

    # step 2. get setting detail for each setting
    for setting in data:
        payload = {
            "pageSize": 30,
            "pageNum": 1,
            "projectId": project_id,
            "filterModel": {},
            "query": "",
            "settingId": setting.get("settingId")
        }
        res = api.post_contributor_crowd_list_by_criteria_search(team_id, payload)
        rsp = res.json_response

        assert rsp['code'] == 200


def test_post_contributor_crowd_criteria_search(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data["qf_project_1"]['projectId']
    team_id = setup['team_id']

    # step 1. get setting list
    res = api.get_contributor_sync_setting_list(team_id, project_id)
    rsp = res.json_response
    assert rsp.get('code') == 200
    data = rsp.get('data')

    # step 2. get setting detail for each setting
    for setting in data:
        payload = {
            "pageSize": 30,
            "pageNum": 1,
            "projectId": project_id,
            "filterModel": {},
            "query": "",
            "settingId": setting.get("settingId")
        }
        res = api.post_contributor_crowd_criteria_search(team_id, payload)
        rsp = res.json_response

        assert rsp['code'] == 200


def test_post_contributor_crowd_batch_detail(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data["qf_project_1"]['projectId']
    contributors = pre_defined_data["ac_project_info_3"]['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    team_id = setup['team_id']

    payload = {
        "projectId": project_id,
        "contributorIds": contributor_ids
    }
    res = api.post_contributor_crowd_batch_detail(team_id, payload)
    rsp = res.json_response

    assert rsp['code'] == 200


def test_post_contributor_crowd_un_assign_job(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    contributors = pre_defined_data["ac_project_info_3"]['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    flow_1 = pre_defined_data['qf_project_1']['flow_1']
    job_ids = [x['job_id'] for x in flow_1]
    team_id = setup['team_id']
    for job_id in job_ids:
        contributor_ids_sample = random.sample(contributor_ids, random.randint(0, len(contributor_ids)))
        if contributor_ids_sample:
            # step 1. Randomly select contributors to assign to job 1
            payload = {
                "projectId": project_id,
                "contributorIds": contributor_ids_sample,
                "jobId": job_id
            }
            res = api.post_contributor_crowd_assign_job(team_id, payload)
            rsp = res.json_response
            assert rsp["code"] == 200

            res = api.post_contributor_crowd_batch_detail(team_id, payload={
                "projectId": project_id,
                "contributorIds": contributor_ids_sample
            })
            assert res.json_response['code'] == 200
            for data in res.json_response['data']:
                assert job_id in data["assignedJobs"]

        # Step 2. Un-assign contributors from job
        res = api.post_contributor_crowd_un_assign_job(team_id, payload={
            "projectId": project_id,
            "contributorIds": contributor_ids_sample,
            "jobId": job_id
        })
        if contributor_ids_sample:
            assert res.json_response["code"] == 200
            assert res.json_response["data"] == len(contributor_ids_sample)

            res = api.post_contributor_crowd_batch_detail(team_id, payload={
                "projectId": project_id,
                "contributorIds": contributor_ids_sample
            })
            assert res.json_response['code'] == 200
            for data in res.json_response['data']:
                assert job_id not in data["assignedJobs"]
        else:
            assert res.json_response["code"] == 1003
            assert res.json_response["message"] == "[1003:ILLEGAL_ARGUMENTS]contributors can't be empty"
            assert res.json_response["data"] is None

    # empty job
    res = api.post_contributor_crowd_un_assign_job(team_id, payload={
        "projectId": project_id,
        "contributorIds": contributor_ids,
        "jobId": ""
    })
    assert res.json_response["code"] == 1003
    assert res.json_response["message"] == "[1003:ILLEGAL_ARGUMENTS]jobId can't be blank"
    assert res.json_response["data"] is None


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'xxxxxxx')
])
def test_post_contributor_crowd_un_assign_job_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']
    pre_defined_data = setup['pre_defined_data']
    contributors = pre_defined_data["ac_project_info_3"]['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    flow_1 = pre_defined_data['qf_project_1']['flow_1']
    job_ids = [x['job_id'] for x in flow_1]
    job_id = random.sample(job_ids, 1)[0]
    res = api.post_contributor_crowd_un_assign_job(team_id, payload={
        "projectId": project_id,
        "contributorIds": contributor_ids,
        "jobId": job_id
    })
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'xxxxxxx', 'Access Denied')
])
def test_post_contributor_crowd_un_assign_job_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    contributors = pre_defined_data["ac_project_info_3"]['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    flow_1 = pre_defined_data['qf_project_1']['flow_1']
    job_ids = [x['job_id'] for x in flow_1]
    job_id = random.sample(job_ids, 1)[0]
    res = api.post_contributor_crowd_un_assign_job(team_id, payload={
        "projectId": project_id,
        "contributorIds": contributor_ids,
        "jobId": job_id
    })
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_post_contributor_crowd_un_assign_job_invalid_cookies(setup):
    api = QualityFlowApiContributor()
    team_id = setup['team_id']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    contributors = pre_defined_data["ac_project_info_3"]['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    flow_1 = pre_defined_data['qf_project_1']['flow_1']
    job_ids = [x['job_id'] for x in flow_1]
    job_id = random.sample(job_ids, 1)[0]
    res = api.post_contributor_crowd_un_assign_job(team_id, payload={
        "projectId": project_id,
        "contributorIds": contributor_ids,
        "jobId": job_id
    })
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


def test_contributor_assign_to_job_main_process(setup):
    """
    step 1. Randomly select contributors to assign to job 1
    step 2. Un-assign these contributors from both job 1
    Remarks: API /contributor/crowd/clone is deprecated since multi-AC is released
    """
    api = setup['api']
    team_id = setup['team_id']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    contributors = pre_defined_data["ac_project_info_3"]['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    flow_1 = pre_defined_data['qf_project_1']['flow_1']
    job_ids = [x['job_id'] for x in flow_1]
    contributor_ids_selected = random.sample(contributor_ids, random.randint(0, len(contributor_ids)))
    job_id_1 = random.sample(job_ids, 1)[0]
    left_job_ids = [x for x in job_ids if x != job_id_1]
    # job_id_2 = random.sample(left_job_ids, 1)[0]

    # precondition - data preparation
    for job_id in [job_id_1]:
        payload = {
            "projectId": project_id,
            "contributorIds": contributor_ids,
            "jobId": job_id
        }
        res = api.post_contributor_crowd_un_assign_job(team_id, payload)
        rsp = res.json_response

        assert rsp['code'] == 200
    # step 1. Randomly select contributors to assign to job 1
    payload = {
        "projectId": project_id,
        "contributorIds": contributor_ids_selected,
        "jobId": job_id_1
    }
    res = api.post_contributor_crowd_assign_job(team_id, payload)
    rsp = res.json_response

    if len(contributor_ids_selected) == 0:
        assert rsp['code'] in [1003, 1002]
        assert rsp['message'] == "[1003:ILLEGAL_ARGUMENTS]contributors can't be empty"
        return
    else:
        assert rsp['code'] == 200

    # check contributors assigned to job
    payload = {
        "projectId": project_id,
        "contributorIds": contributor_ids
    }
    res = api.post_contributor_crowd_batch_detail(team_id, payload)
    rsp = res.json_response

    assert rsp['code'] == 200
    for data in rsp['data']:
        contributor_id = data["contributorInfo"]["contributorId"]
        if contributor_id in contributor_ids_selected:
            assert job_id_1 in data["assignedJobs"]
        else:
            assert job_id_1 not in data["assignedJobs"]
    # # step 2. Copy contributors from job 1 to job 2
    # payload = {
    #     "copiedFrom": job_id_1,
    #     "teamId": team_id,
    #     "projectId": project_id,
    #     "jobId": job_id_2
    # }
    # res = api.post_contributor_crowd_clone(team_id, payload)
    # rsp = res.json_response
    #
    # assert rsp['code'] == 200
    #
    # # check contributors assigned to job
    # payload = {
    #     "projectId": project_id,
    #     "contributorIds": contributor_ids
    # }
    # res = api.post_contributor_crowd_batch_detail(team_id, payload)
    # rsp = res.json_response
    #
    # assert rsp['code'] == 200
    # for data in rsp['data']:
    #     contributor_id = data["contributorInfo"]["contributorId"]
    #     if contributor_id in contributor_ids_selected:
    #         assert job_id_1 in data["assignedJobs"]  and job_id_2 in data["assignedJobs"]
    #     else:
    #         assert job_id_1 not in data["assignedJobs"]   and job_id_2 not in data["assignedJobs"]

    # step 3. Un-assign these contributors from both job 1 and 2
    for job_id in [job_id_1]:
        payload = {
            "projectId": project_id,
            "contributorIds": contributor_ids_selected,
            "jobId": job_id
        }
        res = api.post_contributor_crowd_un_assign_job(team_id, payload)
        rsp = res.json_response

        assert rsp['code'] == 200

    # check contributors assigned to job
    payload = {
        "projectId": project_id,
        "contributorIds": contributor_ids
    }
    res = api.post_contributor_crowd_batch_detail(team_id, payload)
    rsp = res.json_response

    assert rsp['code'] == 200
    for data in rsp['data']:
        assert data["assignedJobs"] == []
