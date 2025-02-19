import time
import datetime as ds
from adap.api_automation.utils.data_util import get_test_data
from adap.api_automation.utils.judgments_util import create_screenshot
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from appen_connect.api_automation.services_config.endpoints.identity_service import URL as identity_url
import pytest
from faker import Faker

from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import new_vendor

mark_env = pytest.mark.skipif(not pytest.env in ['stage'], reason="Stage only")
pytestmark = [pytest.mark.regression_ac_landing_page, pytest.mark.regression_ac, pytest.mark.ac_ui_vendor_registration,
              mark_env]

landing_pages = [
    ('DuPage', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
               '=33a42d6286a7603059bda7ad457aa2f3',
     'Become a Quality Assurance Contractor',
     'English',
     'United States of America',
     '',
     False),
    ('Pow Wow', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
                '=d6b0a559f731012c8d8ca0b9e38e236a',
     'Outbound Calling Mapping Evaluator',
     'English',
     'United States of America',
     '',
     False),
    ('Atlas', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
              '=3261bd8cd88e33e9df7e669ff4a6c4a1',
     'Mapping Evaluator',
     'English',
     'United States of America',
     '',
     False),
    ('Conness', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
                '=161df3697223cc3de228a62216c3db8a',
     'Become a Social Media Ads Evaluator',
     'English',
     'United States of America',
     '',
     False),
    ('Uolo', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
             '=e0aad7745db8121571ac38357c0dc2f7',
     'Become a Social Media Evaluator',
     'English',
     'United States of America',
     '',
     False),
    ('Rowley', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
               '=ae2c59288cef70f07d58ace3e24c24cd',
     'Become a Quality Assurance Contractor',
     'English',
     'United States of America',
     '',
     False),
    ('Reedy Top N', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr'
                    '=4ed4e7c529f5d3d301fbcba7449f29ed',
     'Become a Social Media Evaluator',
     'English',
     'United States of America',
     '',
     False),
    ('Toccata', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr=c84b8676f3a374cae9faa5d51838d20d',
     'Become a Social Media Evaluator',
     'English',
     'Philippines',
     'landing_page_toccata',
     False),
    ('Enoree', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr=bac1aea8b330807a979eb6100a25c62b',
     'Become a Video Evaluator',
     'English',
     'Philippines',
     'landing_page_enoree',
     False),
    ('Reedy', 'https://connect-stage.integration.cf3.us/qrp/public/project?pftr=6fc1815f61c08e20fabd47e9b01272e3',
     'Become a Social Media Evaluator',
     'English',
     'Philippines',
     'landing_page_reedy',
     False
     )
]


@pytest.mark.parametrize('name, landing_url, project_name,  language, region, vendor, apply_project',
                         landing_pages)
def test_not_interested_in_project_landing_page(app_test,
                                                name,
                                                landing_url,
                                                project_name,
                                                language,
                                                region,
                                                vendor,
                                                apply_project
                                                ):
    app_test.navigation.open_page(landing_url)
    time.sleep(1)

    app_test.navigation.accept_cookies()

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.verification.text_present_on_page(project_name)
    app_test.ac_user.shasta_click_btn("I’m not interested in this project")

    app_test.verification.text_present_on_page("Create an Account")
    app_test.verification.text_present_on_page("Sign In")

    # create account
    app_test.ac_user.shasta_click_btn("Create an Account")
    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.verification.text_present_on_page("Create your account")
    app_test.verification.text_present_on_page("EMAIL ADDRESS")
    app_test.verification.text_present_on_page("First Name")

    app_test.verification.current_url_contains('/qrp/core/sign-up')

    # Sign in
    app_test.navigation.browser_back()
    app_test.navigation.switch_to_frame("page-wrapper")
    app_test.ac_user.shasta_click_btn("I’m not interested in this project")
    app_test.ac_user.shasta_click_btn("Sign In")

    app_test.verification.current_url_contains(identity_url(pytest.env))
    app_test.verification.current_url_contains('/auth/realms/QRP/protocol/openid-connect/')


@pytest.mark.parametrize('name, landing_url, project_name,  language, region, vendor, apply_project',
                         landing_pages)
def test_project_sign_in_landing_page(app_test,
                                      name,
                                      landing_url,
                                      project_name,
                                      language,
                                      region,
                                      vendor,
                                      apply_project
                                      ):
    app_test.navigation.open_page(landing_url)
    time.sleep(1)

    app_test.navigation.accept_cookies()

    app_test.navigation.switch_to_frame("page-wrapper")

    app_test.ac_user.shasta_click_btn("Start now! Apply to {name}.".format(name=name))
    app_test.ac_user.shasta_click_btn("Sign In")

    if vendor:
        vendor_email = get_test_data(vendor, 'email')
        vendor_password = get_test_data(vendor, 'password')

        app_test.ac_user.login_as(user_name=vendor_email, password=vendor_password)
        app_test.navigation.switch_to_frame("page-wrapper")
        app_test.verification.text_present_on_page('You are a project match!')

        app_test.navigation.click_btn('Fill & Submit Profile')
