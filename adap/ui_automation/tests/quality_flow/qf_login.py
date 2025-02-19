import pytest

@pytest.mark.regression_qf
def test_qf_login_wrong_email(app):
    wrong_email = 'integration+ard00002@figure-eight.com'
    password = 'Password001!'

    app.user.login_as_failed_customer(wrong_email, password)

    assert app.verification.text_present_on_page('The password you entered is incorrect. Please try again.')

@pytest.mark.regression_qf
def test_qf_login_wrong_password(app):
    email = 'integration+ard02@figure-eight.com'
    wrong_password = 'Password01!'

    app.user.login_as_failed_customer(email, wrong_password)

    assert app.verification.text_present_on_page('The password you entered is incorrect. Please try again.')

@pytest.mark.regression_qf
def test_qf_login_wrong_email_wrong_password(app):
    wrong_email = 'inintegration+ard00002@figure-eight.com'
    wrong_password = 'Password01!'

    app.user.login_as_failed_customer(wrong_email, wrong_password)

    assert app.verification.text_present_on_page('The password you entered is incorrect. Please try again.')

@pytest.mark.regression_qf
def test_qf_login_empty_email(app):
    empty_email = ''
    password = 'Password01!'

    app.user.login_as_empty_email_customer(empty_email, password)

@pytest.mark.regression_qf
def test_qf_login_empty_password(app):
    email = 'integration+ard02@figure-eight.com'
    empty_password = ''

    app.user.login_as_empty_password_customer(email, empty_password)

@pytest.mark.regression_qf
def test_qf_login(app):
    email = 'integration+ard02@figure-eight.com'
    password = 'Password001!'

    app.user.login_as_customer(email, password)