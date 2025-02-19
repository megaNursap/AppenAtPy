import time

import pytest
from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data-one-unit.csv")
RULE_DESCRIPTION = 'Do not set of "abc" in sequence'


@pytest.fixture(scope='module')
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_beta_data_validation,
                                        job_title="Testing audio transcription beta job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage custom data validation')
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.add_regex_search_rule(regular_expression='abc',
                                                                  error_description=RULE_DESCRIPTION,
                                                                  enable_fix_suggestion=True, empty_string=False,
                                                                  replace_string='ABC')
    app.navigation.click_btn('Save')
    time.sleep(3)
    assert app.verification.text_present_on_page(RULE_DESCRIPTION)
    app.navigation.click_btn('Add rules')
    app.audio_transcription.data_validation.enter_language_check_rule_info(language='English', locale='American')
    app.navigation.click_btn('Save')

    app.job.preview_job()

    return job_id


def test_add_custom_data_validation_multi_segments(at_job, app):
    """
        Verify requestor could add/edit/delete  transcription in text area, add span/event/timestamp
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)

    app.audio_transcription_beta.add_text_to_segment("test that abc do not alow in sequence")

    assert app.audio_transcription.data_validation.count_number_of_regex_error_messages() == 1
    assert app.audio_transcription.data_validation.count_error_for_transcription_text_validation() == 3
    assert app.audio_transcription.data_validation.get_regex_error_description() == RULE_DESCRIPTION

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()

    app.audio_transcription_beta.activate_iframe_by_index(0)
    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error.get(1) == ["Address or ignore all transcription validation errors."]
    app.audio_transcription_beta.click_on_segment()
    app.audio_transcription.data_validation.ignore_spell_check_error()
    app.audio_transcription.data_validation.click_on_correct_word('allow')

    app.navigation.click_btn("CORRECT")
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.submit_test_validators()
    app.audio_transcription_beta.activate_iframe_by_index(0)
    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error.get(1) == ['']
