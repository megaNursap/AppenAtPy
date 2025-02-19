import time

import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data.csv")


@pytest.fixture(scope='module')
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_beta,
                                        job_title="Testing audio transcription beta job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_error_icon_on_test_validation(at_job, app):
    """
        Verify requestor can see error icon if he/she doesn't do require action for
        audio transcription tools (transcribe the text, listen enough audio, set require labels)
        """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    time.sleep(2)
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'All segments have to be transcribed or ' \
                                                                         'marked as nothing to transcribe.', \
        "The error message on page ABSENT"
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error[2][0] == 'Provide transcription text or mark as nothing to transcribe.'
    assert payload_error[2][2] == 'Meet minimum listening duration requirement of all audio blocks.'
    assert payload_error[2][1] == "Select labels from all required groups."

    app.audio_transcription_beta.deactivate_iframe()

def test_error_icon_disappeared_after_all_validation(at_job, app):
    """
        Verify error icon disappeared  for this waveform on which the requestor done all required field
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(3, transcribe_all_segment=True)

    app.verification.wait_untill_text_present_on_the_page("Segment 4", 15)

    app.audio_transcription_beta.add_text_to_segment("test_text")

    app.audio_transcription.group_labels.choose_labels_by_name('Pets', multi_select=True)

    app.audio_transcription_beta.click_on_listen_to_block(time_value=5)

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    time.sleep(2)
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'All segments have to be transcribed or ' \
                                                                         'marked as nothing to transcribe.', \
        "The error message on page ABSENT"
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error[4] == ['', '', '']

    app.audio_transcription_beta.deactivate_iframe()
