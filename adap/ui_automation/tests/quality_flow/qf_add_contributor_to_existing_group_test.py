import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.selenium_utils import sleep_for_seconds

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]
icm_email = faker.email()
icm_name = faker.name()
icm_group_name = faker.name()
username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)
    app.driver.implicitly_wait(2)


@pytest.fixture(scope="module")
def new_contributor(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    res = api.post_internal_contributor_create(email=icm_email, name=icm_name, team_id=team_id)
    assert res.status_code == 200


@pytest.fixture(scope="module")
def new_contributor_group(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    res = api.post_search_contributor_by_name(name=icm_name, team_id=team_id)

    response = res.json_response
    assert res.status_code == 200

    contributor_id = response.get("data").get("list")[0].get("id")

    res = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name, contributor_ids=[contributor_id],
                                                          team_id=team_id)
    assert res.status_code == 200


@pytest.mark.regression_qf
def test_validate_ui_add_contributor_to_existing_group(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.navigate_to_project_resource()
    sleep_for_seconds(5)
    app.project_resource.contributor.search_internal_contributor(contributor_email=icm_email)
    app.project_resource.contributor.select_contributor_action_menu(action='Add to existing Contributor Group')
    app.project_resource.contributor.validate_ui_elements_in_add_contributor_to_existing_group()
    app.project_resource.contributor.close_dialog()


@pytest.mark.regression_qf
def test_cancel_button_work_properly(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.contributor.search_internal_contributor(contributor_email=icm_email)
    app.project_resource.contributor.select_contributor_action_menu(action='Add to existing Contributor Group')
    app.project_resource.contributor.add_to_existing_contributor_group(contributor_group=icm_group_name,
                                                                       action='Cancel')
    assert app.project_resource.contributor_group.is_dialog_visible(contributor=icm_email) == False
    app.project_resource.contributor.close_dialog()


@pytest.mark.regression_qf
def test_close_button_work_properly(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.contributor.search_internal_contributor(contributor_email=icm_email)
    app.project_resource.contributor.select_contributor_action_menu(action='Add to existing Contributor Group')
    app.project_resource.contributor.add_to_existing_contributor_group(contributor_group=icm_group_name,
                                                                       action='Close')
    assert app.project_resource.contributor_group.is_dialog_visible(contributor=icm_email) == False
    app.project_resource.contributor.close_dialog()


@pytest.mark.regression_qf
def test_add_contributor_to_existing_group(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.navigate_to_project_resource()
    sleep_for_seconds(5)
    app.project_resource.contributor.search_internal_contributor(contributor_email=icm_email)
    app.project_resource.contributor.select_contributor_action_menu(action='Add to existing Contributor Group')
    app.project_resource.contributor.validate_ui_elements_in_add_contributor_to_existing_group()
    app.project_resource.contributor.add_to_existing_contributor_group(contributor_group=icm_group_name, action='Add')
    assert app.verification.text_present_on_page("You have successfully added contributor to existing group")
    app.project_resource.contributor.navigate_to_project_resource_contributor_group()
    app.project_resource.contributor_group.validate_ui_elements_in_contributor_group_tab()
    app.project_resource.contributor_group.search_internal_contributor_group(group_name=icm_group_name)
    app.project_resource.contributor_group.select_contributor_group_action_menu(action='Edit Contributor Group')
    assert app.project_resource.contributor_group.is_dialog_contains_contributor(contributor=icm_email) == True


@pytest.mark.regression_qf
def test_add_multiple_contributors_to_existing_group(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.contributor.add_multiple_contributors_to_existing_group(number_of_contributors=4,
                                                                                 group_name=icm_group_name,
                                                                                 action='Add')
    assert app.verification.text_present_on_page("You have successfully added contributor to existing group")


@pytest.mark.regression_qf
def test_remove_contributor_from_existing_group(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.contributor.navigate_to_project_resource_contributor_group()
    app.project_resource.contributor_group.search_internal_contributor_group(group_name=icm_group_name)
    app.project_resource.contributor_group.select_contributor_group_action_menu(action='Edit Contributor Group')
    app.project_resource.contributor_group.remove_contributors_from_existing_groups(contributor=icm_email)
    assert app.verification.text_present_on_page("You have successfully deleted contributor in contributors group")
    assert app.project_resource.contributor_group.is_dialog_contains_contributor(contributor=icm_email) == False
    app.project_resource.contributor_group.close_dialog()
