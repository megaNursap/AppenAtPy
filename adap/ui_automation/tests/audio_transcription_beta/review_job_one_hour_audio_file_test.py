import time

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/preprocesing_data.csv")

@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """

    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_multi_segment_large_data,
                                        job_title="Testing audio transcription beta for one segment job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-label-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_load_long_audio_data_for_contributor(app, at_job):
    """
    Verify the big audio data not break Job
    """

    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.wait_until_text_disappear_on_the_page("Preparing Audio Data", 20)
    list_of_segments = len(app.audio_transcription_beta.audio_transcription_beta_element.get_segment_list())
    for index_segment in range(0, list_of_segments):
        app.audio_transcription_beta.click_on_segment(index=index_segment)
        app.audio_transcription_beta.click_on_listen_to_block(time_value=6)

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.activate_iframe_by_index(1)
    app.verification.wait_until_text_disappear_on_the_page("Preparing Audio Data", 20)
    list_of_segments = len(app.audio_transcription_beta.audio_transcription_beta_element.get_segment_list())
    for index_segment in range(0, list_of_segments):
        app.audio_transcription_beta.click_on_segment(index=index_segment)
        app.audio_transcription_beta.click_on_listen_to_block(time_value=6)

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()