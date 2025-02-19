import time

import requests
from allure_commons.types import AttachmentType

from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job


pytestmark = [pytest.mark.regression_audio_transcription_contributor, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/arb_data.csv")

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module", autouse=True)
def tx_job_deprecated(tmpdir_factory, app):
    """
    Create Audio Tx review job using data stored in S3
    Upload matching ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_arbitration_task_type,
                                        job_title="Testing audio transcription job correct task-type", units_per_page=1)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology-correct-task.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.open_action("Settings")
    app.driver.find_element('xpath', "//label[@for='externalChannelsEnabled' or text()='External']").click()
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
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.user.close_guide()

    return job_id

def test_contributor_respond_all_acknowledge(app, tx_job_deprecated):
    """
    Verify contributor respond for all feedback, some off them dispute and successful submit the Job
    """
    app.navigation.refresh_page()
    app.audio_transcription.activate_iframe_by_index(0)

    list_of_segments = app.audio_transcription.get_bubbles_list()

    for segment_index in list_of_segments:
        app.audio_transcription.select_bubble_by_name(segment_index['name'], default_name=segment_index['name'])
        if segment_index['name'] == 'Segment 1':
            app.audio_transcription.arbitration_of_feedback()
        else:
            app.audio_transcription.arbitration_of_feedback('Approve')

    app.audio_transcription.deactivate_iframe()

    app.audio_transcription.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()


def test_acknowledge_result_loading_unit_page(app, tx_job_deprecated):
    """
    Verify that requestor can see result of arbitration decision in report, this units that was
    rejected should return the origin judgment result,
    the units that was approve QA modification should be return the corrected judgment
    """
    app.user.customer.open_home_page()
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job_deprecated)

    report_type = 'Full'

    app.job.open_tab("RESULTS")
    app.job.results.download_report(report_type, tx_job_deprecated)
    file_name_zip = "/" + app.job.results.get_file_report_name(tx_job_deprecated, report_type)
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    audio_transcription_org = read_csv_file(DATA_FILE, 'audio_transcription_original')
    audio_transcription_correct = read_csv_file(DATA_FILE, 'audio_transcription_correction')
    list_of_output_audio_transcription_arb = read_csv_file(csv_name, 'audio_transcription_arbitration')
    json_of_output = json.loads(list_of_output_audio_transcription_arb[0])
    url_key_arb = json_of_output['url']

    rp = RP()
    cookie = rp.get_valid_sid(USER_EMAIL, PASSWORD)
    result_arb = requests.get(url_key_arb, cookies=cookie)
    result_org = requests.get(audio_transcription_org[0], cookies=cookie)
    result_correct = requests.get(audio_transcription_correct[0], cookies=cookie)
    actual_result_report_arb = json.loads(result_arb.text)
    expected_result_report_org = result_org.json()
    expected_result_report_cor = result_correct.json()

    label_org_first_unit = expected_result_report_org['annotation']['segments'][0]['labels']
    transcription_org_first_unit = expected_result_report_org['annotation']['segments'][0]['transcription']

    # verify judgment  of rejected first unit the same as in origin Job
    assert actual_result_report_arb['annotation']['segments'][0]['labels'] == label_org_first_unit
    assert actual_result_report_arb['annotation']['segments'][0]['transcription'] == transcription_org_first_unit

    label_corrected_third_unit = expected_result_report_cor['annotation']['segments'][3]['labels']
    transcription_corrected_third_unit = expected_result_report_cor['annotation']['segments'][3]['transcription']

    # verify judgment of approve QA modification in third unit the same as in corrected Job
    assert actual_result_report_arb['annotation']['segments'][3]['labels'] == label_corrected_third_unit
    assert actual_result_report_arb['annotation']['segments'][3]['transcription'] == transcription_corrected_third_unit