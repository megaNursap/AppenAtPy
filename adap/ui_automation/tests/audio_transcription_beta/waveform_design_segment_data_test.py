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

    ontology_file = get_data_file('/audio_transcription/AT-new-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()

    return job_id

def test_at_preview_data_unit(app, at_job):
    """
    Verify requestor can preview data and see baby waveform, segment list
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.verification.text_present_on_page("segments list")

    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_segment_list()) == 5
    second_segment_info = app.audio_transcription_beta.get_segment_info()
    assert second_segment_info['2'] == '00:00:03.57 / 00:00:07.89'

    app.audio_transcription.deactivate_iframe()


def test_work_area(app, at_job):
    """
    Verify Audio Tx ontology class has 'Transcribe the layer' checkbox
    Verify enabling 'Transcribe the layer' allows requestor to add spans and events
    """
    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)

    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.click_on_segment()
    app.verification.wait_untill_text_present_on_the_page("Segment 1", 15)
    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_area()) == 1
    app.verification.wait_untill_text_present_on_the_page("2.8 s", 35)
    listen_to_progress = app.audio_transcription_beta.get_work_area_listen_to()

    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info()
    assert header_waveform_info['segment_name'] == 'Segment 1', 'The title of chosen segment incorrect'
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' Timestamp',
                                                      ' NothingToTranscribe',
                                                      ' PlaySegment PlayPauseButton',
                                                      ' WorkPanel'], "Not all button for waveform action present"
    assert header_waveform_info['segment_event'][1] == 'EventMarker'
    assert listen_to_progress[0]['listen_to_progress'] == '0 s', "Start point NOT on 0"
    app.verification.text_present_on_page('Add Transcription')

    app.audio_transcription.deactivate_iframe()


def test_waveform_type_transcription(app, at_job):
    """
    Verify requestor can create job just with type='transcription' and cannot add label to the segments
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
    segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['transcription']" beta='true' 
    allow-timestamping='true'/> """

    job = Builder(API_KEY)

    job.job_id = at_job

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

    app.audio_transcription_beta.click_on_segment(index=1, transcribe_all_segment=True)
    # app.audio_transcription_beta.click_on_segment(index=1)

    app.verification.wait_untill_text_present_on_the_page("Segment 2", 15)
    app.verification.wait_untill_text_present_on_the_page("4.3 s", 35)

    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info()
    assert header_waveform_info['segment_name'] == 'Segment 2', 'The title of chosen segment incorrect'
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' Timestamp',
                                                      ' NothingToTranscribe',
                                                      ' PlaySegment PlayPauseButton'], "Not all button for waveform action present"
    assert header_waveform_info['segment_event'][1] == 'EventMarker'
    app.verification.text_present_on_page('Add Transcription')


def test_waveform_type_labeling(app, at_job):
    """
    Verify requestor can create job with type='labeling' and cannot transcribe the text, add span or events,
    but still mark the segments as nothing to transcribe
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
    segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling']" beta='true' 
    allow-timestamping='true'/> """

    job = Builder(API_KEY)

    job.job_id = at_job

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

    app.audio_transcription_beta.click_on_segment(index=2)
    app.verification.wait_untill_text_present_on_the_page("Segment 3", 15)
    app.verification.wait_untill_text_present_on_the_page("1.9 s", 35)

    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info(transcription=False)
    assert header_waveform_info['segment_name'] == 'Segment 3', 'The title of chosen segment incorrect'
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' NothingToTranscribe',
                                                      ' PlaySegment PlayPauseButton',
                                                      ' WorkPanel'], "Not all button for waveform action present"
    assert header_waveform_info['segment_event'] == []
    app.verification.text_present_on_page('Add Transcription', False )


def test_waveform_zoom_hot_key_multi_segment(app, at_job):
    app.navigation.refresh_page()

    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.audio_transcription_beta.click_on_segment(index=1)
    app.verification.wait_untill_text_present_on_the_page("Segment 2", 15)
    app.audio_transcription_beta.click_on_waveform()

    default_interval_lines = app.audio_transcription_beta.get_interval_lines_height(min_height=0, max_height=200)
    assert default_interval_lines == "773"

    app.audio_transcription_beta.click_on_action_button('ButtonZoomIn', index=1)
    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, '=')
    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, '-')
    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, '=')

    waveform_after_zoom = app.audio_transcription_beta.get_interval_lines_height(min_height=0, max_height=200)
    assert waveform_after_zoom == "2170"

    app.navigation.combine_hotkey(Keys.LEFT_CONTROL, 'r')

    waveform_after_zoom_reset = app.audio_transcription_beta.get_interval_lines_height(min_height=0, max_height=200)
    assert waveform_after_zoom_reset == default_interval_lines

def test_waveform_type_segmentation(app, at_job):
    """
    Verify requestor can create job with type='segmentation' and cannot transcribe the text, add span or events,
    but still mark the segments as nothing to transcribe and could add labels
    """
    type_transcription = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
    segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['segmentation']" beta='true' 
    allow-timestamping='true'/> """

    job = Builder(API_KEY)

    job.job_id = at_job

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
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.wait_untill_text_present_on_the_page('segments list', 20)
    big_waveform_info = app.audio_transcription_beta.get_big_waveform_info()
    segment_list = len(app.audio_transcription_beta.audio_transcription_beta_element.get_segment_list())
    assert big_waveform_info['region'] == segment_list
    assert app.audio_transcription_beta.get_active_region_from_waveform() == 'Segment 1'
    app.audio_transcription_beta.click_on_segment(index=3)
    assert app.audio_transcription_beta.get_active_region_from_waveform() == 'Segment 4'
    app.verification.text_present_on_page('Add Transcription', False)
    header_waveform_info = app.audio_transcription_beta.get_header_waveform_info(transcription=False)
    assert header_waveform_info['segment_action'] == [' ZoomIn',
                                                      ' ZoomOut ZoomOut--disabled --disabled',
                                                      ' ZoomReset ZoomReset--disabled --disabled',
                                                      ' PlaySegment PlayPauseButton',
                                                      ], "Not all button for waveform action present"
    app.audio_transcription_beta.choose_region_on_waveform(2)
    assert app.audio_transcription_beta.get_active_region_from_waveform() == "Segment 3"
    app.audio_transcription_beta.deactivate_iframe()
