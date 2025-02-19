import time

import allure
from selenium.webdriver import Keys

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")



@pytest.fixture(scope="module")
def at_job_single_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_beta,
                                        job_title="Testing audio transcription beta for one segment job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-new-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id

@allure.issue("https://appen.atlassian.net/browse/AT-6523", "The issue related to playback cursor")
def test_at_preview_data_unit_one_segment(app, at_job_single_segment):
    """
    Verify requestor can preview data and not segment list, just one segment,
    See waveform, text area for transcription, all buttons in listen-to panel
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.verification.text_present_on_page("Audio Segment")

    app.verification.text_present_on_page("segments list", False)

    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_area()) == 1

    app.verification.wait_untill_text_present_on_the_page("19.1 s", 35)
    listen_to_progress = app.audio_transcription_beta.get_work_area_listen_to()

    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info()
    waveform_info = app.audio_transcription_beta.get_waveform_info()

    assert header_waveform_info['segment_name'] == 'Audio Segment', 'The title of chosen segment incorrect'
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' Timestamp',
                                                      ' NothingToTranscribe',
                                                      ' PlaySegment PlayPauseButton',
                                                      ' WorkPanel'], "Not all button for waveform action present"
    assert header_waveform_info['segment_event'][1] == 'EventMarker'
    assert listen_to_progress[0]['listen_to_progress'] == '0 s', "Start point NOT on 0"
    assert waveform_info['cursor'] == {'height': 72, 'width': 10}, "The cursor Not present on page"
    assert waveform_info['audio_duration'] == '00:00:19.19', "The incorrect audio duration"
    app.verification.text_present_on_page('Add Transcription')
    app.audio_transcription.deactivate_iframe()


def test_waveform_type_transcription_one_segment(app, at_job_single_segment):
    """
    Verify requestor can create job just with type='transcription' and cannot add label to the segments
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
    name="audio_transcription" type="['transcription']" beta='true' allow-timestamping='true'/> """

    job = Builder(API_KEY)

    job.job_id = at_job_single_segment

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test type=['transcription']",
            'instructions': "all fields CML",
            'cml': type_transcription,
            'project_number': 'PN000112'
        }
    }

    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.text_present_on_page("Audio Segment")
    app.verification.wait_untill_text_present_on_the_page("18.3 s", 35)

    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info()
    assert header_waveform_info['segment_name'] == 'Audio Segment', 'The title of chosen segment incorrect'
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' Timestamp',
                                                      ' NothingToTranscribe',
                                                      ' PlaySegment PlayPauseButton'], "Not all button for waveform action present"
    assert header_waveform_info['segment_event'][1] == 'EventMarker'
    app.verification.text_present_on_page('Add Transcription')


def test_waveform_type_labeling_one_segment(app, at_job_single_segment):
    """
    Verify requestor can create job with type='labeling' and cannot transcribe the text, add span or events,
    but still mark the segments as nothing to transcribe
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
     name="audio_transcription" type="['labeling']" beta='true' allow-timestamping='true'/> """

    job = Builder(API_KEY)

    job.job_id = at_job_single_segment

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test type=['labeling']",
            'instructions': "all fields CML",
            'cml': type_transcription,
            'project_number': 'PN000112'
        }
    }

    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.text_present_on_page("Audio Segment")

    app.verification.wait_untill_text_present_on_the_page("18.3 s", 35)

    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info(transcription=False)
    assert header_waveform_info['segment_name'] == 'Audio Segment', 'The title of chosen segment incorrect'
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' NothingToTranscribe',
                                                      ' PlaySegment PlayPauseButton',
                                                      ' WorkPanel'], "Not all button for waveform action present"
    assert header_waveform_info['segment_event'] == []
    app.verification.text_present_on_page('Add Transcription', False)


def test_waveform_zoom_hot_key_one_segment(app, at_job_single_segment):
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.text_present_on_page("Audio Segment")

    default_interval_lines = app.audio_transcription_beta.get_interval_lines_height(min_height=0, max_height=200)
    assert default_interval_lines == "1048"

    app.audio_transcription_beta.click_on_action_button('ButtonZoomIn')
    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, '=')
    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, '-')

    waveform_after_zoom = app.audio_transcription_beta.get_interval_lines_height(min_height=0, max_height=200)
    assert waveform_after_zoom == "2096"

    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, 'r')

    waveform_after_zoom_reset = app.audio_transcription_beta.get_interval_lines_height(min_height=0, max_height=200)
    assert waveform_after_zoom_reset == default_interval_lines


def test_waveform_type_segmentation_one_segment(app, at_job_single_segment):
    """
    Verify requestor can create job with type='segmentation' and  see big waveform
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
     name="audio_transcription" type="['segmentation']" beta='true' allow-timestamping='true'/> """

    job = Builder(API_KEY)

    job.job_id = at_job_single_segment

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test type=['segmentation']",
            'instructions': "all fields CML",
            'cml': type_transcription,
            'project_number': 'PN000112'
        }
    }

    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.text_present_on_page("Create Your First Segment")

    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_big_waveform()) == 1

    app.audio_transcription_beta.deactivate_iframe()

    app.audio_transcription_beta.activate_iframe_by_index(1)
    app.verification.text_present_on_page("Create Your First Segment")

    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_big_waveform()) == 1
    app.audio_transcription_beta.deactivate_iframe()

