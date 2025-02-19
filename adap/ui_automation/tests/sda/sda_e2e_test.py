"""
This end to end test covers SDA for S3, GCP and Azure.
1. We create job uploading corresponding data and using correct CML
2. Launch the job.
3. Preview job and do test validation.
4. Submit the judgments.
5. Download the report to make sure correct number of records in the report.
"""
import pytest
import time
from adap.ui_automation.services_config.sda import create_sda_azure_job, create_sda_s3_job, create_sda_gcp_job
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.utils.data_util import *

USER_EMAIL = get_user_email('test_sda')
PASSWORD = get_user_password('test_sda')
API_KEY = get_user_api_key('test_sda')

mark_only_envs = pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
pytestmark = [pytest.mark.sdas, mark_only_envs]

job_ids = []


@pytest.mark.parametrize(
    'team',
    [
        's3',
        'azure',
        'gcp'
    ]
)
def test_sda_create_job_and_submit_judgments(app, team):
    if team == 'azure' and pytest.env == 'integration':
        pytest.skip("No test data setup for Azure SDA in Integration")

    app.sda.sign_in_as(team)
    app.navigation.close_tour_guide_popup()
    if team == 's3':
        job_id = create_sda_s3_job()
        job_ids.append(job_id)
    if team == 'gcp':
        job_id = create_sda_gcp_job()
        job_ids.append(job_id)
    #  No full report for azure, so we do not add it to job_ids to check report
    if team == 'azure':
        job_id = create_sda_azure_job()

    # preview job and do test validation
    app.user.customer.open_home_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    app.image_annotation.activate_iframe_by_index(0)
    app.image_annotation.annotate_image(mode='ontology', value={"Boat": 3})
    app.image_annotation.deactivate_iframe()
    app.image_annotation.submit_test_validators()
    app.verification.text_present_on_page('Validation succeeded')
    app.driver.close()
    app.navigation.switch_to_window(job_window)

    # submit judgments on SDA jobs
    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)
    for i in range(0, 3):
        app.image_annotation.activate_iframe_by_index(0)
        app.image_annotation.annotate_image(mode='ontology', value={"Boat": 3})
        app.image_annotation.deactivate_iframe()
        app.image_annotation.submit_page()
        time.sleep(2)
    time.sleep(3)


def test_download_sda_reports(app_test):
    """
    Verify user can download sda report and see the correct number of records inside the report
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    for job_id in job_ids:
        app_test.mainMenu.jobs_page()
        app_test.job.open_job_with_id(job_id)
        for report_type in ['Full']:
            app_test.job.open_tab("RESULTS")
            app_test.job.results.download_report(report_type, job_id)
            file_name_zip = "/" + app_test.job.results.get_file_report_name(job_id, report_type)
            full_file_name_zip = app_test.temp_path_file + file_name_zip

            unzip_file(full_file_name_zip)
            csv_name = str(full_file_name_zip)[:-4]

            _df = pd.read_csv(csv_name)
            assert 'annotation' in _df.columns
            assert 'image_url' in _df.columns
            assert _df.shape[0] == 3
            os.remove(csv_name)
            os.remove(full_file_name_zip)