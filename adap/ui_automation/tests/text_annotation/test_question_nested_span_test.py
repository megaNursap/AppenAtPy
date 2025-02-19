"""
https://appen.atlassian.net/browse/QED-1664
Tests cover:
Create nested span annotations for test question
https://appen.spiraservice.net/5/TestCase/2156.aspx
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
    Create Text Annotation nested spans job with 5 rows, and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.text_annotation_nested_cml,
                                        job_title="Testing text annotation tool", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Annotation Ontology')

    ontology_file = get_data_file("/text_annotation/ontology_nestedspan.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='10']")
    app.job.open_tab('QUALITY')
    app.job.quality.click_to_create_tq()
    return job_id


def test_create_multiple_nested_span_tq(app, tx_job):
    """
    Verify requestor can create nested span annotations for test question and save successfully
    """
    for i in range(3):
        app.job.quality.switch_to_tq_iframe()
        app.text_annotation.activate_iframe_by_index(0)

        # create multiple spans for a given token
        app.text_annotation.click_token('Google')
        app.text_annotation.click_span('9th token')
        app.text_annotation.click_span('last token (of the 5)')
        app.text_annotation.click_span('7th and 8th tokens')
        google_label = app.text_annotation.get_word_count_with_label('7th and 8th tokens', 'Google')
        assert google_label == 1

        merge_tokens = ["When", "Sebastian", "Thrun", "started", "working"]
        app.text_annotation.merge_token(merge_tokens)
        app.text_annotation.click_span('First 5 tokens merged')
        when_label = app.text_annotation.get_word_count_with_label('First 5 tokens merged', 'When')
        assert when_label == 1
        sebastian_label = app.text_annotation.get_word_count_with_label('First 5 tokens merged', 'Sebastian')
        assert sebastian_label == 1
        thrun_label = app.text_annotation.get_word_count_with_label('First 5 tokens merged', 'Thrun')
        assert thrun_label == 1
        started_label = app.text_annotation.get_word_count_with_label('First 5 tokens merged', 'started')
        assert started_label == 1
        working_label = app.text_annotation.get_word_count_with_label('First 5 tokens merged', 'working')
        assert working_label == 1

        app.text_annotation.deactivate_iframe()
        app.job.quality.switch_to_tq_iframe()
        app.navigation.click_link("Save & Create Another")

    app.driver.switch_to.default_content()

    # verify the test questions count
    app.job.open_tab("QUALITY")
    tq_row_count = app.job.quality.get_number_of_active_tq()
    assert tq_row_count == 3

