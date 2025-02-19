"""
https://appen.atlassian.net/browse/QED-1734
"""
import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link


pytestmark = [
    pytest.mark.regression_audio_transcription_contributor,
    pytest.mark.audio_transcription_ui,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-dv.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module")
def create_job_for_validation(app):
    """
    Create Audio Tx job with 2 data rows, upload ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_span_even_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    # launch job
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

    job.wait_until_status('running', 180)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app.user.logout()
    return job_id


# https://appen.spiraservice.net/5/TestCase/2107.aspx
@pytest.mark.dependency()
def test_submit_judgments_without_transcribe(app, create_job_for_validation):
    """
    Verify "Submit Judgement" throws an error when segment bubbles are either left empty, or not marked “Nothing to transcribe"
    """
    job_link = generate_job_link(create_job_for_validation, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    app.audio_transcription.submit_page()
    app.verification.text_present_on_page('All segments have to be transcribed or marked as nothing to transcribe.')


@pytest.mark.dependency(depends=["test_submit_judgments_without_transcribe"])
# https://appen.spiraservice.net/5/TestCase/2108.aspx
def test_save_judgments_then_delete_and_submit(app, create_job_for_validation):
    """
    Verify "Submit Judgement" throws an error when a previously saved transcription is deleted
    """
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.full_screen()
    checked_bubbels = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    for bubble in bubbles:
        name = bubble['name']
        if checked_bubbels.get(name, False):
            checked_bubbels[name] = checked_bubbels[name] + 1
        else:
            checked_bubbels[name] = 1

        index = checked_bubbels[name] - 1
        app.audio_transcription.add_text_to_bubble(name, 'test validation error', index)

    app.audio_transcription.toolbar.save_annotation()

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.activate_iframe_by_index(1)
    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.audio_transcription.full_screen()
    app.audio_transcription.toolbar.save_annotation()
    # delete transcription and click submit, see error message
    app.audio_transcription.full_screen()
    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.audio_transcription.toolbar.save_annotation()
    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    app.verification.text_present_on_page('All segments have to be transcribed or marked as nothing to transcribe.')


@pytest.mark.dependency(depends=["test_save_judgments_then_delete_and_submit"])
# https://appen.spiraservice.net/5/TestCase/2109.aspx
def test_submit_judgments_pass_validation(app, create_job_for_validation):
    """
    Verify "Submit Judgement" validation passes when all transcription bubbles are marked as “Nothing to transcribe” at tool level
    """
    app.audio_transcription.activate_iframe_by_index(1)
    app.audio_transcription.toolbar.click_btn_right_panel("ButtonNothingToTranscribe")
    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_page()
    time.sleep(5)
    app.verification.text_present_on_page('There is no work currently available in this task.')

