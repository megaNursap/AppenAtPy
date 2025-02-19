"""
https://appen.atlassian.net/browse/QED-1255
"""

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.api_automation.services_config.builder import Builder as JobAPI
import time

pytestmark = [
    pytest.mark.fed_ui,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat,
    pytest.mark.cml_group_aggregation
]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    

def test_cml_validator_missing_groupname(app, login):
    """
    The CML has aggregation = "true" in the cml:group tag without a "group_name" attribute, show proper warning message
    """
    job = JobAPI(API_KEY)
    resp = job.create_simple_job(aggregation=True, cml=data.cml_group_aggregation_missing_group_name)
    assert resp is True, "Aggregation job was not created"
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DESIGN")
    time.sleep(2)
    app.navigation.click_btn("Save")
    time.sleep(2)
    alert_message = app.job.design.get_alert_message()
    error_message = "CML <cml:group> requires 'group_name' attribute to be set when 'aggregation' is present"
    assert alert_message, f"Alert message {error_message} not found"
    assert error_message == alert_message[0].text


def test_cml_validator_missing_aggregation(app, login):
    """
    The CML has a "group_name" without an aggregation = "true" tag within the CML:Group tag, show proper warning message
    """
    job = JobAPI(API_KEY)
    resp = job.create_simple_job(aggregation=True, cml=data.cml_group_aggregation_missing_aggregation)
    assert resp is True, "Aggregation job was not created"
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DESIGN")
    time.sleep(2)
    app.navigation.click_btn("Save")
    time.sleep(2)
    alert_message = app.job.design.get_alert_message()
    error_message = "CML <cml:group> 'aggregation' attribute must be set to 'true' when 'group-name' is present"
    assert alert_message, f"Alert message {error_message} not found"
    assert error_message == alert_message[0].text


def test_cml_validator_duplicate_name(app, login):
    """
    The CML has a "name" and "group_name" attribute within the CML:Group tag, show proper waring message
    """
    job = JobAPI(API_KEY)
    resp = job.create_simple_job(aggregation=True, cml=data.cml_group_aggregation_duplicate_name)
    assert resp is True, "Aggregation job was not created"
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DESIGN")
    time.sleep(2)
    app.navigation.click_btn("Save")
    time.sleep(2)
    alert_message = app.job.design.get_alert_message()
    error_message = "CML <cml:group> cannot use name when group_name is present"
    assert alert_message, f"Alert message {error_message} not found"
    assert error_message == alert_message[0].text
