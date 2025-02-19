import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
from adap.api_automation.utils.data_util import get_test_data

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]
icm_email = faker.email()
icm_name = faker.name()
icm_group_name_1 = 'AutomationGroupTest' + faker.name()
icm_group_name_2 = 'AutomationGroupTest' + faker.name()
icm_group_name_3 = 'AutomationGroupTest' + faker.name()
icm_group_name_4 = 'AutomationGroupTest' + faker.name()

contributor_email_1 = faker.email()
contributor_name_1 = faker.name()

contributor_email_2 = faker.email()
contributor_name_2 = faker.name()

contributor_email_3 = faker.email()
contributor_name_3 = faker.name()

contributor_email_4 = faker.email()
contributor_name_4 = faker.name()

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)
    app.driver.implicitly_wait(2)


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

    res_4 = api.post_internal_contributor_create(email=contributor_email_4, name=contributor_name_4, team_id=team_id)
    assert res_4.status_code == 200


@pytest.fixture(scope="module")
def contributor_groups(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    res_1 = api.post_search_contributor_by_name(name=contributor_name_1, team_id=team_id)
    assert res_1.status_code == 200

    res_2 = api.post_search_contributor_by_name(name=contributor_name_2, team_id=team_id)
    assert res_1.status_code == 200

    res_3 = api.post_search_contributor_by_name(name=contributor_name_3, team_id=team_id)
    assert res_1.status_code == 200

    res_4 = api.post_search_contributor_by_name(name=contributor_name_4, team_id=team_id)
    assert res_1.status_code == 200

    contributor_id_1 = res_1.json_response.get("data").get("list")[0].get("id")
    contributor_id_2 = res_2.json_response.get("data").get("list")[0].get("id")
    contributor_id_3 = res_3.json_response.get("data").get("list")[0].get("id")
    contributor_id_4 = res_4.json_response.get("data").get("list")[0].get("id")

    res_1 = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name_1, contributor_ids=[contributor_id_1],
                                                            team_id=team_id)
    assert res_1.status_code == 200

    res_2 = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name_2, contributor_ids=[contributor_id_2],
                                                            team_id=team_id)
    assert res_2.status_code == 200

    res_3 = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name_3, contributor_ids=[contributor_id_3],
                                                            team_id=team_id)
    assert res_3.status_code == 200

    res_4 = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name_4, contributor_ids=[contributor_id_4],
                                                            team_id=team_id)
    assert res_4.status_code == 200


@pytest.mark.regression_qf
def test_delete_single_contributor_group(app, contributors, contributor_groups, qf_login):
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.navigate_to_project_resource_contributor_group()
    app.project_resource.icm.validate_ui_elements_in_contributor_group_tab()
    app.project_resource.icm.search_internal_contributor_group(icm_group_name_1)
    app.project_resource.icm.navigate_to_delete_popup()
    app.project_resource.icm.validate_ui_elements_on_delete_popup(icm_group_name_1)
    app.project_resource.icm.confirm_to_delete()

    app.verification.text_present_on_page('You have successfully deleted contributors group')

    app.project_resource.icm.validate_the_table_not_contains_contributor_group(icm_group_name_1)


@pytest.mark.regression_qf
def test_delete_multiple_contributor_groups(app, contributors, contributor_groups, qf_login):
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.navigate_to_project_resource_contributor_group()
    app.project_resource.icm.validate_ui_elements_in_contributor_group_tab()

    app.project_resource.icm.search_internal_contributor_group("AutomationGroupTest")

    group_name_1 = app.project_resource.icm.get_group_name_by_index(1)
    group_name_2 = app.project_resource.icm.get_group_name_by_index(2)
    group_name_3 = app.project_resource.icm.get_group_name_by_index(3)

    app.project_resource.icm.delete_multiple_contributor_groups(3)

    app.project_resource.icm.validate_the_table_contains_contributor_group_in_delete_confirmation_popup(group_name_1)
    app.project_resource.icm.validate_the_table_contains_contributor_group_in_delete_confirmation_popup(group_name_2)
    app.project_resource.icm.validate_the_table_contains_contributor_group_in_delete_confirmation_popup(group_name_3)

    app.project_resource.icm.confirm_to_delete_multiple_contributor_group()

    app.verification.text_present_on_page('You have successfully deleted contributors group')

    app.project_resource.icm.validate_the_table_not_contains_contributor_group(group_name_1)
    app.project_resource.icm.validate_the_table_not_contains_contributor_group(group_name_2)
    app.project_resource.icm.validate_the_table_not_contains_contributor_group(group_name_3)

