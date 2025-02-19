"""
https://appen.atlassian.net/browse/QED-1946
"""
import time

import allure

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]


USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-dv.csv")


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

@pytest.fixture(autouse=True)
def close_preview_job(app, login):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])


def test_audio_annotation_data_not_found_with_incorrect_data_file(app, login):
    """
    Verify error message “Audio Annotation data not found” is shown for data row,
    when column value for audio-annotation-data is incorrect in data file
    """
    incorrect_data_file = get_data_file("/audio_transcription/incorrect_annotate_the_audio.csv")
    job_id = create_annotation_tool_job(API_KEY, incorrect_data_file,
                                        data.audio_transcription_cml,
                                        job_title="Testing audio annotation data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.navigation.click_bytext("Details")
    app.verification.text_present_on_page('Not found')


def test_audio_annotation_data_not_found_with_incorrect_cml(app, login):
    """
    Verify error message “Audio Annotation data not found” is shown for data row,
    when audio-annotation-data attribute value is defined incorrectly in CML
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_invalid_audio_annotation_data_cml,
                                        job_title="Testing audio annotation data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Tool cannot be initialized')

def test_judgment_data_not_found_with_invalid_cml(app, login):
    """
    Verify error message “Invalid task-type in payload” is shown for data row,
    when task-type attribute value is defined incorrectly in CML
    """
    data_file = get_data_file("/audio_transcription/full_report.csv")
    job_id = create_annotation_tool_job(API_KEY, data_file,
                                        data.audio_transcription_review_data_not_found_cml,
                                        job_title="Testing review data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.navigation.click_bytext("Details")
    app.verification.text_present_on_page('Invalid task-type in payload')

def test_audio_data_not_found_with_incorrect_cml(app, login):
    """
    Verify error message “Audio data not found” is shown for data row
    when column value for audio-url is incorrect in data file
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_invalid_audio_url_cml,
                                        job_title="Testing audio data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Audio data not found')


# https://appen.spiraservice.net/5/TestCase/3036.aspx
def test_error_show_on_data_unit_page(app, login):
    """
    Verify ‘Question Unavailable’ is shown in Unit page when data is not available
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_invalid_audio_url_cml,
                                        job_title="Testing audio data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('new')
    first_unit = units['unit id'][0]
    app.job.data.open_unit_by_id(first_unit)
    app.audio_transcription.data_unit.activate_iframe_on_unit_page()
    app.verification.text_present_on_page('Question Unavailable')
    app.verification.text_present_on_page('Audio data not found')
    app.audio_transcription.deactivate_iframe()
    app.job.preview_job()
    time.sleep(3)

