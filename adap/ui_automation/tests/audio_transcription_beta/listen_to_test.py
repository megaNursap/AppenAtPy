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
                                        data.audio_transcription_beta,
                                        job_title="Testing audio transcription beta job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id


def test_listen_to_no_specify(at_job, app):
    """
        Verify if requestor  is not specified the listen-to attribute
        then default to "must listen to 100% of entire segment"
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    value = app.audio_transcription_beta.get_segment_info()['1'].split(" ")
    start_time = convert_audio_datatime_to_second(value[0])
    end_time = convert_audio_datatime_to_second(value[2])
    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)
    app.audio_transcription_beta.click_on_action_button('ButtonPlaySegment')
    app.audio_transcription_beta.stop_play_audio_by_tab()

    app.audio_transcription_beta.add_text_to_segment("test_text")
    app.audio_transcription.group_labels.choose_labels_by_name('Pets', multi_select=True)

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error[1] == ['Meet minimum listening duration requirement of all audio blocks.']
    app.audio_transcription_beta.click_on_listen_to_block(end_time - start_time)
    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error[1] == ['', '', '']


def test_listen_to_portion(at_job, app):
    """
        Verify if requestor specified the listen-to range
        then the audio divide on portion and the user should listen each portion according
        to configuration
    """

    job = Builder(API_KEY)

    job.job_id = at_job

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test listen-to portion",
            'instructions': "all fields CML",
            'cml': data.audio_transcription_beta_listen_to,
            'project_number': 'PN000112'
        }
    }

    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.audio_transcription_beta.click_on_segment(2)
    app.verification.wait_untill_text_present_on_the_page("Segment 3", 15)

    count_of_listen_to_block = app.audio_transcription_beta.click_on_listen_to_block(time_value=0.2)
    app.audio_transcription_beta.stop_play_audio_by_tab()

    assert count_of_listen_to_block == 2, "The incorrect portion of listen to block"
    app.audio_transcription_beta.click_on_listen_to_block(time_value=1, index=1)
    app.audio_transcription_beta.stop_play_audio_by_tab()

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_test_validators()
    app.audio_transcription_beta.activate_iframe_by_index(0)

    payload_error = app.audio_transcription_beta.get_error_icon_info()
    assert payload_error[3] == ['Provide transcription text or mark as nothing to transcribe.',
                                'Select labels from all required groups.']
    app.audio_transcription_beta.deactivate_iframe()


def test_listen_to_invalid_range(at_job, app):
    """
    Verify requestor could see error message for when the range of listen-to set up incorrect, the correct listen-to
    range when one of he ranges have to add up to 1. That means, if we sort them, first should start at 0,
    last should end at 1, and those in between should be adjacent to each other.
    """

    listen_to_invalid = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' 
    allow-timestamping='true' listen-to='[[0, 0.2, 0.1], [0.2, 0.7, 0.5]]'/> """

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
        "CML listen-to value is invalid: '[[0, 0.2, 0.1], [0.2, 0.7, 0.5]]' (Out of Range)")
    time.sleep(1)
    app.audio_transcription_beta.deactivate_iframe()
