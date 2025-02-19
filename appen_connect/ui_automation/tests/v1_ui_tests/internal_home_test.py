"""
    Internal Home Tests
"""

import pytest
import time
import datetime

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.data_util import get_user_info
from faker import Faker

from adap.api_automation.utils.judgments_util import create_screenshot

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.internal_home,
              pytest.mark.ac_ui_uat]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

VENDOR_ID = get_user_id('test_active_vendor_account')


@pytest.fixture(scope="function")
def login(app_test):
    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


def generate_sql():
    faker = Faker()
    today = datetime.date.today().strftime("%mmm/%dd")
    return [(faker.name() + today), faker.name()]


def generated_unique_digit():
    faker = Faker()
    return faker.random_int(100, 10000)


def go_to_vendor_profile(app_test, vendor_id):
    app_test.internal_home_pages.search_vendor(vendor_id)
    app_test.navigation_old_ui.click_input_btn("Go")
    app_test.navigation.click_link(vendor_id)


@pytest.mark.ac_old_ui_smoke
def test_internal_tabs_home_validation(app_test, login):
    expected_tab_names = {"Home": ['HOME', 'Snippets', 'URL Punchcard'],
                          "Recruiting": ['Recruiting Dashboards','USER SCREENING DASHBOARD', 'Project Qualifications', 'Applicant Referrals',
                                         'Project Permissions', 'Vendors By Locale', 'User Static Notes',
                                         'New Hire Documents', 'Do Not Hire', 'Recruiting Reports'],
                          "Vendors": ['VENDOR LIST', 'Project Qualifications', 'Project Permissions', 'Bulk Process',
                                      'Bulk Notes', 'EWOQ Exams','Termination Portal', ''],
                          "Jobs": ['JOB LIST', 'Regions', 'Default Country Payrates'],
                          "Contracts": ['CONTRACT RENEWALS'],
                          "Campaigns": ['CAMPAIGNS', 'Campaign Applicants'],
                          "Invoices": ['INVOICE LIST', 'Summarized Invoice List', 'PM approval invoices', 'Variances',
                                       'Reports', 'Batch Process'],
                          "Quality": ['Blind Tests', 'AQM Levels', 'Quality Review Survey Responses', 'Training Tasks',
                                      'Quizzes', 'Reports'],
                          "Reports": ['Blind Tests', 'AQM Levels', 'Quality Review Survey Responses', 'Training Tasks',
                                      'Quizzes', 'Reports'],
                          "Tickets": ['TICKET LIST', 'Ticket Reports', 'Ticket Reports New', 'Survey Responses',
                                      'Ticket Templates', 'Email Templates', 'Bulk Email', 'Orders', 'Teams', ''],
                          "Global IAs": ['STANDARD GLOBAL IAS', 'Global IAs'],
                          "Administration": ['ACTION LIST', 'System Configuration', 'Quality Review Budgets'
                                             ],
                          'Partner Home': ['Locale Priorities', 'Locales', 'Customers', 'PROJECTS', 'Experiment List',
                                           'Groups', 'User Rates', 'Partner Data Files', 'Partner Data',
                                           'Partner Invoice Data', 'Partner Raw Data Field Mappings',
                                           'Partner Data Files (Beta)',
                                           "Customer:\nAll Customers\nA_QA QualityCustomer\nA9\nAA "
                                           "Recruitment\nABCTest\nAC_Invoicing\nAC_to_AG\nACSupport@appen.com\nA F8 "
                                           "Testing\nag_customer1\nAgency_Wilkins\nAlbanian\nAlibaba\nAmazon Web "
                                           "Services Inc\nAPPEN\nAppen Internal\nApple\nApple Demo\nApple Maps\nApple "
                                           "Raterqualification\nAQA "
                                           "Customer\nAragorn\nAragorn\nArogorn_NER\nBaidu\nBeans\nBergul Test\nBing "
                                           "Multimedia Image\nBloomreach\nBossa Nova\nCameron "
                                           "Test\nCicada\nCosmos\nCRM\nCRM "
                                           "Express\nCthulhu\nDavidHungOne\neBay\nErminia_test\nFacebook\nFalcon"
                                           "\nFalcon1\nFalcon Ads MegaTaxon Classification\nFalcon Entities\nFalcon "
                                           "Entities_RAY\nFalcon Entity Rating\nFalcon Search\nFalcon Speech DC "
                                           "Eval\nFalcon Speech DC "
                                           "Training\nFerry\nFigure8_Cavite\nFinney\nFinney\nFunhub\nFunLand\nFunLand"
                                           "\nFunLand2\nGetty Test\nGoogle\nGoogle "
                                           "Geo\nGRR_sample\nHogwartsTest\nIceberg test\nKamila's "
                                           "test\nLeapforce\nLenovo\nLinkedIn\nLL JM TEST\nMacro_Lang\nMacrolanguage "
                                           "Test\nMatrix\nMcDondal's\nMicrosoft Bing\nMicrosoft Bing Ads\nMicrosoft "
                                           "Bing Multimedia\nMicrosoft NLX\nMilyoni\nMultimedia Test\nMynah "
                                           "Bird\nNeon\nNewton\nPaula_test\nPentatonix\nPeter one\nQA Customer\nQA "
                                           "Support\nRachael's fun "
                                           "customer\nRaven\nRush\nSabre\nSakura\nSamsung\nSamsung\nSeha_test\nSIL "
                                           "Criteria Validation - DO NOT ENABLE\nStudio 71\nSusan Baker\nSweet "
                                           "Tasting Thing\nSWFH\nTeal Real Client Name\nTest\ntest123\nTEST "
                                           "Customer\nTier1 Test\nTomTom\nToroda\nTracy AC One\nTracy Two\nTracy "
                                           "Two\nTraining\nTwitter\nUmbrella "
                                           "Client\nUnicorn\nVerdant\nVerint\nWal-Mart\nWalmart Labs DO NOT "
                                           "USE\nWestfield_test\nWilkins\nYahoo\nYandex"],
                          'Vendor Home': ['PROJECTS', 'My Languages', 'ACAN Timesheet Reports', 'News & Updates'],
                          ' ': ['PROJECTS', 'My Languages', 'ACAN Timesheet Reports', 'News & Updates']}

    expected_main_tab_titles = ["Home", "Recruiting", "Vendors", "Jobs", "Contracts", "Campaigns", "Invoices",
                                "Quality", "Reports", "Tickets", "Global IAs", "Administration", 'Partner Home',
                                'Vendor Home', ' ']

    # assert expected_main_tab_titles == actual_tabs_internal_home_pages, \
    #     "The titles of the main tabs %s are not matching with expected results %s" % (
    #         expected_main_tab_titles, actual_tabs_internal_home_pages)

    for key in expected_tab_names:
        actual_tab_names = app_test.navigation_old_ui.sub_tab_links([key])
        for key1, value1 in actual_tab_names.items():
            if key1 != 'Partner Home':
                if key == 'Reports':
                    app_test.navigation.click_btn("SQL Reports")
                    time.sleep(5)
                assert key1 == key, " %s %s" % (key1, key)
                assert expected_tab_names[key] == actual_tab_names[
                    key1], "Expected sub tabs %s are not matching with actual sub tabs %s" % (
                expected_tab_names[key], value1)


@pytest.mark.skip(reason='Only admin create the new SQL reports now')
@pytest.mark.ac_old_ui_smoke
@pytest.mark.flaky(reruns=2)
def test_execute_report(app_test, login):
    sql_report = generate_sql()
    app_test.navigation.click_link("Reports")
    app_test.navigation.click_link("Add")
    app_test.internal_home_pages.fill_out_fields(data={
        "Category": "Engineering",
        "Name": sql_report[0],
        "Statement": sql_report[1]
    })
    app_test.internal_home_pages.fill_description("test")
    app_test.navigation_old_ui.click_input_btn("Save")

    app_test.navigation_old_ui.click_input_btn("Go")
    time.sleep(5)
    app_test.verification.text_present_on_page(sql_report[0])


#@pytest.mark.skip(reason="https://appen.atlassian.net/browse/ACE-13823")
@pytest.mark.ac_old_ui_smoke
@pytest.mark.flaky(reruns=2)
def test_create_ticket(app_test, login):
    app_test.navigation.click_link("Add")
    ticket_title = "Ticket created using Automation" + str(generated_unique_digit())
    app_test.tickets.fill_out_fields(data={
        "Project": "A A Quiz",
        "Type": "Support",
        "Recipients": "spajjuri@appen.com",
        "Title": ticket_title
    })
    app_test.tickets.fill_ticket_body("Test ticket body")
    app_test.navigation_old_ui.click_input_btn("Send")
    app_test.verification.text_present_on_page(ticket_title)


@pytest.mark.ac_old_ui_smoke
@pytest.mark.flaky(reruns=2)
def test_impersonate_a_vendor(app_test, login):
    app_test.navigation.click_link("Vendors")
    go_to_vendor_profile(app_test, VENDOR_ID)
    create_screenshot(app_test.driver, "before_impersonate")
    app_test.navigation.click_link("Impersonate")
    time.sleep(4)
    create_screenshot(app_test.driver, "after_impersonate")
    app_test.verification.text_present_on_page("Stop Impersonating")


@pytest.mark.ac_old_ui_smoke
@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_vendor_profile_ui(app_test, login):
    app_test.navigation.click_link("Vendors")
    go_to_vendor_profile(app_test, VENDOR_ID)
    app_test.verification.text_present_on_page("Qualifications")
    app_test.verification.text_present_on_page("Profile Information")
    app_test.verification.text_present_on_page("Contract Details")
    app_test.verification.text_present_on_page("Documents")
    app_test.verification.text_present_on_page("Viewed / Downloaded Guidelines")
    app_test.verification.text_present_on_page("Demographics")
    app_test.verification.text_present_on_page("Permissions")


@pytest.mark.ac_old_ui_smoke
def test_vendor_list(app_test, login):
    app_test.navigation.click_link("Vendors")
    app_test.internal_home_pages.select_vendor_status('Active')
    app_test.navigation_old_ui.click_input_btn("Go")
    time.sleep(10)
    assert (len(app_test.navigation_old_ui.get_columns_of_table()) > 0)


@pytest.mark.ac_old_ui_smoke
def test_invoices_list_table(app_test, login):
    expected_invoice_table_columns = ["Invoice ID",
                                      "Invoice Period",
                                      "Submitted",
                                      "Last Updated▾",
                                      "First Name",
                                      "Last Name",
                                      "Email Address",
                                      "User Status",
                                      "Termination Date",
                                      "Time Submitted",
                                      "# of Piece Rate Tasks",
                                      "EWOQ Variance",
                                      "EWOQ Tasks (norm)",
                                      "EWOQ TPH",
                                      "Current Status",
                                      "Amount",
                                      ]
    app_test.navigation.click_link("Invoices")
    app_test.navigation_old_ui.click_input_btn("Go")
    assert (len(app_test.navigation_old_ui.get_columns_of_table()) > 0)
    actual_invoice_table_columns = app_test.navigation_old_ui.get_columns_of_table()
    assert expected_invoice_table_columns == actual_invoice_table_columns, \
        "The titles of the main tabs %s are not matching with expected results %s" % (
            expected_invoice_table_columns, actual_invoice_table_columns)
