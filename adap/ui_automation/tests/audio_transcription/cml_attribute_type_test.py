"""
This tests verify different state of transcription in audio transcription job
https://appen.atlassian.net/browse/AT-6068
https://appen.atlassian.net/browse/AT-6005
"""
import time

import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/audio_transcription_rd_for_multi_segments.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows and upload ontology (using force-fullscreen="true")
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_cml,
                                        job_title="Testing audio transcription job with att type", units_per_page=2)
    # job_id = 2045720
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology-correct-task.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.preview_job()
    time.sleep(10)

    return job_id

@pytest.mark.audio_transcription_ui
def test_type_labeling_disabled(app, at_job):
    """
    Verify label just in read-only mode. You cannot add or delete label
    """

    cml_without_type_labeling = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{audio_transcription}}" task-type="qa"  type ="[\'transcription\']" name="new_audio_transcription"/>'

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test with read-only labeling",
            'instructions': " CML just with type=['transcription']",
            'cml': cml_without_type_labeling,
            'project_number': 'PN000112'
        }
    }
    job = Builder(API_KEY)
    job.job_id = at_job
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)
    app.audio_transcription.select_bubble_by_name('Background')
    assert app.audio_transcription.group_labels.delete_label_button_disabled()
    assert app.audio_transcription.open_label_panel_disabled()


@pytest.mark.audio_transcription_ui
def test_type_transcription_disabled(app, at_job):
    """
    Verify transcription for segment just in read-only.
    Nothing to transcribe/event/span modal button disabled

    """

    cml_without_type_labeling = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{audio_transcription}}" task-type="qa"  type ="[\'labeling\']" name="new_audio_transcription"/>'

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Audio Transcription Test with read-only labeling",
            'instructions': " CML just with type=['labelong']",
            'cml': cml_without_type_labeling,
            'project_number': 'PN000112'
        }
    }
    job = Builder(API_KEY)
    job.job_id = at_job
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()

    app.audio_transcription.activate_iframe_by_index(0)
    assert app.audio_transcription.event.event_btn_is_disable('Segment 1')
    assert not app.audio_transcription.nothing_to_transcribe_checkbox_is_displayed()
    assert not app.audio_transcription.span.span_modal_is_displayed()

