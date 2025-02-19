"""
https://appen.atlassian.net/browse/QED-2238
https://appen.atlassian.net/browse/AT-3214
https://appen.atlassian.net/browse/AT-3478
https://appen.atlassian.net/browse/AT-3578
https://appen.atlassian.net/browse/AT-3579
This test covers a simple end to end flow for mlait image rotation feature:
1. create image transcription job enables image rotation via cml
2. select host channel if it is fed env.
3. launch the job
4. check hot keys to rotate image in preview mode
5. contributor check image rotation feature and submit judgments
6. download full and aggregate report
7. leverage full report in above steps to create peer review job, check negative case-data has rotation, but cml does not have rotation tag
7. update cml to include rotation tag, check positive case for image rotation peer review job
"""
import time
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.services_config.annotation import create_peer_review_job
from selenium.webdriver.common.keys import Keys
from adap.api_automation.services_config.builder import Builder
pytestmark = [pytest.mark.regression_image_transcription, pytest.mark.regression_image_rotation]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_transcription/receipts.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
WORKER_ID = get_user_worker_id('test_contributor_task')


@pytest.fixture(scope="module")
def mlait_image_rotation_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_transcription_image_rotation_cml,
                                        job_title="Testing mlait image rotation job", units_per_page=2)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')
    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")

    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job = Builder(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    return job_id


@pytest.mark.dependency()
def test_mlait_image_rotation_hotkeys(app, mlait_image_rotation_job):
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.image_transcription.activate_iframe_by_index(0)
    app.image_transcription.click_image_rotation_button()
    app.image_transcription.image_rotation_slider_bar_available()
    assert app.image_transcription.get_image_rotation_degree() == "0°"
    app.image_transcription.move_image_rotation_knob()
    degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    app.image_transcription.combine_hotkey(Keys.COMMAND, ",")
    left_one_degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    assert left_one_degree == degree - 1
    app.image_transcription.combine_hotkey(Keys.COMMAND, ".")
    right_one_degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    assert right_one_degree == left_one_degree + 1
    app.image_transcription.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ",")
    left_fifteen_degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    assert left_fifteen_degree == right_one_degree - 15
    app.image_transcription.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ".")
    right_fifteen_degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    assert right_fifteen_degree == left_fifteen_degree + 15
    app.image_transcription.combine_hotkey(Keys.COMMAND, "z")
    undo_degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    assert undo_degree == left_fifteen_degree
    app.image_transcription.combine_hotkey(Keys.COMMAND, "y")
    redo_degree = int(app.image_transcription.get_image_rotation_degree()[:-1])
    assert redo_degree == right_fifteen_degree
    app.image_transcription.deactivate_iframe()
    app.driver.close()
    app.navigation.switch_to_window(job_window)
    app.user.logout()


@pytest.mark.dependency(depends=["test_mlait_image_rotation_hotkeys"])
def test_mlait_image_rotation_submit_judgments(app, mlait_image_rotation_job):
    job_link = generate_job_link(mlait_image_rotation_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    # app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link, close_guide=False)
    coordinates = [[200, 200, 100, 100], [350, 350, 100, 100]]
    for i, val in enumerate(coordinates):
        app.image_transcription.activate_iframe_by_index(i)
        try:
            app.image_transcription.draw_box_with_coordination(*val)
        except Exception as r:
            app.image_transcription.draw_box_with_coordination(10, 10, 20, 20)
        try:
            app.image_transcription.save_prediction()
        except Exception as r:
            app.image_transcription.input_transcription_text('no ocr text')
        app.image_transcription.click_image_rotation_button()
        app.image_transcription.image_rotation_slider_bar_available()
        assert app.image_transcription.get_image_rotation_degree() == "0°"
        app.image_transcription.move_image_rotation_knob()
        assert int(app.image_transcription.get_image_rotation_degree()[:-1]) > 180
        app.image_transcription.close_image_rotation_bar()
        app.image_transcription.image_rotation_slider_bar_available(is_not=False)
        app.image_transcription.deactivate_iframe()
        time.sleep(2)

    app.image_transcription.submit_page()
    time.sleep(5)
    app.user.task.logout()


@pytest.mark.dependency(depends=["test_mlait_image_rotation_submit_judgments"])
def test_mlait_image_rotation_download_reports(app_test, mlait_image_rotation_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(mlait_image_rotation_job)

    for report_type in ['Full', 'Aggregated']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, mlait_image_rotation_job)
        file_name_zip = "/" + app_test.job.results.get_file_report_name(mlait_image_rotation_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'label_this' in _df.columns
        assert 'image_url' in _df.columns

        random_row = random.randint(0, _df.shape[0] - 1)
        annotation_url = _df['label_this'][random_row]
        # import requests
        # annotation_res = requests.get(annotation_url)
        # assert annotation_res.status_code == 200
        # print("json value is:", annotation_res.json())
        # assert annotation_res.json().get("ableToAnnotate")
        # assert int(annotation_res.json().get("imageRotation")) > 180
        # assert len(annotation_res.json().get("annotation")) > 0

        os.remove(csv_name)
        os.remove(full_file_name_zip)


@pytest.mark.dependency(depends=["test_mlait_image_rotation_download_reports"])
@allure.issue("https://appen.atlassian.net/browse/AT-6374", "Bug AT-6374")
def test_mlait_image_rotation_peer_review_job(tmpdir_factory, app_test, mlait_image_rotation_job):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, mlait_image_rotation_job, data.image_transcription_peer_review_cml)
    app_test.user.customer.open_home_page()
    login = app_test.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app_test.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)
    app_test.job.open_tab('DESIGN')
    app_test.navigation.click_link('Manage Image Transcription Ontology')

    ontology_file = get_data_file("/image_transcription/ontology.json")
    app_test.ontology.upload_ontology(ontology_file, rebrand=True)
    app_test.verification.text_present_on_page("Classes Created")

    app_test.job.preview_job()
    time.sleep(8)
    # https://appen.atlassian.net/browse/AT-3478
    app_test.image_transcription.activate_iframe_by_index(0)
    app_test.verification.text_present_on_page('Tool was loaded with invalid review-data')
    app_test.image_transcription.deactivate_iframe()
    # update cml and check regular peer review job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.image_transcription_rotation_peer_review_cml
        }
    }

    job = Builder(API_KEY)
    job.job_id = job_id
    job.update_job(payload=updated_payload)

    app_test.navigation.refresh_page()
    app_test.image_transcription.activate_iframe_by_index(0)
    app_test.image_transcription.click_image_rotation_button()
    app_test.image_transcription.image_rotation_slider_bar_available()
    assert int(app_test.image_transcription.get_image_rotation_degree()[:-1]) > 180
    app_test.image_transcription.close_image_rotation_bar()
    app_test.image_transcription.image_rotation_slider_bar_available(is_not=False)
    app_test.image_transcription.deactivate_iframe()
