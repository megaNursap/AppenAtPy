import json
import os
import time

import pandas as pd
import pytest
import requests
from deepdiff import DeepDiff

from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_user_api_key, get_data_file, \
    read_csv_file, unzip_file, retrive_data
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-beta-source-data.csv")

@pytest.fixture(scope='module')
def at_job_one_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
    CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_one_segment_with_speed_attribute,
                                        job_title="Testing audio transcription beta job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    job_id = job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-beta-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.open_action("Settings")
    app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
    app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    app.user.logout()

    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)

    time.sleep(2)
    return job_id


@pytest.mark.dependency()
def test_transcribe_first_unit_for_one_segment_job(app, at_job_one_segment):

    global time_of_audio

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    time.sleep(3)
    app.audio_transcription_beta.activate_iframe_by_index(0)

    app.audio_transcription_beta.add_text_to_segment("test single segment with transcription")

    app.audio_transcription_beta.highlight_text_in_segments("single")
    app.audio_transcription.span.add_span('span3')

    app.audio_transcription_beta.click_event_marker('segment')
    app.audio_transcription.event.add_event('event1')

    app.audio_transcription_beta.move_to_word('transcription')
    app.audio_transcription_beta.click_on_action_button('ButtonTimestamp')
    app.audio_transcription_beta.click_on_waveform()

    time_of_audio = app.audio_transcription_beta.speed_specific_audio(speed_time=6)

    app.audio_transcription.group_labels.choose_labels_by_name('Pets', multi_select=True)

    app.audio_transcription_beta.deactivate_iframe()


@pytest.mark.dependency(depends=["test_transcribe_first_unit_for_one_segment_job"])
def test_transcribe_second_unit_for_one_segment_job(app, at_job_one_segment):

    app.verification.wait_untill_text_present_on_the_page('Audio Transcription', 25)
    time.sleep(3)
    app.audio_transcription_beta.activate_iframe_by_index(1)

    app.audio_transcription_beta.click_on_action_button("NothingToTranscribe")

    app.audio_transcription_beta.speed_specific_audio(speed_time=6)

    app.audio_transcription.group_labels.choose_labels_by_name('male', multi_select=True)
    app.audio_transcription_beta.scroll_to_label("Person voice")
    app.audio_transcription.group_labels.choose_labels_by_name('loud', index=1)
    app.audio_transcription.group_labels.choose_labels_by_name('quite', index=1)

    app.audio_transcription_beta.deactivate_iframe()
    app.audio_transcription_beta.submit_page()
    time.sleep(2)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()


@pytest.mark.dependency(depends=["test_transcribe_second_unit_for_one_segment_job"])
def test_download_report_one_segment_job(app, at_job_one_segment):

    expected_json_output = retrive_data(get_data_file("/audio_transcription/report_for_one_segment_job.json"))
    expected_json_output_four_min = retrive_data(get_data_file("/audio_transcription/report_for_one_segment_job_four_min.json"))

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.user.customer.open_home_page()
    actual_result_report = []
    app.job.open_job_with_id(at_job_one_segment)
    report_type = 'Full'

    app.job.open_tab("RESULTS")
    app.job.results.download_report(report_type, at_job_one_segment)
    file_name_zip = "/" + app.job.results.get_file_report_name(at_job_one_segment, report_type)
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    list_of_output_audio_transcription = read_csv_file(csv_name, 'audio_transcription')

    for output_audio in list_of_output_audio_transcription:
        json_of_output = json.loads(output_audio)
        url_key = json_of_output['url']

        rp = RP()
        cookie = rp.get_valid_sid(USER_EMAIL, PASSWORD)
        result = requests.get(url_key, cookies=cookie)
        actual_result_report.append(json.loads(result.text))
    if time_of_audio > 19:
        diff = DeepDiff(actual_result_report, expected_json_output_four_min, ignore_order=True)
    else:
        diff = DeepDiff(actual_result_report, expected_json_output, ignore_order=True)
    assert not diff, f"difference in response: {diff}"
    os.remove(csv_name)
    os.remove(full_file_name_zip)