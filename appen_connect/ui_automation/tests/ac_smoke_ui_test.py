import time

import allure

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import send_keys_by_xpath, select_option_value

USER_NAME = get_test_data('test_ui_account', 'email')
PASSWORD = get_test_data('test_ui_account', 'password')
FULL_NAME = get_test_data('test_ui_account', 'full_name')

pytestmark = [pytest.mark.ac_ui_smoke]

URL = {
    'stage': 'https://connect-stage.integration.cf3.us/qrp/core',
    'qa': 'https://connect-qa.sandbox.cf3.us/qrp/core',
    'prod': 'https://connect.appen.com/qrp/cor',
    'integration': 'https://connect.integration.cf3.us/qrp/core'
}

@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


@allure.issue("https://appen.atlassian.net/browse/ACE-13842", 'Bug: ACE-13842')
@allure.issue("https://appen.atlassian.net/browse/ACE-16953", 'Bug: ACE-16953')
@pytest.mark.parametrize('endpoint, verification, iframe, submit, delay, custom_filter',
                         [
                          ("/tickets", ["Ticket ID","Title", "Rows Per Page:"], False,  True, 15, [{'element':'status', 'value': 'Closed'}]),
                          ("/vendors/project_site/1/1", ["SETTING UP YOUR COMPUTER","CHROME EXTENSION", "Raterhub Mobile App"], False,  False, 0, []),
                          ("/partners/previous_projects",  ["Id", "Alias", "Rows Per Page:"], False, False, 0, []),
                          ("/partners/projects", ["PROJECT", "TYPE OF TASK", "Showing"], True,  False, 0, []),
                          ("/partners/project/newProject", ["Project Overview", "Project Setup", "Project Name"], True, False, 0, []),
                          ("/admin/locales", ["Locale Name", "Code 2-digit"], False, False, 0, []),
                          ("/customers", ["Experiments", "Links", "Rows Per Page:"], False, False, 0, []),
                          ("/partners/experiment_groups", ["Group Name", "Links", "Rows Per Page:"], False, False, 0, []),
                          ("/admin/locales", ["Locale Name", "Code 2-digit"], False, False, 0, []),
                          ("/partners/experiments", ["Priority", "Name", "Date Reviewed", "Rows Per Page:"], False, True, 0, []),
                          ("/user_project_rates", ["First Name", "Customer", "Locale", "Rows Per Page:"], False, True, 0, []),
                          ("/partners/external_data", ["File Name", "Project", "Column Map", "Rows Per Page:"], False, True, 0, []),
                          ("/partners/external_partner_data",
                               ["Partner Data File Name", "Report Date", "Completion Date", "Rows Per Page:"],
                               False,
                               True,
                               30,
                              [{'element':'selectedPartnerDataFileId',
                                 'value': '1108_no-errors.csv'}]),
                          ("/partners/external_partner_invoice_data",
                               ["Partner Data Id", "Task Type", "Time Worked Milliseconds", "Rows Per Page:"],
                               False,
                               True,
                               30,
                               [{'element': 'selectedPartnerDataFileId',
                                 'value': '1108_no-errors.csv'}]),
                          ("/partners/external_partner_raw_data_field_mapping",
                                               ["Client Name", "Field Value", "Project Name", "Rows Per Page:"], False, True, 0, []),
                          ("/vendors/profile", ["Email Address", "Experience", FULL_NAME], False, False, 0, []),
                          ("/vendors/inbox_messages", ["MY MESSAGES"], False, False, 0, []),
                          ("/vendors/user_profile/view", ["PROFILE INFORMATION", FULL_NAME, "COUNTRY", "YOUR PRIMARY LANGUAGE"], True, False, 0, []),
                          ("/vendors/academy_home/view", ["Welcome to the Appen Academy!", "APPEN ACADEMY" ], False, False, 0, []),
                          ("/partners/documents", ["Status", "Roles", "Comments Disabled?", "Rows Per Page:"], False, False, 0, []),
                          ("/vendors/moderators", ["Role of the Moderator", "Moderator Interface and Workflow"], False, False, 0, []),
                          ("/vendors/social/chat/console/1", ["Appen Chat Server", "Prohibited Conduct", "Chat Etiquette"], False, False, 0, []),
                          ("/vendors/register_profile", ["CREATE SOCIAL PROFILE", "User Submitted Content", "Limitation of Liability"], False, False, 0, []),
                          ("/ticket_statistics", ["Tickets Closed", "Ticket Close Information (last 30 days)", "Quality Tickets Logged"], False, False, 0, []),
                          ("/recruiting", ["RECRUITING DASHBOARDS", "Actionable Items", "Users staged +"], False, False, 0, []),
                          ("/vendor_list", ["User ID", "Email Address", "State", "Rows Per Page:"], False, True, 30,
                           [{'element':'status',
                             'value': 'Active'}]),
                          ("/contract_tasks", ["Renewal Id", "Contract Id", "Vendor"], False, False, 0, []),
                          ("/tickets/list", ["Ticket ID", "Vendor", "Owner", "Rows Per Page:"],
                               False,
                               True,
                               30,
                               [{'element':'status', 'value': 'New'}]),
                          ("/email", ["Specify Recipients", "Manual List", "Mail Merge"], False, False, 0, []),
                          ("/jobs", ["Job Name", "Active Vendors",  "Rows Per Page:"], False, True, 0, []),
                          ("/campaigns", ["Campaign Date", "Source", "Vendor"], False, True, 0, []),
                          ("/search_tickets", ["Found", "Period", "Status"], False, False, 0, []),
                          ("/invoices", ["Invoice Period", "Email Address", "Termination Date"], False, True, 15,
                            [{'element':'status', 'value': 'Approved'}]),
                          ("/sql?template.id=1", ["SQL Execution", "SQL Statement", "Redshift SQL Statement", ], False, False, 0, []),
                          ("/partners/falcon/reports", ["Daily Performance Report", "REPORT TYPE", "CREATED AT"], True, False, 0, []),
                          ("/partners/falcon/metrics_config", ["Cross-Project Metric Configuration", "REPORT TEMPLATE NAME", "LAST WBR UPDATE"], True, False, 0, []),
                          ("/partners/project_setup/view/1", ["Overview & tools", "Recruitment", "User Project Page"], True, False, 0, []), #TODO "Need to fix https://appen.atlassian.net/browse/ACE-12611"
                          ("/partners/roster_management/trackers/1", ["PRODUCTIVE", "ONBOARDING", "REVOKED"], True, False, 0, []),
                          ("/partners/roster_management/trackers/1/onboarding", ["Production Onboarding"], True, False, 0, []),
                          ("/partners/roster_management/trackers/1/revoked", ["Revoked Workers"], True, False, 0, []),
                          ("/partners/roster_management/trackers/1/markets/ENG-GBR-GBR?startDate=2021-08-02T15:28:48.000Z&endDate=2021-08-09T15:28:48.000Z",["Weekly Metrics & Goals"], True, False, 0, []),
                          ("/partners/roster_management/trackers/1/markets/ENG-GBR-GBR/onboarding",["Onboarding Workers per Market"], True, False, 0, []),
                         ])

#@allure.issue("https://appen.atlassian.net/browse/ACE-15462", "BUG  on STAGE ACE-15462")
def test_ac_smoke_ui_admin(app, login, endpoint, verification, iframe, submit, delay, custom_filter):
    _url = URL[app.env] + endpoint
    app.navigation.open_page(_url)
    time.sleep(2)

    if iframe:
        app.navigation.switch_to_frame("page-wrapper")
        time.sleep(1)

    if custom_filter:
        time.sleep(1)
        select_option_value(app.driver, custom_filter[0]['element'], custom_filter[0]['value'])

    if submit:
        app.navigation_old_ui.click_input_btn("Go")
        time.sleep(4+delay)

    for verify_text in verification:
        assert app.verification.text_present_on_page(verify_text)

    if iframe:
        app.driver.switch_to.default_content()



