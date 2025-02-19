import time

from adap.api_automation.utils.data_util import get_test_data
from appen_connect.api_automation.services_config.endpoints.identity_service import URL as identity_url
from adap.ui_automation.utils.selenium_utils import click_element_by_xpath
import pytest

pytestmark = [pytest.mark.regression_ac_yukon]

URL = {
    "stage": "https://connect-stage.integration.cf3.us/qrp/public/project?pftr=a0d493f24e1ed6e7e51633351322906c"
}


def test_landing_page_yukon(app_test):
    app_test.navigation.open_page(URL[pytest.env])

    try:
        app_test.navigation.click_btn("Accept All Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.verification.text_present_on_page("Search Evaluation")
    app_test.verification.text_present_on_page("Join Yukon as a Search Evaluator")
    app_test.verification.text_present_on_page("A flexible and rewarding work from home opportunity:")
    app_test.verification.text_present_on_page("Embrace the opportunity to become a part-time employee with a "
                                               "competitive pay, starting at $14/hour and the flexibility to work "
                                               "from home. As a valued contributor, you'll assess and analyze search "
                                               "results for specific queries, helping search engines provide more "
                                               "precise and relevant results. Experience the perfect balance of "
                                               "flexible work and meaningful impact with the Yukon project.")
    app_test.verification.text_present_on_page("No experience necessary, all you need is:")
    app_test.verification.text_present_on_page("Be eligible to work in the United States")
    app_test.verification.text_present_on_page("A smart phone and a personal computer")
    app_test.verification.text_present_on_page("Ability to work independently with minimal supervision")
    app_test.verification.text_present_on_page("Detail-orientated")
    app_test.verification.text_present_on_page("Commitment of at least 15hrs per week [flexible schedule]")
    app_test.verification.text_present_on_page("Gmail account and be willing to install an app on your phone")

    app_test.verification.text_present_on_page("As a valued contributor, you'll have access to:")
    app_test.verification.text_present_on_page("Live webinars")
    app_test.verification.text_present_on_page("A dedicated Yukon Quality team for support")
    app_test.verification.text_present_on_page("Simulated practice tasks to hone your skills")
    app_test.verification.text_present_on_page("Interactive decision trees for guidance")

    app_test.verification.text_present_on_page("How to sign up and join:")
    app_test.verification.text_present_on_page("Click the “Start Now! Apply to Yukon” button")
    app_test.verification.text_present_on_page("Complete your profile and project registration [5 min]")
    app_test.verification.text_present_on_page("We’ll email you when your application is approved [usually within 24 hrs]")
    app_test.verification.text_present_on_page("Pass a 3-part exam [prep and exam time 10-12 hrs]")
    app_test.verification.text_present_on_page("Start making money!")

    app_test.verification.text_present_on_page("Start now! Apply to Yukon.")
    app_test.verification.text_present_on_page("I want to learn more about joining the Yukon project.")

    app_test.verification.text_present_on_page("I’m not interested in this project, but I would like to check out "
                                               "other Appen opportunities.")


def test_no_yukon_project_create_account(app):
    app.navigation.open_page(URL[pytest.env])

    try:
        app.navigation.click_btn("Accept All Cookies")
    except:
        print("no Accept Cookies button")

    app.navigation.switch_to_frame("page-wrapper")

    app.ac_user.shasta_click_btn("I’m not interested in this project, but I would like to check out other Appen "
                                 "opportunities.")

    app.verification.text_present_on_page("Create an Account")
    app.verification.text_present_on_page("Sign In")

    app.ac_user.shasta_click_btn("Create an Account")
    app.navigation.switch_to_frame("page-wrapper")

    app.verification.text_present_on_page("Create your account")
    app.verification.text_present_on_page("EMAIL ADDRESS")
    app.verification.text_present_on_page("First Name")

    app.verification.current_url_contains('/qrp/core/sign-up')


def test_no_yukon_project_sign_in(app):
    app.navigation.open_page(URL[pytest.env])

    try:
        app.navigation.click_btn("Accept All Cookies")
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


def test_yukon_project_sign_in(app_test):
    app_test.navigation.open_page(URL[pytest.env])

    try:
        app_test.navigation.click_btn("Accept All Cookies")
    except:
        print("no Accept Cookies button")

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.ac_user.shasta_click_btn("Start now! Apply to Yukon.")
    app_test.ac_user.shasta_click_btn("Sign In")

    USER_NAME = get_test_data('yukon_express_user', 'email')
    PASSWORD = get_test_data('yukon_express_user', 'password')

    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.verification.text_present_on_page('Yukon')
    app_test.verification.text_present_on_page('Work This')

