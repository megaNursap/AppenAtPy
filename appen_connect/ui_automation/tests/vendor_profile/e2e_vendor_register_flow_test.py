"""
https://appen.atlassian.net/browse/QED-2259
This test covers end to end registration flow, test cases steps here:
https://appen.spiraservice.net/5/TestCase/3332.aspx
"""
import random
import time
import datetime as ds
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom

USER_NAME = "sandbox+" + str(random.randint(1000000, 9999999)) + "@figure-eight.com"
PASSWORD = get_test_data('test_ui_account', 'password')
INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')
VERIFICATION_CODE = {"stage":"4FC81D",
                     "qa":"CA0016"}

pytestmark = [pytest.mark.regression_ac_vendor_profile,
              pytest.mark.regression_ac,
              pytest.mark.ac_ui_uat,
              pytest.mark.ac_ui_vendor_registration]


@pytest.fixture(scope="module")
def register(app):
    app.vendor_profile.registration_flow.register_user(user_name=USER_NAME, user_password=PASSWORD,
                                                       user_first_name="firstname", user_last_name="lastname", residence_value='United States of America', state='Alabama')
    app.vendor_profile.registration_flow.fill_out_fields({"CERTIFY DATA PRIVACY": 1,
                                                          "CERTIFY SSN": 1}, action="Create Account")
    app.vendor_profile.registration_flow.fill_out_fields({"VERIFICATION CODE": VERIFICATION_CODE[pytest.env]}, action="Verify Email")


@pytest.mark.dependency()
def test_check_account_created(app, register):
    app.verification.text_present_on_page("Account Created")
    app.verification.text_present_on_page("You will be redirected to login into the system.")
    app.verification.text_present_on_page("Questions about this SSO login, please")
    app.verification.text_present_on_page("read our FAQ page.")
    app.navigation.click_btn("Go to Login page")


# Validate step 6 express qualifying status here https://appen.spiraservice.net/5/TestCase/3332.aspx
@pytest.mark.dependency(depends=["test_check_account_created"])
def test_check_express_qualifying_status(app, register):
    app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
    # app.navigation.maximize_window()
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Skip")
    app.driver.switch_to.default_content()
    app.navigation.click_link('Internal Home')
    app.navigation.click_link("Vendors")
    app.vendor_pages.open_vendor_profile_by(USER_NAME, search_type='name', status='Any Status')
    assert "ROLE_USER" in app.vendor_pages.get_roles()
    assert "ROLE_EXPRESS_PENDING" in app.vendor_pages.get_roles()
    vendor_id = app.vendor_pages.get_vendor_id()
    global url
    url = {
        "stage":"https://connect-" + app.env + ".integration.cf3.us/qrp/core/vendor/view/" + vendor_id,
        "qa": "https://connect-" + app.env + ".sandbox.cf3.us/qrp/core/vendor/view/" + vendor_id,
        "prod":"https://connect.appen.com/qrp/core/vendor/view/" + vendor_id
    }

    assert app.vendor_pages.get_vendor_status() == "EXPRESS QUALIFYING"
    app.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_check_express_qualifying_status"])
def test_set_up_language(app, register):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    time.sleep(3)
    app.verification.current_url_contains('/qrp/core/vendors/primary_language')
    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page("Language")
    app.vendor_profile.registration_flow.fill_out_fields({"YOUR PRIMARY LANGUAGE": "English",
                                                         "YOUR LANGUAGE REGION": "United States of America"})
    app.navigation.click_btn("Continue")



@pytest.mark.dependency(depends=["test_set_up_language"])
def test_welcome_page(app, register):
    time.sleep(2)
    app.verification.current_url_contains("/qrp/core/vendors/projects")
    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page("Suggested")
    app.verification.text_present_on_page("Applied")
    app.verification.text_present_on_page("Continue Profile")
    app.verification.text_present_on_page("My Projects")
    app.verification.text_present_on_page("All Projects")
    app.vendor_profile.registration_flow.get_start_from_welcome_page("Continue Profile")


@pytest.mark.dependency(depends=["test_welcome_page"])
def test_finish_location_setup(app, register):
    app.verification.current_url_contains("/vendors/user_profile_setup")
    app.navigation.switch_to_frame("page-wrapper")
    app.vendor_profile.open_tab('Location')
    residency_history_date = (ds.date.today() - ds.timedelta(days=1800)).strftime("%Y/%m/%d")
    # https://appen.atlassian.net/browse/QED-2789 created this, I am not able to interactive this element
    app.vendor_profile.location.fill_out_fields({"Street Address": "12529 State Road 535",
                                                 "CITY": "Birmingham",
                                                 "ZIP CODE": "35211",
                                                 "YEARS": "2 years"
                                                 #"Residency History": residency_history_date
                                                 })

    app.navigation.click_btn("Next: Education")


@pytest.mark.dependency(depends=["test_finish_location_setup"])
def test_finish_education_setup(app, register):
    app.vendor_profile.open_tab('Education')
    app.verification.text_present_on_page("STEP 04")
    app.verification.text_present_on_page("Enter information about your education level")
    app.vendor_profile.education.fill_out_fields(
        {
            "HIGHEST LEVEL OF EDUCATION": "Doctorate degree or equivalent",
            "LINGUISTICS QUALIFICATION": "Doctoral degree – Completed"
        }
    )
    app.navigation.click_btn("Next: Work Experience")


@pytest.mark.dependency(depends=["test_finish_education_setup"])
def test_finish_phone_number_setup(app, register):
    app.vendor_profile.open_tab('Phone Number')
    app.verification.text_present_on_page("STEP 06")
    app.verification.text_present_on_page("Add at least one phone number for personal contact")
    app.verification.text_present_on_page("Mobile Phone Number")
    app.vendor_profile.phone.fill_out_fields({"Mobile Phone Number": "205-225-1234"})
    app.navigation.click_btn("Next: Preview")


@pytest.mark.dependency(depends=["test_finish_phone_number_setup"])
def test_save_and_submit_profile(app, register):
    app.vendor_profile.open_tab('Preview')
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Save and Submit Profile")
    time.sleep(3)
    app.navigation.click_btn("Continue")


@pytest.mark.dependency(depends=["test_save_and_submit_profile"])
def test_smartphone_questionnaire(app, register):
    app.verification.current_url_contains("/complete_profile/smartphone")
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio', 'No')[0].click()
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()
    app.verification.current_url_contains("/complete_profile/view")
    additional_info_elements = app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio', 'false')
    for i in range(0, 3):
        additional_info_elements[i].click()
    app.vendor_profile.registration_flow.select_familiarity_level('Expert')
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Submit')[0].click()
    app.verification.current_url_contains("/process_resolution")
    app.navigation.click_link("Logout")


# Validate step 64 application received here https://appen.spiraservice.net/5/TestCase/3332.aspx
@pytest.mark.dependency(depends=["test_smartphone_questionnaire"])
def test_check_application_received_status(app, register):
    app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
    go_to_page(app.driver, url.get(app.env))
    assert "ROLE_USER" in app.vendor_pages.get_roles()
    assert "ROLE_EXPRESS_PENDING" in app.vendor_pages.get_roles()
    assert app.vendor_pages.get_vendor_status() == "APPLICATION RECEIVED"


# Validate step 65 and 66 screened status here https://appen.spiraservice.net/5/TestCase/3332.aspx
@pytest.mark.dependency(depends=["test_check_application_received_status"])
def test_click_complete_and_check_screened_status(app, register):
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Completed')[0].click()
    app.vendor_profile.registration_flow.select_option_and_proceed('complete-reason', 'REGISTRATION_IP')
    app.navigation.click_btn('Complete')

    go_to_page(app.driver, url.get(app.env))
    assert "ROLE_USER" in app.vendor_pages.get_roles()
    assert "ROLE_EXPRESS_PENDING" in app.vendor_pages.get_roles()
    assert app.vendor_pages.get_vendor_status() == "SCREENED"
    app.navigation.click_link("Logout")


 # Validate step 68~70 here https://appen.spiraservice.net/5/TestCase/3332.aspx
@pytest.mark.dependency(depends=["test_click_complete_and_check_screened_status"])
def test_sign_form(app, register):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    form_titles = ["APPEN ELECTRONIC RECORDS CONSENT FORM", "APPEN BONA FIDE OCCUPATIONAL QUALIFICATION DISCLOSURE", "APPEN CONFIDENTIALITY AGREEMENT"]
    for i in range(0, 3):
        app.verification.text_present_on_page(form_titles[i])
        app.vendor_profile.registration_flow.accept_the_form(action="I Agree")
        app.navigation.click_btn("Continue")
    time.sleep(2)
    app.verification.current_url_contains("/qrp/core/vendors/projects")
    app.navigation.click_link("Logout")


# Validate step 71 contract pending status here https://appen.spiraservice.net/5/TestCase/3332.aspx
@pytest.mark.dependency(depends=["test_sign_form"])
def test_check_contract_pending_status(app, register):
    app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
    go_to_page(app.driver, url.get(app.env))
    assert "ROLE_USER" in app.vendor_pages.get_roles()
    assert "ROLE_EXPRESS_PENDING" in app.vendor_pages.get_roles()
    assert "ROLE_CONTRACT_PENDING" in app.vendor_pages.get_roles()
    assert app.vendor_pages.get_vendor_status() == "CONTRACT PENDING"
    app.navigation.click_link("Logout")


# Step 72 apply project
# Steps changed, need to update
@pytest.mark.dependency(depends=["test_check_contract_pending_status"])
def test_apply_project(app, register):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.vendor_profile.registration_flow.refresh_page_and_wait_until_project_load(5, 1000, 'No Projects Yet', 'page-wrapper')
    app.vendor_profile.registration_flow.apply_the_project_by_name("Automation Express Project")
    time.sleep(3)
    #app.vendor_profile.registration_flow.sign_the_form(user_name=USER_NAME, user_password=PASSWORD, action="I Agree")
    app.vendor_profile.registration_flow.accept_the_form(action="I Agree")
    app.navigation.click_btn("Continue")
    app.vendor_profile.registration_flow.select_option_and_proceed('attributes[0].stringValue', 'Windows')
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Save')[0].click()
    app.vendor_profile.registration_flow.accept_the_form(action="I Agree")
    app.navigation.click_btn("Continue")
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio', 'No')[0].click()
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()

    app.navigation.click_btn("Close")
    app.navigation.click_link("Logout")


# # Step 73 click complete on vendor page
# @pytest.mark.dependency(depends=["test_apply_project"])
# def test_end_registration_and_qualification_flow(app, register):
#     app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
#     go_to_page(app.driver, url.get(app.env))
#     app.navigation.click_link("Projects")
#     app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Completed')[0].click()
#     time.sleep(3)
#     app.navigation.click_link("Logout")


# # step 74, sign other documents
# @pytest.mark.dependency(depends=["test_end_registration_and_qualification_flow"])
# def test_sign_form_again(app, register):
#     app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
#     for i in range(0, 3):
#         app.vendor_profile.registration_flow.sign_the_form(user_name=USER_NAME, user_password=PASSWORD, action="I Agree")
#     app.navigation.click_link("Logout")

#
# # step 75, validate payoneer setup status
# @pytest.mark.dependency(depends=["test_apply_project"])
# def test_check_payoneer_setup_status(app, register):
#     app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
#     go_to_page(app.driver, url.get(app.env))
#     assert "ROLE_USER" in app.vendor_pages.get_roles()
#     assert "ROLE_EXPRESS_PENDING" in app.vendor_pages.get_roles()
#     assert "ROLE_CONTRACT_PENDING" in app.vendor_pages.get_roles()
#     assert app.vendor_pages.get_vendor_status() == "PAYONEER SETUP"
#     app.navigation.click_link("Logout")