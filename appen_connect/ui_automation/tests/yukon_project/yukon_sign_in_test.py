import time

import pytest

from adap.api_automation.utils.data_util import get_test_data

pytestmark = [pytest.mark.regression_ac_yukon]


def test_yukon_sign_in_express_user(app_test):
    user_email = get_test_data('yukon_express_user', 'email')
    password = get_test_data('yukon_express_user', 'password')

    app_test.ac_user.login_as(user_email, password)
    time.sleep(5)

    app_test.navigation.switch_to_frame(0)
    app_test.verification.text_present_on_page('Yukon')
    app_test.verification.text_present_on_page('Data Collector')
    app_test.verification.text_present_on_page("Test Yukon Project")
    app_test.verification.text_present_on_page("Search Engine Evaluator")
    app_test.verification.text_present_on_page('Work This')

    app_test.driver.switch_to.default_content()

