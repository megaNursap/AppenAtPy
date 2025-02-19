"""
This test covers a simple end to end flow including below items:
1. create job via cml
2. select host channel if it is fed env.
3. launch the job
4. do judgments via internal link
5. download full and aggregate report
"""
import time

import requests
from deepdiff import DeepDiff

from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-one-row-data.csv")

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

expected_json_output = retrive_data(get_data_file("/audio_transcription/audio_tx_judgment_output.json"))


@pytest.fixture(scope="module")
def audio_tx_job(app):
    """
    Create Audio Transcription job with 1 rows and attribute segments-data, upload ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_segments_data_cml,
                                        job_title="Testing audio transcription job", units_per_page=1)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology-correct-task.json')
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
    return job_id



@pytest.mark.dependency()
def test_submit_judgements_audio_annotation_segments_data(app, audio_tx_job):
    """
    Submit judgments where one segments transcribe and second mark as
    nothing to transcribe
    """
    #
    job_link = generate_job_link(audio_tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.user.close_guide()

    app.audio_transcription.activate_iframe_by_index(0)
    # add text/span/event
    app.audio_transcription.add_text_to_bubble("Pet", "Slightly more clever solution")
    app.audio_transcription.event.click_event_marker('Pet')
    app.audio_transcription.event.add_event('event1')
    app.audio_transcription.span.highlight_text_in_bubble('clever', 'Pet', index=0)
    app.audio_transcription.span.add_span('span1')
    app.audio_transcription.group_labels.choose_labels_by_name('female')

    # mark as nothing to transcribe the second bubble
    app.audio_transcription.select_bubble_by_name('Background')
    app.audio_transcription.click_nothing_to_transcribe_for_bubble('Background')
    app.audio_transcription.group_labels.choose_labels_by_name('pets', True)

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')

    app.user.logout()


@pytest.mark.dependency(depends=['test_submit_judgements_audio_annotation_segments_data'])
def test_download_reports_audio_transcription(app, audio_tx_job):
    """
    Verify user can download full  reports
    Verify output report the same as expected json file
    """
    app.user.customer.open_home_page()
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(audio_tx_job)
    report_type = 'Full'

    app.job.open_tab("RESULTS")
    app.job.results.download_report(report_type, audio_tx_job)
    file_name_zip = "/" + app.job.results.get_file_report_name(audio_tx_job, report_type)
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    list_of_output_audio_transcription = read_csv_file(csv_name, 'audio_transcription')
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