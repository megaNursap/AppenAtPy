"""
https://appen.spiraservice.net/5/TestCase/975.aspx
This test covers negative cases to create text annotation job with invalid cml
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_text_annotation,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module", autouse=True)
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


def test_invalid_source_type_cml(app, login):
    """
    Verify error message is shown when invalid value is used for source-type CML attribute
    """
    job = Builder(API_KEY)
    resp = job.create_job_with_cml(data.text_annotation_invalid_source_type_cml)
    assert resp.status_code == 200
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/text_annotation/multiplelinesdata.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")
    alert_message = app.job.design.get_alert_message()
    assert len(alert_message) > 0, "Alert message not found"
    error = 'CML <cml:text_annotation> source-type should be "json" or "text"'
    assert error in alert_message[0].text


def test_invalid_tokenizer_cml(app, login):
    """
    Verify error is shown when invalid value is used for tokenizer CML attribute
    """
    job = Builder(API_KEY)
    resp = job.create_job_with_cml(data.text_annotation_invalid_tokenizer_cml)
    assert resp.status_code == 200
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/text_annotation/multiplelinesdata.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")
    danger_message = app.job.design.get_danger_message()
    message = 'There was a problem saving the job. Please try again.'
    assert message in danger_message
