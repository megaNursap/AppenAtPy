"""
https://appen.atlassian.net/browse/QED-1753
"""
import time

import allure
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


@pytest.fixture(scope="module")
def at_job(app):
    """
    Create Audio Tx job with 2 data rows
    Upload ontology, add span/event
    Add spell check data validation rule
    Launch job
    """
    target_mode = 'AT'
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

    # add spell check rule
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, job_id)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.enter_language_check_rule_info(language='English', locale='American')
    app.navigation.click_btn('Save')
    time.sleep(3)

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
def test_contributor_correct_spell_check_error(app, at_job):
    """
    Where there are duplicate spell check errors, verify that user can correct them individually
    Verify clicking on the available fix suggestions replaces the misspelled text with the selected string
    """
    job_link = generate_job_link(at_job, API_KEY, pytest.env)
    allure.attach(app.driver.get_screenshot_as_png(), name="Open page", attachment_type=AttachmentType.PNG)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    app.audio_transcription.activate_iframe_by_index(0)

    # add text with two spell check errors then correct them one by one
    app.audio_transcription.add_text_to_bubble('Person', 'test eror and test eror')
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 2
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.audio_transcription.data_validation.click_on_correct_word('error')
    assert app.audio_transcription.get_text_from_bubble('Person') == 'test error and test eror'
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 1
    app.audio_transcription.data_validation.click_on_correct_word('error')
    assert app.audio_transcription.get_text_from_bubble('Person') == 'test error and test error'
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 0


@pytest.mark.dependency(depends=["test_contributor_correct_spell_check_error"])
def test_contributor_check_error_icon_before_ignore(app, at_job):
    """
    Verify validation error icon is shown for spell check rule
    """
    app.audio_transcription.add_text_to_bubble('Noise', 'test speling')
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 1
    assert app.audio_transcription.btn_is_displayed('IGNORE')

    app.audio_transcription.edit_text_from_bubble('Person', 'test span and event, speling check')
    app.audio_transcription.span.highlight_text_in_bubble(span_text='span', bubble_name='Person', index=0)
    app.audio_transcription.span.add_span('person span')
    span_info = app.audio_transcription.span.get_text_with_spans('Person', index=0)
    assert span_info[0]['span_name'] == '<person_span>'
    assert span_info[0]['text'] == 'span'
    app.audio_transcription.event.move_cursor_to_the_end_of_text_in_bubble('Person', index=0)
    app.audio_transcription.event.click_event_marker('Person', index=0)
    app.audio_transcription.event.add_event('event1')
    _events = app.audio_transcription.event.get_events_from_bubble('Person', index=0)
    assert _events == ['<event_1/>']
    assert app.audio_transcription.data_validation.count_number_of_error_icon() == 2


@pytest.mark.dependency(depends=["test_contributor_check_error_icon_before_ignore"])
def test_contributor_ignore_spell_check_error(app, at_job):
    """
    Verify validation error icon is no longer shown when spell check error is ignored
    """
    app.audio_transcription.data_validation.ignore_spell_check_error()
    time.sleep(2)
    assert app.audio_transcription.data_validation.count_number_of_error_icon() == 0


@pytest.mark.dependency(depends=["test_contributor_ignore_spell_check_error"])
def test_no_impact_to_span_and_event(app, at_job):
    """
    Verify ignoring spell check error does not impact span/event in the transcription text
    """
    span_info = app.audio_transcription.span.get_text_with_spans('Person', index=0)
    assert span_info[0]['span_name'] == '<person_span>'
    assert span_info[0]['text'] == 'span'
    time.sleep(2)
    _events = app.audio_transcription.event.get_events_from_bubble('Person', index=0)
    assert _events == ['<event_1/>']


@pytest.mark.dependency(depends=["test_no_impact_to_span_and_event"])
def test_once_ignore_no_longer_trigger_validation_for_same_error(app, at_job):
    """
    Verify clicking on 'Ignore' for spell check error ignores the spelling for the entire audio file
    """
    app.audio_transcription.add_text_to_bubble('Noise', 'speling check error', index=1)
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 0


@pytest.mark.dependency(depends=["test_once_ignore_no_longer_trigger_validation_for_same_error"])
def test_once_ignore_still_trigger_validation_for_different_word(app, at_job):
    """
    Verify that ignoring one spell check error, does not ignore all other errors in the data row
    """
    app.audio_transcription.add_text_to_bubble('Pet', 'test eror')
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 1
    app.audio_transcription.deactivate_iframe()


@pytest.mark.dependency(depends=["test_once_ignore_still_trigger_validation_for_different_word"])
def test_once_ignore_no_impact_to_other_file(app, at_job):
    """
    Verify ignoring spell check error in one audio file does not ignore it in another audio file
    """
    app.audio_transcription.activate_iframe_by_index(1)
    app.audio_transcription.add_text_to_bubble('Pet', 'test speling error')
    assert app.audio_transcription.data_validation.count_number_of_spell_check_error_messages() == 1
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.audio_transcription.deactivate_iframe()