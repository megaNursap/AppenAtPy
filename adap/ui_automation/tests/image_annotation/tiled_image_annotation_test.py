"""
https://appen.atlassian.net/browse/QED-2576
https://appen.atlassian.net/browse/QED-2578
https://appen.atlassian.net/browse/QED-2579
https://appen.atlassian.net/browse/QED-2580
This test covers a simple end to end flow for tile image annotation including below items:
1. create tiled image annotation job via cml
2. upload ontology file
3. launch the job
4. do judgments via internal link
5. download full and aggregate report
"""
import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_annotation]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/tiled-image-layerOpt.csv")


@pytest.fixture(scope="module")
def tiled_image_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.tile_image_annotation_cml,
                                        job_title="Testing tiled image annotation job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Tiled Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/tiled-image-ontology.json")
    app.ontology.upload_ontology(ontology_file)
    # app.verification.text_present_on_page("2/1000 Classes Created")
    time.sleep(3)
    # need to select hosted channel if it is fed env
    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.driver.find_elements('xpath',"//label[@class='b-Checkbox__icon']")[1].click()
        time.sleep(1)
        app.navigation.click_link('Ok')
        time.sleep(1)
        app.navigation.click_link('Save')

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_submit_judgements_tiled_image_annotation(app, tiled_image_job):
    job_link = generate_job_link(tiled_image_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)
    for i in range(0, 2):
            app.image_annotation.activate_iframe_by_index(i)
            app.image_annotation.click_toolbar_button('polygons')
            app.image_annotation.click_toolbar_button('boxes')
            for j in range(0, 2):
                app.image_annotation.draw_box_for_tile_image()
            app.image_annotation.deactivate_iframe()
            time.sleep(2)
    app.image_annotation.submit_page()
    time.sleep(10)


@pytest.mark.dependency(depends=["test_submit_judgements_tiled_image_annotation"])
@allure.issue("https://appen.atlassian.net/browse/ADAP-3571", "BUG ADAP-3571")
def test_download_report_tiled_image_annotation(app, tiled_image_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tiled_image_job)
    for report_type in ['Full', 'Aggregated']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, tiled_image_job)
        file_name_zip = "/" + app.job.results.get_file_report_name(tiled_image_job, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'annotation' in _df.columns
        assert 'demotiledimagery_gold' in _df.columns
        assert 'demotiledimagery_gold_reason' in _df.columns
        assert 'canvas_options' in _df.columns
        os.remove(csv_name)
        os.remove(full_file_name_zip)
