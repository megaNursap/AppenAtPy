"""
swagger - https://api-kepler.sandbox.cf3.us/contributor/swagger-ui/index.html#/
"""
import time

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


def test_post_contributor_sync_setting_create_invalid_ac_id(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    payload = {
        "projectId": project_id,
        "externalName": "APPEN_CONNECT",
        "externalProjectId": "0mvml",
        "syncType": "ALL"
    }
    res = api.post_contributor_sync_setting_create(team_id, payload)
    rsp = res.json_response
    assert rsp['code'] == 2103
    assert rsp['message'] == "[2103:Integration UNKNOWN ERROR]AC Project Not Found"


@pytest.mark.parametrize("criteria_type", [
    "Empty",
    "With_FilterModel",
    "With_Query_emailAddress",
    "With_Query_externalId",
    "With_Query_substring"
])
def test_post_contributor_crowd_main_criteria_search(setup, criteria_type):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    team_id = setup['team_id']
    filter_model = pre_defined_data['ac_project_info_3']['filterModel_1']['filterModel']
    contributor_info_random_selected = random.sample(pre_defined_data['ac_project_info_3']['filterModel_1']['filterResult'], 1)[0]
    ac_project_info = pre_defined_data['ac_project_info_3']
    setting_id = pre_defined_data['qf_project_1']['sync_setting_3']['settingId']

    payload = {
        "pageSize": 30,
        "pageNum": 1,
        "projectId": project_id,
        "filterModel": filter_model,
        "settingId": setting_id
    }
    if criteria_type == "Empty":
        payload["filterModel"] = {}
        res = api.post_contributor_crowd_criteria_search(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        assert rsp['data']['totalElements'] == ac_project_info['Number_of_Users_by_ALL']
    elif criteria_type == "With_FilterModel":
        res = api.post_contributor_crowd_criteria_search(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        assert rsp['data']['totalElements'] == ac_project_info['Number_of_Users_by_filter']
    elif criteria_type == "With_Query_emailAddress":
        payload["query"] = contributor_info_random_selected['emailAddress']
        res = api.post_contributor_crowd_criteria_search(team_id, payload)
        rsp = res.json_response
        assert rsp['data']['totalElements'] == ac_project_info['Number_of_Users_by_query_email']
    elif criteria_type == "With_Query_externalId":
        payload["query"] = contributor_info_random_selected['externalId']
        res = api.post_contributor_crowd_criteria_search(team_id, payload)
        rsp = res.json_response
        assert rsp['data']['totalElements'] == ac_project_info['Number_of_Users_by_query_id']
    else:
        payload["query"] = contributor_info_random_selected['externalId'][:3]
        res = api.post_contributor_crowd_criteria_search(team_id, payload)
        rsp = res.json_response
        assert rsp['data']['totalElements'] == ac_project_info['Number_of_Users_by_query_substring']

