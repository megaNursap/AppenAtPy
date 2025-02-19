"""
https://appen.atlassian.net/browse/QED-1667
Tests cover:
1.Verify contributor is presented with quiz mode, when text annotation job has test questions
https://appen.spiraservice.net/5/TestCase/2165.aspx
2.Verify that contributor is presented with work mode, upon passing quiz mode
https://appen.spiraservice.net/5/TestCase/2166.aspx
3.As a contributor, verify that failing quiz mode shows "Your accuracy is too low" message
https://appen.spiraservice.net/5/TestCase/2167.aspx
"""
import time
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.e2e_automation.services_config.contributor_ui_support import define_mode
from adap.ui_automation.services_config.text_annotation import copy_with_tq_and_launch_job


pytestmark = pytest.mark.regression_text_annotation

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

FLAT_JOB_ID = pytest.data.predefined_data['text_annotation'].get(pytest.env)['tq_flat']


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_contributor_pass_quiz_mode(app):
    """
    Verify contributor is presented with quiz mode, when text annotation job has test questions
    Verify that contributor is presented with work mode, upon passing quiz mode
    """
    job_id = copy_with_tq_and_launch_job(API_KEY, FLAT_JOB_ID)
    time.sleep(5)
    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    current_mode = define_mode(app.driver)
    assert current_mode == 'Quiz mode'

    # answer test questions correctly to pass quiz mode to go to work mode
    for i in range(5):
        app.text_annotation.activate_iframe_by_index(i)
        merge_tokens = ["When", "Sebastian", "Thrun"]
        app.text_annotation.merge_token(merge_tokens)
        app.text_annotation.click_span('1st, 2nd, and 3rd spans merged')

        merge_tokens = ["working", "on", "self"]
        app.text_annotation.merge_token(merge_tokens)
        app.text_annotation.click_span('5th, 6th and 7th  spans merged')

        app.text_annotation.click_token('driving')
        app.text_annotation.click_span('8th span')
        app.text_annotation.deactivate_iframe()
        time.sleep(2)

    app.text_annotation.submit_page()
    time.sleep(12)
    current_mode = define_mode(app.driver)
    assert current_mode == 'Work mode'


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_contributor_fail_quiz_mode(app_test):
    """
    As a contributor, verify that failing quiz mode shows "Your accuracy is too low" message
    """
    job_id = copy_with_tq_and_launch_job(API_KEY, FLAT_JOB_ID)
    time.sleep(5)
    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app_test.navigation.open_page(job_link)
    app_test.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app_test.user.close_guide()
    time.sleep(2)
    app_test.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    current_mode = define_mode(app_test.driver)
    assert current_mode == 'Quiz mode'

    # answer test questions incorrectly to fail quiz mode
    for i in range(5):
        app_test.text_annotation.activate_iframe_by_index(i)
        app_test.text_annotation.click_token('driving')
        app_test.text_annotation.click_span('8th span')
        app_test.text_annotation.deactivate_iframe()
        time.sleep(2)

    app_test.text_annotation.submit_page()
    time.sleep(2)
    app_test.verification.text_present_on_page('Your accuracy is too low.')


