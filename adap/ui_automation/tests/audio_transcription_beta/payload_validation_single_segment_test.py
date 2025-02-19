import time

import pytest

from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data-one-unit.csv")


@pytest.fixture(scope='module')
def at_job_single_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_beta,
                                        job_title="Testing audio transcription beta single segment job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_error_icon_for_one_segment(at_job_single_segment, app):
    """
        Verify requestor could see error message for one segment
        audio transcription tools (transcribe the text, listen enough audio, set require labels)
    """


    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    time.sleep(1)
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'All segments have to be transcribed or ' \
                                                                         'marked as nothing to transcribe.', \
        "The error message on page ABSENT"
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.verification.wait_untill_text_present_on_the_page("Audio Segment", 10)
    app.audio_transcription_beta.add_text_to_segment("test_text")
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()

    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'Some segments do not contain valid labeling ' \
                                                                         'work. Please select labels from all ' \
                                                                         'required groups.', \
        "The error message on page ABSENT"

    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.text_present_on_page("Audio Segment")
    app.audio_transcription.group_labels.choose_labels_by_name('Pets', multi_select=True)
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()

    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'You have not listened to the minimum ' \
                                                                         'required duration of available listening ' \
                                                                         'blocks in some segments.', \
        "The error message on page ABSENT"

    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.text_present_on_page("Audio Segment")
    app.audio_transcription_beta.click_on_action_button("PlayPauseButton")
    time.sleep(19)
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()

    time.sleep(2)
    app.verification.verify_validation_status()
