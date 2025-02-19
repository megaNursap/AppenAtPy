"""
https://appen.atlassian.net/browse/QED-1735
This test covers:
1. Create peer review job for audio transcription using right CML
2. Verify contributor can see transcription, span and event for a peer-review job, and also submit judgements
3. Verify contributor can add/edit/delete transcription, span and event
"""
import time

import pytest as pytest

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription__contributor, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/full_report.csv")

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Audio Tx review job using data stored in S3 (instead of sourcing from Audio Annotation output)
    Upload matching ontology and launch job
    """
    target_mode = 'AT'
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
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
    return job_id


@pytest.mark.dependency()
# @pytest.mark.skipif(pytest.env not in ["sandbox","integration"], reason="configured predefined job for sandbox")
def test_contributor_view_transcription_span_event(app, tx_job):
    """
    Verify contributor can view the segment transcription, spans, & events data
    """
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.review_all_segments()

    assert app.audio_transcription.get_text_from_bubble('Person') == 'This is person <person_span>noise</person_span>'
    assert app.audio_transcription.get_text_from_bubble('Noise') == 'This is background <noise_span>noise</noise_span><event_1/> '

    person_span_info = app.audio_transcription.get_span_event('Person')
    assert person_span_info['span_name'][0] == '<person_span>'
    # assert person_span_info[0]['text'] == 'noise'
    app.audio_transcription.group_labels.choose_labels_by_name('Noise', True)
    app.audio_transcription.group_labels.close_label_panel()

    noise_span_info = app.audio_transcription.get_span_event('Noise', index=0)
    assert noise_span_info['span_name'][0] == '<noise_span>'

    noise_event_info = app.audio_transcription.get_span_event('Noise', index=0)
    assert noise_event_info['event_name'][0] == '<event_1/>'
    app.audio_transcription.open_label_panel(1)
    app.audio_transcription.group_labels.choose_labels_by_name('Person', True)
    app.audio_transcription.group_labels.close_label_panel()


    app.audio_transcription.deactivate_iframe()


# TODO: Modify test as per changes being made in AT-3405
# @pytest.mark.skip(reason="New feature - Contributor cannot submit judgments until segment is reviewed")
@pytest.mark.dependency(depends=["test_contributor_view_transcription_span_event"])
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_contributor_add_transcription_span_event(app, tx_job):
    """
    Verify contributor can edit transcription, add spans/events in review job
    """

    app.audio_transcription.activate_iframe_by_index(1)
    # edit existing transcription
    app.audio_transcription.review_all_segments()
    app.audio_transcription.edit_text_from_bubble('Person', 'Updated person text')
    # add labels
    app.audio_transcription.group_labels.choose_labels_by_name('Music', True)
    app.audio_transcription.group_labels.close_label_panel()
    # delete transcription and add it again
    app.audio_transcription.delete_text_from_bubble('Noise')
    app.audio_transcription.add_text_to_bubble('Noise', 'test span')
    # add span
    app.audio_transcription.span.highlight_text_in_bubble(span_text='span', bubble_name='Noise', index=0)
    app.audio_transcription.span.add_span('noise span')
    span_info = app.audio_transcription.get_span_event('Noise', index=0)
    assert span_info['span_name'][0] == '<noise_span>'

    # add event
    app.audio_transcription.event.move_cursor_to_text_in_bubble('span', 'Noise', index=0)
    app.audio_transcription.event.click_event_marker('Noise', index=0)
    app.audio_transcription.event.add_event('event1')
    _events = app.audio_transcription.get_span_event('Noise', index=0)
    assert _events['event_name'] == ['<event_1>']
    # add labels
    app.audio_transcription.open_label_panel(1)
    app.audio_transcription.group_labels.choose_labels_by_name('Pet', True)
    app.audio_transcription.group_labels.close_label_panel()
    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')
