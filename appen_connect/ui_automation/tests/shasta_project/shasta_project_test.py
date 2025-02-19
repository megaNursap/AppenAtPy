import time
import datetime as ds
from adap.api_automation.utils.data_util import get_test_data
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from appen_connect.api_automation.services_config.endpoints.identity_service import URL as identity_url
import pytest
from faker import Faker

from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor

pytestmark = [pytest.mark.regression_ac_shasta, pytest.mark.regression_ac,  pytest.mark.ac_ui_vendor_registration]


URL = {
    "stage": "https://connect-stage.integration.cf3.us/qrp/public/project?pftr=29f44d8af69bcd7384d314395dada220",
    "qa":  "https://connect-qa.sandbox.cf3.us/qrp/public/project?pftr=29f44d8af69bcd7384d314395dada220"
}


def test_landing_page_shasta(app_test):
    app_test.navigation.open_page(URL[pytest.env])
    time.sleep(7)
    try:
        app_test.navigation.click_btn("Accept Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.verification.text_present_on_page("Search Evaluation")
    app_test.verification.text_present_on_page("Shasta")
    app_test.verification.text_present_on_page("Project Shasta is part of Appen’s global partnership with one of the "
                                               "largest technology companies in the world! It is a maps search "
                                               "relevance project that relies on individuals such as yourself to "
                                               "improve maps related search accuracy including:")
    app_test.verification.text_present_on_page("Join Project Shasta to help improve the machine learning and "
                                               "artificial intelligence used by millions of users around the globe "
                                               "every day, all from the comfort of your own home!")
    app_test.verification.text_present_on_page("Project requirements:")
    app_test.verification.text_present_on_page("Personal computer")
    app_test.verification.text_present_on_page("Stable internet access (No VPN’s or Proxy Connections)")
    app_test.verification.text_present_on_page("15 hours/week time commitment")
    app_test.verification.text_present_on_page("Complete and pass an online assessment test (approx. 2 hours to complete)")
    app_test.verification.text_present_on_page("To join Project Shasta, you will need to first create a profile with "
                                               "Appen to allow us to capture some important information, setup your "
                                               "payment account, and pass the qualification exam.")

    app_test.verification.text_present_on_page("Start now! Apply to Shasta.")
    app_test.verification.text_present_on_page("I want to learn more about joining the Shasta project.")

    app_test.verification.text_present_on_page("I’m not interested in this project, but I would like to check out "
                                               "other Appen opportunities.")


def test_no_shasta_project_create_account(app):
    app.navigation.open_page(URL[pytest.env])
    time.sleep(7)

    try:
        app.navigation.click_btn("Accept Cookies")
    except:
        print("no Accept Cookies button")

    app.navigation.switch_to_frame("page-wrapper")

    app.ac_user.shasta_click_btn("I’m not interested in this project")

    app.verification.text_present_on_page("Create an Account")
    app.verification.text_present_on_page("Sign In")

    app.ac_user.shasta_click_btn("Create an Account")
    app.navigation.switch_to_frame("page-wrapper")

    app.verification.text_present_on_page("Create your account")
    app.verification.text_present_on_page("EMAIL ADDRESS")
    app.verification.text_present_on_page("First Name")

    app.verification.current_url_contains('/qrp/core/sign-up')


def test_no_shasta_project_sign_in(app):
    app.navigation.open_page(URL[pytest.env])
    time.sleep(7)
    try:
        app.navigation.click_btn("Accept Cookies")
    except:
        print("no Accept Cookies button")

    app.navigation.switch_to_frame("page-wrapper")
    app.ac_user.shasta_click_btn("I’m not interested in this project")

    app.ac_user.shasta_click_btn("Sign In")

    app.verification.text_present_on_page("Login")
    app.verification.text_present_on_page("Email")
    app.verification.text_present_on_page("Password")
    app.verification.text_present_on_page("Remember me")

    app.verification.current_url_contains(identity_url(pytest.env))
    app.verification.current_url_contains('/auth/realms/QRP/protocol/openid-connect/')


def test_shasta_project_sign_in(app_test):
    app_test.navigation.open_page(URL[pytest.env])
    time.sleep(7)

    try:
        app_test.navigation.click_btn("Accept Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.ac_user.shasta_click_btn("Start now! Apply to Shasta.")
    app_test.ac_user.shasta_click_btn("Sign In")

    USER_NAME = get_test_data('test_shasta_account', 'email')
    PASSWORD = get_test_data('test_shasta_account', 'password')

    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.verification.text_present_on_page('Shasta')
    app_test.verification.text_present_on_page('Work This')

    assert app_test.vendor_pages.project_found_on_page('Shasta')


@pytest.mark.dependency()
def test_shasta_project_create_account(app_test):
    fake = Faker()
    app_test.navigation.open_page(URL[pytest.env])
    time.sleep(7)

    try:
        app_test.navigation.click_btn("Accept Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.ac_user.shasta_click_btn("Start now! Apply to Shasta.")
    app_test.ac_user.shasta_click_btn("Create an Account")

    verification_code = {
        "stage": "05C799",
        "qa": "D92570"
    }
    global shasta_vendor
    shasta_vendor = new_vendor(app_test, pr='sha_', verification_code=verification_code[pytest.env],
                        language='English', region='United States of America',state='Alabama', open_sign_up_page=False)


    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.verification.text_present_on_page('Shasta´s Project Requirements')
    app_test.verification.text_present_on_page('You are a project match!')

    app_test.navigation.click_btn('Fill & Submit Profile')

    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.vendor_profile.open_tab('Location')
    #residency_history_date = (ds.date.today() - ds.timedelta(days=1800)).strftime("%Y/%m/%d")
    residency_history_years = "2 years"
    app_test.vendor_profile.location.fill_out_fields({"Street Address": "12529 State Road 535",
                                                 "CITY": "Birmingham",
                                                 "ZIP CODE": "35211"
                                                 #"Residency History": residency_history_date
                                                 })
    app_test.vendor_profile.location.residence_history_of_worker(residency_history_years)


    app_test.navigation.click_btn("Next: Education")

    app_test.vendor_profile.open_tab('Education')
    app_test.vendor_profile.education.fill_out_fields(
        {
            "HIGHEST LEVEL OF EDUCATION": "Doctorate degree or equivalent",
            "LINGUISTICS QUALIFICATION": "Doctoral degree – Completed"
        }
    )
    app_test.navigation.click_btn("Next: Work Experience")

    app_test.vendor_profile.open_tab('Phone Number')
    app_test.vendor_profile.phone.fill_out_fields({"Mobile Phone Number": fake.phone_number()})
    app_test.navigation.click_btn("Next: Preview")

    app_test.vendor_profile.open_tab('Preview')
    scroll_to_page_bottom(app_test.driver)
    app_test.navigation.click_btn("Save and Submit Profile")
    time.sleep(3)
    app_test.navigation.click_btn("Continue")

    app_test.verification.current_url_contains("/complete_profile/smartphone")
    app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio', 'No')[0].click()
    app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Continue')[0].click()
    app_test.verification.current_url_contains("/complete_profile/view")
    additional_info_elements = app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('radio',
                                                                                                        'false')
    for i in range(0, 3):
        additional_info_elements[i].click()
    app_test.vendor_profile.registration_flow.select_familiarity_level('Expert')
    app_test.vendor_profile.registration_flow.select_value_for_choice_and_proceed('submit', 'Submit')[0].click()
    app_test.verification.current_url_contains("/process_resolution")
    app_test.navigation.click_link("Logout")

    print("------", shasta_vendor)


@pytest.mark.dependency(depends=["test_shasta_project_create_account"])
def test_shasta_project_add_vendor(app_test):
    PASSWORD = get_test_data('test_ui_account', 'password')
    INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')

    app_test.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)

    app_test.navigation.click_link("Vendors")
    app_test.vendor_pages.open_vendor_profile_by(shasta_vendor['vendor'], search_type='name', status='Any Status')

    app_test.vendor_pages.add_vendor_to_project(project_name='Apple Shasta', locale='English (United States)', action='Add')
    time.sleep(2)

    app_test.vendor_pages.vendor_qualification_action("Completed")


@pytest.mark.dependency(depends=["test_shasta_project_add_vendor"])
def test_shasta_vendor_project_access(app_test):
    app_test.navigation.open_page(URL[pytest.env])
    time.sleep(7)

    try:
        app_test.navigation.click_btn("Accept Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.ac_user.shasta_click_btn("Start now! Apply to Shasta.")
    app_test.ac_user.shasta_click_btn("Sign In")

    app_test.ac_user.login_as(user_name=shasta_vendor['vendor'], password=shasta_vendor['password'])

    electronic_signature = True
    while electronic_signature:
        try:
            app_test.vendor_profile.registration_flow.sign_the_form(user_name=shasta_vendor['vendor'],
                                                               user_password=shasta_vendor['password'], action="I Agree")
        except:
            electronic_signature = False

    # app_test.navigation.click_link('Projects')
    # app_test.navigation.switch_to_frame("page-wrapper")
    assert app_test.vendor_pages.project_found_on_page('Shasta')
