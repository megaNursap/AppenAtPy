"""
https://appen.atlassian.net/browse/QED-1909
https://appen.atlassian.net/browse/QED-1910
Include test cases:
1. Contributor submit judgments error
2. Contributor submit judgments successfully
3. Download full and aggregated report and verify them
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_transcription import create_video_transcription_job
import time
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import find_element
from adap.data.video_transcription import data

# pytestmark = [pytest.mark.regression_video_transcription]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')
DATA_FILE = get_data_file("/video_transcription/video_transcription_data.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module", autouse=True)
def login_and_create_vt(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job_id = create_video_transcription_job(API_KEY, DATA_FILE, data.full_cml, JWT_TOKEN)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_action("Settings")

    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
        app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
        app.navigation.click_link('Save')
    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)
    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    app.user.logout()
    return job_id


# https://appen.spiraservice.net/5/TestCase/2929.aspx
@pytest.mark.dependency()
def test_contributor_submit_judgment_without_creating_segments(app, login_and_create_vt):
    job_link = generate_job_link(login_and_create_vt, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.video_transcription.submit_page()
    app.verification.text_present_on_page('Check below for errors!')
    assert app.verification.count_text_present_on_page('Check below for errors!') == 3


@pytest.mark.dependency(depends=["test_contributor_submit_judgment_without_creating_segments"])
def test_contributor_submit_without_turn_id_or_category_or_transcription(app, login_and_create_vt):
    # submit with segments, but did not fill out turn id
    iframes_count = app.video_transcription.get_number_iframes_on_page()
    assert iframes_count == 3
    for i in range(iframes_count):
        app.video_transcription.activate_iframe_by_index(i)
        app.video_transcription.create_segment_while_playing(start_time=5, end_time=10)
        app.video_transcription.click_to_select_segment()
        # for first iframe, miss turn id, input category and transcription
        if i == 0:
            app.video_transcription.click_to_select_ontology_under_category('Pet')
            app.video_transcription.input_transcription_in_textbox('test with optional fields in cml')
        # for second iframe, miss category, input turn id and transcription
        if i == 1:
            app.video_transcription.create_turn_id_and_select_it('new turn id')
            app.video_transcription.input_transcription_in_textbox('test with optional fields in cml')
        # for third iframe, miss transcription, input turn id and category
        if i == 2:
            app.video_transcription.create_turn_id_and_select_it('new turn id')
            app.video_transcription.click_to_select_ontology_under_category('Pet')
        app.navigation.click_btn('Save Segment')
        app.video_transcription.deactivate_iframe()

    app.video_transcription.submit_page()
    app.verification.text_present_on_page('Check below for errors!')
    assert app.verification.count_text_present_on_page('Check below for errors!') == 3


@pytest.mark.dependency(depends=["test_contributor_submit_without_turn_id_or_category_or_transcription"])
def test_contributor_submit_judgments_successfully(app, login_and_create_vt):
    iframes_count = app.video_transcription.get_number_iframes_on_page()
    for i in range(iframes_count):
        app.video_transcription.activate_iframe_by_index(i)
        app.video_transcription.click_to_select_segment()
        if i == 0:
            app.video_transcription.create_turn_id_and_select_it('new turn id')
        if i == 1:
            app.video_transcription.click_to_select_ontology_under_category('Pet')
        if i == 2:
            app.video_transcription.input_transcription_in_textbox('test with optional fields in cml')
        app.navigation.click_btn('Save Segment')
        app.video_transcription.deactivate_iframe()

    app.video_transcription.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('Check below for errors!', is_not=False)
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_contributor_submit_judgments_successfully"])
def test_download_report_vt(app_test, login_and_create_vt):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(login_and_create_vt)

    for report_type in ['Full', 'Aggregated']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, login_and_create_vt)
        file_name_zip = "/" + app_test.job.results.get_file_report_name(login_and_create_vt, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert '_unit_id' in _df.columns
        assert 'video_transcription' in _df.columns
        assert 'url' in _df.columns
        if report_type == 'Full':
            assert '_worker_id' in _df.columns

        random_row = random.randint(0, _df.shape[0] - 1)
        output = _df['video_transcription'][random_row]
        assert 'requestor-proxy.' + pytest.env + '.cf3.us' in output
        assert 'annotations/secure_redirect?token=' in output

        import requests
        output_json_resp = requests.get(output)
        assert output_json_resp.status_code == 200
        assert "regions" in output_json_resp.json()
        assert len(output_json_resp.json()['regions']) > 0
        assert "start" in output_json_resp.json()['regions'][0]
        assert "end" in output_json_resp.json()['regions'][0]
        assert "data" in output_json_resp.json()['regions'][0]
        assert "Pet" == output_json_resp.json()['regions'][0]['data']['category']
        assert "test with optional fields in cml" == output_json_resp.json()['regions'][0]['data']['text']
        assert "new turn id" == output_json_resp.json()['regions'][0]['data']['turn']

        # app_test.navigation.click_link("Force regenerate this report")
        # progressbar = find_element(app_test.driver, "//div[@id='progressbar']")
        # time_to_wait = 30
        # current_time = 0
        # while current_time < time_to_wait:
        #     progress = progressbar.get_attribute('aria-valuenow')
        #     if progress == '100':
        #         break
        #     else:
        #         current_time += 1
        #         time.sleep(1)
        # else:
        #     msg = f'Max wait time reached, regenerate report failed'
        #     raise Exception(msg)

        os.remove(csv_name)
        os.remove(full_file_name_zip)

