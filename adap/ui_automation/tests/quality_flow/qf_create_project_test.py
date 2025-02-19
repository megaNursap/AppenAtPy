import datetime
import time
import pytest
from adap.api_automation.utils.data_util import get_test_data

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              mark_env]


@pytest.fixture(scope="module")
def qf_login(app):
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')
    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    if not app.quality_flow.qf_is_enabled_to_team(team_id):
        app.quality_flow.enable_qf_for_team(team_id)
        time.sleep(3)

    app.user.login_as_customer(username, password)

    app.mainMenu.menu_item_is_disabled('quality', is_not=True)
    app.mainMenu.quality_flow_page()


@pytest.mark.qf_ui_smoke
def test_qf_new_project_required_fields(app, qf_login):
    """
    verify that name is required fields
    description is optional fields
    verify - Confirm btn is enabled if name fields are provided
    verify - cancel creating project - no project is created
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Create Project')
    app.navigation.click_link('Create Project')

    app.verification.text_present_on_page('Create Project')
    app.verification.text_present_on_page('PROJECT NAME*:')
    app.verification.text_present_on_page('DESCRIPTION:')

    assert app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.fill_out_project_details(description='test')
    app.verification.text_present_on_page('name is a required field')
    assert app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.fill_out_project_details(name='Test create new project')
    app.verification.text_present_on_page('name is a required field', is_not=False)
    assert not app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.fill_out_project_details(description='test')
    assert not app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.close_create_project_window()

    assert app.quality_flow.find_project(by='name', value='Test create new project') == []


@pytest.mark.qf_ui_smoke
def test_project_name_duplicate(app, qf_login):
    """
    verify no duplicated name is allowed
    """
    app.navigation.refresh_page()
    predefined_project = get_test_data('qf_user', 'default_project').get('name', '')

    app.verification.wait_untill_text_present_on_the_page('Create Project')
    app.navigation.click_link('Create Project')
    app.quality_flow.fill_out_project_details(name=predefined_project,
                                              description="Test name duplication",
                                              action="Confirm")

    app.verification.text_present_on_page('Project name already exists.')

    assert app.quality_flow.find_project(by='name', value=predefined_project) == []


@pytest.mark.qf_ui_smoke
def test_create_new_qf_project(app, qf_login):
    """
    verify user is able to create new QF project
    """
    app.navigation.refresh_page()

    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    project_name = f"New project test - {_today} {app.faker.zipcode()}"

    app.verification.wait_untill_text_present_on_the_page('Create Project')
    app.navigation.click_link('Create Project')
    app.quality_flow.fill_out_project_details(name=project_name,
                                              description=f"Test project: {project_name}",
                                              action="Confirm")
    time.sleep(3)
    project_details = app.quality_flow.get_project_details()
    assert project_details["name"] == project_name

    app.verification.text_present_on_page('Dataset')
    app.verification.text_present_on_page('Jobs')
    app.verification.text_present_on_page('Curated Contributors')
    app.verification.text_present_on_page('Dashboards')

    app.verification.text_present_on_page('TOTAL UNITS')
    app.verification.text_present_on_page('NEW')
    app.verification.text_present_on_page('WORKING')
    app.verification.text_present_on_page('JUDGABLE')
    app.verification.text_present_on_page('SUBMITTED')
    app.verification.text_present_on_page('Last updated: ')

    app.verification.text_present_on_page('all data')
    app.verification.text_present_on_page('data group')
    app.verification.text_present_on_page('deleted')

    app.verification.current_url_contains('/dataset')


# feature is deprecated
# @pytest.mark.qf_uat_ui
# def test_create_new_segmented_qf_project(app_test):
#     """
#     verify user is able to create new project with unit type 'Segmented'
#     """
#     username = get_test_data('qf_user_ui', 'email')
#     password = get_test_data('qf_user_ui', 'password')
#
#     app_test.user.login_as_customer(username, password)
#     app_test.mainMenu.quality_flow_page()
#
#     _today = datetime.datetime.now().strftime("%Y_%m_%d")
#     project_name = f"New Segmented project test - {_today} {app_test.faker.zipcode()}"
#
#     app_test.navigation.click_link('Create Project')
#     app_test.quality_flow.fill_out_project_details(name=project_name,
#                                                    unit_type='SEGMENTED',
#                                                    description=f"Test project: {project_name}",
#                                                    action="Confirm")
#
#     assert app_test.quality_flow.find_project(by='name', value=project_name) != []
#
#     app_test.quality_flow.open_project(by='name', value=project_name)
#
#     project_details = app_test.quality_flow.get_project_details()
#     assert project_details["name"] == project_name
#
#     app_test.verification.text_present_on_page('Dataset')
#     app_test.verification.text_present_on_page('Jobs')
#     app_test.verification.text_present_on_page('Curated Crowd')
#     app_test.verification.text_present_on_page('Dashboard')
#
#     app_test.verification.text_present_on_page('TOTAL UNIT GROUPS')
#     app_test.verification.text_present_on_page('TOTAL UNITS')
#     app_test.verification.text_present_on_page('NEW UNITS')
#     app_test.verification.text_present_on_page('ASSIGNED UNITS')
#     app_test.verification.text_present_on_page('JUDGEABLE UNITS')
#     app_test.verification.text_present_on_page('FINALIZED UNITS')
#     app_test.verification.text_present_on_page('Last updated:')
#
#     app_test.verification.text_present_on_page('all data')
#     app_test.verification.text_present_on_page('data group')
#     app_test.verification.text_present_on_page('deleted')
#
#     app_test.verification.current_url_contains('/dataset')


