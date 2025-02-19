import pytest
from adap.api_automation.services_config.qf_api_logic import faker

@pytest.mark.regression_qf
def test_qf_register_name_only_space(app):
    user_name = ' s'

    app.user.register_name_only_space_customer(user_name)

@pytest.mark.regression_qf
def test_qf_register_name_special_char(app):
    user_name = 'Ard One Automate !@#$%^&*()'

    app.user.register_name_special_char_customer(user_name)

@pytest.mark.regression_qf
def test_qf_register_name_long_char(app):
    user_name = 'Ard One Automate Appen Ard One Automate Appen'

    app.user.register_name_long_char_customer(user_name)

@pytest.mark.regression_qf
def test_qf_register_incorrect_email_format(app):
    user_name = 'Ard One Automate One'
    email = 'integration+ard01automate@figure-eight'

    app.user.register_incorrect_email_format_customer(user_name, email)

@pytest.mark.regression_qf
def test_qf_register_existing_email(app):
    user_name = 'Ard One Automate'
    email = 'integration+ard02@figure-eight.com'
    password = 'Password001!'
    confirm_password = 'Password001!'

    app.user.register_as_customer(user_name, email, password, confirm_password)

    assert app.verification.text_present_on_page('The email address provided is invalid. Please use a business email.')

@pytest.mark.regression_qf
def test_qf_register_password_not_meet_requirement(app):
    user_name = 'Ard One Automate'
    email = 'integration+ard01automate@'
    password = 'Password'

    app.user.register_password_not_meet_requirement_customer(user_name, email, password)

@pytest.mark.regression_qf
def test_qf_register_password_and_confirm_password_not_match(app):
    user_name = 'Ard One Automate'
    email = 'integration+ard01automate@'
    password = 'Password002!'
    confirm_password = 'Password001!'

    app.user.register_password_and_confirm_password_not_match(user_name, email, password, confirm_password)

@pytest.mark.regression_qf
def test_qf_register_all_fields_empty(app):
    user_name = ''
    email = ''
    password = ''
    confirm_password = ''

    app.user.register_all_fields_empty_customer(user_name, email, password, confirm_password)

@pytest.mark.regression_qf
def test_qf_register_checkbox_not_ticked(app):
    user_name = 'Ard One Automate'
    email = 'integration+ard01automate@figure-eight.com'
    password = 'Password001!'
    confirm_password = 'Password001!'

    app.user.register_checkbox_not_ticked_customer(user_name, email, password, confirm_password)

@pytest.mark.regression_qf
def test_qf_register_tnc(app):
    user_name = 'Ard One Automate'
    email = 'integration+ard01automate@'
    password = 'Password001!'
    confirm_password = 'Password001!'

    app.user.register_as_click_tnc(user_name, email, password, confirm_password)

@pytest.mark.regression_qf
def test_qf_register_privacy(app):
    user_name = 'Ard One Automate'
    email = 'integration+ard01automate@'
    password = 'Password001!'
    confirm_password = 'Password001!'

    app.user.register_as_click_privacy(user_name, email, password, confirm_password)

@pytest.mark.regression_qf
def test_qf_register(app):
    user_name = 'Ard One Automate'
    email = f'integration+{faker.zipcode()}@figure-eight.com'
    password = 'Password001!'
    confirm_password = 'Password001!'

    app.user.register_as_customer(user_name, email, password, confirm_password)
