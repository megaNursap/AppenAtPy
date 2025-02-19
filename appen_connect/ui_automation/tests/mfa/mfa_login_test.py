"""
https://appen.atlassian.net/browse/QED-3741
This test covers mfa flow, test cases steps here:
"""

from adap.ui_automation.utils.selenium_utils import *
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import *

USER_NAME = get_test_data('mfa_profile', 'email')
PASSWORD = get_test_data('mfa_profile', 'password')


pytestmark = pytest.mark.regression_ac_mfa_profile


def test_check_account_created_mfa(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.verification.text_present_on_page("Multi-Factor Authentication")
    app.mfa_profile.select_multi_factor_authentication(title_name="Email")
    app.verification.text_present_on_page("Authentication via Email")
