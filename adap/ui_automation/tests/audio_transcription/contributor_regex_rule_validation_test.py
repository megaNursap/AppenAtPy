"""
https://appen.atlassian.net/browse/QED-1752
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import go_to_page
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]


USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
RULE_DESCRIPTION = 'Do not enter two punctuation mark'


@pytest.fixture(scope="module")
def at_job(app):
    """
    Create Audio Tx job with 2 data rows
    Upload ontology, and add regex validation rule
    Launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    # add regex rule
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, job_id)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION,
                                                                  enable_fix_suggestion=True, empty_string=False, replace_string='.')
    app.navigation.click_btn('Save')
    time.sleep(3)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION)

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

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app.user.logout()
    return job_id



@pytest.mark.dependency()
def test_contributor_trigger_regex_rule_embedded_mode(app, at_job):
    """
    Verify that regex error message is displayed when contributor enters a regex, that was defined in the rule
    Verify regex rule popup has ‘Ignore’ and ‘Correct’ buttons along with rule description
    Verify that regex error message disappears when user deletes the regex that causes the error
    If the same regex error is typed twice in the transcription bubble, verify that 2 regex error popups appear
    """
    job_link = generate_job_link(at_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    app.audio_transcription.activate_iframe_by_index(0)

    # https://appen.spiraservice.net/5/TestCase/2810.aspx
    app.audio_transcription.add_text_to_bubble('Person', 'test,!')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    assert app.audio_transcription.data_validation.get_regex_error_description() == 'Do not enter two punctuation mark'

    # https://appen.spiraservice.net/5/TestCase/2807.aspx
    assert app.audio_transcription.btn_is_displayed('CORRECT')
    assert app.audio_transcription.btn_is_displayed('IGNORE')

    # https://appen.spiraservice.net/5/TestCase/2809.aspx
    # assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 0
    # https://appen.spiraservice.net/5/TestCase/2808.aspx
    app.audio_transcription.edit_text_from_bubble('Person', 'test.,test.!')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 2


@pytest.mark.dependency(depends=["test_contributor_trigger_regex_rule_embedded_mode"])
def test_contributor_trigger_regex_rule_fullscreen_mode(app, at_job):
    """
    Verify validation error popup shows in full screen mode as well
    """
    app.audio_transcription.full_screen()
    app.audio_transcription.add_text_to_bubble('Noise', 'test!!')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1