"""
https://appen.atlassian.net/browse/QED-1902
Include test cases:
1. Create video transcription job with required fields in cml
2. Create video transcription job with optional fields in cml
3. Create video transcription job with invalid cml
4. Verify data on unit page
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_transcription import create_video_transcription_job
import time
from adap.api_automation.services_config.builder import Builder
from adap.data.video_transcription import data

# pytestmark = [pytest.mark.regression_video_transcription,
#               pytest.mark.adap_ui_uat,
#               pytest.mark.adap_uat
#               ]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')
DATA_FILE = get_data_file("/video_transcription/video_transcription_data.csv")


@pytest.fixture(scope="module", autouse=True)
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


def test_create_job_with_required_fields_in_cml(app, login):
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.required_cml, JWT_TOKEN, USER_EMAIL, PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.video_transcription.activate_iframe_by_index(0)
    app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
    segments_number = app.video_transcription.get_number_of_segment()
    assert segments_number == 1
    app.video_transcription.click_to_select_segment()
    assert not app.video_transcription.turn_id_is_displayed()
    app.verification.button_is_displayed('Save Segment')
    app.verification.button_is_displayed('Delete Segment')
    app.video_transcription.deactivate_iframe()
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_create_job_with_optional_fields_in_cml(app, login):
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.full_cml, JWT_TOKEN, USER_EMAIL, PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.video_transcription.activate_iframe_by_index(0)
    app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
    segments_number = app.video_transcription.get_number_of_segment()
    assert segments_number == 1
    app.video_transcription.click_to_select_segment()
    assert app.video_transcription.turn_id_is_displayed()
    app.verification.text_present_on_page('Category')
    app.verification.text_present_on_page('Transcription')
    app.verification.button_is_displayed('Save Segment')
    app.verification.button_is_displayed('Delete Segment')
    app.video_transcription.deactivate_iframe()
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_create_job_with_invalid_cml(app, login):
    job = Builder(API_KEY)
    resp = job.create_job_with_cml(data.invalid_cml)
    assert resp.status_code == 200
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    app.job.data.upload_file(DATA_FILE)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")
    alert_message = app.job.design.get_alert_message()
    assert len(alert_message) == 2
    assert alert_message[0].text == "CML <cml:video_transcription> 'ontology' must be either 'true' or 'false'"
    assert alert_message[1].text == "CML <cml:video_transcription> 'allow-transcription' must be either 'true' or 'false'"


def test_ontology_displayed_under_category(app, login):
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.full_cml, JWT_TOKEN, USER_EMAIL, PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.video_transcription.activate_iframe_by_index(0)
    app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
    app.video_transcription.click_to_select_segment()
    ontologys = app.video_transcription.get_ontology_displayed_under_category()
    assert 'Person' in ontologys
    assert 'Pet' in ontologys
    assert 'Background' in ontologys
    assert 'Noise' in ontologys
    assert 'Male voice' in ontologys
    assert 'Female voice' in ontologys
    assert 'Dog' in ontologys
    assert 'Cat' in ontologys
    assert 'Music' in ontologys
    assert 'Kids' in ontologys
    app.video_transcription.deactivate_iframe()
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_unit_page_data(app, login):
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.full_cml, JWT_TOKEN, USER_EMAIL, PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('new')
    first_unit = units['unit id'][0]

    app.job.data.open_unit_by_id(first_unit)
    app.verification.current_url_contains("/units/%s" % first_unit)
    time.sleep(5)
    app.video_transcription.activate_iframe_on_unit_page()
    app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
    app.video_transcription.click_to_select_segment()
    app.verification.button_is_displayed('Delete Segment')
    app.video_transcription.click_to_select_ontology_under_category('Pet')
    app.video_transcription.input_transcription_in_textbox('test unit page')
    app.video_transcription.create_turn_id_and_select_it('new turn in')
    app.navigation.click_btn('Save Segment')
    app.video_transcription.deactivate_iframe()