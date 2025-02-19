import pytest

@pytest.mark.regression_qf
def test_qf_forgot_password_invalid_email_format(app):
    email = 'integration+ard02'

    app.user.forgot_password_invalid_email_format_customer(email)

@pytest.mark.regression_qf
def test_qf_forgot_password_click_signin_in_forgot_password_page(app):

    app.user.forgot_password_click_signin_customer()

@pytest.mark.regression_qf
def test_qf_forgot_password_click_continue_email_empty(app):
    email = ''

    app.user.forgot_password_click_continue_but_email_empty_customer(email)

@pytest.mark.regression_qf
def test_qf_forgot_password_email_not_registered(app):
    email = 'integration+ard001Automatenotregistered@figure-eight.com'

    app.user.forgot_password_email_not_registered_customer(email)

@pytest.mark.regression_qf
def test_qf_forgot_password(app):
    email = 'integration+ard02@figure-eight.com'

    app.user.forgot_password_customer(email)



