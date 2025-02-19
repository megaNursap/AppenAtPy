"""
https://appen.atlassian.net/browse/QED-2031
This test covers a simple end to end flow for image rotation feature:
1. create job enables image rotation via cml
2. select host channel if it is fed env.
3. launch the job
4. contributor check image rotation feature and submit judgments
5. download full and aggregate report
6. check unit page image rotation feature
7. create peer review job and check preview mode test validation
"""
import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.ui_automation.services_config.annotation import create_peer_review_job
from selenium.webdriver.common.keys import Keys
from adap.api_automation.services_config.builder import Builder

pytestmark = [pytest.mark.regression_image_annotations, pytest.mark.regression_image_rotation]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
WORKER_ID = get_user_worker_id('test_contributor_task')


@pytest.fixture(scope="module")
def image_rotation_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_rotation_cml,
                                        job_title="Testing image rotation feature job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")
    time.sleep(3)
    # need to select hosted channel if it is fed env
    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_image_rotation_hotkeys(app, image_rotation_job):
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.image_annotation.activate_iframe_by_index(0)
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 3})
    app.image_annotation.annotate_image(mode='ontology', value={"dog": 3})
    app.image_annotation.click_image_rotation_button()
    app.image_annotation.image_rotation_slider_bar_available()
    assert app.image_annotation.get_image_rotation_degree() == "0°"
    app.image_annotation.move_image_rotation_knob()
    degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    app.image_annotation.combine_hotkey(Keys.COMMAND, ",")
    left_one_degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    assert left_one_degree == degree - 1
    app.image_annotation.combine_hotkey(Keys.COMMAND, ".")
    right_one_degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    assert right_one_degree == left_one_degree + 1
    app.image_annotation.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ",")
    left_fifteen_degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    assert left_fifteen_degree == right_one_degree - 15
    app.image_annotation.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ".")
    right_fifteen_degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    assert right_fifteen_degree == left_fifteen_degree + 15
    app.image_annotation.combine_hotkey(Keys.COMMAND, "z")
    undo_degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    assert undo_degree == left_fifteen_degree
    app.image_annotation.combine_hotkey(Keys.COMMAND, "y")
    redo_degree = int(app.image_annotation.get_image_rotation_degree()[:-1])
    assert redo_degree == right_fifteen_degree
    app.image_annotation.deactivate_iframe()
    app.driver.close()
    app.navigation.switch_to_window(job_window)
    app.user.logout()


@pytest.mark.dependency(depends=["test_image_rotation_hotkeys"])
def test_image_rotation_submit_judgments(app, image_rotation_job):
    job_link = generate_job_link(image_rotation_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    for i in range(2):
        app.image_annotation.activate_iframe_by_index(i)
        app.image_annotation.annotate_image(mode='ontology', value={"cat": 3})
        app.image_annotation.annotate_image(mode='ontology', value={"dog": 3})
        app.image_annotation.click_image_rotation_button()
        app.image_annotation.image_rotation_slider_bar_available()
        assert app.image_annotation.get_image_rotation_degree() == "0°"
        app.image_annotation.move_image_rotation_knob()
        assert int(app.image_annotation.get_image_rotation_degree()[:-1]) > 180
        app.image_annotation.close_image_rotation_bar()
        app.image_annotation.image_rotation_slider_bar_available(is_not=False)
        app.image_annotation.deactivate_iframe()

    app.image_annotation.submit_page()
    time.sleep(3)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()


@pytest.mark.dependency(depends=["test_image_rotation_submit_judgments"])
def test_image_rotation_download_reports(app, image_rotation_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(image_rotation_job)

    # for report_type in ['Full', 'Aggregated']:
    for report_type in ['Full']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, image_rotation_job)
        file_name_zip = "/" + app.job.results.get_file_report_name(image_rotation_job, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'annotation' in _df.columns
        assert 'image_url' in _df.columns

        # if report_type == 'Full':
        #     random_row = random.randint(0, _df.shape[0] - 1)
            # annotation_url = _df['annotation'][random_row]
            # import requests
            # annotation_res = requests.get(annotation_url)
            # assert annotation_res.status_code == 200
            # print("json value is:", annotation_res.json())
            # assert annotation_res.json().get("ableToAnnotate")
            # assert int(annotation_res.json().get("imageRotation")) > 180
            # assert len(annotation_res.json().get("annotation")) > 0
            # annotation_url = json.loads(_df['annotation'][random_row]).get("url")

        # app.navigation.click_link("Force regenerate this report")
        # progressbar = find_element(app.driver, "//div[@id='progressbar']")
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


@pytest.mark.dependency(depends=["test_image_rotation_download_reports"])
def test_image_rotation_units_page(app, image_rotation_job):
    app.user.customer.open_home_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(image_rotation_job)
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('judgable')
    first_unit = units['unit id'][0]
    app.job.data.open_unit_by_id(first_unit)
    app.image_annotation.data_unit.activate_iframe_on_unit_page()
    app.image_annotation.data_unit.find_a_judgment_dropdown_button_is_displayed()
    # do not select contributor from dropdown, click image rotation button, it will show 0°
    app.image_annotation.click_image_rotation_button()
    app.image_annotation.image_rotation_slider_bar_available()
    assert app.image_annotation.get_image_rotation_degree() == "0°"

    app.image_annotation.data_unit.click_find_a_judgment_dropdown_button()
    app.image_annotation.data_unit.click_worker_id_from_dropdown_list(WORKER_ID)
    assert int(app.image_annotation.get_image_rotation_degree()[:-1]) > 180


@pytest.mark.dependency(depends=["test_image_rotation_units_page"])
def test_image_rotation_peer_review_job(tmpdir_factory, app, image_rotation_job):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, image_rotation_job, data.image_rotation_peer_review_error_title)
    app.user.customer.open_home_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='2']")

    app.job.preview_job()
    time.sleep(8)
    app.image_annotation.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable')
    app.verification.text_present_on_page('Image rotation is required')
    app.image_annotation.deactivate_iframe()

    # update cml and check regular peer review job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.image_rotation_peer_review_cml
        }
    }
    job = Builder(API_KEY)
    job.job_id = job_id
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.video_annotation.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable', is_not=False)
    app.verification.text_present_on_page('Image rotation is required', is_not=False)
    app.image_annotation.click_image_rotation_button()
    app.image_annotation.image_rotation_slider_bar_available()
    assert int(app.image_annotation.get_image_rotation_degree()[:-1]) > 180
    app.image_annotation.close_image_rotation_bar()
    app.image_annotation.image_rotation_slider_bar_available(is_not=False)
    app.image_annotation.deactivate_iframe()

    app.image_annotation.activate_iframe_by_index(1)
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 3})
    app.image_annotation.annotate_image(mode='ontology', value={"dog": 3})
    app.image_annotation.image_rotation_slider_bar_available(is_not=False)
    app.image_annotation.deactivate_iframe()

    app.image_annotation.submit_test_validators()
    time.sleep(3)
    app.verification.text_present_on_page('Validation succeeded')