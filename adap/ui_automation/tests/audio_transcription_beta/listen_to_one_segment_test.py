import time

import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file, \
    convert_audio_datatime_to_second
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data.csv")


@pytest.fixture(scope='module')
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_beta_listen_to,
                                        job_title="Testing audio transcription beta job listen to", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_listen_to_one_segment_portion(at_job, app):
    """
        Verify if requestor  is not specified the listen-to attribute
        then default to "must listen to 100% of entire segment"
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    listen_require_before_play = app.audio_transcription_beta.listening_required()

    assert listen_require_before_play[0] == 'Listening required (at least 0.38 s)'
    assert listen_require_before_play[1] == 'Listening required (at least 4.8 s)'
    assert listen_require_before_play[2] == 'Listening required (at least 1.15 s)'

    # play first portion of audio
    count_of_listen_to_block = app.audio_transcription_beta.click_on_listen_to_block(time_value=2)

    assert count_of_listen_to_block == 3, "The incorrect portion of listen to block"
    listen_require_after_play = app.audio_transcription_beta.listening_required()
    assert listen_require_after_play[0] == 'Listened enough'
    assert listen_require_after_play[1] == 'Listening required (at least 4.8 s)'
    assert listen_require_before_play[2] =='Listening required (at least 1.15 s)'

    app.audio_transcription_beta.click_on_listen_to_block(time_value=2, index=2)
    listen_require_after_second_play = app.audio_transcription_beta.listening_required()
    assert listen_require_after_second_play[0] == 'Listened enough'
    assert listen_require_after_second_play[1] == 'Listening required (at least 4.8 s)'
    assert listen_require_after_second_play[2] == 'Listened enough'

    app.audio_transcription_beta.deactivate_iframe()


def test_listen_to_invalid_array_in_cml(at_job, app):
    """
    Verify requestor could see error message when listen-to set up with incorrect data array
    Correct set-up when in cml for listen-to aray with nested value
    """

    listen_to_invalid = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' 
    allow-timestamping='true' listen-to='[0, 0.2, 0.1], [0.2, 0.7, 0.5], [0.7,1,0.1]'/> """

    job = Builder(API_KEY)

    job.job_id = at_job

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test listen-to invalid",
            'instructions': "all fields CML",
            'cml': listen_to_invalid,
            'project_number': 'PN000112'
        }
    }

    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.navigation.click_bytext("Details")
    app.verification.text_present_on_page(
        "CML listen-to value is invalid: '[0, 0.2, 0.1], [0.2, 0.7, 0.5], [0.7,1,0.1]' (Unexpected non-whitespace character after JSON at position 13)")
    time.sleep(1)
    app.audio_transcription_beta.deactivate_iframe()
