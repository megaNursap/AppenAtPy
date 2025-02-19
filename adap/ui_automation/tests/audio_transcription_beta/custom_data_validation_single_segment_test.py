import time

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data-one-unit.csv")
RULE_DESCRIPTION = 'Do not enter two punctuation mark'


@pytest.fixture(scope="module")
def at_job_single_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_no_listen_to,
                                        job_title="Testing audio transcription beta for one segment job",
                                        units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-new-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    return job_id


def test_access_data_validation_from_design_page(at_job_single_segment, app):
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage custom data validation')
    app.verification.text_present_on_page("Add rules")
    app.verification.text_present_on_page("No rules yet")
    app.verification.text_present_on_page(("Allows you to configure validation rules that will automatically flag "
                                           "issues with workers' data and offer them a chance to correct their work "
                                           "prior to submission"))


def test_add_custom_rule(at_job_single_segment, app):
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage custom data validation')
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='[,.!?]{2,}',
                                                                  error_description=RULE_DESCRIPTION,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='.')
    app.navigation.click_btn('Save')

    time.sleep(3)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION)
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.enter_language_check_rule_info(language='English', locale='American')
    app.navigation.click_btn('Save')

    app.job.preview_job()

    app.audio_transcription.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment('test,! eror')
    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    assert app.audio_transcription.data_validation.count_error_for_transcription_text_validation() == 2
    assert app.audio_transcription.data_validation.get_regex_error_description() == 'Do not enter two punctuation mark'

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()
    assert app.audio_transcription_beta.get_task_error_msg_by_index() == 'Transcription validation errors in some ' \
                                                                         'segments have not been addressed or ' \
                                                                         'ignored.', \
        "The error message on page ABSENT"

    app.audio_transcription_beta.activate_iframe_by_index(0)
    assert app.audio_transcription.btn_is_displayed('IGNORE')
    assert app.audio_transcription.btn_is_displayed('CORRECT')
    app.audio_transcription.data_validation.click_on_correct_word('error')

    assert app.audio_transcription.data_validation.count_error_for_transcription_text_validation() == 1

    app.navigation.click_btn('CORRECT')

    assert app.audio_transcription.data_validation.count_error_for_transcription_text_validation() == 0
    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()

    app.verification.text_present_on_page('Validation succeeded')
