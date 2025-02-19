"""
https://appen.atlassian.net/browse/QED-1908
Include test cases:
1. Test validators error
2. Test validators successfully
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_transcription import create_video_transcription_job
import time
from adap.data.video_transcription import data

# pytestmark = [pytest.mark.regression_video_transcription]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')
DATA_FILE = get_data_file("/video_transcription/video_transcription_data.csv")


@pytest.fixture(scope="module", autouse=True)
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


# https://appen.spiraservice.net/5/TestCase/2930.aspx
@pytest.mark.dependency()
def test_required_fields_in_cml_test_validators(app, login):
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.required_cml, JWT_TOKEN, USER_EMAIL, PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.video_transcription.submit_test_validators()
    app.verification.text_present_on_page('Annotation should have at least one region')
    # submit with transcription
    iframes_count = app.video_transcription.get_number_iframes_on_page()
    assert iframes_count == 3
    for i in range(iframes_count):
        app.video_transcription.activate_iframe_by_index(i)
        app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
        app.video_transcription.deactivate_iframe()
    app.video_transcription.submit_test_validators()
    app.verification.text_present_on_page('Validation succeeded')
    app.driver.close()
    app.navigation.switch_to_window(job_window)


@pytest.mark.dependency(depends=["test_required_fields_in_cml_test_validators"])
def test_optional_fields_in_cml_submit_without_creating_segments(app, login):
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.full_cml, JWT_TOKEN)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()
    time.sleep(5)
    app.video_transcription.submit_test_validators()
    app.verification.text_present_on_page('Annotation should have at least one region')


@pytest.mark.dependency(depends=["test_optional_fields_in_cml_submit_without_creating_segments"])
def test_optional_fields_in_cml_submit_without_category_transcription(app, login):
    # submit with segments, but did not fill out category, transcription and turn in
    iframes_count = app.video_transcription.get_number_iframes_on_page()
    assert iframes_count == 3
    for i in range(iframes_count):
        app.video_transcription.activate_iframe_by_index(i)
        app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
        app.video_transcription.deactivate_iframe()
    app.video_transcription.submit_test_validators()
    app.verification.text_present_on_page('All regions should have transcription')


@pytest.mark.dependency(depends=["test_optional_fields_in_cml_submit_without_category_transcription"])
def test_optional_fields_in_cml_submit_successfully(app, login):
    iframes_count = app.video_transcription.get_number_iframes_on_page()
    for i in range(iframes_count):
        app.video_transcription.activate_iframe_by_index(i)
        app.video_transcription.click_to_select_segment()
        app.video_transcription.click_to_select_ontology_under_category('Pet')
        app.video_transcription.input_transcription_in_textbox('test with optional fields in cml')
        app.video_transcription.create_turn_id_and_select_it('new turn in')
        app.navigation.click_btn('Save Segment')
        app.video_transcription.deactivate_iframe()
    app.video_transcription.submit_test_validators()
    app.verification.text_present_on_page('Validation succeeded')