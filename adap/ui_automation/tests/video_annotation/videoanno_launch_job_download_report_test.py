"""
This test covers a simple end to end flow including below items:
1. create job via cml
2. select host channel if it is fed env.
3. launch the job
4. do judgments via internal link
5. download full and aggregate report
note, add require-views="false" to CML so that you can skip review each frame
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_annotation import create_video_annotation_job
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = pytest.mark.regression_video_annotation

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/video_annotation/video_withoutannotation.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_video_annotation_job(app, API_KEY, data.video_annotation_object_tracking_cml, USER_EMAIL, PASSWORD, DATA_FILE)
    app.job.open_action("Settings")
    app.navigation.click_link("Pay")
    app.job.launch.enter_row_per_page_FP(1)
    app.navigation.click_link('Save')
    return job_id


@pytest.mark.dependency()
def test_submit_judgements_videoanno(app, tx_job):
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(10)
    app.video_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.video_annotation.draw_box()
    shape_counts = app.video_annotation.get_sidepanel_shapelabel_count()
    app.video_annotation.click_save_button()
    assert shape_counts > 0
    app.navigation.refresh_page()
    time.sleep(10)
    app.video_annotation.activate_iframe_by_index(0)
    app.video_annotation.click_classes_or_objects_tab('OBJECTS')
    assert shape_counts == app.video_annotation.get_sidepanel_shapelabel_count()
    app.video_annotation.deactivate_iframe()
    app.video_annotation.submit_page()
    time.sleep(10)

    for i in range(4):
        app.video_annotation.activate_iframe_by_index(0)
        time.sleep(2)
        app.video_annotation.draw_box()
        app.video_annotation.deactivate_iframe()
        app.video_annotation.submit_page()
        time.sleep(10)


@allure.issue("https://appen.atlassian.net/browse/ADAP-523", "BUG ADAP-523")
@pytest.mark.dependency(depends=["test_submit_judgements_videoanno"])
def test_download_reports_videoanno(app, tx_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    for report_type in ['Full', 'Aggregated']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, tx_job)
        file_name_zip = "/" + app.job.results.get_file_report_name(tx_job, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'video_annotation' in _df.columns
        assert 'video_url' in _df.columns
        os.remove(csv_name)
        os.remove(full_file_name_zip)


@pytest.mark.dependency(depends=["test_download_reports_videoanno"])
def test_frame_rotation_peer_review_job_error_tile(tmpdir_factory, app, tx_job):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, tx_job, data.video_annotation_frame_rotation_peer_review_cml)
    app.user.customer.open_home_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')

    ontology_file = get_data_file("/video_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    # app.verification.text_present_on_page("2/1000 Classes Created")
    time.sleep(3)

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()
    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    app.job.preview_job()
    time.sleep(10)

    app.video_annotation.activate_iframe_by_index(0)
    time.sleep(5)
    app.video_annotation.click_image_rotation_button()
    app.video_annotation.image_rotation_slider_bar_available()
    assert app.video_annotation.get_image_rotation_degree() == "0°"
    app.video_annotation.close_image_rotation_bar()
    app.video_annotation.image_rotation_slider_bar_available(is_not=False)
    app.video_annotation.deactivate_iframe()
