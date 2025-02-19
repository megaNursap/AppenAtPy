import time

import allure
import requests
from deepdiff import DeepDiff

from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = [pytest.mark.regression_audio_transcription_beta, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/peer_review_one_segment_download.csv")


@pytest.fixture(scope="module")
def at_job_one_segment(tmpdir_factory, app):
    """
    Create Audio Tx beta='true' job with 2 data rows
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_peer_review_one_segment,
                                        job_title="Testing audio transcription beta for one segment job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-label-ontology.json')
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

    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)

    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)
    return job_id

@pytest.mark.dependency()
def test_contributor_review_one_segment_job(app, at_job_one_segment):
    """
    Verify contributor can review the work Job of one segment
    """
    app.navigation.refresh_page()
    app.audio_transcription_beta.activate_iframe_by_index(0)
    app.verification.wait_untill_text_present_on_the_page("Test", 20)
    added_label = app.audio_transcription_beta.get_selected_labels()
    assert added_label == ['person']

    app.audio_transcription_beta.click_event_marker("Test")
    app.audio_transcription.event.add_event("event1")

    app.audio_transcription.group_labels.choose_labels_by_name('pets', True)

    app.audio_transcription_beta.click_on_action_button("PlayPauseButton")
    time.sleep(19)

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription_beta.submit_page()
    time.sleep(2)

@pytest.mark.dependency(depends=['test_contributor_review_one_segment_job'])
@allure.issue("https://appen.atlassian.net/browse/ADAP-4365", "This test has been wait after the ADAP-4365 implemented ")
def test_download_reports_review_job_one_segment(app, at_job_one_segment):
    """
    Verify user could download full  reports
    Verify output report the same as expected json file
    """
    expected_json_output = retrive_data(get_data_file("/audio_transcription/audio_tx_judgment_output_review_job.json"))

    app.user.customer.open_home_page()

    app.job.open_job_with_id(at_job_one_segment)
    report_type = 'Full'

    app.job.open_tab("RESULTS")
    app.job.results.download_report(report_type, at_job_one_segment)
    file_name_zip = "/" + app.job.results.get_file_report_name(at_job_one_segment, report_type)
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    list_of_output_audio_transcription = read_csv_file(csv_name, 'new_audio_transcription')
    json_of_output = json.loads(list_of_output_audio_transcription[0])
    url_key = json_of_output['url']

    rp = RP()
    cookie = rp.get_valid_sid(USER_EMAIL, PASSWORD)
    result = requests.get(url_key, cookies=cookie)
    actual_result_report = json.loads(result.text)
    diff = DeepDiff(actual_result_report, expected_json_output, ignore_order=True)
    assert not diff, f"difference in response: {diff}"
    os.remove(csv_name)
    os.remove(full_file_name_zip)