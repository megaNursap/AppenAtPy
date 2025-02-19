import allure

from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.utils.pandas_utils import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import create_screenshot

pytestmark = [pytest.mark.regression_audio_transcription_design, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")


@pytest.fixture(scope="module")
def at_job(tmpdir_factory, app):
    """
    Create Audio Tx job with 2 data rows, upload ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.audio_transcription_cml,
                                        job_title="Testing audio transcription job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Audio Transcription Ontology')

    ontology_file = get_data_file('/audio_transcription/AT-ontology.json')
    app.ontology.upload_ontology(ontology_file, rebrand=True)

    app.job.open_action("Settings")

    app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
    app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running',60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_open_launched_job_at(app, at_job):
    """
    Verify contributor can view audio segments
    Verify error is shown when contributor submits work without annotation
    """

    job_link = generate_job_link(at_job, API_KEY, pytest.env)

    app.navigation.open_page(job_link)
    # app.user.close_guide()

    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)

    questions_on_page = app.annotation.get_number_iframes_on_page()
    global page_task
    page_task = []
    for iframe in range(questions_on_page - 1):
        app.text_relationship.activate_iframe_by_index(iframe)
        # app.audio_transcription.toolbar.full_screen()
        # app.verification.text_present_on_page("Audio Transcription")
        # app.verification.text_present_on_page("Segments Transcribed")
        # segments = app.audio_transcription.get_num_segments_to_transcribe()
        segments = app.audio_transcription.get_bubbles_list()
        page_task.append(len(segments))
        # page_task.append(segments)
        app.audio_transcription.close_at_tool_without_saving()
        app.image_annotation.deactivate_iframe()

    app.audio_transcription.submit_page()
    app.verification.text_present_on_page('Error: All segments have to be transcribed or marked as nothing to transcribe.')


@pytest.mark.dependency(depends=["test_open_launched_job_at"])
def test_save_transcription(app, at_job):
    """
    Verify contributor can add transcription text into segment bubbles
    """
    # app.driver.find_element('xpath',"//div[@data-module]//button").click()
    app.navigation.refresh_page()
    time.sleep(3)
    min_task = page_task.index(min(page_task))

    # app.navigation.refresh_page()
    app.text_relationship.activate_iframe_by_index(min_task)
    # app.navigation.click_btn("Open Transcription Tool")
    # app.audio_transcription.toolbar.full_screen()
    time.sleep(3)

    checked_bubbels = {}
    bubbles = app.audio_transcription.get_bubbles_list()
    i = 0
    for bubble in bubbles:

        name = bubble['name']
        create_screenshot(app.driver, name+str(i))

        if checked_bubbels.get(name, False):
            checked_bubbels[name] = checked_bubbels[name] + 1
        else:
            checked_bubbels[name] = 1
        index = checked_bubbels[name] - 1

        app.audio_transcription.add_text_to_bubble(name, "test",index)
        i += 1

    # app.audio_transcription.toolbar.click_btn('save')

    app.image_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_open_launched_job_at"])
def test_nothing_to_transcribe_judgements(app, at_job):
    """
    Verify contributor can mark 'Nothing to transcribe' at unit level
    """
    _task = page_task.index(max(page_task))
    app.text_relationship.activate_iframe_by_index(_task)
    # app.navigation.click_btn("Open Transcription Tool")
    # app.audio_transcription.toolbar.full_screen()
    time.sleep(3)

    app.audio_transcription.click_nothing_to_transcribe_for_task()
    # app.audio_transcription.toolbar.click_btn('save')

    app.verification.text_present_on_page('Nothing to Transcribe')
    create_screenshot(app.driver, "nothing")
    app.image_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_nothing_to_transcribe_judgements","test_save_transcription"])
def test_submit_at_judgements(app, at_job):
    """
    Verify contributor can submit work after marking 'Nothing to transcribe' at unit level
    """
    app.audio_transcription.submit_page()
    time.sleep(5)
    create_screenshot(app.driver, "submit")
    app.verification.text_present_on_page('Error: All segments have to be transcribed or marked as nothing to transcribe.', is_not=False)
    time.sleep(2)
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_submit_at_judgements"])
def test_at_reports(app_test,at_job):
    """
    Verify requestor can download full and aggregated report
    Verify report's output json shows annotation accordingly
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(at_job)
    time.sleep(30)
    for report_type in ['Full', 'Aggregated']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, at_job)

        file_name_zip = "/"+app_test.job.results.get_file_report_name(at_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'audio_transcription' in _df.columns
        # feature changed,need update later, right now, returns 403
        # random_row = random.randint(0, _df.shape[0]-1)
        # url = json.loads(_df['audio_transcription'][random_row]).get("url")
        # import requests
        # res = requests.get(url)
        # assert res.status_code == 200
        # assert len(res.json()['annotation']) > 0
        # if not res.json()['nothingToTranscribe']:
        #     assert res.json()['annotation'][0][0]['metadata']['transcription'] != {}
        #     assert res.json()['annotation'][0][0]['metadata']['transcription']['text'] == 'test'
        #     assert res.json()['annotation'][0][0]['nothingToTranscribe'] == False
        # else:
        #     assert res.json()['annotation'][0][0]['metadata'] == {}
        #
        # assert res.json()['annotation'][0][0]['annotatedBy'] == 'human'

        os.remove(csv_name)
        os.remove(full_file_name_zip)
