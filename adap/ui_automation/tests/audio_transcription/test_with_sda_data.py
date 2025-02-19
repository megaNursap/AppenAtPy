"""
Test Audio Transcription tool with SDA data
"""

import time
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import create_screenshot

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui, pytest.mark.skip]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT_sda_2rows.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

# todo, Audio data not found, data maybe invalid. plus the account is test_sda_account is not ready.

@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Transcription job with SDA audio file and valid ontology
    """
    # create blank job first
    job = Builder(API_KEY)
    job.create_job()

    # Update job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Testing Audio Tx job with SDA data do not delete",
            'instructions': "Updated",
            'cml': data.audio_transcription_sda_cml,
            'project_number': 'PN000112',
            'units_per_assignment': 2,
            'judgments_per_unit': 1,
        }
    }
    job.update_job(payload=updated_payload)
    job_id = job.job_id

    # Upload data file
    job.upload_data(DATA_FILE, job_id, data_type='csv')

    # Log in as a customer and open job
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    # Upload ontology file
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')
    ontology_file = get_data_file('/audio_transcription/AT_sda_job_ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    # Verify data is shown in preview page
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(3)
    questions_on_page = app.annotation.get_number_iframes_on_page()
    assert questions_on_page == 2
    app.audio_transcription.activate_iframe_by_index(0)
    assert app.audio_transcription.nothing_to_transcribe_checkbox_is_displayed()
    app.driver.close()
    app.navigation.switch_to_window(job_window)

    # Launch job
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


@pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
@pytest.mark.dependency()
def test_submit_judgments(app, at_job):
    """
    Submit judgments as a contributor for SDA Audio Tx job
    """
    # Open external job link and login as contributor
    job_link = generate_job_link(at_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)

    questions_on_page = app.annotation.get_number_iframes_on_page()
    global page_task
    page_task = []
    for iframe in range(questions_on_page - 1):
        app.text_relationship.activate_iframe_by_index(iframe)
        segments = app.audio_transcription.get_bubbles_list()
        page_task.append(len(segments))
        app.audio_transcription.close_at_tool_without_saving()
        app.image_annotation.deactivate_iframe()

    # Add transcription to all segments in one data row
    min_task = page_task.index(min(page_task))
    app.text_relationship.activate_iframe_by_index(min_task)
    time.sleep(3)
    checked_bubbles = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    i = 0
    for bubble in bubbles:
        name = bubble['name']
        create_screenshot(app.driver, name + str(i))

        if checked_bubbles.get(name, False):
            checked_bubbles[name] = checked_bubbles[name] + 1
        else:
            checked_bubbles[name] = 1
        index = checked_bubbles[name] - 1

        app.audio_transcription.add_text_to_bubble(name, "test", index)
        i += 1
    app.image_annotation.deactivate_iframe()

    # Mark another data row as 'Nothing to Transcribe'
    _task = page_task.index(max(page_task))
    app.text_relationship.activate_iframe_by_index(_task)
    time.sleep(3)
    app.audio_transcription.click_nothing_to_transcribe_for_task()
    app.verification.text_present_on_page('Nothing to Transcribe')
    create_screenshot(app.driver, "nothing")
    app.image_annotation.deactivate_iframe()

    # Submit judgments
    time.sleep(2)
    app.audio_transcription.submit_page()
    time.sleep(5)
    create_screenshot(app.driver, "submit")
    app.verification.text_present_on_page('Check below for errors!', is_not=False)
    time.sleep(2)
    app.verification.text_present_on_page('There is no work currently available in this task.')

    app.user.logout()


@pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
@pytest.mark.dependency(depends=["test_submit_judgments"])
def test_at_report(app, at_job):
    """
    Verify report shows contributor judgments accurately
    """
    # Log in as Customer and open job
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    time.sleep(30)

    # Go to 'Results' tab, download Full report and verify output json
    app.job.open_tab("RESULTS")
    app.job.results.download_report('Full', at_job)

    file_name_zip = "/" + app.job.results.get_file_report_name(at_job, 'Full')
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    assert 'audio_transcription' in _df.columns

    random_row = random.randint(0, _df.shape[0] - 1)
    url = _df['audio_transcription'][random_row]

    import requests
    res = requests.get(url)
    assert res.status_code == 200
    assert len(res.json()['annotation']) > 0
    if not res.json()['nothingToTranscribe']:
        assert res.json()['annotation'][0][0]['metadata']['transcription'] != {}
        assert res.json()['annotation'][0][0]['metadata']['transcription']['text'] == 'test'
        assert res.json()['annotation'][0][0]['nothingToTranscribe'] == False
    else:
        assert res.json()['annotation'][0][0]['metadata'] == {}

    assert res.json()['annotation'][0][0]['annotatedBy'] == 'human'

    os.remove(csv_name)
    os.remove(full_file_name_zip)

