
import time

import pytest

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user
from appen_connect.api_automation.services_config.contributor_experience import ContributorExperience

pytestmark = pytest.mark.regression_ac_web_mobile


@pytest.fixture(scope="function", autouse=True)
def open_sign_up_page(app):
    user = ContributorExperience()
    user_data = generate_data_for_contributor_experience_user()
    res = user.post_create_user(email=user_data['email'], password=user_data['password'],
                                firstname=user_data['firstname'], lastname=user_data['lastname'])

    app.ac_user.sign_up_contributor_experience(endpoint="/account-setup")
    app.ac_user.login_as(user_name=res.json_response['email'], password=user_data['password'])
    app.verification.text_present_on_page("Account Created")
    app.verification.text_present_on_page("All you have to do now is complete the account setup process in just three "
                                          "simple steps, and you'll be ready to start earning right away!")
    app.navigation.click_btn("Set Up My Account")
    app.verification.wait_until_text_disappear_on_the_page("Account Created", 5)
    return [user_data['email'], user_data['password']]


def test_web_mobile_decline_user(app, open_sign_up_page):
    app.navigation.click_btn('Decline')
    app.verification.text_present_on_page('Attention!')
    text_from_decline_modal = app.ce_account_setup.grab_text_from_pop_up()
    assert text_from_decline_modal == "Once you decline the agreements and consent we cannot continue with your " \
                                      "account setup and we won't continue with your account. If you wish to give up " \
                                      "with your Appen account, please click to decline and cancel account."
    app.navigation.click_btn("Decline & Cancel Account")
    time.sleep(2)
    app.verification.text_present_on_page("Sorry to see you go")
    app.verification.text_present_on_page("Log in", False)


def test_web_mobile_agreements_consent(app, open_sign_up_page):
    app.verification.text_present_on_page("Agreements & Consent")
    app.verification.text_present_on_page("APPEN CONFIDENTIALITY AGREEMENT")
    app.ce_account_setup.accept_consent()
    app.verification.text_present_on_page("About you")