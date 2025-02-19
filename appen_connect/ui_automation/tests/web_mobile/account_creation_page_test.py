import random
import time

import pytest
from faker import Faker

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user

pytestmark = pytest.mark.regression_ac_web_mobile

faker = Faker()


@pytest.fixture(scope="function", autouse=True)
def open_sign_up_page(app):
    app.ac_user.sign_up_contributor_experience()


def test_web_mobile_sign_up_login_page(app, open_sign_up_page):
    app.navigation.refresh_page()
    app.navigation.click_link('Log In!')
    time.sleep(3)
    app.verification.text_present_on_page('Login with Appen SSO')


def test_web_mobile_sign_up_with_correct_data(app, open_sign_up_page):
    user_data = generate_data_for_contributor_experience_user()
    app.sign_up_web_mobile.create_uses(user_data)

    app.navigation.click_bytext("Create Account")
    app.verification.text_present_on_page("Verify E-mail")
    app.sign_up_web_mobile.sign_up_page.send_verification_code("999999")
    app.navigation.click_btn("Verify E-mail")
    time.sleep(2)
    app.ac_user.login_as(user_name=user_data['email'], password=user_data['password'], open_login_page=False)
    app.verification.text_present_on_page("Account Created")


@pytest.mark.parametrize('password, error',
                         [('cF_!2w', 'Password must be at least 8 characters long'),
                          ('cfghtyuq', 'Password does not meet minimum security requirements'),
                          ('12asDfgh', 'Password does not meet minimum security requirements'),
                          ('!asFgfhW', 'Password does not meet minimum security requirements')]
                         )
def test_web_mobile_sign_up_with_incorrect_password(app, open_sign_up_page, password, error):
    name = faker.name().split(' ')
    firstname = name[0]
    app.navigation.refresh_page()
    app.sign_up_web_mobile.sign_up_page.set_password(password)
    app.sign_up_web_mobile.sign_up_page.set_first_name(firstname)

    app.verification.text_present_on_page(error)


@pytest.mark.parametrize('email, password, firstname, lastname, error',
                         [('', 'cfghty!2Uq', 'Josh', 'Bonton', 'Required field'),
                          ('integration+josh@appen.com', 'cfghty!2uq', '', 'Bonton', 'Required field'),
                          ('integration+josh@appen.com', '', 'Josh', 'Bonton', 'Required field'),
                          ('integration+josh@appen.com', 'cfghty!2uq', 'Josh', '', 'Required field')]
                         )
def test_web_mobile_sign_up_with_miss_require_field(app, open_sign_up_page, email, password, firstname, lastname,
                                                    error):
    app.navigation.refresh_page()
    app.sign_up_web_mobile.sign_up_page.set_email(email)
    app.sign_up_web_mobile.sign_up_page.set_password(password)
    app.sign_up_web_mobile.sign_up_page.set_first_name(firstname)
    app.sign_up_web_mobile.sign_up_page.set_last_name(lastname)
    app.sign_up_web_mobile.sign_up_page.click_by_agree_term()

    app.verification.text_present_on_page(error)


def test_web_mobile_sign_up_password_information_button(app, open_sign_up_page):
    app.navigation.refresh_page()
    app.sign_up_web_mobile.sign_up_page.click_on_read_info()
    time.sleep(2)
    text = app.sign_up_web_mobile.sign_up_page.read_info()
    assert text == "Password Requirements Your password must:  • be 8 characters long • contain at least 1 number • " \
                   "contain at least 1 upper case letter • contain at least 1 lower case letter • contain at least 1 " \
                   "of the following special characters: @#!$%&+=-_"


def test_web_mobile_sign_up_firstname_information_button(app, open_sign_up_page):
    app.navigation.refresh_page()
    app.sign_up_web_mobile.sign_up_page.click_on_read_info(index=1)
    text = app.sign_up_web_mobile.sign_up_page.read_info()
    assert text == "First Name: Legal Name We need you to enter your legal name, once we use this information for payment."


@pytest.mark.parametrize("link, verification_message",
                         [
                             ("Terms of Service", 'Appen Contributor Portal Terms of Service'),
                             ("Privacy Policy", "Appen Privacy Statement")
                         ])
def test_web_mobile_sign_up_link_pages(app, open_sign_up_page, link, verification_message):
    app.navigation.refresh_page()
    app.navigation.click_link(link)
    app.navigation.switch_to_window(app.driver.window_handles[1])
    app.verification.text_present_on_page(verification_message)
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])
