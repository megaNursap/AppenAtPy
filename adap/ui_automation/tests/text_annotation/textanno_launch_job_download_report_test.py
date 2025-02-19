"""
This test covers a simple end to end flow including below items:
1. create job via cml
2. select host channel if it is fed env.
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

pytestmark = [pytest.mark.regression_text_annotation,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/text_annotation/multiplelinesdata.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    """
    Create Text Annotation job with 5 rows, upload ontology and launch job
    """
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.text_annotation_cml,
                                        job_title="Testing text annotation tool", units_per_page=5)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Annotation Ontology')

    ontology_file = get_data_file("/text_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='3']")
    time.sleep(3)

    app.job.open_action("Settings")
    # need to select hosted channel if it is fed env
    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
        app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
        app.navigation.click_link('Save')
    time.sleep(2)

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_submit_judgements_textanno(app, tx_job):
    """
    Submit judgments without annotating all rows and check for validation error
    Submit judgments with annotations for all rows to pass validation
    """
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    app.text_annotation.activate_iframe_by_index(0)
    # add span
    app.text_annotation.click_token('Sebastian')
    app.text_annotation.click_span('name')
    app.text_annotation.deactivate_iframe()
    app.text_annotation.submit_page()
    time.sleep(5)
    app.verification.text_present_on_page("Check below for errors!")

    for i in range(1, 5):
        app.text_annotation.activate_iframe_by_index(i)
        app.text_annotation.click_token('Google')
        app.text_annotation.click_span('company')
        app.text_annotation.deactivate_iframe()
        time.sleep(2)

    app.text_annotation.submit_page()
    time.sleep(2)
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_submit_judgements_textanno"])
def test_download_reports_textanno(app_test, tx_job):
    """
    Verify user can download full and aggregated reports
    Verify output report has annotations column
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)

    for report_type in ['Full', 'Aggregated']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, tx_job)
        file_name_zip = "/" + app_test.job.results.get_file_report_name(tx_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'my_annotations' in _df.columns
        assert 'text' in _df.columns
        os.remove(csv_name)
        os.remove(full_file_name_zip)