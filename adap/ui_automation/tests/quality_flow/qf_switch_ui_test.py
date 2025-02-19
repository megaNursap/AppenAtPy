import pytest

@pytest.mark.regression_qf
def test_switch_old_to_new_after_login(app):
    email = 'integration+ard02@figure-eight.com'
    password = 'Password001!'

    app.user.switch_old_to_new_after_login_customer(email, password)

@pytest.mark.regression_qf
def test_switch_new_to_old(app):
    email = 'integration+ard02@figure-eight.com'
    password = 'Password001!'

    app.user.switch_new_to_old_customer(email, password)

@pytest.mark.regression_qf
def test_switch_using_read_only(app):
    email = 'integration+ard05readonlyuser@figure-eight.com'
    password = 'Password001!'

    app.user.switch_using_read_only_customer(email, password)


