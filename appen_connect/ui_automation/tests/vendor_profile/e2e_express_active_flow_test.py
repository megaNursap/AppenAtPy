"""
       Test will Create an Express Active user
"""
import time
import random
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import *

USER_NAME = "sandbox+" + str(random.randint(1000000, 9999999)) + "@figure-eight.com"
PASSWORD = get_test_data('test_ui_account', 'password')
INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')
VERIFICATION_CODE = "4FC81D"

pytestmark = [pytest.mark.regression_ac_vendor_profile,
              pytest.mark.regression_ac,
              pytest.mark.ac_ui_uat,
              pytest.mark.ac_ui_express_user_flow,
              pytest.mark.ac_ui_vendor_registration]


@pytest.fixture(scope="module")
@pytest.mark.ac_ui_smoke
def register(app):
    app.vendor_profile.registration_flow.register_user(user_name=USER_NAME, user_password=PASSWORD,
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')
    app.vendor_profile.registration_flow.fill_out_fields({"CERTIFY DATA PRIVACY": 1,
                                                          "CERTIFY SSN": 1}, action="Create Account")
    app.vendor_profile.registration_flow.fill_out_fields({"VERIFICATION CODE": VERIFICATION_CODE},
                                                         action="Verify Email")


@pytest.mark.dependency()
@pytest.mark.ac_ui_smoke
def test_check_account_created_express(app, register):
    app.verification.text_present_on_page("Account Created")
    app.verification.text_present_on_page("You will be redirected to login into the system.")
    app.verification.text_present_on_page("Questions about this SSO login, please")
    app.verification.text_present_on_page("read our FAQ page.")
    app.navigation.click_btn("Go to Login page")


@pytest.mark.dependency(depends=["test_check_account_created_express"])
@pytest.mark.ac_ui_smoke
def test_check_express_qualifying_status_express(app, register):
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

    # TODO Get URL from appen_connect/api_automation/services_config/endpoints/core.py

    global url
    if app.env == "stage":
        url = "https://connect-" + app.env + ".integration.cf3.us/qrp/core/vendor/view/" + vendor_id
    else:
        if app.env == "qa":
            url = "https://connect-" + app.env + ".sandbox.cf3.us/qrp/core/vendor/view/" + vendor_id
        else:
            url = "https://connect.appen.com/qrp/core/vendor/view/" + vendor_id

    assert app.vendor_pages.get_vendor_status() == "EXPRESS QUALIFYING"
    app.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_check_express_qualifying_status_express"])
def test_set_up_language_express(app, register):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.verification.current_url_contains('/qrp/core/vendors/primary_language')
    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page("Language")
    app.vendor_profile.registration_flow.fill_out_fields({"YOUR PRIMARY LANGUAGE": "English",
                                                          "YOUR LANGUAGE REGION": "United States of America"})
    app.navigation.click_btn("Continue")
    time.sleep(1)


#
# @pytest.mark.skip(reason='Deprecated')
# @pytest.mark.dependency(depends=["test_set_up_language_express"])
# def test_demographic_survey(app, register):
#     app.verification.current_url_contains("/qrp/core/vendors/demographic_survey")
#     app.navigation.switch_to_frame("page-wrapper")
#     app.verification.text_present_on_page("Informed Consent Form for Appen Crowd Research")
#     app.verification.text_present_on_page("Activity Contact: support@connect-mail.appen.com")
#     assert not app.verification.button_is_disable("Decline")
#     assert not app.verification.button_is_disable("Accept")
#     app.navigation.click_btn("Accept")
#     app.verification.current_url_contains("/qrp/core/vendors/demographic_survey")
#     app.verification.text_present_on_page("Demographic Data Survey")
#     app.verification.text_present_on_page("See targeted jobs opportunities by disclosing your demographic information.")
#     app.navigation.click_btn("Skip")


@pytest.mark.dependency(depends=["test_set_up_language_express"])
def test_welcome_page_express(app, register):
    app.verification.current_url_contains("/qrp/core/vendors/projects")
    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page("Suggested")
    app.verification.text_present_on_page("Applied")
    app.verification.text_present_on_page("Continue profile")
    app.verification.text_present_on_page("My Projects")
    app.verification.text_present_on_page("All Projects")
    #app.vendor_profile.registration_flow.get_start_from_welcome_page("Unlock long-Term Projects")


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/ACE-11296")
@pytest.mark.dependency(depends=["test_welcome_page_express"])
def test_apply_project_express(app, register):
    app.vendor_profile.registration_flow.refresh_page_and_wait_until_project_load(5, 1000, 'No Projects Yet',
                                                                                  'page-wrapper')
    app.vendor_profile.registration_flow.apply_the_project_by_name("Automatic Express Project - Auto Screening")
    time.sleep(3)
    # app.navigation.click_btn("Continue To Registration")
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio', 'No')[0].click()
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()
    app.navigation.refresh_page()
    time.sleep(10)
    app.vendor_pages.close_process_status_popup()
    app.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_apply_project_express"])
def test_end_registration_and_qualification_flow_express(app, register):
    app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
    go_to_page(app.driver, url)
    app.navigation.click_link("Projects")
    app.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Completed')[0].click()
    time.sleep(3)
    app.navigation.click_btn("Confirm")
    time.sleep(3)
    app.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_end_registration_and_qualification_flow_express"])
def test_add_paypal_information(app, register):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.vendor_profile.registration_flow.add_paypal(user_name=USER_NAME)
    app.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_add_paypal_information"])
def test_sign_form_again_express(app,register):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    #app.vendor_profile.registration_flow.sign_the_form(user_name=USER_NAME, user_password=PASSWORD, action="I Agree")
    app.vendor_profile.registration_flow.accept_the_form(action='I understand and agree')
    app.navigation.click_btn("Continue")
    app.navigation.click_link("Logout")


@pytest.mark.dependency(depends=["test_sign_form_again_express"])
def test_check_express_active_status(app, register):
    app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
    go_to_page(app.driver, url)
    assert "ROLE_USER" in app.vendor_pages.get_roles()
    assert "ROLE_VENDOR_EXPRESS" in app.vendor_pages.get_roles()
    assert app.vendor_pages.get_vendor_status() == "EXPRESS ACTIVE"
    app.navigation.click_link("Logout")
