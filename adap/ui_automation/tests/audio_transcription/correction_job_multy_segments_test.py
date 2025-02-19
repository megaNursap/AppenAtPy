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
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.utils.selenium_utils import split_text

pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/audio_transcription_rd_for_multi_segments.csv")

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

input_data_for_peer_review_job = read_csv_file(DATA_FILE, 'audio_transcription')


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Audio Tx review job using data stored in S3
    Upload matching ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_correct_task,
                                        job_title="Testing audio transcription job correct task-type", units_per_page=2)
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


def test_contributor_add_feedback_multy_segments(app, tx_job):
    """
    Verify contributor can view the segment transcription, spans,  events data and feedback for segments
    """
    iframe_index = 0
    app.audio_transcription.activate_iframe_by_index(iframe_index)
    if len(app.audio_transcription.get_bubbles_list()) != 4:
        iframe_index = 1
        app.audio_transcription.deactivate_iframe()
        app.audio_transcription.activate_iframe_by_index(iframe_index)
    app.audio_transcription.review_all_segments()

    app.audio_transcription.select_bubble_by_name('Background')
    app.audio_transcription.event.click_event_marker('Background')
    app.audio_transcription.event.add_event('event1')
    app.audio_transcription.span.highlight_text_in_bubble('serialize', 'Background', index=0)
    app.audio_transcription.span.add_span('span1')

    app.audio_transcription.group_labels.choose_labels_by_name('kids')
    app.audio_transcription.group_labels.close_label_panel()
    app.audio_transcription.add_feedback("Miss one label 'kids'")
    time.sleep(5)

    app.audio_transcription.select_bubble_by_name('Noise', default_name='Segment 2')
    assert app.audio_transcription.get_text_from_bubble('Noise', default_name='Segment 2') == '<span_2>humility</span_2> is a virtue'

    assert ['backgroud'] == app.audio_transcription.group_labels.get_selected_labels()
    app.audio_transcription.add_feedback("You should add event1 in the end of virtue")
    app.audio_transcription.event.click_event_marker('Segment 2')
    app.audio_transcription.event.add_event('event1')

    # check if autosave working
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(iframe_index)
    background_span_info = app.audio_transcription.get_span_event('Background', index=0)

    assert app.audio_transcription.group_labels.get_selected_labels() == ['female', 'kids']
    app.verification.text_present_on_page("Miss one label 'kids'")
    assert background_span_info['span_name'][0] == '<span_1>'
    assert background_span_info['span_name'][2] == '<span_2>'
    background_event_info = app.audio_transcription.get_span_event('Background', index=0)
    assert background_event_info['event_name'][0] == '<event_1/>'

    app.audio_transcription.deactivate_iframe()


@pytest.mark.dependency()
def test_contributor_add_label_multy_segments(app, tx_job):
    """
    Verify contributor can view the segment transcription, spans,  events data and feedback for segments
    """
    app.navigation.refresh_page()
    iframe_index = 1
    app.audio_transcription.activate_iframe_by_index(iframe_index)
    if len(app.audio_transcription.get_bubbles_list()) != 3:
        iframe_index = 0
        app.audio_transcription.deactivate_iframe()
        app.audio_transcription.activate_iframe_by_index(iframe_index)
    app.audio_transcription.review_all_segments()

    bubble_names = app.audio_transcription.get_bubbles_name()

    for bubble_index in range(0, len(bubble_names)):
        app.audio_transcription.select_bubble_by_index(bubble_index)
        app.audio_transcription.open_label_panel(bubble_index)

        app.audio_transcription.group_labels.choose_labels_by_name('person', True)
        app.audio_transcription.group_labels.close_label_panel()

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()


@pytest.mark.dependency(depends=["test_contributor_add_label_multy_segments"])
def test_feedback_for_multy_segment_loading_unit_page(app, tx_job):
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
        if v['audio_transcription'] == input_data_for_peer_review_job[0]:
            id_for_data = k

    app.navigation.click_link(id_for_data)
    app.annotation.activate_iframe_by_name("unit_page")
    app.annotation.activate_iframe_by_index(1)
    assert split_text(app.job.data.get_contributor_feedback()) == "Miss one label 'kids'", 'Incorrect feedback display on unit page'
    assert split_text(app.job.data.get_contributor_feedback(index=1)) == "You should add event1 in the end of virtue", 'Incorrect feedback display on unit page'
    assert len(app.audio_transcription.get_bubbles_list()) == 4, "Incorrect size of segments displays on unit page "


