"""
AT - UI Automation - CML tag attributes   https://appen.atlassian.net/browse/QED-1234

AT - UI Automation - Preview and data unit layout
https://appen.atlassian.net/browse/QED-1236

AT - UI Automation - Class events
https://appen.atlassian.net/browse/QED-1237

AT - UI Automation - Class spans
https://appen.atlassian.net/browse/QED-1238

AT - UI Automation - Spans/Events
https://appen.atlassian.net/browse/QED-1285
"""
import time

import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_deign, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology (using force-fullscreen="true")
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_full_Screen_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology-without-span-event.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    return job_id



@pytest.mark.audio_transcription_api
def test_no_required_cml_tag():
    """
    Verify job cannot be saved, if mandatory attributes are missing in CML tag
    """
    invalid_CML = '<cml:audio_transcription validates="required" audio-annotation-data="{{annotate_the_audio}}" name="audio transcription"/>'

    job = Builder(API_KEY)

    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test Invalid CML",
            'instructions': "invalid CML",
            'cml': invalid_CML,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(422)
    assert res.json_response == {'error': {'errors': ['&lt;cml:audio_transcription&gt; requires a source-data '
                                                      'attribute']}}


@pytest.mark.audio_transcription_api
def test_all_cml_tag():
    """
    Verify requestor can create job with all available CML attributes
    """
    all_CML = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{' \
              'annotate_the_audio}}"  label="output_column" review-data="{{audio_url}}" task-type="qa" /> '

    job = Builder(API_KEY)

    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test ALL CML",
            'instructions': "all fields CML",
            'cml': all_CML,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response['title'] == "Audio Transcription Test All Cml"
    assert not res.json_response.get('errors', False)


def test_create_at_job(app, at_job):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")

    msg = app.job.get_job_messages()
    assert msg == []


def test_at_preview_data_unit_design(app, at_job):
    """
    Verify requestor can preview data
    When cml force-fullscreen="true", verify requestor can open tool using "Open Transcription Tool"
    Verify tool level nothing to transcribe popup is shown in full screen mode
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    app.job.open_tab('DATA')

    units = app.job.data.find_all_units_with_status('new')
    first_unit = units['unit id'][0]

    app.job.data.open_unit_by_id(first_unit)
    app.verification.current_url_contains("/units/%s" % first_unit)
    app.job.preview_job()
    # page takes long time to load and show the button
    time.sleep(10)
    app.audio_transcription.activate_iframe_by_index(2)
    app.audio_transcription.activate_iframe_by_index(2)
    app.navigation.click_btn("Open Transcription Tool")

    app.verification.text_present_on_page("Empty Segments")
    app.verification.text_present_on_page("No Transcriptions have been made. Is there nothing to transcribe?")

    assert not app.audio_transcription.toolbar.button_is_disable('play')
    assert not app.audio_transcription.toolbar.button_is_disable('back')
    assert not app.audio_transcription.toolbar.button_is_disable('forward')
    assert not app.audio_transcription.toolbar.button_is_disable('help')

    app.audio_transcription.toolbar.save_annotation()
    app.verification.text_present_on_page("Audio Transcription")

    app.audio_transcription.deactivate_iframe()


# ---------- Class Events ---------
@pytest.mark.dependency()
def test_transcribe_this_layer_checkbox(app, at_job):
    """
    Verify Audio Tx ontology class has 'Transcribe the layer' checkbox
    Verify enabling 'Transcribe the layer' allows requestor to add spans and events
    """

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    app.navigation.click_link('Manage Audio Transcription Ontology')

    app.verification.text_present_on_page("Transcribe the layer")

    assert app.verification.checkbox_by_text_is_selected('Transcribe the layer')

    app.verification.text_present_on_page("Events")
    app.verification.text_present_on_page("Spans")
    app.verification.text_present_on_page("Labels")

    app.navigation.click_checkbox_by_text('Transcribe the layer')
    assert not app.verification.checkbox_by_text_is_selected('Transcribe the layer')

    app.verification.text_present_on_page("Add Span")
    app.verification.text_present_on_page("Add Event")
    app.verification.text_present_on_page("Add Label Group")


@pytest.mark.dependency(depends=["test_transcribe_this_layer_checkbox"])
def test_class_events_required_fields(app, at_job):
    """
    Verify required field validation is shown for name field to add Event
    """

    app.ontology.add_tag("Event", "", "")
    app.verification.text_present_on_page("Title cannot be left blank.")

    events = app.ontology.get_current_class_events()
    assert events == [{'description': '', 'name': ''}]

    app.navigation.click_link('Cancel')


@pytest.mark.dependency(depends=["test_class_events_required_fields"])
def test_add_class_event(app, at_job):
    """
    Verify requestor can successfully add event to an ontology class
    """

    app.navigation.refresh_page()
    app.user.close_guide()
    events = app.ontology.get_current_class_events()
    assert events == []

    app.ontology.add_tag("Event", "test", "test")
    time.sleep(5)

    # assert app.ontology.open_class(random_class, mode=target_mode) == True, "Modal Win Class Edit not present"
    events = app.ontology.get_current_class_events()
    assert events == [{'description': 'test', 'name': 'test'}]

    # app.navigation.click_link('Cancel')


@pytest.mark.dependency(depends=["test_add_class_event"])
def test_add_multiple_class_events(app, at_job):
    """
    Verify requestor can configure multiple Events for a given ontology class
    """
    app.user.close_guide()

    current_events = app.ontology.get_current_class_events()

    new_events = []
    len_new_events = random.randint(1, 4)
    faker = Faker()
    for i in range(len_new_events):
        random_name = faker.zipcode()
        app.ontology.add_tag("Event", random_name, random_name)
        new_events.append({'name':random_name, 'description': random_name})

    time.sleep(4)

    events = app.ontology.get_current_class_events()
    expected_events = current_events + new_events

    assert len(events) == len(expected_events)
    assert sorted_list_of_dict_by_value(events, 'name') == sorted_list_of_dict_by_value(expected_events, 'name')

    time.sleep(5)


@pytest.mark.dependency(depends=["test_add_multiple_class_events"])
def test_class_events_duplicates(app, at_job):
    """
    Verify user cannot add events with duplicate names
    """

    app.ontology.add_tag("Event", 'duplicate', 'duplicate')
    app.ontology.add_tag("Event", 'duplicate', '')

    app.verification.text_present_on_page('Title must be unique.')

    app.navigation.click_link('Cancel')
    time.sleep(3)


@pytest.mark.dependency(depends=["test_add_multiple_class_events", 'test_class_events_duplicates'])
def test_edit_class_event(app, at_job):
    """
    Verify requestor can edit Event name and description fields
    """

    current_events = app.ontology.get_current_class_events()

    _event_to_update = current_events[0]

    app.ontology.edit_class_event(_event_to_update['name'], "updated", 'updated', 'Done')

    time.sleep(4)

    updated_events = app.ontology.get_current_class_events()

    assert updated_events[0]['name'] == 'updated'
    assert updated_events[0]['description'] == 'updated'

    time.sleep(3)


@pytest.mark.dependency(depends=["test_add_multiple_class_events", 'test_class_events_duplicates'])
def test_delete_class_event(app, at_job):
    """
    Verify requestor can delete an Event successfully
    """

    current_events = app.ontology.get_current_class_events()
    _event_to_delete = current_events[0]
    app.ontology.delete_event_by_name(_event_to_delete['name'])
    app.navigation.click_link('Save')
    time.sleep(3)
    app.navigation.refresh_page()

    current_events = app.ontology.get_current_class_events()
    assert not find_dict_in_array_by_value(current_events, 'name', _event_to_delete['name'])

    time.sleep(3)


 # ---------- Class Span ---------
# @allure.issue("https://appen.atlassian.net/browse/QED-3188","Integration/Sandbox QED-3188")
@pytest.mark.dependency()
def test_class_spans_required_fields(app, at_job):
    """
    Verify required field validation is shown for name, when adding span
    """

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    app.navigation.click_link('Manage Audio Transcription Ontology')
    app.user.close_guide()

    app.verification.text_present_on_page("Spans")

    app.ontology.add_tag("Span", "", "")
    app.verification.text_present_on_page("Title cannot be left blank.")

    events = app.ontology.get_current_class_spans()
    assert events[-1] == {'name': '', 'description':''}

    app.navigation.click_link('Cancel')


@pytest.mark.dependency(depends=["test_class_spans_required_fields"])
def test_add_class_span(app, at_job):
    """
    Verify user can successfully 'Add span' to ontology class
    """
    app.navigation.refresh_page()
    app.user.close_guide()

    spans = app.ontology.get_current_class_spans()
    assert spans == []

    app.ontology.add_tag("Span", "test", "test")
    app.navigation.click_link('Save')
    time.sleep(5)

    spans = app.ontology.get_current_class_spans()
    assert spans == [{'name':'test', 'description':'test'}]



@pytest.mark.dependency(depends=["test_add_class_span"])
def test_add_multiple_class_spans(app, at_job):
    """
    Verify requestor can configure multiple Spans for a given ontology class
    """
    app.user.close_guide()

    current_spans = app.ontology.get_current_class_spans()

    new_spans = []
    len_new_spans = random.randint(1, 4)
    faker = Faker()
    for i in range(len_new_spans):
        random_name = faker.zipcode()
        app.ontology.add_tag("Span", random_name, random_name)
        new_spans.append({'name':random_name, 'description':random_name})

    app.navigation.click_link('Save')

    time.sleep(4)

    spans = app.ontology.get_current_class_spans()
    expected_spans = current_spans + new_spans

    assert len(spans) == len(expected_spans)
    assert sorted_list_of_dict_by_value(spans, 'name') == sorted_list_of_dict_by_value(expected_spans, 'name')

    time.sleep(5)


@pytest.mark.dependency(depends=["test_add_multiple_class_spans"])
def test_class_spans_duplicates(app, at_job):
    """
    Verify user cannot add spans with duplicate names
    """
    app.user.close_guide()

    app.ontology.add_tag('Span', 'duplicate', 'duplicate')
    app.ontology.add_tag('Span','duplicate', '')

    app.verification.text_present_on_page('Title must be unique.')

    app.navigation.click_link('Cancel')
    time.sleep(3)


@pytest.mark.dependency(depends=["test_add_multiple_class_spans", 'test_class_spans_duplicates'])
def test_edit_class_span(app, at_job):
    """
    Verify requestor can edit Span
    """
    app.user.close_guide()

    current_spans = app.ontology.get_current_class_spans()

    _span_to_update = current_spans[0]

    app.ontology.edit_class_span(_span_to_update['name'], "updated", 'updated', action='Done')

    app.navigation.click_link('Save')
    time.sleep(4)

    app.navigation.refresh_page()
    updated_spans = app.ontology.get_current_class_spans()

    assert updated_spans[0]['name'] == 'updated'
    assert updated_spans[0]['description'] == 'updated'

    time.sleep(3)


@pytest.mark.dependency(depends=['test_edit_class_span'])
def test_delete_class_span(app, at_job):
    """
    Verify requestor can delete a Span
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)

    # app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    app.user.close_guide()

    current_spans = app.ontology.get_current_class_spans()
    _span_to_delete = current_spans[0]

    app.ontology.delete_span_by_name(_span_to_delete['name'])

    app.navigation.click_link('Save')
    time.sleep(3)

    current_spans = app.ontology.get_current_class_spans()
    assert not find_dict_in_array_by_value(current_spans, 'name', _span_to_delete['name'])

    time.sleep(3)


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/AT-4440")
def test_the_same_name_spans_events(app, at_job):
    """
    Verify user cannot add spans with duplicate names
    """
    app.user.close_guide()

    current_spans = app.ontology.get_current_class_spans()
    current_events = app.ontology.get_current_class_events()

    app.ontology.add_tag("Span","the same", "test")
    app.ontology.add_tag("Event", "the same", "test")

    app.navigation.click_link('Save')

    new_spans = app.ontology.get_current_class_spans()
    new_events = app.ontology.get_current_class_events()

    assert len(current_spans) == len(new_spans) - 1
    assert len(current_events) == len(new_events) - 1

    assert find_dict_in_array_by_value(new_spans, 'name', "the same") == {"name":"the same", "description":"test"}
    assert find_dict_in_array_by_value(new_events, 'name', "the same") == {"name":"the same", "description":"test"}

# TODO: https://appen.spiraservice.net/5/TestCase/840.aspx - Verify that requestor cannot move span to an event stack and vice versa
# TODO : reorder spans and events