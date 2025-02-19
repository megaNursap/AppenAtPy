"""
https://appen.spiraservice.net/5/TestCase/2825.aspx
We will check test validator in this test, segment either have spell check error or regex error not corrected/ignored,
or annotate with "nothing to transcribe"
"""
import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.utils.selenium_utils import go_to_page

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
    Create Audio Tx job with 2 data rows and upload ontology
    Add regex and spell check validation rules
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

    # add regex rule
    url = "https://client.%s.cf3.us/jobs/%s/data_validation" % (pytest.env, job_id)
    go_to_page(app.driver, url)
    app.user.close_guide()
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION,
                                                                  enable_fix_suggestion=True, empty_string=False, replace_string='.')
    app.navigation.click_btn('Save')
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.enter_language_check_rule_info(language='English', locale='American')
    app.navigation.click_btn('Save')
    time.sleep(3)

    assert app.verification.text_present_on_page(RULE_DESCRIPTION)
    assert app.verification.text_present_on_page('Language Check (en-US)')

    return job_id


def test_validator_with_error(app, at_job):
    """
    Verify “Test Validators” passes inspite of data validation error
    """
    app.job.preview_job()
    time.sleep(2)

    app.audio_transcription.activate_iframe_by_index(0)

    checked_bubbles = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    for bubble in bubbles:
        name = bubble['name']
        if checked_bubbles.get(name, False):
            checked_bubbles[name] = checked_bubbles[name] + 1
        else:
            checked_bubbles[name] = 1

        index = checked_bubbles[name] - 1
        app.audio_transcription.add_text_to_bubble(name, 'test regex and speling check.,', index)
    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.activate_iframe_by_index(1)
    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.audio_transcription.deactivate_iframe()
    app.audio_transcription.submit_test_validators()
    time.sleep(5)
    app.verification.text_present_on_page("Validation succeeded")
