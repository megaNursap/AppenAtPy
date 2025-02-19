"""
AT - UI Automation - Span list popup
https://appen.atlassian.net/browse/QED-1615
"""
import time

from selenium.webdriver.common.keys import Keys
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job


pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]


USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_span_even_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)


    return job_id


@pytest.mark.dependency()
def test_no_span_popup_list(app, at_job):
    """
    Verify span list popup is not displayed when segment class has no spans defined
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    global job_window
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.add_text_to_bubble("Noise", "test span")

    assert app.audio_transcription.span.get_popup_list() == {'details': [], 'eraser': False, 'spans': ['', '']}


@pytest.mark.dependency(depends=["test_no_span_popup_list"])
def test_event_btn_disable(app, at_job):
    """
    Verify that ‘Add Event’ icon is enabled for all  segment class
    """
    event_btn = app.audio_transcription.event.get_all_btn_event()
    count_of_segment = app.audio_transcription.get_bubbles_name()
    assert event_btn == len(count_of_segment)
    app.image_annotation.deactivate_iframe()
    app.driver.close()

    app.navigation.switch_to_window(job_window)


@pytest.mark.dependency(depends=["test_event_btn_disable"])
def test_create_spans_and_events_at(app, at_job):
    """
    Create spans and events for multiple classes in ontology manager
    """
    target_mode = 'AT'
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    time.sleep(4)

    # app.ontology.open_class("Noise", mode=target_mode)
    app.ontology.add_tag("Span", "test4")
    app.ontology.add_tag("Span", "test3")
    app.ontology.add_tag("Span", "test2")
    app.ontology.add_tag("Span", "1test", "test description")

    app.ontology.add_tag("Event", "event1_1")
    app.ontology.add_tag("Event", "event2")
    app.ontology.add_tag("Event", "event0", "event with description")

    app.navigation.click_link('Save')
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    global job_window
    job_window = app.driver.window_handles[0]
    app.job.preview_job()


@pytest.mark.dependency()
def test_add_event_before_and_after_span(app, at_job):
    """
    Verify event tag can be added at the start or end of a highlighted span text
    """

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(1)
    app.audio_transcription.add_text_to_bubble("Segment 1", "test span", index=0)

    app.audio_transcription.span.highlight_text_in_bubble("span", "Segment 1", index=0)
    app.audio_transcription.span.add_span('test3')

    span_info = app.audio_transcription.span.get_text_with_spans('Segment 1', index=0)
    assert span_info[0]['span_name'] == '<test_3>'
    assert span_info[0]['text'] == 'span'

    app.audio_transcription.event.move_cursor_to_text_in_bubble("span", "Segment 1", index=0)
    app.audio_transcription.event.click_event_marker("Segment 1", index=0)
    app.audio_transcription.event.add_event('event1')

    _events = app.audio_transcription.event.get_events_from_bubble('Segment 1', index=0)
    assert _events == ['<event_1/>']

    app.audio_transcription.event.move_cursor_to_the_end_of_text_in_bubble('Segment 1', index=0)
    app.audio_transcription.event.click_event_marker('Segment 1', index=0)
    app.audio_transcription.event.add_event('event2')
    _events = app.audio_transcription.event.get_events_from_bubble('Segment 1', index=0)
    assert _events == ['<event_1/>', '<event_2/>']


@pytest.mark.dependency(depends=["test_add_event_before_and_after_span"])
def test_delete_span_without_event(app, at_job):
    """
    Verify event tag can be added at the start or end of a highlighted span text
    Verify erasing span does not delete event tag within it
    """
    app.audio_transcription.event.move_cursor_to_text_in_bubble('an','Segment 1', index=0)
    app.audio_transcription.event.click_event_marker('Segment 1', index=0)
    app.audio_transcription.event.add_event('event0')
    _events = app.audio_transcription.event.get_events_from_bubble('Segment 1', index=0)
    assert _events == ['<event_1/>', '<event_0/>', '<event_2/>']

    app.audio_transcription.span.delete_audio_tx_span(['</test_3>', 'pan'])

    _events = app.audio_transcription.event.get_events_from_bubble('Segment 1', index=0)
    assert _events == ['<event_1/>', '<event_0/>', '<event_2/>']

    span_info = app.audio_transcription.span.get_text_with_spans('Segment 1', index=0)
    assert span_info == []


@pytest.mark.dependency(depends=["test_delete_span_without_event"])
def test_event_hotkeys(app, at_job):
    """
        Verify that hotkeys are automatically displayed for events in the popup list
        Verify the events are assigned a value A - Z  (in order)
        Verify that user can choose any event from popup list using hotkey [Alt/option] + [#] in order to create an event tag at the cursor position
        Verify that user can choose event using [Alt/option] + [#] hotkey when the popup list is either opened by clicking on the icon or via hotkey [Cmd/ctrl] + [E]
    """

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.add_text_to_bubble("Segment 3", "test span")

    app.audio_transcription.event.move_cursor_to_the_end_of_text_in_bubble('Segment 3')
    app.audio_transcription.event.click_event_marker("Segment 3")
    events = app.audio_transcription.event.get_popup_list(details=True)

    assert sorted_list_of_dict_by_value(events['details'], 'key') == events['details']
    assert find_dict_in_array_by_value(events['details'], 'key', value='') == None

    hotkey_first_span = events['details'][0]['key']
    name_first_span = events['details'][0]['name']
    app.navigation.combine_hotkey(Keys.ALT, hotkey_first_span)

    assert app.audio_transcription.event.get_events_from_bubble('Segment 3') == ['<event_1/>']
    assert name_first_span == 'event1'

    app.audio_transcription.event.move_cursor_to_text_in_bubble("test", "Segment 3")
    app.audio_transcription.event.click_event_marker("Segment 3")
    app.navigation.combine_hotkey(Keys.COMMAND, "e")

    event_info = app.audio_transcription.event.get_popup_list()
    assert event_info['events'] == ['event1', 'event1_1', 'event2', 'event0']

    app.navigation.combine_hotkey(Keys.ALT, "b")

    assert app.audio_transcription.event.get_events_from_bubble('Segment 3') == ['<event_1_1/>', '<event_1/>']


@pytest.mark.dependency(depends=["test_create_spans_and_events_at"])
def test_open_event_popup_list(app, at_job):
    """
    Verify that clicking on the ‘Add Event’ icon opens a events list popup along with search filter
    """
    #

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Segment 4')
    app.audio_transcription.add_text_to_bubble("Segment 4", "test span")

    app.audio_transcription.event.move_cursor_to_text_in_bubble("span", "Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")

    event_info = app.audio_transcription.event.get_popup_list(details=True)
    assert event_info['events'] == ['event1', 'event1_1', 'event2', 'event0']
    assert event_info['filter']


@pytest.mark.dependency(depends=["test_open_event_popup_list"])
def test_filter_events(app, at_job):
    """
    Verify 'Filter Events' search field functionality
    Verify user can choose to close the popup without selecting an event tag, by clicking outside of the popup
    """
    app.audio_transcription.event.filter_events("2")
    assert app.audio_transcription.event.get_popup_list()['events'] == ['event2']

    app.audio_transcription.select_bubble_by_name('Segment 4') #  close the event popup list


@pytest.mark.dependency(depends=["test_filter_events"])
def test_event_info(app, at_job):
    """
     Verify that events with description show info icon upon hovering and ones without description don't
    """
    app.audio_transcription.event.move_cursor_to_text_in_bubble("span", "Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")

    app.audio_transcription.event.open_info_bar("event2")
    assert app.audio_transcription.event.grab_info() == {'name': 'event2','hot_keys':'ALT/OPTION + C','description':''}

    app.audio_transcription.event.open_info_bar("event0")
    assert app.audio_transcription.event.grab_info() == {'name': 'event0', 'hot_keys': 'ALT/OPTION + D',
                                                         'description': 'event with description'}
    app.audio_transcription.span.close_span_info_bar()
    app.audio_transcription.select_bubble_by_name('Segment 4') #  close the event popup list


@pytest.mark.dependency(depends=["test_event_info"])
def test_add_event(app, at_job):
    """
     Verify that selecting a event tag from the popup list, places the tag at the cursor position in the transcription area → Smoke test
     Verify user can add event tag at the very beginning and end of the text
     Verify user can add event tag in the middle of a word
     Verify user can add event tags consecutively
    """

    app.audio_transcription.event.move_cursor_to_text_in_bubble("span", "Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")

    app.audio_transcription.event.add_event('event1_1')
    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_1_1/>']

    app.audio_transcription.event.move_cursor_to_text_in_bubble("test", "Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")
    app.audio_transcription.event.add_event('event0')

    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_0/>', '<event_1_1/>']

    app.audio_transcription.event.move_cursor_to_text_in_bubble("span", "Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")
    app.audio_transcription.event.add_event('event1')

    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_0/>', '<event_1_1/>', '<event_1/>']

    app.audio_transcription.event.move_cursor_to_the_end_of_text_in_bubble("Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")
    app.audio_transcription.event.add_event('event2')

    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_0/>', '<event_1_1/>', '<event_1/>', '<event_2/>']

    app.audio_transcription.event.move_cursor_to_text_in_bubble("t","Segment 4")
    app.audio_transcription.event.click_event_marker("Segment 4")
    app.audio_transcription.event.add_event('<event_2/>')

    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_0/>', '<event_2/>','<event_1_1/>', '<event_1/>', '<event_2/>']


@pytest.mark.dependency(depends=["test_add_event"])
def test_delete_event(app, at_job):
    """
    Verify event tag can be deleted via backspace or delete key
    """
    app.audio_transcription.event.move_cursor_to_text_in_bubble("an", "Segment 4")
    app.audio_transcription.event.delete_event(key='backspace')
    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_0/>', '<event_2/>', '<event_1_1/>', '<event_2/>']

    app.audio_transcription.event.move_cursor_to_text_in_bubble("test", "Segment 4")
    app.audio_transcription.event.delete_event(key='backspace')
    _events = app.audio_transcription.event.get_events_from_bubble('Segment 4')
    assert _events == ['<event_0/>', '<event_1_1/>', '<event_2>']


@pytest.mark.dependency()
def test_open_span_popup_list(app, at_job):
    """
    Verify span list popup appears when user selects text in the transcription area for segment class with spans defined
    Verify span popup lists all spans for the segment class (with scroll) in the order defined, along with eraser
    """
    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.add_text_to_bubble("Noise", "test span")

    app.audio_transcription.span.highlight_text_in_bubble("span", "Noise")

    assert app.audio_transcription.span.get_popup_list() == {'spans': ['person span', 'noise span', 'test4', 'test3', 'test2', '1test'],
                                                             'eraser': False, 'details': []}

    app.audio_transcription.span.close_popup_list()


@pytest.mark.dependency(depends=["test_open_span_popup_list"])
def test_filter_spans(app, at_job):
    """
    Verify 'Filter spans' functionality in span list popup (for full & partial string)
    """
    app.audio_transcription.span.highlight_text_in_bubble("span", "Noise")
    app.audio_transcription.span.filter_span("3")
    app.audio_transcription.span.close_popup_list()

    app.audio_transcription.span.highlight_text_in_bubble("span", "Noise")
    app.audio_transcription.span.filter_span("test")
    assert app.audio_transcription.span.get_popup_list() == {'spans': ['test4', 'test3', 'test2', '1test'],
                                                             'eraser': False, 'details': []}
    app.audio_transcription.span.close_popup_list()


@pytest.mark.dependency(depends=["test_filter_spans"])
def test_span_info(app, at_job):
    """
    Verify span with description shows info icon and one without description doesn't
    """
    app.audio_transcription.span.highlight_text_in_bubble("span", "Noise")

    app.audio_transcription.span.open_span_info_bar("person span")
    assert app.audio_transcription.span.grab_span_info() == {'name': 'person span', 'hot_keys': 'ALT/OPTION + A',
                                                             'description': 'Describe here'}

    app.audio_transcription.span.close_span_info_bar()
    app.audio_transcription.span.close_popup_list()


@pytest.mark.dependency(depends=["test_span_info"])
def test_create_span(app, at_job):
    """
    Verify text is highlighted with span label once span is selected in the popup and saves successfully
    """

    app.audio_transcription.span.highlight_text_in_bubble("span", "Noise")

    span_info = app.audio_transcription.span.get_popup_list(details=True)
    span_details = span_info['details']
    assert span_info['spans'] == ['person span', 'noise span', 'test4', 'test3', 'test2', '1test']

    app.audio_transcription.span.add_span('test2')

    app.audio_transcription.span.highlight_text_in_bubble("test", "Noise")
    app.audio_transcription.span.add_span('test4')

    text_with_span = app.audio_transcription.span.get_text_with_spans("Noise")

    assert len(text_with_span) == 2

    text_test = find_dict_in_array_by_value(text_with_span, 'text', 'test')
    text_span = find_dict_in_array_by_value(text_with_span, 'text', 'span')

    assert text_test['span_name'] == 'test4'
    assert text_test['span_color'] == find_dict_in_array_by_value(span_details, 'name', 'test4')['color']

    assert text_span['span_name'] == 'test2'
    assert text_span['span_color'] == find_dict_in_array_by_value(span_details, 'name', 'test2')['color']

#
# @pytest.mark.dependency(depends=["test_create_span"])
# def test_remove_span(app, at_job):
#     """
#     Verify that clicking on ‘Eraser’ will remove the highlight, if there is a span highlight in the selected text area
#     Verify that clicking on ‘Eraser’ doesn’t do anything, if there is no span highlighted in the selected text area
#     """
#     app.audio_transcription.span.highlight_text_in_bubble("test", "Noise")
#     time.sleep(4)
#     app.audio_transcription.span.delete_span()
#     text_with_span = app.audio_transcription.span.get_text_with_labels("Noise")
#     assert len(text_with_span) == 1
#     assert text_with_span[0]['text'] == 'span'
#
#     app.audio_transcription.span.highlight_text_in_bubble("test", "Noise")
#     time.sleep(4)
#     app.audio_transcription.span.delete_span()
#     text_with_span = app.audio_transcription.span.get_text_with_labels("Noise")
#     assert len(text_with_span) == 1
#     assert text_with_span[0]['text'] == 'span'
#
#
# @pytest.mark.dependency(depends=["test_remove_span"])
# def test_undo_erase_span(app, at_job):
#     """
#     Verify user can undo span erase
#     """
#     text_with_span = app.audio_transcription.span.get_text_with_labels("Noise")
#     assert len(text_with_span) == 1
#
#     app.navigation.undo_shortcut()
#
#     text_with_span_undo = app.audio_transcription.span.get_text_with_labels("Noise")
#     # assert len(text_with_span_undo) == 2
#
#
# @pytest.mark.dependency(depends=["test_undo_erase_span"])
# def test_erase_part_of_span(app, at_job):
#     """
#     Verify user can delete span on partial text
#     """
#     app.audio_transcription.add_text_to_bubble("Noise", "1111223333", index=1)
#
#     app.audio_transcription.span.highlight_text_in_bubble('1111223333', 'Noise', index=1)
#     app.audio_transcription.span.add_span('1test')
#
#     start_text_with_span = app.audio_transcription.span.get_text_with_labels('Noise', index=1)
#     assert len(start_text_with_span) == 1
#     assert start_text_with_span[0]['span_name'] == '1test'
#
#     app.audio_transcription.span.highlight_text_in_bubble('22', 'Noise', index=1)
#     app.audio_transcription.span.delete_span()
#
#     text_with_span = app.audio_transcription.span.get_text_with_labels('Noise', index=1)
#     assert len(text_with_span) == 2
#     assert text_with_span[0]['span_name'] == '1test'
#     assert text_with_span[1]['span_name'] == '1test'
#
#     assert start_text_with_span[0]['span_color'] == text_with_span[0]['span_color'] == text_with_span[1]['span_color']
#
#
# @pytest.mark.dependency(depends=["test_erase_part_of_span"])
# def test_erase_span_across_multiple_lines(app, at_job):
#     """
#     Verify user can erase span spread across more than one line
#     """
#     app.audio_transcription.add_text_to_bubble("Person",
#                                                "1111111111 2222222222 3333333333 4444444444 55555555555 6666666666 77777777777 888888888")
#
#     app.audio_transcription.span.highlight_text_in_bubble('55555555555 6666666666', 'Person')
#     app.audio_transcription.span.add_span('span 2')
#
#     start_text_with_span = app.audio_transcription.span.get_text_with_labels('Person')
#     assert len(start_text_with_span) == 1
#     assert start_text_with_span[0]['span_name'] == 'span 2'
#
#     app.audio_transcription.span.highlight_text_in_bubble('55555555555 6666666666', 'Person')
#     time.sleep(4)
#     app.audio_transcription.span.delete_span()
#
#     text_with_span = app.audio_transcription.span.get_text_with_labels('Person')
#     assert len(text_with_span) == 0
#
#
# @pytest.mark.dependency(depends=["test_erase_span_across_multiple_lines"])
# def test_span_hotkeys(app, at_job):
#     """
#     Verify that user can choose any span from popup list using hotkey [Alt/option] + [#] and apply it to the selected text
#     Verify that hotkeys are automatically displayed for spans in the popup list
#     Verify spans in the popup list are assigned a value A - Z (in order)
#     """
#
#     text_with_span = app.audio_transcription.span.get_text_with_labels('Person')
#     assert len(text_with_span) == 0
#
#     app.audio_transcription.span.highlight_text_in_bubble('2222222222', 'Person')
#
#     span_info = app.audio_transcription.span.get_popup_list(details=True)
#
#     assert sorted_list_of_dict_by_value(span_info['details'], 'key') == span_info['details']
#     assert find_dict_in_array_by_value(span_info['details'], 'key', value='') == None
#
#     hotkey_first_span = span_info['details'][0]['key']
#     name_first_span = span_info['details'][0]['name']
#     app.navigation.combine_hotkey(Keys.ALT, hotkey_first_span)
#
#     text_with_span = app.audio_transcription.span.get_text_with_labels('Person')
#     assert len(text_with_span) == 1
#     assert text_with_span[0]['span_name'] == name_first_span


# # TODO https://appen.spiraservice.net/5/TestCase/1408.aspx - Verify that event popup allows scroll when there are more than 5 events → Regression test
# # TODO  https://appen.spiraservice.net/5/TestCase/1396.aspx - Verify span names are shown correctly for when the event also has the same name as class, after ‘Save and close’ → Regression test (Bug:  )
# # https://appen.spiraservice.net/5/TestCase/1397.aspx - Verify span names that start with numbers are shown correctly after ‘Save and close’ → Regression test
# # https://appen.spiraservice.net/5/TestCase/1398.aspx  - Verify long span labels are truncated when span text is spread across 2 lines → Regression test
# # TODO https://appen.spiraservice.net/5/TestCase/1384.aspx - Verify long span names are truncated with ellipses in popup → Regression test
