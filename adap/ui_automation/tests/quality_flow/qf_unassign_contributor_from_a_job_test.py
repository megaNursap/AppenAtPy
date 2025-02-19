import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor, QualityFlowApiWork, \
    QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]
icm_email = faker.email()
icm_name = faker.name()
icm_group_name = faker.name()

contributor_email_1 = faker.email()
contributor_name_1 = faker.name()

contributor_email_2 = faker.email()
contributor_name_2 = faker.name()

contributor_email_3 = faker.email()
contributor_name_3 = faker.name()

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

    return {
        "project_id": data['id'],
        "team_id": data['teamId'],
        "job_id": [res.json_response['data']['id']],
        "job_names": ['New  WORK job'],
        "project_name": project_name,
    }


@pytest.fixture(scope="module")
def new_contributor(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    res = api.post_internal_contributor_create(email=icm_email, name=icm_name, team_id=team_id)
    assert res.status_code == 200


@pytest.fixture(scope="module")
def contributors(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

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

    return {
        "contributor_email_1": contributors['contributor_email_1'],
        "contributor_name_1": contributors['contributor_name_1'],
        "contributor_email_2": contributors['contributor_email_2'],
        "contributor_name_2": contributors['contributor_name_2'],
        "contributor_email_3": contributors['contributor_email_3'],
        "contributor_name_3": contributors['contributor_name_3']
    }


@pytest.mark.regression_qf
def test_remove_a_single_contributor(app, setup, new_contributor, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')
    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup(icm_email)
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(icm_email)
    app.quality_flow.job.setting.remove_contributor_from_current_job(icm_email)
    app.quality_flow.job.setting.validate_ui_elements_in_remove_contributor_tab()
    app.quality_flow.job.setting.confirm_to_remove_contributor()
    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(icm_email)


@pytest.mark.regression_qf
def test_remove_multiple_contributors(app, setup, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')

    contributor_1 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(1)
    contributor_2 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(2)
    contributor_3 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(3)

    app.quality_flow.job.setting.select_multiple_contributor_checkboxes_from_assign_contributor_popup(3)
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')

    app.quality_flow.job.setting.select_checkboxes_by_contributor_email([contributor_1, contributor_2, contributor_3])

    app.quality_flow.job.setting.click_actions_menu('Remove')
    app.quality_flow.job.setting.confirm_to_remove_contributor()

    app.navigation.refresh_page()

    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(contributor_1)
    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(contributor_2)
    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(contributor_3)


@pytest.mark.regression_qf
def test_remove_contributors_after_adding_from_a_group(app, setup, new_contributor_group, qf_login):
    project_id = setup['project_id']
    job_id = setup['job_id'][0]

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('Contributor Groups')
    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup(icm_group_name)
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')

    app.quality_flow.job.setting.select_checkboxes_by_contributor_email([
        new_contributor_group['contributor_email_1'],
        new_contributor_group['contributor_email_2'],
        new_contributor_group['contributor_email_3']])

    app.quality_flow.job.setting.click_actions_menu('Remove')
    app.quality_flow.job.setting.confirm_to_remove_contributor()

    app.navigation.refresh_page()

    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(new_contributor_group['contributor_email_1'])
    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(new_contributor_group['contributor_email_2'])
    app.quality_flow.job.setting.validate_the_table_list_not_contains_contributor(new_contributor_group['contributor_email_3'])
