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

    print("contributor_id ", response.get("data").get("list")[0].get("id"))
    print("icm_group_name ", icm_group_name)
    print("team_id ", team_id)

    contributor_id = response.get("data").get("list")[0].get("id")

    res = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name, contributor_ids=[contributor_id],
                                                          team_id=team_id)
    assert res.status_code == 200


@pytest.mark.regression_qf
def test_delete_contributor_to_existing_group(app, new_contributor, new_contributor_group, qf_login):
    app.project_resource.icm.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    app.project_resource.icm.navigate_to_project_resource_contributor_group()
    app.project_resource.icm.validate_ui_elements_in_contributor_group_tab()
    app.project_resource.icm.search_internal_contributor_group(icm_group_name)
    app.project_resource.icm.navigate_to_edit_contributor_group_popup()
    app.project_resource.icm.validate_ui_elements_in_edit_contributor_group_popup()
    app.project_resource.icm.search_contributor_from_edit_contributor_group_popup(icm_email)
    app.project_resource.icm.delete_contributor_from_edit_contributor_group_popup(icm_email)
    app.project_resource.icm.close_popup()
    app.project_resource.icm.navigate_to_edit_contributor_group_popup()
    app.project_resource.icm.validate_contributor_group_not_contains_contributor(icm_email)
