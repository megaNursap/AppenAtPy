import time

import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file, \
    convert_audio_datatime_to_second
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data

pytestmark = pytest.mark.regression_audio_transcription_beta

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
                                        data.audio_transcription_one_segment_beta,
                                        job_title="Testing audio transcription beta job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    # obj = app.driver.switch_to.alert
    # obj.accept()

    ontology_file = get_data_file('/audio_transcription/AT-label-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.navigation.click_checkbox_by_text('Allow Multi-select', index=0)
    app.navigation.click_checkbox_by_text('Allow Multi-select', index=1)
    app.navigation.click_checkbox_by_text('Transcribe this group', index=1)
    app.navigation.click_checkbox_by_text('Required', index=1)

    app.navigation.click_link('Save')

    app.job.preview_job()

    return job_id


def test_label_manipulation_single_segment(at_job, app):
    """
        Verify requestor could add/delete/change the label
    """

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription.group_labels.choose_labels_by_name('pets')
    app.audio_transcription.group_labels.choose_labels_by_name('noise')
    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['pets', 'noise']

    app.audio_transcription_beta.delete_label_by_button()

    after_remove_label = app.audio_transcription_beta.get_selected_labels()
    assert after_remove_label == ['noise']

    app.audio_transcription.group_labels.choose_labels_by_name('male', multi_select=True, index=1)
    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['noise', 'male']

    app.audio_transcription.deactivate_iframe()


def test_clear_labels_single_segments(at_job, app):
    """
        Verify requestor could clear all labels by of the group button clear-all
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.verification.wait_untill_text_present_on_the_page("Audio Segment", 15)

    app.audio_transcription_beta.click_on_action_button('NothingToTranscribe')
    app.audio_transcription.group_labels.choose_labels_by_name('quite')
    app.audio_transcription.group_labels.choose_labels_by_name('ringing')
    app.audio_transcription.group_labels.choose_labels_by_name('fly', multi_select=True, index=1)

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['quite', 'ringing', 'fly']

    app.audio_transcription_beta.clear_choice_label()

    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['fly']

    app.audio_transcription_beta.deactivate_iframe()


def test_close_work_panel_single_panel(at_job, app):
    """
        Verify requestor could clear close the work panel by button
    """

    app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.verification.wait_untill_text_present_on_the_page("Audio Segment", 15)

    app.audio_transcription.group_labels.choose_labels_by_name('female', multi_select=True, index=1)

    app.audio_transcription_beta.click_on_action_button("WorkPanel")
    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_panel()) == 0, "The work panel NOT closed"

    app.audio_transcription_beta.deactivate_iframe()

def test_hot_key_open_close_label_panel_single_segment(app, at_job):
    """
       User could open/close label panel by hot/key [ for single segment
    """
    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)
    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_panel()) == 1

    app.audio_transcription_beta.click_on_waveform()
    app.navigation.hotkey("[")

    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_panel()) == 0
    app.audio_transcription_beta.add_text_to_segment("[")
    app.verification.text_present_on_page("[")
    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_panel()) == 0
    app.audio_transcription_beta.click_on_waveform()

    app.navigation.hotkey("[")
    assert len(app.audio_transcription_beta.audio_transcription_beta_element.get_work_panel()) == 1

