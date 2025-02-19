"""
swagger - https://api-kepler.sandbox.cf3.us/contributor/swagger-ui/index.html#/
"""
from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
import pytest
import random
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
    api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project,
        "pre_defined_data": pre_defined_data
    }


def test_get_contributor_crowd_group_brief_list(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    team_id = setup['team_id']
    num_of_groups = len(pre_defined_data['qf_project_1']['sync_setting_3']['contributorGroups'])
    setting_id = pre_defined_data['qf_project_1']['sync_setting_3']['settingId']

    res = api.get_contributor_crowd_group_brief_list(project_id, team_id, setting_id)
    rsp = res.json_response

    assert rsp['code'] == 200
    assert len(rsp['data']) >= num_of_groups


def test_post_contributor_crowd_group_detail_list(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    team_id = setup['team_id']
    contributor_groups = pre_defined_data['qf_project_1']['sync_setting_3']['contributorGroups']
    contributor_group_name_random_selected = random.sample(contributor_groups.keys(), 1)[0]
    setting_id = pre_defined_data['qf_project_1']['sync_setting_3']['settingId']

    payload = {
        "pageNum": 1,
        "pageSize": 30,
        "descending": True,
        "orderBy": "name",
        "projectId": project_id,
        "query": contributor_group_name_random_selected,
        "settingId": setting_id
    }
    res = api.post_contributor_crowd_group_detail_list(team_id, payload)
    rsp = res.json_response

    assert rsp.get('code') == 200


@pytest.mark.parametrize("group_create_type", [
    "Empty",
    "With_Contributor_IDs",
    "With_Search_Criteria_filterModel",
    "With_Search_Criteria_Query_emailAddress",
    "With_Search_Criteria_Query_externalId"
])
def test_contributor_crowd_group_main_process(setup, group_create_type):
    """
    step 1. create a contributor group
    step 2. add crowd
    step 3. update the contributor group
    step 4. remove crowd
    step 5. delete the contributor group
    step 6. check group nonexistence
    """
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    team_id = setup['team_id']
    contributors = pre_defined_data['ac_project_info_3']['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    contributor_ids_selected_created = random.sample(contributor_ids, random.randint(0, len(contributor_ids)))
    contributor_info_random_selected = random.sample(contributors, 1)[0]
    filter_model_1 = pre_defined_data['ac_project_info_3']['filterModel_1']
    setting_id = pre_defined_data['qf_project_1']['sync_setting_3']['settingId']

    # step 1. create a contributor group
    group_name = f"Contributor Group {faker.zipcode()}"
    group_desc = f"{faker.text()}"
    payload = {
        "projectId": project_id,
        "name": group_name,
        "description": group_desc,
        "settingId": setting_id
    }
    if group_create_type == "With_Contributor_IDs":
        payload["contributorIds"] = contributor_ids_selected_created
    elif group_create_type.startswith("With_Search_Criteria"):
        if group_create_type == "With_Search_Criteria_filterModel":
            payload["filterModel"] = filter_model_1["filterModel"]
        elif group_create_type == "With_Search_Criteria_Query_emailAddress":
            payload["filterModel"] = {}
            payload["query"] = contributor_info_random_selected["emailAddress"]
        elif group_create_type == "With_Search_Criteria_Query_externalId":
            payload["filterModel"] = {}
            payload["query"] = contributor_info_random_selected["externalId"]
    res = api.post_contributor_crowd_group_create_with_condition(team_id, payload)
    rsp = res.json_response

    assert rsp["code"] == 200
    data = rsp.get('data')

    # check crowd list by group
    res = api.get_contributor_crowd_list_by_group(project_id, team_id, data['groupId'])
    rsp = res.json_response

    crowd_in_group = rsp.get('data')
    if group_create_type == "Empty":
        assert len(crowd_in_group) == 0
    elif group_create_type == "With_Contributor_IDs":
        assert len(crowd_in_group) == len(contributor_ids_selected_created)
    elif group_create_type == "With_Search_Criteria_filterModel":
        assert len(crowd_in_group) == len(filter_model_1["filterResult"])
    elif group_create_type.startswith("With_Search_Criteria_Query"):
        assert len(crowd_in_group) == 1

    # step 2. add crowd
    contributor_ids_in_group = [x["contributorInfo"]["contributorId"] for x in crowd_in_group]
    left_contributor_ids = [x for x in contributor_ids if x not in contributor_ids_in_group]
    left_size = len(left_contributor_ids)
    contributor_ids_random_selected = random.sample(left_contributor_ids, random.randint(0, left_size))
    payload = {
        "groupId": data['groupId'],
        "contributorIds": contributor_ids_random_selected,
        "projectId": project_id
    }
    res = api.post_contributor_crowd_group_add_crowd(team_id, payload)
    rsp = res.json_response

    assert rsp.get('code') == 200

    # check crowd list by group
    res = api.get_contributor_crowd_list_by_group(project_id, team_id, data['groupId'])
    rsp = res.json_response

    crowd_in_group = rsp.get('data')
    if group_create_type == "Empty":
        assert len(crowd_in_group) == len(contributor_ids_random_selected)
    elif group_create_type == "With_Contributor_IDs":
        assert len(crowd_in_group) == len(contributor_ids_random_selected) + len(contributor_ids_selected_created)
    elif group_create_type == "With_Search_Criteria_filterModel":
        assert len(crowd_in_group) == len(contributor_ids_random_selected) + len(filter_model_1["filterResult"])
    elif group_create_type.startswith("With_Search_Criteria_Query"):
        assert len(crowd_in_group) == len(contributor_ids_random_selected) + 1

    # step 3. update the contributor group
    payload = {
        "projectId": project_id,
        "name": group_name + f'_CHANGED_@{_today}',
        "description": group_desc + f'_CHANGED_@{_today}',
        "groupId": data['groupId']
    }
    res = api.put_contributor_crowd_group_update(team_id, payload)
    rsp = res.json_response

    assert rsp["code"] == 200

    # step 4. remove crowd
    contributor_ids_in_group = [x["contributorInfo"]["contributorId"] for x in crowd_in_group]
    cur_size = len(contributor_ids_in_group)
    contributor_ids_random_selected2 = random.sample(contributor_ids_in_group, random.randint(0, cur_size))
    payload = {
        "groupId": data['groupId'],
        "contributorIds": contributor_ids_random_selected2,
        "projectId": project_id
    }
    res = api.post_contributor_crowd_group_remove_crowd(team_id, payload)
    rsp = res.json_response

    assert rsp.get('code') == 200

    # check crowd list by group
    res = api.get_contributor_crowd_list_by_group(project_id, team_id, data['groupId'])
    rsp = res.json_response

    crowd_in_group = rsp.get('data')
    if group_create_type == "Empty":
        assert len(crowd_in_group) == len(contributor_ids_random_selected) - len(contributor_ids_random_selected2)
    elif group_create_type == "With_Contributor_IDs":
        assert len(crowd_in_group) == len(contributor_ids_random_selected) - len(contributor_ids_random_selected2)\
               + len(contributor_ids_selected_created)
    elif group_create_type == "With_Search_Criteria_filterModel":
        assert len(crowd_in_group) == len(contributor_ids_random_selected) - len(contributor_ids_random_selected2)\
               + len(filter_model_1["filterResult"])
    elif group_create_type.startswith("With_Search_Criteria_Query"):
        assert len(crowd_in_group) == len(contributor_ids_random_selected) - len(contributor_ids_random_selected2) + 1

    # step 5. delete the contributor group
    res = api.delete_contributor_crowd_group_delete(project_id, data['groupId'], team_id)
    rsp = res.json_response

    assert rsp["code"] == 200

    # step 6. check group nonexistence
    payload = {
        "pageNum": 1,
        "pageSize": 30,
        "descending": True,
        "orderBy": "name",
        "projectId": project_id,
        "query": data["name"],
        "settingId": setting_id
    }
    res = api.post_contributor_crowd_group_detail_list(team_id, payload)
    rsp = res.json_response

    assert rsp.get('code') == 200
    assert rsp.get('data').get('totalElements') == 0


def test_contributor_group_created_failed_due_to_duplicate_name(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    team_id = setup['team_id']
    contributor_groups = pre_defined_data['qf_project_1']['sync_setting_3']['contributorGroups']
    contributor_group_name_random_selected = random.sample(contributor_groups.keys(), 1)[0]
    contributors = pre_defined_data['ac_project_info_3']['contributors']
    contributor_ids = [x['contributorId'] for x in contributors]
    contributor_ids_selected_created = random.sample(contributor_ids, random.randint(0, len(contributor_ids)))
    contributor_info_random_selected = random.sample(contributors, 1)[0]
    filter_model_1 = pre_defined_data['ac_project_info_3']['filterModel_1']
    setting_id = pre_defined_data['qf_project_1']['sync_setting_3']['settingId']

    payload = {
        "projectId": project_id,
        "name": contributor_group_name_random_selected,
        "description": f"{faker.text()}" + "Duplicate one",
        "settingId": setting_id
    }
    sub_group_create_types = [
        "Empty",
        "With_Contributor_IDs",
        "With_Search_Criteria_filterModel",
        "With_Search_Criteria_Query_emailAddress",
        "With_Search_Criteria_Query_externalId",
    ]
    sub_group_create_type = sub_group_create_types[random.randint(0, len(sub_group_create_types) - 1)]
    if sub_group_create_type == "With_Contributor_IDs":
        payload["contributorIds"] = contributor_ids_selected_created
    elif sub_group_create_type.startswith("With_Search_Criteria"):
        if sub_group_create_type == "With_Search_Criteria_filterModel":
            payload["filterModel"] = filter_model_1["filterModel"]
        elif sub_group_create_type == "With_Search_Criteria_Query_emailAddress":
            payload["filterModel"] = {}
            payload["query"] = contributor_info_random_selected["emailAddress"]
        elif sub_group_create_type == "With_Search_Criteria_Query_externalId":
            payload["query"] = contributor_info_random_selected["externalId"]
    res = api.post_contributor_crowd_group_create_with_condition(team_id, payload)
    rsp = res.json_response

    assert rsp["code"] == 2002
    assert rsp['message'] == "[2002:Entity Exists]Group-Name already exists!!"


def test_contributor_group_updated_failed_due_to_duplicate_name(setup):
    api = setup['api']
    pre_defined_data = setup['pre_defined_data']
    project_id = pre_defined_data['qf_project_1']['projectId']
    team_id = setup['team_id']
    contributor_groups = pre_defined_data['qf_project_1']['sync_setting_3']['contributorGroups']
    contributor_group_name_random_selected = random.sample(contributor_groups.keys(), 1)[0]
    setting_id = pre_defined_data['qf_project_1']['sync_setting_3']['settingId']

    # step 1. create a contributor group
    group_name = f"Contributor Group {faker.zipcode()}"
    group_desc = f"{faker.text()}"
    payload = {
        "projectId": project_id,
        "name": group_name,
        "description": group_desc,
        "settingId": setting_id
    }
    res = api.post_contributor_crowd_group_create_with_condition(team_id, payload)
    rsp = res.json_response

    assert rsp["code"] == 200
    data = rsp.get('data')

    # step 2. update a contributor group with duplicate name
    payload = {
        "projectId": project_id,
        "name": contributor_group_name_random_selected,
        "description": f"{faker.text()}" + "Duplicate one",
        "groupId": data['groupId']
    }
    res = api.put_contributor_crowd_group_update(team_id, payload)
    rsp = res.json_response

    assert rsp["code"] == 2002
    assert rsp['message'] == "[2002:Entity Exists]Group-Name already exists!!"

    # step 3. delete the contributor group
    res = api.delete_contributor_crowd_group_delete(project_id, data['groupId'], team_id)
    rsp = res.json_response

    assert rsp["code"] == 200

    # step 4. check group nonexistence
    payload = {
        "pageNum": 1,
        "pageSize": 30,
        "descending": True,
        "orderBy": "name",
        "projectId": project_id,
        "query": data["name"],
        "settingId": setting_id
    }
    res = api.post_contributor_crowd_group_detail_list(team_id, payload)
    rsp = res.json_response

    assert rsp.get('code') == 200
    assert rsp.get('data').get('totalElements') == 0
