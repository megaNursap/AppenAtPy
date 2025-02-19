"""
https://appen.atlassian.net/browse/QED-1454
Tests cover, create/edit/delete span
https://appen.spiraservice.net/5/TestCase/1209.aspx
https://appen.spiraservice.net/5/TestCase/1211.aspx
https://appen.spiraservice.net/5/TestCase/1259.aspx
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
    Create Text Annotation job with 5 units, and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.text_annotation_cml,
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


def test_create_update_delete_span(app, tx_job):
    """
    Verify requestor can create/edit/delete a span for a given token, in preview mode
    """
    app.job.preview_job()

    app.text_annotation.activate_iframe_by_index(0)
    app.text_annotation.full_screen()

    # add span
    app.text_annotation.click_token('Sebastian')
    app.text_annotation.click_span('name')
    name_label_count = app.text_annotation.get_word_count_with_label('name', 'Sebastian')
    assert name_label_count == 1

    # edit span
    app.text_annotation.click_span('company')
    company_label_count = app.text_annotation.get_word_count_with_label('company', 'Sebastian')
    assert company_label_count == 1
    name_label_count = app.text_annotation.get_word_count_with_label('name', 'Sebastian')
    assert name_label_count == 0

    # delete span
    app.text_annotation.delete_span()
    company_label_count = app.text_annotation.get_word_count_with_label('company', 'Sebastian')
    assert company_label_count == 0
