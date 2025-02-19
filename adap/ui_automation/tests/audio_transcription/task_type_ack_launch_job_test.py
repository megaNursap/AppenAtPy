"""
https://appen.atlassian.net/browse/QED-1735
This test covers:
1. Create peer review job for audio transcription using right CML
2. Verify contributor can see transcription, span and event for a peer-review job, and also submit judgements
3. Verify contributor can add/edit/delete transcription, span and event
"""
import time

import pytest as pytest
from allure_commons.types import AttachmentType

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.utils.selenium_utils import split_text

pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/ack_data.csv")

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Audio Tx review job using data stored in S3
    Upload matching ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_acknowledge_task_type,
                                        job_title="Testing audio transcription job correct task-type", units_per_page=1)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology-correct-task.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.open_action("Settings")
    app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
    app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    app.user.logout()
    # job_id = 2115617

    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.user.close_guide()

    return job_id


def test_contributor_see_original_corrected_judgment_info_ack(app, tx_job):
    """
    Verify the contributor see information about original and corrected judgment
    """


    app.audio_transcription.activate_iframe_by_index(0)
    allure.attach(app.driver.get_screenshot_as_png(), name="Some name", attachment_type=AttachmentType.PNG)
    app.audio_transcription.select_bubble_by_name('Background', default_name='Segment 1')

    # verify transcription original and after review
    actual_original_text = app.audio_transcription.get_text_from_bubble('Background', default_name='Segment 1')
    actual_reviewed_text = app.audio_transcription.get_reviewed_info()
    assert actual_reviewed_text != actual_original_text, 'The reviewed text the same as original'

    # verify span original and after review
    actual_original_span = app.audio_transcription.span.get_text_with_spans('Background', default_name='Segment 1')
    assert actual_original_span[0]['span_name'] == '<span_2>'
    allure.attach(app.driver.get_screenshot_as_png(), name="Review judgment", attachment_type=AttachmentType.PNG)
    actual_reviewed_span = app.audio_transcription.span.get_review_text_span()
    assert actual_reviewed_span[0]['span_name'] == '<span_2>'

    # verify original and reviewed labels
    actual_original_labels = app.audio_transcription.group_labels.get_selected_labels()
    actual_reviewed_labels = app.audio_transcription.group_labels.get_reviewed_label()
    assert actual_reviewed_labels != actual_original_labels
    assert actual_reviewed_labels == ['female', 'male']
    assert actual_original_labels == ['female']

    # verify comment left in corrected Job
    actual_reviewed_comment = app.audio_transcription.get_reviewed_comment()
    assert actual_reviewed_comment == 'Miss one require label \'male\', and event2 should not be present'

    app.audio_transcription.deactivate_iframe()


def test_error_not_respond_all_feedback(app, tx_job):
    """
    Verify if contributor not respond for all feedback, he got error and cannot submit judgment
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Person')
    app.audio_transcription.deactivate_iframe()

    # verify transcription original and after review
    app.audio_transcription.submit_page()
    time.sleep(2)
    assert app.audio_annotation.get_task_error_msg_by_index() == 'Error: you must respond to all feedback before continuing'


@pytest.mark.dependency()
def test_contributor_respond_all_feedback(app, tx_job):
    """
    Verify contributor respond for all feedback, some off them dispute and successful submit the Job
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)

    list_of_segments = app.audio_transcription.get_bubbles_list()

    for segment_index in range(0, len(list_of_segments)):
        time.sleep(2)
        app.audio_transcription.scroll_and_select_bubble(segment_index)
        assert app.audio_transcription.acknowledge_feedback_check()
        if segment_index == 0:
            app.audio_transcription.dispute_the_feedback('Segment 1')
            app.audio_transcription.add_feedback("There should be present")

    app.audio_transcription.scroll_and_select_bubble()
    assert app.verification.text_present_on_page("There should be present")

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()


@pytest.mark.dependency(depends=["test_contributor_respond_all_feedback"])
def test_acknowledge_result_loading_unit_page(app, tx_job):
    """
    Verify requestor can see feedback on unit page
    """
    app.user.customer.open_home_page()
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job = Builder(API_KEY)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.open_tab("DATA")

    job_row = job.get_rows_in_job(tx_job)
    id_for_data = None
    for k, v in job_row.json_response.items():
        id_for_data = k

    app.navigation.click_link(id_for_data)
    app.annotation.activate_iframe_by_name("unit_page")
    app.annotation.activate_iframe_by_index(1)
    app.audio_transcription.select_bubble_by_index()
    result = app.job.data.get_acknowledge_result()
    assert not result['acknowledge_result'], 'The acknowledge feedback should be unchecked'
    assert result['dispute_result'], 'The dispute feedback should be checked'
    assert result['comment'] == 'There should be present', 'The comment NOT match as the contributor left'



