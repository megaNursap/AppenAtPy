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
DATA_FILE = get_data_file("/audio_transcription/peer_review_multi_segments.csv")

@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
    CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_multi_segment,
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


def test_contributor_review_first_segment(app, at_job):
    """
    Verify contributor can review the multi segments transcription, spans, & events data
    """

    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    text_from_fist_segment = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_from_fist_segment == "This <event_2/> segments <span_3>have</span_3> transcription [1.292]"

    span_info = app.audio_transcription_beta.get_tags_info(tag='span')
    assert span_info['span'] == ['<span_3>', '</span_3>']

    event_info = app.audio_transcription_beta.get_tags_info(tag='event')
    assert event_info['event'][0] == '<event_2/>'

    timestamp_info = app.audio_transcription_beta.get_tags_info(tag='timestamp')
    assert timestamp_info['timestamp'][0] == '[1.292]'

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['noise']

    assert app.audio_transcription_beta.verify_checked_label('noise')

    app.audio_transcription_beta.click_event_marker("This")
    app.audio_transcription.event.add_event("event1")

    app.audio_transcription.group_labels.choose_labels_by_name('pets', True)
    app.audio_transcription_beta.click_on_listen_to_block(time_value=5)

    app.audio_transcription.deactivate_iframe()


def test_contributor_review_second_segment(app, at_job):
    """
    Verify contributor can review the second segment of the list that marked non-transcribe
    """
    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(1)

    assert app.audio_transcription_beta.nothing_to_transcribe()

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['female', 'male', 'quite']

    app.audio_transcription_beta.click_on_listen_to_block(time_value=5)

    app.audio_transcription.deactivate_iframe()


def test_contributor_review_third_segment(app, at_job):
    """
      Verify contributor can review the multi segments transcription, spans, & events data
      """

    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(2)
    text_from_fist_segment = app.audio_transcription_beta.grab_text_from_text_area()
    assert text_from_fist_segment == "The third [0.993] segments <event_2/> transcribe <span_3>too</span_3>"

    span_info = app.audio_transcription_beta.get_tags_info(tag='span')
    assert span_info['span'] == ['<span_3>', '</span_3>']

    event_info = app.audio_transcription_beta.get_tags_info(tag='event')
    assert event_info['event'][0] == '<event_2/>'

    timestamp_info = app.audio_transcription_beta.get_tags_info(tag='timestamp')
    assert timestamp_info['timestamp'][0] == '[0.993]'

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['pets']

    assert app.audio_transcription_beta.verify_checked_label('pets')

    app.audio_transcription_beta.highlight_text_in_segments("third")
    app.audio_transcription.span.add_span("span1")

    app.audio_transcription_beta.click_on_listen_to_block(time_value=4)

    app.audio_transcription.deactivate_iframe()


def test_contributor_review_fourth_segment(app, at_job):
    """
    Verify contributor can review the fourth segment of the list that marked non-transcribe
    """
    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment(3)

    assert app.audio_transcription_beta.nothing_to_transcribe()

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['birds', 'butterflies', 'quite', ]

    assert app.audio_transcription_beta.verify_checked_label('quite', 'checkbox')

    app.audio_transcription.group_labels.choose_labels_by_name('kids')

    app.audio_transcription_beta.click_on_listen_to_block(time_value=5)

    app.audio_transcription.deactivate_iframe()
