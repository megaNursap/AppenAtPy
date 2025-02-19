import random
import re
import time

import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_test_data, generate_data_for_contributor_experience_user

pytestmark = pytest.mark.regression_ac_web_mobile


@pytest.fixture(scope='module', autouse=True)
def open_sign_up_page(app):
    user_setup_email = get_test_data("contributor_experience_setup", "email")
    user_setup_password = get_test_data("contributor_experience_setup", "password")
    app.ac_user.sign_up_contributor_experience(endpoint="/account-setup")
    app.ac_user.login_as(user_name=user_setup_email, password=user_setup_password, open_login_page=False)
    app.navigation.refresh_page()


def test_web_mobile_contact_tooltips(app, open_sign_up_page):
    """
    User could read tooltip for correct zipcode and mobile phone
    """
    app.sign_up_web_mobile.sign_up_page.click_on_read_info()
    zipcode_tip = app.sign_up_web_mobile.sign_up_page.read_info()
    assert zipcode_tip == " Zip or Postal Code Your contract information for forthcoming projects will include this " \
                          "information. If your region does not use zip or postal code, use 00000."

    app.navigation.click_btn("Close")
    time.sleep(1)

    app.sign_up_web_mobile.sign_up_page.click_on_read_info(index=1)
    time.sleep(2)
    phone_number_tip = app.sign_up_web_mobile.sign_up_page.read_info()

    assert phone_number_tip == " Mobile Phone Number If you opt-in, we may use your number to send you SMS text messages concerning new " \
                               "task opportunities, task updates, and any necessary verifications such as " \
                               "second-factor authentication."

    app.navigation.click_btn("Close")


@pytest.mark.parametrize('country, country_code',
                         [
                             ("Australia", "+61"),
                             ("China", "+86"),
                             ("United Kingdom", "+44"),
                             ("Brazil", "+55")
                         ])
def test_web_mobile_mobile_phone_based_on_selected_country(app, open_sign_up_page, country, country_code):
    """
    Based on the selected country the first two number of mobile phone set up to this country
    """
    app.ce_account_setup.contact_page.set_country_live(country)
    country_flag = app.ce_account_setup.contact_page.get_mobile_phone_flag().split(':')
    assert country == country_flag[0]
    country_phone_code = app.ce_account_setup.contact_page.get_phone_number_value()
    assert country_code == country_phone_code



def test_web_mobile_select_state_province(app, open_sign_up_page):
    """
    User should select state if that require by selected country
    eg. United State of America, for other country the state should be disabled
    """
    app.ce_account_setup.contact_page.set_country_live('United States of America')
    app.ce_account_setup.contact_page.set_state('California')

    app.verification.text_present_on_page('California')


def test_web_mobile_select_state_province_disabled(app, open_sign_up_page):
    """
       User couldn't select state if the selected country not contain state
    """
    app.ce_account_setup.contact_page.set_country_live('Poland')
    app.ce_account_setup.verify_state_of_element('disabled', app.ce_account_setup.contact_page.STATE)


def test_web_mobile_error_message_displays(app, open_sign_up_page):
    """
     Verify if user not fill all field then he couldn't finish set up and error message appears
    """
    app.ce_account_setup.contact_page.set_country_live('Canada')
    app.ce_account_setup.contact_page.set_state('')
    app.ce_account_setup.contact_page.set_full_address('')
    app.ce_account_setup.contact_page.set_zip_code('')
    app.ce_account_setup.contact_page.set_mobile_phone('')
    app.ce_account_setup.contact_page.set_city('')
    app.ce_account_setup.contact_page.check_receive_email()

    error_msgs = app.ce_account_setup.about_you_page.get_error_message()
    assert len(error_msgs) == 5
    assert [error_msg.text == "Required field" for error_msg in error_msgs]


def test_web_mobile_set_all_contact_field(app, open_sign_up_page):
    """
    User could set all contact field
    """
    user_data = generate_data_for_contributor_experience_user(phone_prefix='415')
    assert app.ce_account_setup.verify_state_of_element("disabled", app.ce_account_setup.contact_page.FINISH_BTN)

    app.ce_account_setup.set_contact_info(user_data)
    app.ce_account_setup.contact_page.check_receive_email()

    _phone_number = re.sub(r'[^0-9]', '', user_data['phone_number'])
    assert app.ce_account_setup.contact_page.get_contact_field_value(app.ce_account_setup.contact_page.ZIP_CODE) == user_data['zipcode']
    assert app.ce_account_setup.contact_page.get_contact_field_value(app.ce_account_setup.contact_page.CITY) == user_data['city']
    assert app.ce_account_setup.contact_page.get_contact_field_value(app.ce_account_setup.contact_page.PHONE) == "+1 " + f"({_phone_number[:3]}) {_phone_number[3:6]}-{_phone_number[6:10]}"
    assert app.ce_account_setup.contact_page.get_contact_field_value(app.ce_account_setup.contact_page.FULL_ADDRESS) == user_data['address']

    app.verification.text_present_on_page('California')
    app.verification.text_present_on_page("United States of America")

    country_flag = app.ce_account_setup.contact_page.get_mobile_phone_flag().split(':')
    assert "United States" == country_flag[0]

    assert not app.ce_account_setup.verify_state_of_element("disabled", app.ce_account_setup.contact_page.FINISH_BTN)



