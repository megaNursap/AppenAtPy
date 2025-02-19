"""
https://appen.atlassian.net/browse/QED-1453
Tests cover:
Verify requester can create multiple spans for a given token when nested span is allowed.
Verify requester can delete span.
Verify requester can merge span
https://appen.spiraservice.net/5/TestCase/1204.aspx
https://appen.spiraservice.net/5/TestCase/1205.aspx
https://appen.spiraservice.net/5/TestCase/1206.aspx
https://appen.spiraservice.net/5/TestCase/1207.aspx
"""

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job


pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/text_annotation/singlelinedata.csv")


@pytest.fixture(scope="module", autouse=True)
def tx_job(app):
    """
    Create Text Annotation nested spans job with 5 rows and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.text_annotation_allow_nesting_cml,
                                        job_title="Testing text annotation tool", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Annotation Ontology')

    ontology_file = get_data_file("/text_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='3']")
    return job_id


@pytest.mark.text_annotation
def test_nested_span(app, tx_job):
    """
    Verify that user can create multiple spans for a given token, when nested spans is enabled
    Once span is created, verify that the token shows the span line plus a grey line under it (when nested span is enabled)
    Verify user can delete nested spans individually
    Verify user can merge multiple spans and create nested spans
    Verify user can create span for individual token in merged ones
    Verify user can merge nested tokens and create span
    """
    app.job.preview_job()

    app.text_annotation.activate_iframe_by_index(0)
    app.text_annotation.full_screen()

    # create multiple spans for a given token
    app.text_annotation.click_token('Google')
    app.text_annotation.click_span('name')
    app.text_annotation.click_span('company')
    app.text_annotation.click_span('designation')
    designation_google_label = app.text_annotation.get_word_count_with_label('designation', 'Google')
    assert designation_google_label == 1
    assert app.text_annotation.get_inactive_span_line_counts() == 2
    assert app.text_annotation.get_gray_span_line_counts() == 1

    # delete nested spans individually
    app.text_annotation.delete_span()
    designation_google_label = app.text_annotation.get_word_count_with_label('designation', 'Google')
    assert designation_google_label == 0
    company_google_label = app.text_annotation.get_word_count_with_label('company', 'Google')
    assert company_google_label == 1
    assert app.text_annotation.get_inactive_span_line_counts() == 1
    assert app.text_annotation.get_gray_span_line_counts() == 1

    # merge tokens and create span for merged tokens
    merge_tokens = ["American", "car", "companies"]
    app.text_annotation.merge_token(merge_tokens)
    app.text_annotation.click_span('name')
    app.text_annotation.click_span('company')
    app.text_annotation.click_span('designation')
    designation_american_label = app.text_annotation.get_word_count_with_label('designation', 'American')
    assert designation_american_label == 1
    designation_car_label = app.text_annotation.get_word_count_with_label('designation', 'car')
    assert designation_car_label == 1
    designation_companies_label = app.text_annotation.get_word_count_with_label('designation', 'companies')
    assert designation_companies_label == 1

    # create span for individual token in merged ones
    app.text_annotation.select_gray_span(2)
    app.text_annotation.click_span('name')
    name_american_label = app.text_annotation.get_word_count_with_label('name', 'American')
    assert name_american_label == 1

    # merge nested tokens and create span
    app.text_annotation.merge_nested_token(1, 'would')
    app.text_annotation.click_span('company')
    company_american_label = app.text_annotation.get_word_count_with_label('company', 'American')
    company_car_label = app.text_annotation.get_word_count_with_label('company', 'car')
    company_companies_label = app.text_annotation.get_word_count_with_label('company', 'companies')
    company_would_label = app.text_annotation.get_word_count_with_label('company', 'would')
    assert company_car_label == 1
    assert company_companies_label == 1
    assert company_would_label == 1
    assert company_american_label == 1







