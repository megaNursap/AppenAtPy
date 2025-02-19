import time
import allure
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/audio_transcription_column_transcription.csv")
ontology_file = get_data_file('/audio_transcription/AT-ontology-more-group-labels.json')


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_review_raw_text_cml,
                                        job_title="Testing audio transcription job", units_per_page=3)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    app.ontology.upload_ontology(ontology_file, rebrand=True)

    return job_id


@pytest.mark.dependency()
def test_review_data_raw_text(app, at_job):
    """
    Verify that review-data working with raw data
    """

    app.job.preview_job()
    time.sleep(2)
    app.navigation.refresh_page()
    actual_transcription_list = read_csv_file(DATA_FILE, 'transcription')
    for index in range(0, len(actual_transcription_list)):
        app.audio_transcription.activate_iframe_by_index(index)
        time.sleep(5)

        text_from_bubble = app.audio_transcription.get_text_from_bubble("Segment 1")
        assert text_from_bubble == actual_transcription_list[index]
        app.image_annotation.deactivate_iframe()