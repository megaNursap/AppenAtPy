import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor, QualityFlowApiWork, \
    QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_data_file

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]

contributor_email_1 = faker.email()
contributor_name_1 = faker.name()

contributor_email_2 = faker.email()
contributor_name_2 = faker.name()

contributor_email_3 = faker.email()
contributor_name_3 = faker.name()

icm_group_name = faker.name()
username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)
    app.driver.implicitly_wait(2)


@pytest.fixture(scope="module")
def setup():
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)
    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    project_name = f"automation project {_today} {faker.zipcode()}: copy job -ui"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    # create job
    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)
    payload = {"title": "New  WORK job",
               "teamId": team_id,
               "projectId": data['id'],
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "",
                       "css": "",
                       "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                       "instructions": "Test CML API update"}
               }

    res = job_api.post_create_job(team_id=team_id, payload=payload)
    assert res.status_code == 200

    print("project_id ", data['id'])
    print("job_id ", [res.json_response['data']['id']])

    return {
        "project_id": data['id'],
        "team_id": data['teamId'],
        "job_id": [res.json_response['data']['id']],
        "job_names": ['New  WORK job'],
        "project_name": project_name,
    }


@pytest.fixture(scope="module")
def contributors(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    print("icm_email[1] ", contributor_email_1)
    print("icm_email[2] ", contributor_email_2)
    print("icm_email[3] ", contributor_email_3)
    print("icm_name[1] ", contributor_name_1)
    print("icm_name[2] ", contributor_name_2)
    print("icm_name[3] ", contributor_name_3)

    res_1 = api.post_internal_contributor_create(email=contributor_email_1, name=contributor_name_1, team_id=team_id)
    assert res_1.status_code == 200

    res_2 = api.post_internal_contributor_create(email=contributor_email_2, name=contributor_name_2, team_id=team_id)
    assert res_2.status_code == 200

    res_3 = api.post_internal_contributor_create(email=contributor_email_3, name=contributor_name_3, team_id=team_id)
    assert res_3.status_code == 200

    return {
        "contributor_email_1": contributor_email_1,
        "contributor_name_1": contributor_name_1,
        "contributor_email_2": contributor_email_2,
        "contributor_name_2": contributor_name_2,
        "contributor_email_3": contributor_email_3,
        "contributor_name_3": contributor_name_3
    }


@pytest.fixture(scope="module")
def new_contributor_group(app, contributors):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    res_1 = api.post_search_contributor_by_name(name=contributors['contributor_email_1'], team_id=team_id)
    res_2 = api.post_search_contributor_by_name(name=contributors['contributor_email_2'], team_id=team_id)
    res_3 = api.post_search_contributor_by_name(name=contributors['contributor_email_3'], team_id=team_id)

    response_1 = res_1.json_response
    assert res_1.status_code == 200

    response_2 = res_2.json_response
    assert res_2.status_code == 200

    response_3 = res_3.json_response
    assert res_3.status_code == 200

    print("contributor_id_1 ", response_1.get("data").get("list")[0].get("id"))
    print("contributor_id_2 ", response_2.get("data").get("list")[0].get("id"))
    print("contributor_id_3 ", response_3.get("data").get("list")[0].get("id"))

    print("icm_group_name ", icm_group_name)
    print("team_id ", team_id)

    contributor_id_1 = response_1.get("data").get("list")[0].get("id")
    contributor_id_2 = response_2.get("data").get("list")[0].get("id")
    contributor_id_3 = response_3.get("data").get("list")[0].get("id")

    res = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name,
                                                          contributor_ids=[contributor_id_1, contributor_id_2,
                                                                           contributor_id_3],
                                                          team_id=team_id)
    assert res.status_code == 200
    group_id = res.json_response.get('data')[0].get('groupId')
    print("group_id ", group_id)

    return {
        "group_id": group_id,
        "group_name": icm_group_name,
    }


@pytest.fixture(scope="module")
def assign_group_to_job(app, setup, new_contributor_group):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    print("project_id ", setup['project_id'])
    print("job_id ", setup['job_id'])
    print("project_id ", [new_contributor_group['group_id']])

    res = api.post_assign_contributor_group_to_job(project_id=setup['project_id'],
                                                   job_id=setup['job_id'][0],
                                                   group_ids=[new_contributor_group['group_id']],
                                                   team_id=team_id)
    print("post_assign_contributor_group_to_job", res.json_response)
    assert res.status_code == 200


@pytest.fixture(scope="module")
def upload_dataset(setup):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_id = setup['project_id']
    dataset_id = '00000000-0000-0000-0000-000000000000'

    res = api.get_upload_dataset(project_id=project_id, team_id=team_id, dataset_id=dataset_id)
    assert res.status_code == 200
    time.sleep(5)


@pytest.fixture(scope="module")
def send_units_to_job(setup):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_id = setup['project_id']

    res = api.post_units(project_id=project_id, team_id=team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {
            "jobStatus": {
                "values": ["NEW"],
                "filterType": "set"
            }
        },
        "sortModel": [],
        "queryString": ""
    })
    assert res.json_response['code'] == 200
    time.sleep(2)

    unit_id_1 = res.json_response['data']['units'][0]['unitId'][0]['value']
    unit_id_2 = res.json_response['data']['units'][1]['unitId'][0]['value']
    unit_id_3 = res.json_response['data']['units'][2]['unitId'][0]['value']
    unit_id_4 = res.json_response['data']['units'][3]['unitId'][0]['value']

    unit_display_id_1 = res.json_response['data']['units'][0]['unitDisplayId'][0]['value']
    unit_display_id_2 = res.json_response['data']['units'][1]['unitDisplayId'][0]['value']
    unit_display_id_3 = res.json_response['data']['units'][2]['unitDisplayId'][0]['value']
    unit_display_id_4 = res.json_response['data']['units'][3]['unitDisplayId'][0]['value']

    print("unit_id_1 ", unit_id_1)
    print("unit_id_2 ", unit_id_2)
    print("unit_id_3 ", unit_id_3)
    print("unit_id_4 ", unit_id_4)

    print("unit_display_id_1 ", unit_display_id_1)
    print("unit_display_id_2 ", unit_display_id_2)
    print("unit_display_id_3 ", unit_display_id_3)
    print("unit_display_id_4 ", unit_display_id_4)

    res = api.post_job_preview_v2(setup['job_id'][0], team_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # res = api.post_launch_job_v2(job_id=work_job['job_id'], team_id=team_id)
    # assert res.status_code == 200

    # Send unit to job
    payload = {"projectId": project_id,
               "unitIds": [unit_id_1, unit_id_2, unit_id_3, unit_id_4],
               "percentage": 100,
               "sendEntireGroup": "false",
               "carryJudgment": "true",
               "overwriteJudgment": "true"}
    res = api.post_send_to_job(job_id=setup['job_id'][0], team_id=team_id, payload=payload)
    print("res.json_response ", res.json_response)
    assert res.json_response['code'] == 200
    assert res.json_response['message'] == 'success'
    time.sleep(2)

    return {
        "unit_id_1": unit_display_id_1,
        "unit_id_2": unit_display_id_2,
        "unit_id_3": unit_display_id_3,
        "unit_id_4": unit_display_id_4
    }


@pytest.mark.regression_qf
def test_assign_one_unit_to_one_contributor(app, setup, assign_group_to_job, upload_dataset,
                                            send_units_to_job, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_data_page_by_project_id_and_job_id(project_id, job_id)
    app.quality_flow.job.data.select_units_checkbox_by_unit_ids([send_units_to_job['unit_id_1']])
    app.quality_flow.job.data.click_actions_menu('Assign Selected Units to Contributor(s)')
    app.quality_flow.job.data.assign_selected_units_to_contributors([contributor_email_1])
    app.navigation.refresh_page()
    all_units = app.quality_flow.job.data.get_all_units_on_page()
    assert all_units.iloc[0, 7] == 'ASSIGNED'
    assert all_units.iloc[0, 8] == contributor_email_1
    assert all_units.iloc[0, 11] == 'ASSIGNED'
    assert all_units.iloc[0, 12] == contributor_email_1
    assert all_units.iloc[0, 14] == 'ASSIGNED'
    assert all_units.iloc[0, 15] == contributor_email_1

    assert (all_units.iloc[0] == 'ASSIGNED').sum() == 3
    assert (all_units.iloc[0] == contributor_email_1).sum() == 3

    app.quality_flow.job.data.select_units_checkbox_by_unit_ids([send_units_to_job['unit_id_1']])
    app.quality_flow.job.data.click_actions_menu('Unassign Selected Units from Contributor(s)')
    time.sleep(2)
    app.navigation.refresh_page()
    all_units = app.quality_flow.job.data.get_all_units_on_page()

    assert (all_units.iloc[0] == 'ASSIGNED').sum() == 0
    assert (all_units.iloc[0] == contributor_email_1).sum() == 0


@pytest.mark.regression_qf
def test_assign_one_unit_to_multiple_contributor(app, setup, assign_group_to_job, upload_dataset,
                                                 send_units_to_job, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_data_page_by_project_id_and_job_id(project_id, job_id)
    app.quality_flow.job.data.select_units_checkbox_by_unit_ids([send_units_to_job['unit_id_1']])
    app.quality_flow.job.data.click_actions_menu('Assign Selected Units to Contributor(s)')
    app.quality_flow.job.data.assign_selected_units_to_contributors(
        [contributor_email_1, contributor_email_2, contributor_email_3])
    app.quality_flow.job.data.validate_ui_elements_of_assign_selected_units_to_contributors_popup()


@pytest.mark.regression_qf
def test_assign_multiple_units_to_one_contributor(app, setup, assign_group_to_job, upload_dataset,
                                                  send_units_to_job, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_data_page_by_project_id_and_job_id(project_id, job_id)
    app.quality_flow.job.data.select_units_checkbox_by_unit_ids(
        [send_units_to_job['unit_id_2'], send_units_to_job['unit_id_3'], send_units_to_job['unit_id_4']])
    app.quality_flow.job.data.click_actions_menu('Assign Selected Units to Contributor(s)')
    app.quality_flow.job.data.validate_ui_elements_of_assign_selected_units_to_contributors_popup()
    app.quality_flow.job.data.assign_selected_units_to_contributors([contributor_email_2])
    app.navigation.refresh_page()
    all_units = app.quality_flow.job.data.get_all_units_on_page()

    assert (all_units.iloc[1] == 'ASSIGNED').sum() == 3
    assert (all_units.iloc[1] == contributor_email_2).sum() == 3
    assert (all_units.iloc[2] == 'ASSIGNED').sum() == 3
    assert (all_units.iloc[2] == contributor_email_2).sum() == 3
    assert (all_units.iloc[3] == 'ASSIGNED').sum() == 3
    assert (all_units.iloc[3] == contributor_email_2).sum() == 3


@pytest.mark.regression_qf
def test_assign_multiple_units_to_multiple_contributors(app, setup, assign_group_to_job, upload_dataset,
                                                        send_units_to_job, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_data_page_by_project_id_and_job_id(project_id, job_id)
    app.quality_flow.job.data.select_units_checkbox_by_unit_ids(
        [send_units_to_job['unit_id_2'], send_units_to_job['unit_id_3'], send_units_to_job['unit_id_4']])
    app.quality_flow.job.data.click_actions_menu('Assign Selected Units to Contributor(s)')
    app.quality_flow.job.data.assign_selected_units_to_contributors(
        [contributor_email_1, contributor_email_2, contributor_email_3])
    app.quality_flow.job.data.validate_ui_elements_of_assign_selected_units_to_contributors_popup()
