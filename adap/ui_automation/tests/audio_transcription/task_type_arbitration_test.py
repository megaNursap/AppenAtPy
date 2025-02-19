
import time
import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.utils.selenium_utils import split_text

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/arb_data.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_arbitration_task_type,
                                        job_title="Testing audio transcription job ARB task-type", units_per_page=1)

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


def test_review_data_task_type_arb(app, at_job):
    """
    Verify that task-type='arbitration' review-data=[{{original_judgment}}, {{corrected_judgment}}, {{acknowledge_judgment}}]
    render data for original and corrected judgment
    """

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Segment 1')

    # verify transcription original and after review
    actual_original_text = app.audio_transcription.get_text_from_bubble('Segment 1')
    actual_reviewed_text = app.audio_transcription.get_reviewed_info()
    assert actual_reviewed_text == 'Short and sweet; I like it! We <span_2>need</span_2> more answers', 'The reviewed text Not the same as expected'
    assert actual_original_text == 'Short and sweet; I like it! We <span_2>need</span_2> more answers<event_2/>', 'The original text Not the same as expected'

    #verify that review judgment reedonly
    actual_reviewed_comment = app.audio_transcription.get_reviewed_comment()
    assert actual_reviewed_comment == 'Miss one require label \'Person\', and event2 should not be present'

    # verify information about reply feedback
    actual_feedback = app.job.data.get_acknowledge_result()
    assert actual_feedback['dispute_result'], 'The feedback should be DISPUTE'
    assert actual_feedback['comment'] == 'The label \'Person\' should be present', 'The comment NOT match as the contributor left'

    # verify original and reviewed labels
    actual_original_labels = app.audio_transcription.group_labels.get_selected_labels()
    actual_reviewed_labels = app.audio_transcription.group_labels.get_reviewed_label()
    assert actual_reviewed_labels != actual_original_labels
    assert actual_reviewed_labels == ['female', 'Person']
    assert actual_original_labels == ['female']


def test_review_data_without_one_of_judgments_data(app, at_job):
    """
    Verify that if the review-data=[{{}}, {{}}] got just not all data parameters, tools return
    'Nothing to Transcribe' in reviewed box, or in two box if missed original judgment data
    """

    cml_without_acknowledge_data_judgment = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription_arbitration" task-type="arbitration" review-data="[{{audio_transcription_original}}, {{audio_transcription_correction}}]" />'
    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test without acknowledge judgment",
            'cml': cml_without_acknowledge_data_judgment,
            'project_number': 'PN000112'
        }
    }
    job = Builder(API_KEY)
    job.job_id = at_job
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Segment 1')

    # verify information about reply feedback Not provided
    actual_feedback = app.audio_transcription.get_acknowledge_feedback()
    assert app.audio_transcription.acknowledge_feedback_check(), "The acknowledge feedback Not check"
    assert actual_feedback == 'Comment was not provided.'

    app.audio_transcription.deactivate_iframe()

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test task-type ACK",
            'cml': data.audio_transcription_arbitration_task_type,
            'project_number': 'PN000112'
        }
    }
    job = Builder(API_KEY)
    job.job_id = at_job
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)


def test_all_segment_require_arbitration_action(app, at_job):
    """
    Verify if contributor dispute feedback and not provide comment,
    the error raise
    """

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)

    app.audio_transcription.select_bubble_by_index(1)
    app.audio_transcription.arbitration_of_feedback()

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_test_validators()
    time.sleep(2)
    assert app.audio_annotation.get_task_error_msg_by_index() == 'Error: All segments need to be marked with an arbitration decision'