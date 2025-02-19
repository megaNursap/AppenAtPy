"""
https://appen.atlassian.net/browse/QED-1748
"""

import time
from adap.api_automation.utils.data_util import *

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = pytest.mark.regression_core


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.skip(reason='Broken test QED-2653')
def test_change_template_order(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    time.sleep(2)
    app.mainMenu.account_menu("Templates")
    app.verification.current_url_contains('/job_templates')
    app.job_template.change_template_order(1, 2)
    time.sleep(3)
    app.navigation.click_link('← Back to Template Library')
    app.verification.current_url_contains('/job_templates')


