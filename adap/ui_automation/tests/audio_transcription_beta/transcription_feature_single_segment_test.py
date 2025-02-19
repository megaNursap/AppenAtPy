import time

import pytest
from selenium.webdriver import Keys

from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data.csv")


@pytest.fixture(scope='module')
def at_job_single_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_beta,
                                        job_title="Testing audio transcription beta job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    job_id = job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id

def test_transcribe_the_single_segment(at_job_single_segment, app):
    """
    Verify requestor could add/edit/delete transcription for single segment
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("test single")

    app.verification.text_present_on_page('test single')

    app.audio_transcription_beta.add_text_to_segment(" segment with transcription")
    text_after_add_text = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_text == "test single segment with transcription", "The transcribe text NOT as expected after added text"
    app.audio_transcription_beta.delete_word_in_segment("segment with")

    text_after_delete = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete == "test single  transcription", "The transcribe text NOT as expected"
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'Some segments do not contain valid labeling ' \
                                                                         'work. Please select labels from all ' \
                                                                         'required groups.', \
        "The error message on page ABSENT"

    app.audio_transcription_beta.deactivate_iframe()


def test_transcribe_undo_redo_hot_key_single_segment(at_job_single_segment, app):
    """
       Verify requestor could undo/redo action in text area for single segment
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test hot key for undo/redo")
    app.audio_transcription_beta.highlight_text_in_segments("hot")
    app.audio_transcription.span.add_span("span2")

    app.audio_transcription_beta.highlight_text_in_segments("undo")
    app.audio_transcription.span.add_span("span1")

    text_after_add_text_span = app.audio_transcription_beta.grab_text_from_text_area()

    assert text_after_add_text_span == "test <span_2>h</span_2> ot key for <span_1>u</span_1> ndo/redo"
    app.audio_transcription_beta.delete_tag("<span_2>")
    app.audio_transcription_beta.delete_highlight_text_in_segments("key")
    app.audio_transcription_beta.move_to_word('redo')

    app.navigation.combine_hotkey(Keys.CONTROL, "z")
    app.navigation.combine_hotkey(Keys.CONTROL, "z")

    text_after_undo_text_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_undo_text_span == text_after_add_text_span

    app.navigation.combine_hotkey(Keys.CONTROL, "Z")

    text_after_undo_text_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_undo_text_span == "test h ot key for <span_1>u</span_1> ndo/redo"
