"""
https://appen.atlassian.net/browse/QED-1516
https://appen.atlassian.net/browse/QED-1651
This test covers:
1. create machine learning assisted image transcription job with OCR
2. create machine learning assisted image transcription job without OCR
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = [
    pytest.mark.regression_image_transcription,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat,
    pytest.mark.fed_ui
]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def login_for_create_job(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


def test_create_job_with_ocr(login_for_create_job, app):
    job = Builder(API_KEY)
    job.create_job_with_cml(data.image_transcription_ocr_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/image_transcription/receipts.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")


def test_create_job_without_ocr(login_for_create_job, app):
    job = Builder(API_KEY)
    job.create_job_with_cml(data.image_transcription_withoutocr_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/image_transcription/receipts.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")


def test_create_job_with_language_attribute_ocr_true(login_for_create_job, app):
    job = Builder(API_KEY)
    job.create_job_with_cml(data.image_transcription_language_attribute_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/image_transcription/multiple_langs_ocr.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")


def test_create_job_with_language_attribute_ocr_false(login_for_create_job, app):
    job = Builder(API_KEY)
    job.create_job_with_cml(data.image_transcription_language_attribute_ocr_false_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/image_transcription/multiple_langs_ocr.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn('Save')
    alert_message = app.job.design.get_alert_message()
    assert len(alert_message) > 0, "Alert message not exist"
    error_message = 'CML <cml:image_transcription> must set ocr="true" to use language attribute'
    assert error_message == alert_message[0].text
