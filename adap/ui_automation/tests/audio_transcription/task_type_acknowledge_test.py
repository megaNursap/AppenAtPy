
import time
import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/ack_data.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_acknowledge_task_type,
                                        job_title="Testing audio transcription job ACK task-type", units_per_page=1)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology-correct-task.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()
    time.sleep(10)

    return job_id


def test_review_data_task_type_ack(app, at_job):
    """
    Verify that task-type='acknowledge' review-data=[{{original_judgment}}, {{corrected_judgment}}]
    render data for original and corrected judgment
    https://appen.spiraservice.net/5/TestCase/4940.aspx
    """

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Person')

    # verify transcription original and after review
    actual_original_text = app.audio_transcription.get_text_from_bubble('Person')
    actual_reviewed_text = app.audio_transcription.get_reviewed_info()
    assert actual_reviewed_text == 'Short and sweet; I like it! We <span_2>need</span_2> more answers', 'The reviewed text Not the same as expected'
    assert actual_original_text == 'Short and sweet; I like it! We <span_2>need</span_2> more answers <event_2/>', 'The original text Not the same as expected'

    # verify span original and after review
    actual_original_span = app.audio_transcription.span.get_text_with_spans('Person', index=0)
    assert actual_original_span[0]['span_name'] == '<span_2>'
    assert actual_original_span[0]['text'] == 'need'

    actual_reviewed_span = app.audio_transcription.span.get_review_text_span()
    assert actual_reviewed_span[0]['span_name'] == '<span_2>'
    assert actual_reviewed_span[0]['text'] == 'need'

    # verify event original and after review
    actual_original_events = app.audio_transcription.event.get_events_from_bubble('Person')
    assert actual_original_events == ['<event_2/>']

    actual_reviewed_event = app.audio_transcription.event.get_events_from_reviewed_bubble()
    assert actual_reviewed_event == []

    # verify original and reviewed labels
    actual_original_labels = app.audio_transcription.group_labels.get_selected_labels()
    actual_reviewed_labels = app.audio_transcription.group_labels.get_reviewed_label()
    assert actual_reviewed_labels != actual_original_labels
    assert actual_reviewed_labels == ['female', 'male']
    assert actual_original_labels == ['female']

    # verify comment left in corrected Job
    actual_reviewed_comment = app.audio_transcription.get_reviewed_comment()
    assert actual_reviewed_comment == 'Miss one require label \'male\', and event2 should not be present'


def test_review_data_without_one_judgment_data(app, at_job):
    """
    Verify that if the review-data=[{{}}] got just one data parameters, tools return
    'Nothing to Transcribe' in reviewed box, or in two box if missed original judgment data
    https://appen.spiraservice.net/5/TestCase/4887.aspx
    """

    cml_without_correction_data_judgment = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription_acknowledgment" task-type="acknowledge" review-data="[{{audio_transcription_original}}]" />'
    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test without correction judgment",
            'cml': cml_without_correction_data_judgment,
            'project_number': 'PN000112'
        }
    }
    job = Builder(API_KEY)
    job.job_id = at_job
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Person')
    actual_result = app.audio_transcription.get_reviewed_info()
    assert actual_result == 'Nothing to Transcribe'
    app.audio_transcription.deactivate_iframe()

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test task-type ACK",
            'cml': data.audio_transcription_acknowledge_task_type,
            'project_number': 'PN000112'
        }
    }
    job = Builder(API_KEY)
    job.job_id = at_job
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)


def test_dispute_feedback_comment_require(app, at_job):
    """
    Verify if contributor dispute feedback and not provide comment,
     he got error and cannot submit judgment
    """

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    list_of_segments = app.audio_transcription.get_bubbles_list()

    for segment_index in range(0, len(list_of_segments)-2):
        app.audio_transcription.select_bubble_by_index(segment_index)
        if segment_index == 0:
            app.audio_transcription.dispute_the_feedback('Segment 1')

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_test_validators()
    time.sleep(2)
    assert app.audio_annotation.get_task_error_msg_by_index() == 'Error: you must respond to all feedback before continuing'