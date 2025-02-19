
import time

import allure

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job


USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-dv.csv")


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

def test_ontology_not_match_data_with_missing_ontology(app, login):
    """
    Verify error message “Ontology does not match data” is shown,
    when there are no ontology classes that match input audio segments
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_cml,
                                        job_title="Testing ontology not match", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/missing_one_ontology_class.csv')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Ontology does not match data')
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_ontology_not_match_data_with_unmatch_ontology(app, login):
    """
    Verify error message “Ontology does not match data” when 1 or a subset of ontology classes are missing,
    for which audio segments are available
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_cml,
                                        job_title="Testing ontology not match", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/unmatch_ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Ontology does not match data')
    app.driver.close()
    app.navigation.switch_to_window(job_window)


@pytest.mark.skip(reason='The behaviour changes. For now with invalid data annotation tool should work property')
def test_judgment_data_not_found_with_incorrect_data_file(app, login):
    """
    Verify error message “Review data not found” is shown for data row,
    when column value for review-from is incorrect in data file
    """
    data_file = get_data_file("/audio_transcription/review_data_not_found.csv")
    job_id = create_annotation_tool_job(API_KEY, data_file,
                                        data.audio_transcription_peer_review_cml,
                                        job_title="Testing review data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Review data not found')
    app.driver.close()
    app.navigation.switch_to_window(job_window)

