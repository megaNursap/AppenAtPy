"""
    Partner Home Tests
"""
import time

from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name


pytestmark = [pytest.mark.regression_ac_core, pytest.mark.ac_ui_uat, pytest.mark.regression_ac]


USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


@pytest.fixture(scope="function")
def login(app_test):
    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


@pytest.mark.ac_old_ui_smoke
def test_partner_home_landing_page(app_test, login):

    app_test.navigation.click_link("Partner Home")
    app_test.navigation.click_link("View previous list page")
    app_test.verification.current_url_contains('/partners/previous_projects')
    app_test.verification.element_is_visible_on_the_page("//button[@id='new-project-btn']")
    assert(len(app_test.navigation_old_ui.get_columns_of_table())>0)
 # verify all the tabs on Partner Home Page.
    #This is available to Admins only
    #app_test.verification.text_present_on_page("Locale Priorities")
    app_test.verification.text_present_on_page("Locales")
    app_test.verification.text_present_on_page("Programs")
    app_test.verification.text_present_on_page("Experiment List")
    app_test.verification.text_present_on_page("Groups")
    app_test.verification.text_present_on_page("User Rates")
    app_test.verification.text_present_on_page("Partner Data Files")
    app_test.verification.text_present_on_page("Partner Data")
    app_test.verification.text_present_on_page("Partner Invoice Data")
    app_test.verification.text_present_on_page("Client Data Mappings")
    

def test_project_configuration(app_test, login):
    app_test.navigation.click_link("Partner Home")
    app_test.verification.current_url_contains('/partners/projects')
    app_test.navigation.click_link("View previous list page")
    name_of_the_project = app_test.partner_home.get_project_name_on_project_list()
    app_test.partner_home.click_on_project_link(name_of_the_project)
    app_test.verification.current_url_contains("partners/project/view")
    app_test.verification.text_present_on_page(name_of_the_project)


def test_project_user_rate_page(app_test, login):
    app_test.navigation.click_link("Partner Home")
    time.sleep(3)
    app_test.navigation.click_link("User Rates")
    app_test.navigation_old_ui.click_input_btn("Go")
    time.sleep(5)
    assert (len(app_test.navigation_old_ui.get_columns_of_table()) > 0)


def test_create_new_project_v1(app_test, login):
    project_name = generate_project_name()
    app_test.navigation.click_link("Partner Home")
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.navigation.click_btn('Create New Project')
    # app_test.partner_home.create_new_project_v1("APPEN")
    app_test.ac_project.create_new_project(use_old_interface=True)
    app_test.partner_home.fill_out_fields_project(data={
        "Project Name": project_name[0],
        "Project Alias": project_name[1],
        "Workday ID": "223344",
        "Project Type": "Translation",
        "Project Rate Type": "Hourly",
        "Project Business Unit": "CR"})
    app_test.partner_home.fill_in_project_description("Test Description")
    app_test.navigation_old_ui.click_input_btn("Save")
    app_test.verification.text_present_on_page('Project')

