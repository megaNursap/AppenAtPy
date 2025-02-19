import time

import allure

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]


USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-dv.csv")


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


def test_error_from_contributor_side_and_submit_judgments(app, login):
    """
    Verify contributor can submit job even when data rows are not available.
    """
    incorrect_data_file = get_data_file("/audio_transcription/incorrect_audio_url.csv")
    job_id = create_annotation_tool_job(API_KEY, incorrect_data_file,
                                        data.audio_transcription_cml,
                                        job_title="Testing audio data not found error", units_per_page=2)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')

    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-new-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(3)
    app.audio_transcription.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable')
    app.driver.close()
    app.navigation.switch_to_window(job_window)

    app.job.open_action("Settings")
    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
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
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    app.audio_transcription.activate_iframe_by_index(0)
    # there are total 2 iframes, we do not know which iframe will show Audio data not found
    if app.verification.count_text_present_on_page('Question Unavailable') == 1:
        app.audio_transcription.deactivate_iframe()
        app.audio_transcription.activate_iframe_by_index(1)
        app.audio_transcription.click_nothing_to_transcribe_for_task()
        app.audio_transcription.deactivate_iframe()
    else:
        app.audio_transcription.click_nothing_to_transcribe_for_task()
        app.audio_transcription.deactivate_iframe()
        app.audio_transcription.activate_iframe_by_index(1)
        app.verification.text_present_on_page('Question Unavailable')
        app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(2)
    app.verification.text_present_on_page('There is no work currently available in this task.')