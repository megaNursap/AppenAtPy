"""
https://appen.atlassian.net/browse/QED-1754
"""
import time

from allure_commons.types import AttachmentType

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
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-dv.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
RULE_DESCRIPTION = 'Do not enter two punctuation mark'


@pytest.fixture(scope="module")
def at_job(app):
    """
    Create Audio Transcription job with 2 data rows
    Upload ontology, add span & event to 2 ontology classes
    Add regex validation rule
    Launch job
    """
    target_mode = 'AT'
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
def test_contributor_correct_regex_error(app, at_job):
    """
    Verify contributor can see regex validation error popup with Ignore and Correct buttons
    Verify contributor can correct a regex validation error, and the text is corrected accordingly and the error popup is removed
    """
    job_link = generate_job_link(at_job, API_KEY, pytest.env)
    allure.attach(app.driver.get_screenshot_as_png(), name='Open Page', attachment_type=AttachmentType.PNG)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    app.audio_transcription.activate_iframe_by_index(0)

    # add text with two regex errors then correct them one by one
    assert not app.audio_transcription.review_button_is_displayed('Person')
    app.audio_transcription.add_text_to_bubble('Person', 'test correct?. regex error.!')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 2
    assert app.audio_transcription.data_validation.get_regex_error_description() == 'Do not enter two punctuation mark'
    assert app.audio_transcription.btn_is_displayed('CORRECT')
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.navigation.click_btn('CORRECT')
    assert app.audio_transcription.get_text_from_bubble('Person') == 'test correct. regex error.!'
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    app.navigation.click_btn('CORRECT')
    time.sleep(3)
    assert app.audio_transcription.get_text_from_bubble('Person') == 'test correct. regex error.'
    app.audio_transcription.group_labels.choose_labels_by_name('Noise', True)
    app.audio_transcription.group_labels.close_label_panel()


@allure.issue("https://appen.atlassian.net/browse/ADAP-2693", "Integration, Bug ADAP-2693")
@pytest.mark.dependency(depends=["test_contributor_correct_regex_error"])
def test_contributor_check_error_icon_before_ignore_regex(app, at_job):
    """
    Verify validation error icon is shown in segment bubble
    add text with regex error for second segment, add span and event at the same time,
    before ignore it, check the error icon for first segment, it should be there
    """
    # add text with regex error for first segment
    app.audio_transcription.select_bubble_by_name('Noise')
    app.audio_transcription.add_text_to_bubble('Noise', 'test ignore., error')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    assert app.audio_transcription.data_validation.get_regex_error_description() == 'Do not enter two punctuation mark'
    assert app.audio_transcription.btn_is_displayed('CORRECT')
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.audio_transcription.open_label_panel(1)
    app.audio_transcription.group_labels.choose_labels_by_name('Noise', True)
    app.audio_transcription.group_labels.close_label_panel()

    app.audio_transcription.edit_text_from_bubble('Person', 'test span and event., and ignore regex rule')
    app.audio_transcription.span.highlight_text_in_bubble(span_text='span', bubble_name='Person', index=0)
    app.audio_transcription.span.add_span('person span')
    span_info = app.audio_transcription.get_span_event('Person', index=0)
    assert span_info['span_name'][0] == '<person_span>'
    app.audio_transcription.event.move_cursor_to_the_end_of_text_in_bubble('Person', index=0)
    app.audio_transcription.event.click_event_marker('Person', index=0)
    app.audio_transcription.event.add_event('event1')
    _events = app.audio_transcription.get_span_event('Person', index=0)
    assert _events['event_name'] == ['<event_1/>']
    assert app.audio_transcription.data_validation.count_number_of_error_icon() == 2


@pytest.mark.dependency(depends=["test_contributor_check_error_icon_before_ignore_regex"])
def test_contributor_ignore_regex_error(app, at_job):
    """
    Verify that error icon is not displayed when regex/spell_check error is ignored or corrected
    Verify that ignoring a validation error removes error icon from previous segment bubbles that had the same error
    """
    app.navigation.click_btn('IGNORE')
    time.sleep(3)
    assert app.audio_transcription.data_validation.count_number_of_error_icon() == 0


@pytest.mark.dependency(depends=["test_contributor_ignore_regex_error"])
def test_no_impact_to_span_and_event_regex(app, at_job):
    """
    Verify applying ignore/correct to validation errors does not effect spans/events in it
    """
    span_info = app.audio_transcription.span.get_text_with_spans('Person', index=0)
    assert span_info[0]['span_name'] == '<person_span>'
    assert span_info[0]['text'] == 'span'
    time.sleep(2)
    _events = app.audio_transcription.get_span_event('Person', index=0)
    assert _events['event_name'] == ['<event_1/>']


@pytest.mark.dependency(depends=["test_no_impact_to_span_and_event_regex"])
def test_once_ignore_no_longer_trigger_validation(app, at_job):
    """
    Once a validation error is ignored, it is no longer triggered for the entire audio file
    """
    app.audio_transcription.select_bubble_by_name('Pet')
    app.audio_transcription.add_text_to_bubble('Pet', 'test ignore., error')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 0
    app.audio_transcription.select_bubble_by_name('Noise', 1)
    app.audio_transcription.add_text_to_bubble('Noise', 'test ignore., error', 1)
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 0
    app.audio_transcription.deactivate_iframe()


@pytest.mark.dependency(depends=["test_once_ignore_no_longer_trigger_validation"])
def test_once_ignore_no_impact_to_other_file_regex(app, at_job):
    """
    Check other audio file, ignore will not impact it, regex error will still show
    """
    app.audio_transcription.activate_iframe_by_index(1)
    app.audio_transcription.add_text_to_bubble('Pet', 'test ignore., error')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    assert app.audio_transcription.data_validation.get_regex_error_description() == 'Do not enter two punctuation mark'
    assert app.audio_transcription.btn_is_displayed('CORRECT')
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.audio_transcription.deactivate_iframe()


