import time

import allure
import pytest
from allure_commons.types import AttachmentType
from selenium.webdriver import Keys


from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file
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
    DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_beta,
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

@pytest.fixture(autouse=True)
def at_job_after(app, at_job):
    yield
    app.audio_transcription_beta.clear_text_area()
    app.audio_transcription_beta.deactivate_iframe()


def test_add_span_in_single_segment(at_job, app):
    """
    Verify requestor could add span for text transcription for single segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("test single segment with transcription")

    app.audio_transcription_beta.highlight_words_in_segments("transcription")
    app.audio_transcription.span.add_span('span3')

    text_after_add_span = app.audio_transcription_beta.grab_text_from_text_area()

    assert "<span_3>transcription</span_3>" in text_after_add_span.split(' ')
    assert text_after_add_span == 'test single segment with <span_3>transcription</span_3> ', "The transcribe text NOT as expected"


def test_delete_span_in_single_segment(at_job, app):
    """
    Verify requestor could delete span for text transcription for single segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for delete span")

    app.audio_transcription_beta.highlight_text_in_segments("transcription")
    app.audio_transcription.span.add_span('span3')

    app.audio_transcription_beta.highlight_words_in_segments("delete span")
    app.audio_transcription.span.add_span('span2')

    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_spans == 'text in <span_3>t</span_3> ranscription area for <span_2>delete span</span_2> ', "The transcribe text NOT as expected "

    app.audio_transcription_beta.delete_tag('</span_2>')

    text_delete_added_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_delete_added_span == 'text in <span_3>t</span_3> ranscription area for delete span ', "The transcribe text NOT as expected after deleted span"


def test_open_span_popup_list_one_segment(app, at_job):
    """
    Verify span list popup appears when user selects text in the transcription area for segment class with spans defined
    Verify span popup lists all spans for the segment class (with scroll) in the order defined, along with eraser
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for test pop up span")

    app.audio_transcription_beta.highlight_text_in_segments("area")
    assert app.audio_transcription.span.get_popup_list(details=True) == {'spans': ['span1', 'span2', 'span3'],
                                                                         'eraser': False,
                                                                         'details':
                                                                         [{'name': 'span1', 'key': 'ALT/OPTION+A', 'color': ' #A92D26'},
                                                                         {'name': 'span2', 'key': 'ALT/OPTION+B', 'color': ' #7D1F4E'},
                                                                         {'name': 'span3', 'key': 'ALT/OPTION+C', 'color': ' #431F87'}]}

    app.audio_transcription.span.close_popup_list()

def test_filter_spans_one_segment(app, at_job):
    """
    Verify 'Filter spans' functionality in span list popup (for full & partial string)
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for test filter span")

    app.audio_transcription_beta.highlight_text_in_segments("test")
    time.sleep(2)
    app.audio_transcription.span.filter_span("2")
    assert {'spans': ['span2'],
             'eraser': False,
             'details':
                 [{'color': ' #7D1F4E', 'key': 'ALT/OPTION+B', 'name': 'span2'}]} == app.audio_transcription.span.get_popup_list(details=True), "List of span not contains proper information after filter"
    app.audio_transcription.span.close_popup_list()

    app.audio_transcription_beta.highlight_text_in_segments("transcription")
    app.audio_transcription.span.filter_span("test")

    assert app.audio_transcription.span.get_popup_list() == {'spans': [],
                                                             'eraser': False, 'details': []}
    app.audio_transcription.span.close_popup_list()


def test_add_span_by_hot_key(app, at_job):
    """
    Verify that user could add span by hot key
    1. Highlight text
    2. Alt+{letter}
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for test hot key of span")

    app.audio_transcription_beta.highlight_text_in_segments("test")

    app.navigation.combine_hotkey(Keys.ALT, "b")

    text_after_added_first_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_added_first_span == 'text in transcription area for <span_2>t</span_2> est hot key of span', "The " \
                                                                                                                   "transcribe text NOT as expected after add span by hot key "

    app.audio_transcription_beta.highlight_text_in_segments("text")

    app.navigation.combine_hotkey(Keys.ALT, "a")

    text_after_added_second_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_added_second_span == '<span_1>t</span_1> ext in transcription area for <span_2>t</span_2> est hot key of span', \
        "The transcribe text NOT as expected after add second " \
        "span by hot key "


def test_open_event_popup_list_one_segment(app, at_job):
    """
    Verify that clicking on the ‘Add Event’ icon opens a events list popup along with search filter
    """

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for test popup event")

    app.audio_transcription_beta.click_event_marker("popup")

    event_info = app.audio_transcription.event.get_popup_list(details=True)
    assert event_info['events'] == ['event1', 'event2', 'event3']
    assert event_info['filter']
    assert event_info['details'] == [{'name': 'event1', 'key': 'ALT/OPTION+A', 'color': '#2C238C'},
                                     {'name': 'event2', 'key': 'ALT/OPTION+B', 'color': '#192779'},
                                     {'name': 'event3', 'key': 'ALT/OPTION+C', 'color': '#1D499C'}
                                     ]



def test_filter_events_one_segment(app, at_job):
    """
    Verify 'Filter Events' search field functionality
    Verify user can choose to close the popup without selecting an event tag, by clicking outside of the popup
    """

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for test filter event")
    app.audio_transcription_beta.click_event_marker("filter")

    app.audio_transcription.event.filter_events("2")
    assert app.audio_transcription.event.get_popup_list()['events'] == ['event2']

    app.audio_transcription.event.filter_events("test")
    assert app.audio_transcription.event.get_popup_list()['events'] == []



def test_add_event_in_single_segment(at_job, app):
    """
    Verify requestor could add event for text transcription for single segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for add event")

    app.audio_transcription_beta.click_event_marker('area')
    app.audio_transcription.event.add_event('event2')
    text_after_add_event = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_event == 'text in transcription  <event_2/> area for add event', "The transcribe text NOT " \
                                                                                           "as expected after added" \
                                                                                           " the event "



def test_delete_event_in_single_segment(at_job, app):
    """
    Verify requestor could delete event for text transcription for single segment
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for delete event")

    app.audio_transcription_beta.click_event_marker('transcription')
    app.audio_transcription.event.add_event('event2')

    app.audio_transcription_beta.click_event_marker('delete')
    app.audio_transcription.event.add_event('event1')
    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_spans == 'text in  <event_2/> transcription area for  <event_1/> delete event', "The transcribe text NOT " \
                                                                                                          "as expected after added" \
                                                                                                          " the event "

    app.audio_transcription_beta.delete_tag('<event_2/>')

    text_after_delete_event = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_event == 'text in   transcription area for  <event_1/> delete event', "The transcribe text NOT " \
                                                                                                   "as expected after added" \
                                                                                                   " the event "



def test_add_event_by_hot_key(app, at_job):

    app.navigation.refresh_page()

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for add event")

    app.audio_transcription_beta.move_to_word('area')
    app.navigation.combine_hotkey(Keys.CONTROL,'e')
    app.navigation.combine_hotkey(Keys.ALT, 'c')
    text_after_add_spans = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_spans == 'text in transcription  <event_3/> area for add event', "The transcribe text NOT " \
                                                                                                          "as expected after added" \
                                                                                                          " the event by hot key "

    app.audio_transcription_beta.click_event_marker("event")
    app.navigation.combine_hotkey(Keys.ALT, 'a')


def test_add_timestamp_by_hot_key_one_segment(app, at_job):

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for add event")

    app.audio_transcription_beta.move_to_word('area')
    app.navigation.combine_hotkey(Keys.CONTROL,'b')
    app.audio_transcription_beta.click_on_waveform()
    text_after_add_first_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_first_timestamp == 'text in transcription [9.582] area for add event', "The transcribe text NOT as " \
                                                                                                   "expected after added the " \
                                                                                                   "timestamp by hot key "


def test_delete_timestamp_one_segment(app, at_job):

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for add event")

    app.audio_transcription_beta.move_to_word('area')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()


    text_after_add_first_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_first_timestamp == 'text in transcription [9.582] area for add event', "The transcribe text NOT " \
                                                                                                    "as expected after added" \
                                                                                                    " the timestamp by hot key "
    #
    app.audio_transcription_beta.move_to_word('add')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()

    #
    text_after_add_second_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_second_timestamp == 'text in transcription [9.582] area for [9.582] add event', "The transcribe " \
                                                                                                    "text NOT as " \
                                                                                                    "expected after " \
                                                                                                    "added the second " \
                                                                                                    "timestamp by hot " \
                                                                                                    "key "
    #
    app.audio_transcription_beta.delete_tag("[9.582]")
    #
    text_after_delete_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_timestamp == 'text in transcription  area for [9.582] add event', "The transcribe " \
                                                                                                              "text NOT as " \
                                                                                                              "expected after " \
                                                                                                              "delete the first " \
                                                                                                              "timestamp"


def test_span_event_timestamp(app,at_job):

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("text in transcription area for add event, span and timestamp")

    app.audio_transcription_beta.highlight_text_in_segments("area")
    app.audio_transcription.span.add_span('span3')

    app.audio_transcription_beta.click_event_marker('event')
    app.audio_transcription.event.add_event('event1')

    app.audio_transcription_beta.move_to_word('timestamp')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()

    text_after_add_tags = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_add_tags == "text in transcription <span_3>a</span_3> rea for add  <event_1/> event, span and [9.582] timestamp"

    app.audio_transcription_beta.delete_tag("<span_3>")
    text_after_delete_span = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_span == "text in transcription a rea for add  <event_1/> event, span and [9.582] timestamp"

    app.audio_transcription_beta.highlight_text_in_segments("text")
    app.audio_transcription.span.add_span('span1')

    app.audio_transcription_beta.delete_tag("<event_1/>", index=1)
    app.audio_transcription_beta.delete_tag("[9.582]", index=1)

    text_after_delete_event_timestamp = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_after_delete_event_timestamp == "<span_1>t</span_1> ext in transcription a rea for add   event, span and  timestamp"




