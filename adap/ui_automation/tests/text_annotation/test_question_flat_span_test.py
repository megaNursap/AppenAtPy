"""
https://appen.atlassian.net/browse/QED-1664
Tests cover:
1. Checking passing threshold on test question page
2. Create flat span annotations for test question
3. Update threshold percentage
https://appen.spiraservice.net/5/TestCase/2155.aspx
https://appen.spiraservice.net/5/TestCase/2157.aspx
https://appen.spiraservice.net/5/TestCase/2158.aspx
https://appen.spiraservice.net/5/TestCase/2159.aspx
"""
import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job


pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/text_annotation/data_tq.csv")


@pytest.fixture(scope="module", autouse=True)
def tx_job(app):
    """
    Create Text Annotation flat spans job with 5 rows, and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.text_annotation_flat_cml,
                                        job_title="Testing text annotation tool", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Annotation Ontology')

    ontology_file = get_data_file("/text_annotation/ontology_flatspan.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='5']")
    app.job.open_tab('QUALITY')
    app.job.quality.click_to_create_tq()
    app.job.quality.switch_to_tq_iframe()
    app.text_annotation.activate_iframe_by_index(0)
    return job_id


def test_manage_threshold(app, tx_job):
    """
    As a requestor, verify that test question page shows default 'Passing Threshold' of 100%
    Verify requestor can change the passing threshold percentage within 0-100 range, for test question
    Verify error is shown when passing threshold value is out of range
    """
    threshold = app.job.quality.get_passing_threshold()

    # validate min, max and default value for threshold
    assert threshold.get_attribute('value') == '100'
    assert threshold.get_attribute('min') == '0'
    assert threshold.get_attribute('max') == '100'

    # able to edit threshold to be value between 0~100, failed to edit value more than 100
    assert app.job.quality.edit_passing_threshold_successfully(0)
    assert app.job.quality.edit_passing_threshold_successfully(99)
    assert not app.job.quality.edit_passing_threshold_successfully(101)
    assert not app.job.quality.edit_passing_threshold_successfully(-1)


def test_create_single_flat_span_tq(app, tx_job):
    """
    Verify requestor can create flat span annotations for test question and save successfully
    """
    # add span for test question
    merge_tokens = ["When", "Sebastian", "Thrun"]
    app.text_annotation.merge_token(merge_tokens)
    app.text_annotation.click_span('5th, 6th and 7th  spans merged')
    app.text_annotation.click_span('1st, 2nd, and 3rd spans merged')
    when_label = app.text_annotation.get_word_count_with_label('1st, 2nd, and 3rd spans merged', 'When')
    assert when_label == 1
    sebastian_label = app.text_annotation.get_word_count_with_label('1st, 2nd, and 3rd spans merged', 'Sebastian')
    assert sebastian_label == 1
    thrun_label = app.text_annotation.get_word_count_with_label('1st, 2nd, and 3rd spans merged', 'Thrun')
    assert thrun_label == 1

    app.text_annotation.click_token('Google')
    app.text_annotation.click_span('8th span')
    name_label_count = app.text_annotation.get_word_count_with_label('8th span', 'Google')
    assert name_label_count == 1
    app.text_annotation.deactivate_iframe()
    app.job.quality.switch_to_tq_iframe()
    app.navigation.click_link("Save & Create Another")
    app.driver.switch_to.default_content()

