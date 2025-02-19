
import time

import requests
from allure_commons.types import AttachmentType

from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job


pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/arb_data.csv")

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')



@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Audio Tx review job using data stored in S3
    Upload matching ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_arbitration_task_type,
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


    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.user.close_guide()

    return job_id


def test_contributor_see_original_corrected_judgment_info(app, tx_job):
    """
    Verify the contributor see information about original, corrected, acknowledge judgment
    """
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Person')

    # verify transcription original and after review
    actual_original_text = app.audio_transcription.get_text_from_bubble('Person')
    actual_reviewed_text = app.audio_transcription.get_reviewed_info()
    assert actual_reviewed_text.rstrip() != actual_original_text.rstrip(), 'The reviewed text the same as original'

    # verify span original and after review
    allure.attach(app.driver.get_screenshot_as_png(), name="Review judgment", attachment_type=AttachmentType.PNG)
    original_span = app.audio_transcription.span.get_text_with_spans('Person')
    reviewed_span = app.audio_transcription.span.get_review_text_span()
    assert original_span[0]['span_name'] == reviewed_span[0]['span_name']
    assert original_span[0]['text'] == reviewed_span[0]['text']

    assert reviewed_span[0]['span_name'] == '<span_2>'
    assert reviewed_span[0]['text'] == 'need'

    # verify original and reviewed labels
    original_labels = app.audio_transcription.group_labels.get_selected_labels()
    reviewed_labels = app.audio_transcription.group_labels.get_reviewed_label()

    assert reviewed_labels == ['female', 'male']
    assert original_labels == ['female']
    assert reviewed_labels != original_labels

    # verify original and review event
    original_events = app.audio_transcription.event.get_events_from_bubble('Person')
    reviewed_event = app.audio_transcription.event.get_events_from_reviewed_bubble()
    assert original_events != reviewed_event
    assert original_events == ['<event_2/>']
    assert reviewed_event == []

    # verify comment left in corrected Job
    reviewed_comment = app.audio_transcription.get_reviewed_comment()
    assert reviewed_comment == "Miss one require label 'male', and event2 should not be present"

    # verify acknowledge feedback
    ack_feedback = app.job.data.get_acknowledge_result()
    assert not ack_feedback['acknowledge_result'], 'The acknowledge feedback should be checked'
    assert ack_feedback['dispute_result'], 'The dispute feedback should be unchecked'
    assert ack_feedback['comment'] == "The changes should be revert to original", 'The comment NOT match as the contributor left'

    app.audio_transcription.deactivate_iframe()







