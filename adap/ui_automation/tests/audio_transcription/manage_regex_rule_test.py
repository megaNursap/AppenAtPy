"""
https://appen.atlassian.net/browse/QED-1943
https://appen.atlassian.net/browse/QED-1944
https://appen.atlassian.net/browse/QED-1945
This test covers edit/delete regex rule for audio transcription data validation and regex syntax check
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
RULE_DESCRIPTION_1 = 'Do not enter two punctuation mark'
RULE_DESCRIPTION_2 = 'Multiple rules'
RULE_DESCRIPTION_EDIT = "Rule for edit"


# Failed cases because of bug https://appen.atlassian.net/browse/AT-4440
@pytest.fixture(scope="module")
def at_job(app):
    """
    Create Audio Tx job with 2 data rows and upload ontology
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
    return job_id


# https://appen.atlassian.net/browse/QED-1945
def test_regex_syntax_check(app, at_job):
    """
    Verify that error msg “Incorrect Regex syntax” is shown when incorrect python regex expression is entered
    Verify that ‘Regular Expression’ text field shows an info icon
    Verify user cannot save rule when incorrect regex is entered
    """
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, at_job)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?{2,}',
                                                                  error_description=RULE_DESCRIPTION_1,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='.')
    # assert app.audio_transcription.data_validation.get_regular_expression_tooltip() == 'Please use Python Regex format'
    app.verification.text_present_on_page('Incorrect Regex syntax')
    app.navigation.click_btn('Cancel')


# https://appen.atlassian.net/browse/QED-1943 delete rule
@pytest.mark.skip(reason="bug https://appen.atlassian.net/browse/AT-4440")
@pytest.mark.dependency()
def test_cancel_delete_regex_syntax_rule(app, at_job):
    """
    Verify requestor can cancel rule deletion
    """
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, at_job)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION_1,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='.')
    app.navigation.click_btn('Save')
    time.sleep(1)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_1)
    app.audio_transcription.data_validation.delete_rule(RULE_DESCRIPTION_1, save=False)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_1)


@pytest.mark.skip(reason="bug https://appen.atlassian.net/browse/AT-4440")
def test_delete_regex_syntax_rule(app, at_job):
    """
    Verify requestor can delete a validation rule
    """
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, at_job)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION_2,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='.')
    app.navigation.click_btn('Save')
    time.sleep(1)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_2)
    app.audio_transcription.data_validation.delete_rule(RULE_DESCRIPTION_2)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_2, is_not=False)


@pytest.mark.dependency(depends=["test_cancel_delete_regex_syntax_rule"])
def test_delete_all_regex_syntax_rules(app, at_job):
    """
    Verify requestor can delete all rules
    """
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, at_job)
    go_to_page(app.driver, url)
    app.user.close_guide()
    # one rule already exist, add one more and delete both of them
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION_2,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='.')
    app.navigation.click_btn('Save')
    time.sleep(1)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_2)
    app.audio_transcription.data_validation.delete_rule(RULE_DESCRIPTION_1)
    app.audio_transcription.data_validation.delete_rule(RULE_DESCRIPTION_2)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_1, is_not=False)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_2, is_not=False)
    app.verification.text_present_on_page('No rules yet')


# https://appen.atlassian.net/browse/QED-1944 edit rule
@pytest.mark.dependency()
def test_mandatory_fields_in_edit_mode(app, at_job):
    """
    Verify mandatory fields validation is shown when editing regex validation rule
    """
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, at_job)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}', error_description=RULE_DESCRIPTION_EDIT)
    app.navigation.click_btn('Save')
    time.sleep(1)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_EDIT)
    # verify mandatory fields for regular expression and error description
    app.audio_transcription.data_validation.click_edit_icon_for_rule(RULE_DESCRIPTION_EDIT)
    app.audio_transcription.data_validation.clear_regular_expression_error_description_in_edit_mode()
    app.verification.text_present_on_page('This field cannot be empty')
    # verify mandatory fields for empty string
    if not app.verification.checkbox_by_text_is_selected('Enable fix suggestion'):
        app.navigation.click_checkbox_by_text('Enable fix suggestion')
        app.audio_transcription.data_validation.click_empty_string_toggle_button()
    app.audio_transcription.data_validation.clear_replace_string_in_edit_mode()
    app.verification.text_present_on_page('This field cannot be empty. To apply empty string as error fix, please enable it.')
    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_mandatory_fields_in_edit_mode"])
def test_cancel_edit_regex_syntax_rule(app, at_job):
    """
    Verify changes are not saved when user clicks ‘Cancel’
    """
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, at_job)
    go_to_page(app.driver, url)
    app.user.close_guide()
    assert app.verification.text_present_on_page(RULE_DESCRIPTION_EDIT)
    app.audio_transcription.data_validation.edit_regex_search_rule(rule_name=RULE_DESCRIPTION_EDIT, regular_expression='[,.!?;]{2,}', error_description='Edited the rule', enable_fix_suggestion=False,
                                                                   empty_string=True, replace_string=None, test_the_rule=False, input_rule=None,
                                                                   test_rule_error_message=False)
    app.navigation.click_btn('Cancel')
    time.sleep(1)
    app.verification.text_present_on_page('Edited the rule', is_not=False)
    app.verification.text_present_on_page(RULE_DESCRIPTION_EDIT)


@pytest.mark.dependency(depends=["test_cancel_edit_regex_syntax_rule"])
def test_edit_regex_syntax_rule(app, at_job):
    """
    Verify requestor can edit Regex validation rule
    """
    test_rule_message = app.audio_transcription.data_validation.edit_regex_search_rule(rule_name=RULE_DESCRIPTION_EDIT,
                                                                                       regular_expression='[,.!?;]{2,}',
                                                                                       error_description='Edited the rule',
                                                                                       enable_fix_suggestion=True,
                                                                                       empty_string=False,
                                                                                       replace_string='.',
                                                                                       test_the_rule=True,
                                                                                       input_rule='test!?',
                                                                                       test_rule_error_message=True)
    assert test_rule_message == 'Edited the rule'
    app.navigation.click_btn('Save')
    time.sleep(1)
    app.verification.text_present_on_page('Edited the rule')
    app.verification.text_present_on_page(RULE_DESCRIPTION_EDIT, is_not=False)


@pytest.mark.dependency(depends=["test_edit_regex_syntax_rule"])
def test_contributor_validate_edited_rule(app, at_job):
    """
    Verify updated validation errors are shown correctly on contributor side after successfully editing Regex rule
    """
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
    job = JobAPI(API_KEY, job_id=at_job)
    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    app.user.logout()

    job_link = generate_job_link(at_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.add_text_to_bubble('Person', 'test,;')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    assert app.audio_transcription.data_validation.get_regex_error_description() == 'Edited the rule'
    assert app.audio_transcription.btn_is_displayed('CORRECT')
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    app.navigation.click_btn('CORRECT')
    assert app.audio_transcription.get_text_from_bubble('Person') == 'test.'
    app.audio_transcription.deactivate_iframe()
