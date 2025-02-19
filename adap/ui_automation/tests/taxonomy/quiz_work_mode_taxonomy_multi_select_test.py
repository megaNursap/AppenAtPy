"""
Tests cover:
Verify contributor is presented with quiz mode, when taxonomy job has test questions
https://appen.spiraservice.net/5/TestCase/4687.aspx
"""
import time

from allure_commons.types import AttachmentType

from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.e2e_automation.services_config.contributor_ui_support import define_mode
from adap.ui_automation.services_config.text_annotation import copy_with_tq_and_launch_job


pytestmark = pytest.mark.regression_taxonomy

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

TAXONOMY_TQ_MULTY_SELECT_JOB_ID = pytest.data.predefined_data['taxonomy_api'].get(pytest.env, {}).get('tq_job_multy_select', '')
TAXONOMY_TQ_JOB_ID = pytest.data.predefined_data['taxonomy_api'].get(pytest.env, {}).get('tq_job', '')

ITEMS_TEXT_DATA = {
    'vegetable': ['VEGETABLE', 'Red and orange vegetables', 'Tomato'],
    'protein': ['PROTEIN FOODS', 'Fish and seafood', 'Salmon, Cod'],
    'fat': ['FAT', 'Saturated', 'Whole-milk dairy products'],
    'vegatable': ['FRUIT', 'Berries', 'Banana'],
    'fruit': ['FRUIT', 'Pomes', 'Apple']
}

@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_taxonomy_contributor_pass_quiz_mode(app_test):
    """
    Verify contributor is presented with quiz mode, when taxonomy job has test questions
    Verify that contributor is presented with work mode, upon passing quiz mode
    """
    CONTRIBUTOR_EMAIL = get_user_email('test_account')
    CONTRIBUTOR_PASSWORD = get_user_password('test_account')
    job_id = copy_with_tq_and_launch_job(API_KEY, TAXONOMY_TQ_MULTY_SELECT_JOB_ID)
    time.sleep(5)
    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app_test.navigation.open_page(job_link)
    app_test.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app_test.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    current_mode = define_mode(app_test.driver)
    assert current_mode == 'Quiz mode'
    time.sleep(2)

    for i in range(5):
        taxonome_ti = app_test.taxonomy.taxonomy_title(i)
        app_test.text_annotation.activate_iframe_by_index(i)
        app_test.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[taxonome_ti], index_of_select=1)
        app_test.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA['vegetable'], index_of_select=2)

        app_test.text_annotation.deactivate_iframe()
        time.sleep(2)

    app_test.text_annotation.submit_page()
    time.sleep(12)
    current_mode = define_mode(app_test.driver)
    assert current_mode == 'Work mode'


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_taxonomy_contributor_fail_quiz_mode(app_test):
    """
    As a contributor, verify that failing quiz mode shows "Your accuracy is too low" message
    """
    CONTRIBUTOR_EMAIL = get_user_email('test_ui_contributor1')
    CONTRIBUTOR_PASSWORD = get_user_password('test_ui_contributor1')
    job_id = copy_with_tq_and_launch_job(API_KEY, TAXONOMY_TQ_JOB_ID)
    time.sleep(5)
    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app_test.navigation.open_page(job_link)
    app_test.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    time.sleep(2)
    app_test.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    current_mode = define_mode(app_test.driver)

    assert current_mode == 'Quiz mode'

    # answer test questions incorrectly to fail quiz mode
    for i in range(5):
        taxonome_ti = app_test.taxonomy.taxonomy_title(i)
        app_test.text_annotation.activate_iframe_by_index(i)
        app_test.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[taxonome_ti])

        app_test.text_annotation.deactivate_iframe()
        time.sleep(2)

    app_test.text_annotation.submit_page()
    time.sleep(2)
    app_test.verification.text_present_on_page('Your accuracy is too low.')


