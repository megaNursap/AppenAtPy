import time

import pytest
from selenium.webdriver import Keys

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file, \
    convert_audio_datatime_to_second
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


def test_add_edit_delete_transcription_to_multi_segments(at_job, app):
    """
        Verify requestor could add/edit/delete  transcription in text area, add span/event/timestamp
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)

    app.audio_transcription_beta.add_text_to_segment("test that")

    app.verification.text_present_on_page('test that')

    app.audio_transcription_beta.add_text_to_segment(" this text should be transcribe")
    app.audio_transcription_beta.delete_word_in_segment("should")

    text_after_delete = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete == "test that this text  be transcribe", "The transcribe text NOT as expected"

    app.audio_transcription_beta.deactivate_iframe()


def test_transcribe_all_multi_segments(at_job, app):
    """
        Verify that user should transcribe all segments of mark Nothing to transcribe
         if in cml set type=['transcription']
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    list_of_segment = len(app.audio_transcription_beta.audio_transcription_beta_element.get_segment_list())

    for index_segment in range(0, list_of_segment):
        app.audio_transcription_beta.click_on_segment(index_segment, transcribe_all_segment=True)
        app.audio_transcription_beta.clear_text_area()
        app.audio_transcription_beta.add_text_to_segment(f" the transcription for segment {index_segment+1}")

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'Some segments do not contain valid labeling ' \
                                                                         'work. Please select labels from all ' \
                                                                         'required groups.'
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert ['Provide transcription text or mark as nothing to transcribe.' not in payload_error[index] for index in range(1, list_of_segment+1)]
    app.audio_transcription_beta.deactivate_iframe()

def test_transcribe_undo_redo_hot_key_multi_segment(at_job, app):
    """
       Verify requestor could undo/redo action in text area for multi segment
    """

    app.navigation.refresh_page()

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.audio_transcription_beta.click_on_segment(1)
    app.verification.wait_untill_text_present_on_the_page("Segment 2", 15)

    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test hot key for undo/redo for multi segment")
    app.audio_transcription_beta.highlight_text_in_segments("multi")
    app.audio_transcription.span.add_span("span1")

    app.audio_transcription_beta.click_event_marker('segment')
    app.audio_transcription.event.add_event("event2")

    text_after_add_text_span_event = app.audio_transcription_beta.grab_text_from_text_area()

    assert text_after_add_text_span_event == "test hot key for undo/redo for <span_1>m</span_1> ulti  <event_2/> segment"
    app.audio_transcription_beta.delete_tag("<span_1>")
    app.audio_transcription_beta.delete_highlight_text_in_segments("key")
    app.audio_transcription_beta.move_to_word('redo')

    app.navigation.combine_hotkey(Keys.CONTROL, "z")
    app.navigation.combine_hotkey(Keys.CONTROL, "z")

    text_after_undo_text_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_undo_text_span == text_after_add_text_span_event

    app.audio_transcription_beta.delete_tag("<event_2/>")
    app.navigation.combine_hotkey(Keys.CONTROL, "z")

    text_after_undo_delete_event = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_undo_delete_event == text_after_add_text_span_event

    app.navigation.combine_hotkey(Keys.CONTROL, "Z")

    text_after_undo_text_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_undo_text_span == "test hot key for undo/redo for <span_1>m</span_1> ulti   segment"

    app.audio_transcription_beta.deactivate_iframe()

