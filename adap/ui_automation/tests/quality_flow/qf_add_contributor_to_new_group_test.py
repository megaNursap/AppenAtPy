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
icm_name = faker.name()
icm_group_name = faker.name()
icm_group_name_uppercase = faker.name().upper()
invalid_icm_group_name = "GROUP123@%$!^%^&*()_WithSpecialCharacters"
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
def new_contributor_uppercase(app):
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


@pytest.mark.ui_smoke
def test_validate_ui_add_contributor_group(app, qf_login):
    app.project_resource.navigate_to_project_resource()
    sleep_for_seconds(5)
    app.project_resource.contributor.navigate_to_project_resource_contributor_group()
    app.project_resource.contributor_group.open_create_contributor_group_popup()
    app.project_resource.contributor_group.validate_ui_elements_in_create_new_contributor_group_dialog()


@pytest.mark.regression_qf
def test_close_dialog(app):
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def testr_cancel_button_work_properly(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_import(icm_group_name, icm_email, 'Add',
                                                                               'Cancel')
    assert app.project_resource.contributor_group.is_dialog_visible() is False


@pytest.mark.regression_qf
def test_import_contributor_back_button_work_properly(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_import(icm_group_name, icm_email, 'Back',
                                                                               None)
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_import_contributor_close_button_work_properly(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_import(icm_group_name, icm_email, 'Close')
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_create_contributor_group_by_import_with_valid_name(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_import(icm_group_name, icm_email, 'Add', 'Add')
    assert app.verification.text_present_on_page("You have successfully created new contributors group")
    app.project_resource.contributor_group.search_internal_contributor_group(icm_group_name)
    sleep_for_seconds(2)
    assert app.verification.text_present_on_page(icm_group_name)


@pytest.mark.regression_qf
def test_create_contributor_group_by_import_with_upper_case_group_name(app, new_contributor, qf_login):
    app.navigation.refresh_page()
    app.project_resource.contributor_group.add_new_contributor_group_by_import(icm_group_name_uppercase, icm_email,
                                                                               'Add', 'Add')
    assert app.verification.text_present_on_page("You have successfully created new contributors group")
    app.project_resource.contributor_group.search_internal_contributor_group(icm_group_name_uppercase)
    sleep_for_seconds(2)
    assert app.verification.text_present_on_page(icm_group_name_uppercase)


@pytest.mark.regression_qf
def test_create_contributor_group_by_import_with_existing_group_name(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_import(icm_group_name, icm_email, 'Add', 'Add')
    assert app.verification.text_present_on_page("[2002:Entity Exists]Group-Name already exists!!")


@pytest.mark.regression_qf
def test_create_contributor_group_by_import_with_group_name_including_special_character(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_import(invalid_icm_group_name)
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_create_contributor_group_by_import_with_group_name_more_than_255_character(app, new_contributor, qf_login):
    group_name = generate_string(256)
    app.project_resource.contributor_group.add_new_contributor_group_by_import(group_name)
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_create_contributor_group_by_import_without_selecting_contributor(app, new_contributor, qf_login):
    group_name = faker.name()
    app.project_resource.contributor_group.add_new_contributor_group_by_import(group_name, None, None, 'Add')
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_upload_contributor_back_button_work_properly(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_upload(icm_group_name, None, 'Back')
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_upload_contributor_close_button_work_properly(app, new_contributor, qf_login):
    app.project_resource.contributor_group.add_new_contributor_group_by_upload(icm_group_name, None, 'Close')
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_create_contributor_group_by_upload_with_valid_name(app, new_contributor, qf_login):
    group_name = faker.name()
    file_name = get_data_file("/internal_contributor/InternalContributor.csv")
    contributor_email = 'integration+test1sep27@appen.com'
    app.project_resource.contributor_group.add_new_contributor_group_by_upload(group_name, file_name, 'Add',
                                                                               contributor_email, 'Add')
    assert app.verification.text_present_on_page("You have successfully created new contributors group")
    app.project_resource.contributor_group.search_internal_contributor_group(group_name)
    sleep_for_seconds(2)
    assert app.verification.text_present_on_page(group_name)


@pytest.mark.regression_qf
def test_create_contributor_group_by_upload_with_invalid_type(app, new_contributor, qf_login):
    group_name = faker.name()
    file_name = get_data_file("/internal_contributor/InternalContributor.tsv")
    app.project_resource.contributor_group.add_new_contributor_group_by_upload(group_name, file_name, 'Add')
    app.project_resource.contributor_group.close_dialog()
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


@pytest.mark.regression_qf
def test_create_contributor_group_by_upload_with_format_csv(app, new_contributor, qf_login):
    group_name = faker.name()
    file_name = get_data_file("/internal_contributor/InternalContributorInvalidFormat.csv")
    app.project_resource.contributor_group.add_new_contributor_group_by_upload(group_name, file_name, 'Add')
    assert app.verification.text_present_on_page(
        "There was an error uploading contributors to group. Please try again.")
    assert app.project_resource.contributor_group.is_dialog_visible() is True
    app.project_resource.contributor_group.close_dialog()


