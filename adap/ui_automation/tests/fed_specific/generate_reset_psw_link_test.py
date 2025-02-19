from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *

user_email = get_user_email('cf_internal_role')
password = get_user_password('cf_internal_role')

user_email_for_reset_pwd = get_user_email('test_ui_reset_password')
user_password_for_reset_pwd = get_user_password('test_ui_reset_password')


@pytest.mark.fed_ui
def test_generate_reset_password_link(app):
    new_password_encrypt = "gAAAAABfgIjFdi3F4hu-yezRWfuxpEkvocNphdlDimD4fFm_URccVqJKSdO1LExdT5QptWogyc-56zTgTg2gdJU2XdGljyTZ0Pj05e2PWvTQT89f1r-9Dm4="
    new_password = decrypt_user_new_password(new_password_encrypt)
    app.user.login_as_customer(user_name=user_email, password=password)
    app.mainMenu.account_menu("Contributor Admin")
    pwd_link = app.user.customer.generate_reset_password_link(user_email_for_reset_pwd)
    go_to_page(app.driver, pwd_link)
    time.sleep(2)
    assert app.verification.text_present_on_page('Reset Password')
    assert app.verification.text_present_on_page('Please enter a new password.')
    app.user.customer.reset_password_by_link(new_password)

    # make sure user can login with new password
    app.user.login_as_customer(user_name=user_email_for_reset_pwd, password=new_password)

    # reset the password back to the original one, so it won't impact other testing
    app.user.login_as_customer(user_name=user_email, password=password)
    app.mainMenu.account_menu("Contributor Admin")
    pwd_link = app.user.customer.generate_reset_password_link(user_email_for_reset_pwd)
    go_to_page(app.driver, pwd_link)
    time.sleep(2)
    assert app.verification.text_present_on_page('Reset Password')
    assert app.verification.text_present_on_page('Please enter a new password.')
    app.user.customer.reset_password_by_link(user_password_for_reset_pwd)


