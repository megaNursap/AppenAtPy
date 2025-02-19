"""
https://appen.atlassian.net/browse/QED-1515
This test covers cases to create plss job via valid/invalid cml.
https://appen.spiraservice.net/5/TestCase/597.aspx
https://appen.spiraservice.net/5/TestCase/598.aspx

PLSS stands for pixel labeling semantic segmentation. You can get more info here:
https://appen.atlassian.net/wiki/spaces/PROD/pages/447842149/PRD+PLSS+in+new+tool
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_plss,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


def test_create_job_valid_cml(app):
    job = Builder(API_KEY)
    job.create_job_with_cml(data.plss_cml)
    job_id = job.job_id
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/plss/catdog.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Segmentation Ontology')

    ontology_file = get_data_file("/plss/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")


def test_create_job_invalid_cml(app_test):
    job = Builder(API_KEY)
    job.create_job_with_cml(data.plss_invalid_cml)
    job_id = job.job_id
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab("DATA")
    data_file = get_data_file("/plss/catdog.csv")
    app_test.job.data.upload_file(data_file)

    app_test.job.open_tab('DESIGN')
    app_test.navigation.click_btn("Save")
    alert_message = app_test.job.design.get_alert_message()
    error = "CML contains invalid validators: yes"
    assert error in alert_message[0].text

