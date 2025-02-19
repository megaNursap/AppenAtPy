"""
https://appen.atlassian.net/browse/QED-1765
"""

import time

from selenium.webdriver.common.alert import Alert

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

pytestmark = [pytest.mark.regression_core,
              pytest.mark.ui_smoke,
              pytest.mark.ui_uat,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.fed_ui]


def test_job_quality_control_page(app):
    job = JobAPI(API_KEY)
    job.create_simple_job()
    job_id = job.job_id

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    time.sleep(2)

    app.job.open_action('Settings')
    app.job.open_settings_tab('Quality Control,Quality Control Settings')
    app.verification.current_url_contains('/settings/quality_control')
    app.verification.text_present_on_page('Minimum Time Per Page')
    app.verification.text_present_on_page('Disable Google Translate for Contributors')
    app.verification.text_present_on_page('Contributor Answer Distribution Rules')
    app.verification.text_present_on_page('Max Judgments per Contributor')

    app.job.set_minimum_time_per_page(15)
    app.job.set_max_judgments_per_contributors(60)

    app.navigation.click_checkbox_by_text('When on, this disables Google Translate for contributors using the Chrome browser to ensure that context and meaning are not lost in translation')
    app.navigation.click_checkbox_by_text('Monitor answer patterns to remove contributors whose answers are outside the expected distribution')
    app.verification.text_present_on_page('Activation Threshold')
    assert app.job.get_activation_threshold() == '20'
    app.verification.text_present_on_page('Question')
    app.verification.text_present_on_page('Answer Distribution Rules')
    app.navigation.click_btn('Add Rule')
    app.job.add_regular_expression(generate_random_string())
    app.navigation.click_btn('Save')

    # at this moment, after click save button, no success message, so we just refresh page and validate the value on the page is what we set
    app.navigation.refresh_page()
    try:
        Alert(app.driver).accept()
    except:
       pass

    assert app.job.get_minimum_time_per_page() == '15'
    assert app.job.get_max_judgments_per_contributors() == '60'

    app.job.delete_regular_expression()
    app.verification.text_present_on_page('Add Rule')

