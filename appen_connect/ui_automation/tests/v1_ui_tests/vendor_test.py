import time

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import mouse_click_element
from adap.ui_automation.utils.selenium_utils import click_element_by_xpath

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.ac_ui_smoke, pytest.mark.regression_ac, pytest.mark.ac_ui_uat]


@pytest.mark.ac_ui_smoke
def test_active_vendor_landing_page(app_test):
    user_name = get_user_email('test_active_vendor_account')
    psw = get_user_password('test_active_vendor_account')
    app_test.ac_user.login_as(user_name=user_name, password=psw)
    ex_results = {"Home": ["HOME"], "Academy": ["APPEN ACADEMY"], "Social": ["FEED", "Profile", "Chat"],
                  "Projects": ["PROJECTS", "My Languages", "News & Updates"],
                  "Micro Tasks": ["MICRO TASKS", "Payment", "Payment Method", "Job History"],
                  "Project Tickets": ["PROJECT TICKETS"], "Inbox": ["MY MESSAGES"],
                  "My Invoices": ["INVOICES", "Tax Forms"], "Privacy": ["PRIVACY"], "Referrals": ["REFERRALS"],
                  "Profile": ["PROFILE", "Intelligent Attributes", "Appen China Platform"]}

    time.sleep(10)
    actual_results = app_test.vendor_pages.links_in_main_and_sub_tabs()

    assert ex_results.keys() == actual_results.keys(), \
        "The titles of the main tabs %s are not matching with expected results %s" % (
            ex_results.keys(), actual_results.keys())

    assert ex_results == actual_results, \
        "The titles of the sub tabs %s are not matching with expected results %s" % (
            ex_results.values(), actual_results.values())


@pytest.mark.ac_ui_smoke
def test_active_vendor_projects(app_test):
    user_name = get_user_email('test_active_vendor_account')
    psw = get_user_password('test_active_vendor_account')
    app_test.ac_user.login_as(user_name=user_name, password=psw)
    app_test.navigation.click_link("Projects")
    app_test.navigation.switch_to_frame("page-wrapper")
    qualified_projects = app_test.vendor_pages.qualified_projects_vendor()
    assert (len(qualified_projects) >= 1)
    all_projects = app_test.vendor_pages.all_projects_vendor()
    assert (len(all_projects) >= 1)


@pytest.mark.ac_old_ui_smoke
def test_express_active_vendor_projects(app_test):
    user_name = get_user_email('test_express_active_vendor_account')
    psw = get_user_password('test_express_active_vendor_account')
    app_test.ac_user.login_as(user_name=user_name, password=psw)
    app_test.navigation.click_link("Projects")
    app_test.navigation.switch_to_frame("page-wrapper")
    qualified_projects = app_test.vendor_pages.qualified_projects_vendor()
    assert (len(qualified_projects) >= 1)
    all_projects = app_test.vendor_pages.all_projects_vendor()
    assert (len(all_projects) >= 1)


@pytest.mark.ac_old_ui_smoke
def test_contract_pending_vendor_projects(app_test):
    user_name = get_user_email('test_contract_pending_vendor_account')
    psw = get_user_password('test_contract_pending_vendor_account')
    app_test.ac_user.login_as(user_name=user_name, password=psw)
    app_test.navigation.click_link("Projects")
    app_test.navigation.switch_to_frame("page-wrapper")
    qualified_projects = app_test.vendor_pages.qualified_projects_vendor()
    assert (len(qualified_projects) >= 1)
    all_projects = app_test.vendor_pages.all_projects_vendor()
    assert (len(all_projects) >= 1)


@pytest.mark.ac_old_ui_smoke
def test_DNH_active_vendor_projects(app_test):
    user_name = get_user_email('test_DNH_active_vendor_account')
    psw = get_user_password('test_DNH_active_vendor_account')
    app_test.ac_user.login_as(user_name=user_name, password=psw)
    app_test.navigation.switch_to_frame("page-wrapper")
    qualified_projects = app_test.vendor_pages.qualified_projects_vendor()
    assert (len(qualified_projects) >= 1)
    app_test.vendor_pages.navigate_to_suggested_projects()
    app_test.verification.text_present_on_page("No Projects Yet")


@pytest.mark.ac_old_ui_smoke
def test_check_applied_projects(app_test):
    # the test checks functionality when a vendor applies to a project
    # we expect this project to be listed in the Applied tab
    language_option = 'English (United States)'
    vendor_acc = 'test_active_vendor_account'
    project_name = get_test_data(vendor_acc, 'project_name')
    user_name = get_user_email(vendor_acc)
    psw = get_user_password(vendor_acc)
    vendor_acc_id = get_user_id(vendor_acc)
    app_test.ac_user.login_as(user_name=user_name, password=psw)
    app_test.navigation.click_link("Projects")
    app_test.navigation.switch_to_frame("page-wrapper")
    all_projects = app_test.vendor_pages.all_projects_vendor()
    assert (len(all_projects) >= 1), 'all projects\' tab is empty'

    app_test.vendor_pages.search_project_by_name(project_name)
    assert app_test.vendor_pages.project_found_on_page(project_name), 'no projects found'

    app_test.vendor_pages.click_action_for_project(project_name, 'Apply')

    app_test.vendor_pages.select_language_option(language_option, 'Proceed')

    time.sleep(5)
    click_element_by_xpath(app_test.driver, "//div[@class='ui-dialog-buttonset']//button[text()='Close']")

    app_test.navigation.click_link('Projects')
    app_test.navigation.switch_to_frame("page-wrapper")
    applied_projects = app_test.vendor_pages.applied_projects_vendor()
    assert (len(applied_projects) >= 1), 'no applied projects found'

    # teardown
    app_test.vendor_pages.click_action_for_project(project_name, 'Cancel Application')
    app_test.driver.switch_to.default_content()
    app_test.ac_user.sign_out()

    internal_acc = 'test_ui_account'
    user_name = get_user_email(internal_acc)
    psw = get_user_password(internal_acc)

    app_test.ac_user.login_as(user_name=user_name, password=psw)
    app_test.navigation.click_link('Vendors')
    app_test.vendor_pages.open_vendor_profile_by(vendor_acc_id, 'id')
    app_test.vendor_pages \
        .screen_user_take_action_on_project(project_name, "Allow Reapply", 'button')
    app_test.navigation.click_link("Logout")
