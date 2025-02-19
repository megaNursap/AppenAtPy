"""
UI VALIDATIONS ON SIGN UP PAGE
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *

# EMAIL = "aut" + str(random.randint(1000000, 9999999)) + "connect.stage.xyz@outlook.com"
EMAIL = "sandbox+" + str(random.randint(1000000, 9999999)) + "@figure-eight.com"
PASSWORD = get_test_data('test_ui_account', 'password')
INTERNAL_USER_NAME = get_test_data('test_ui_account', 'email')

pytestmark = [pytest.mark.regression_ac_vendor_profile, pytest.mark.regression_ac, pytest.mark.ac_ui_vendor_registration]


def test_invalid_password_longer(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL,
                                                       user_password='Abc@123456789012345678901234567890',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("Password does not meet minimum security requirements")


def test_invalid_password_smaller(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Invalid',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("Password must be at least 8 characters long")


def test_invalid_password_minimum_security(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='12345678',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("Password does not meet minimum security requirements")


def test_invalid_first_name(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Appen@001',
                                                       user_first_name="Appen1", user_last_name="Connect",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("Only Alphabetical characters were allowed")


def test_invalid_email_address(app):
    app.vendor_profile.registration_flow.register_user(user_name='Appen', user_password='Appen@001',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("Invalid e-mail address")


def test_invalid_last_name(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Appen@001',
                                                       user_first_name="firstname", user_last_name="Appen232",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("Only Alphabetical characters were allowed")


def test_certify_usa_ssn(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Appen@001',
                                                       user_first_name="Appen", user_last_name="Connect Automation",
                                                       residence_value='United States of America', state='Alabama')
    app.verification.text_present_on_page("I certify that I have a valid SSN or EIN")
    app.verification.text_present_on_page("STATE")


def test_certify_brazil(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Appen@001',
                                                       user_first_name="Appen", user_last_name="Connect Automation",
                                                       residence_value='Brazil', state=None)
    app.verification.text_present_on_page("I certify that I am able to provide legal country specific")


def test_required_firstname(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Abc@1234',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')

    app.vendor_profile.registration_flow.remove_data_from_fields({"FIRST NAME": "firstname"})
    app.verification.text_present_on_page("Required field")


def test_required_lastname(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Abc@1234',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')

    app.vendor_profile.registration_flow.remove_data_from_fields({"LAST NAME": "lastname"})
    app.verification.text_present_on_page("Required field")


# TODO fix test
# def test_required_email(app):
#     app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Abc@1234',
#                                                        user_first_name="firstname", user_last_name="lastname",
#                                                        residence_value='United States of America', state='Alabama')
#
#     app.vendor_profile.registration_flow.remove_data_from_fields({"EMAIL": EMAIL})
#     app.verification.text_present_on_page("Required field")


def test_required_password(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password='Abc@1234',
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')

    app.vendor_profile.registration_flow.remove_data_from_fields({"PASSWORD": 'Abc@1234'})
    app.verification.text_present_on_page("Required field")


def test_invalid_verification_code(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password=PASSWORD,
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')

    app.vendor_profile.registration_flow.fill_out_fields({"CERTIFY DATA PRIVACY": 1,
                                                          "CERTIFY SSN": 1}, action="Create Account")
    app.vendor_profile.registration_flow.fill_out_fields({"VERIFICATION CODE": 999998}, action="Verify Email")

    app.verification.text_present_on_page("Verify your Email")
    app.verification.text_present_on_page("A verification code has been send to")
    app.verification.text_present_on_page("%s" % EMAIL)
    app.verification.text_present_on_page(". Copy and enter it below.")
    app.verification.text_present_on_page("Invalid code. Try again or resend email.")


@pytest.mark.skip(reason='Avoid generate bounced email')
@pytest.mark.dependency(depends=["test_invalid_verification_code"])
def test_resend_email(app):
    app.navigation.click_btn("Resend email")
    app.verification.text_present_on_page("A new message was sent to your email address")
    app.navigation.click_btn("Back")


def test_need_more_info(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password=PASSWORD,
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')

    app.verification.text_present_on_page("Need more information about the work within Appen?")
    app.navigation.click_link("Take a look in our FAQ")


def test_go_to_sign_in(app):
    app.vendor_profile.registration_flow.register_user(user_name=EMAIL, user_password=PASSWORD,
                                                       user_first_name="firstname", user_last_name="lastname",
                                                       residence_value='United States of America', state='Alabama')

    app.verification.text_present_on_page("Have an account?")
    app.navigation.click_link("Sign In!")
    app.verification.current_url_contains('QRP/protocol/openid-connect')
