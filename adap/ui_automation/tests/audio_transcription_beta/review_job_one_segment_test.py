import time

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/peer_review_one_segment.csv")

@pytest.fixture(scope="module")
def at_job_one_segment(tmpdir_factory, app):
    CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
    CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_one_segment,
                                        job_title="Testing audio transcription beta for one segment job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-label-ontology.json')
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

    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)
    return job_id


def test_contributor_review_transcription_span_event_one_segment(app, at_job_one_segment):
    """
    Verify contributor can view the segment transcription, spans, & events data
    """

    app.navigation.refresh_page()
    iframe_index = 0
    time.sleep(3)
    app.audio_transcription_beta.activate_iframe_by_index(iframe_index)
    if app.audio_transcription_beta.nothing_to_transcribe():
        iframe_index = 1
        app.audio_transcription.deactivate_iframe()
        app.audio_transcription.activate_iframe_by_index(iframe_index)

    assert app.audio_transcription_beta.grab_text_from_text_area() == 'Test [6.389] peer <span_2>review</span_2> Job <event_3/>'

    span_info = app.audio_transcription_beta.get_tags_info(tag='span')
    assert span_info['span'] == ['<span_2>', '</span_2>']

    event_info = app.audio_transcription_beta.get_tags_info(tag='event')
    assert event_info['event'][0] == '<event_3/>'

    timestamp_info = app.audio_transcription_beta.get_tags_info(tag='timestamp')
    assert timestamp_info['timestamp'][0] == '[6.389]'

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['person']

    assert app.audio_transcription_beta.verify_checked_label('person')

    app.audio_transcription_beta.click_event_marker("Test")
    app.audio_transcription.event.add_event("event2")

    app.audio_transcription.group_labels.choose_labels_by_name('pets', True)
    app.audio_transcription_beta.click_on_action_button("PlayPauseButton")
    time.sleep(13)

    app.audio_transcription.deactivate_iframe()


def test_contributor_review_nontranscription_segment(app, at_job_one_segment):
    """
    Verify contributor can review the segment that marked non-transcribe
    """
    app.navigation.refresh_page()
    iframe_index = 0
    app.audio_transcription_beta.activate_iframe_by_index(iframe_index)
    if not app.audio_transcription_beta.nothing_to_transcribe():
        iframe_index = 1
        app.audio_transcription.deactivate_iframe()
        app.audio_transcription.activate_iframe_by_index(iframe_index)

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['female','male','quite','mosquitoes']

    assert app.audio_transcription_beta.verify_checked_label('female', button_type='checkbox')
    assert app.audio_transcription_beta.verify_checked_label('male', button_type='checkbox')

    app.audio_transcription.group_labels.choose_labels_by_name('birds')

    app.audio_transcription_beta.click_on_listen_to_block(time_value=20)
    app.audio_transcription.deactivate_iframe()

    app.audio_transcription_beta.submit_page()