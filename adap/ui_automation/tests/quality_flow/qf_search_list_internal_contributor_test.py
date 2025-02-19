import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
from adap.api_automation.utils.data_util import get_test_data, get_data_file
from adap.ui_automation.utils.selenium_utils import sleep_for_seconds
from adap.ui_automation.utils.utils import generate_string

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]
icm_email = faker.email()
icm_email_2 = faker.email()
icm_email_3 = 'automation.test+' + generate_string(10) + '@appen.com'
icm_name = faker.name()
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
def new_contributor_2(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    res = api.post_internal_contributor_create(email=icm_email_2, name=icm_name, team_id=team_id)
    assert res.status_code == 200


@pytest.fixture(scope="module")
def new_contributor_3(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    res = api.post_internal_contributor_create(email=icm_email_3, name=icm_name, team_id=team_id)
    assert res.status_code == 200


@pytest.mark.regression_qf
def test_can_retrieve_data_using_email(app, new_contributor, qf_login):
    app.project_resource.navigate_to_project_resource()
    sleep_for_seconds(5)
    app.project_resource.contributor.search_internal_contributor(contributor=icm_email)
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_name) == True


@pytest.mark.regression_qf
def test_can_retrieve_data_using_name(app, new_contributor, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=icm_name)
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_name) == True


@pytest.mark.regression_qf
def test_can_retrieve_data_using_uppercase_email(app, new_contributor, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=icm_email.upper())
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_name) == True


@pytest.mark.regression_qf
def test_can_retrieve_data_using_uppercase_name(app, new_contributor, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=icm_name.upper())
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_name) == True


@pytest.mark.regression_qf
def test_can_retrieve_data_using_only_similar_couple_string(app, new_contributor, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=icm_name.split('@')[0])
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_name) == True


@pytest.mark.regression_qf
def test_not_existing_data_will_not_displayed(app, new_contributor, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=generate_string(20))
    app.verification.text_present_on_page("Please click on Add Contributor button to begin")


@pytest.mark.regression_qf
def test_can_retrieve_two_data_with_same_name_and_different_email(app, new_contributor_2, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=icm_name)
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email_2) == True
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_name) == True


@pytest.mark.regression_qf
def test_can_retrieve_data_using_special_char(app, new_contributor_3, qf_login):
    app.project_resource.contributor.search_internal_contributor(contributor=icm_email_3)
    assert app.project_resource.contributor.is_table_contains_contributor(contributor=icm_email_3) == True

