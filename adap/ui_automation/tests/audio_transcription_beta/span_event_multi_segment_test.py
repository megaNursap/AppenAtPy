import time

import pytest
from selenium.webdriver import Keys

from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file, \
    convert_audio_datatime_to_second
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]




@pytest.fixture(scope='module')
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    USER_EMAIL = get_user_email('test_ui_account')
    PASSWORD = get_user_password('test_ui_account')
    API_KEY = get_user_api_key('test_ui_account')
    DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data.csv")
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


def test_add_span_to_text(at_job, app):
    """
        Verify requestor could add span to transcribe text
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)

    app.audio_transcription_beta.add_text_to_segment("test that")

    app.audio_transcription_beta.add_text_to_segment(" this text should be transcribe")

    app.verification.text_present_on_page('test that this text should be transcribe')

    app.audio_transcription_beta.delete_word_in_segment("should")

    text_after_delete = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete == "test that this text  be transcribe", "The transcribe text NOT as expected"

    app.audio_transcription_beta.deactivate_iframe()


def test_transcribe_all_segments(at_job, app):
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
        app.audio_transcription_beta.add_text_to_segment(f" the transcription for segment {index_segment+1}")

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()
    time.sleep(2)
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'Some segments do not contain valid labeling ' \
                                                                         'work. Please select labels from all ' \
                                                                         'required groups.'
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert ['Provide transcription text or mark as nothing to transcribe.' not in payload_error[index] for index in range(1, list_of_segment+1)]
    app.audio_transcription_beta.deactivate_iframe()


def test_add_span_multi_segment(at_job, app):
    """
    Verify requestor could add span for multi segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test for add segment for multi segments")
    app.audio_transcription_beta.highlight_words_in_segments('segments')
    app.audio_transcription.span.add_span('span2')

    text_after_add_span = app.audio_transcription_beta.grab_text_from_text_area()

    assert "<span_2>segments</span_2>" in text_after_add_span.split(' ')
    assert text_after_add_span == 'test for add segment for multi <span_2>segments</span_2> ', "The transcribe text NOT as expected"

    app.audio_transcription_beta.deactivate_iframe()


def test_delete_span_multi_segment(at_job, app):
    """
    Verify requestor could delete span in multi segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=1)
    app.verification.wait_untill_text_present_on_the_page("Segment 2", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test for delete span in multi segment")
    app.audio_transcription_beta.highlight_text_in_segments('delete')
    app.audio_transcription.span.add_span('span1')

    app.audio_transcription_beta.highlight_text_in_segments('multi')
    app.audio_transcription.span.add_span('span3')

    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()

    assert text_after_add_spans == 'test for <span_1>d</span_1> elete span in <span_3>m</span_3> ulti segment', "The transcribe text NOT as expected after added spans"

    app.audio_transcription_beta.delete_tag('<span_1>')

    text_after_delete_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_span == 'test for d elete span in <span_3>m</span_3> ulti segment', "The transcribe text NOT as expected after delete span"

    app.audio_transcription_beta.deactivate_iframe()


def test_add_span_by_hot_key_multi_segment(at_job, app):
    """
    Verify requestor could add span in multi segment by hot key
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test for add span in multi segment by hot key")
    app.audio_transcription_beta.highlight_words_in_segments('key')
    app.navigation.combine_hotkey(Keys.ALT, 'c')

    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()

    assert text_after_add_spans == 'test for add span in multi segment by hot <span_3>key</span_3> ', "The transcribe text NOT as expected after added spans by hot key"

    app.audio_transcription_beta.deactivate_iframe()


def test_add_event_by_hot_key_multi_segment(at_job, app):
    """
    Verify requestor could add event in multi segment by hot key
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=2)
    app.verification.wait_untill_text_present_on_the_page("Segment 3", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test for add event in multi segment by hot key")

    app.audio_transcription_beta.move_to_word('event')
    app.navigation.combine_hotkey(Keys.CONTROL, 'e')
    app.navigation.combine_hotkey(Keys.ALT, 'b')
    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_spans == 'test for add  <event_2/> event in multi segment by hot key', "The transcribe text NOT " \
                                                                                           "as expected after added" \
                                                                                           " the event by hot key "

    app.audio_transcription_beta.click_event_marker("key")
    app.navigation.combine_hotkey(Keys.ALT, 'a')

    app.audio_transcription_beta.deactivate_iframe()


def test_add_event_multi_segment(at_job, app):
    """
    Verify requestor could add event in multi segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=1)
    app.verification.wait_untill_text_present_on_the_page("Segment 2", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test for add event in multi segment")

    app.audio_transcription_beta.click_event_marker('event')
    app.audio_transcription.event.add_event('event1')

    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_spans == 'test for add  <event_1/> event in multi segment', "The transcribe text NOT " \
                                                                                        "as expected after added" \
                                                                                           " the event"

    app.audio_transcription_beta.deactivate_iframe()


def test_delete_event_multi_segment(at_job, app):
    """
    Verify requestor could add event in multi segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=1)
    app.verification.wait_untill_text_present_on_the_page("Segment 2", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("test for delete event in multi segment")

    app.audio_transcription_beta.click_event_marker('event')
    app.audio_transcription.event.add_event('event1')

    app.audio_transcription_beta.click_event_marker('multi')
    app.audio_transcription.event.add_event('event3')

    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_spans == 'test for delete  <event_1/> event in  <event_3/> multi segment', "The transcribe text NOT " \
                                                                                        "as expected after added" \
                                                                                           " the event"

    app.audio_transcription_beta.delete_tag("<event_1/>")

    text_after_delete_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_span == 'test for delete   event in  <event_3/> multi segment', "The transcribe text NOT " \
                                                                                                     "as expected after delete" \
                                                                                                     " the event"



    app.audio_transcription_beta.deactivate_iframe()


def test_add_timestamp_multi_segment_by_hot_key(at_job, app):
    """
    Verify requestor could add timestamp in multi segment by hot key
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=3)
    app.verification.wait_untill_text_present_on_the_page("Segment 4", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for add timestamp in multi segments")

    app.audio_transcription_beta.move_to_word('timestamp')
    app.navigation.combine_hotkey(Keys.CONTROL, 'b')
    app.audio_transcription_beta.click_on_waveform()
    text_after_add_first_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_first_timestamp == 'text in transcription area for add [2.139] timestamp in multi segments', "The transcribe text NOT as expected after added the timestamp by hot key "

    app.audio_transcription_beta.deactivate_iframe()


def test_delete_timestamp_multi_segment(at_job, app):
    """
    Verify requestor could delete timestamp in multi segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=4)
    app.verification.wait_untill_text_present_on_the_page("Segment 5", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for delete timestamp in multi segments")

    app.audio_transcription_beta.move_to_word('delete')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()

    text_after_add_first_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_first_timestamp == 'text in transcription area for [1.612] delete timestamp in multi segments', "The transcribe text NOT as expected after added the timestamp "
    #
    app.audio_transcription_beta.move_to_word('multi')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()

    #
    text_after_add_second_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_second_timestamp == 'text in transcription area for [1.612] delete timestamp in [1.612] multi segments', "The transcribe text NOT as expected after added the second timestamp by hotkey"
    #
    app.audio_transcription_beta.delete_tag("[1.612]")
    #
    text_after_delete_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_timestamp == 'text in transcription area for  delete timestamp in [1.612] multi segments', "The transcribe text NOT as expected after delete the first timestamp"

    app.audio_transcription_beta.deactivate_iframe()


def test_span_event_timestamp_multi_segment(at_job, app):
    """
    Verify requestor could manipulate with different tags in the same time  in multi segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(index=2)
    app.verification.wait_untill_text_present_on_the_page("Segment 3", 15)
    app.audio_transcription_beta.clear_text_area()

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for manipulate with timestamp/event/span in multi segments")

    app.audio_transcription_beta.click_event_marker('transcription')
    app.audio_transcription.event.add_event('event2')

    app.audio_transcription_beta.highlight_text_in_segments('manipulate')
    app.audio_transcription.span.add_span("span2")

    app.audio_transcription_beta.move_to_word('multi')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()

    app.audio_transcription_beta.highlight_words_in_segments('segments')
    app.audio_transcription.span.add_span("span1")


    text_after_add_tags = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_tags == 'text in  <event_2/> transcription area for <span_2>m</span_2> anipulate with timestamp/event/span in [0.934] multi <span_1>segments</span_1> ', "The transcription text NOT as expected after added tags"

    app.audio_transcription_beta.delete_tag("<span_2>")
    app.audio_transcription_beta.delete_tag("<event_2/>")

    app.audio_transcription_beta.click_event_marker("text")
    app.audio_transcription.event.add_event("event3")

    text_after_delete_tags = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_tags == '<event_3/> text in   transcription area for m anipulate with timestamp/event/span in [0.934] multi <span_1>segments</span_1> ', "The transcription text NOT as expected after added tags"

    app.audio_transcription_beta.deactivate_iframe()


