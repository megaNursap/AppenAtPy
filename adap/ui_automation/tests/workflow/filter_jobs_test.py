"""
Workflow canvas tests
"""
import time

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import create_screenshot

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


def create_job_with_tag(api_key, tags):
    job = Builder(api_key)
    res = job.create_job()
    job_id = res.json_response.get('id')
    for t in tags:
        job.add_job_tag(t)
    return job_id


@pytest.mark.fed_ui_smoke_wf
def test_filter_jobs_by_tag(app_test):
    """
    As a customer, I see an option to search by job or model in the operator panel
    As a customer, I can filter my jobs by tag
    """
    job_tag1 = create_job_with_tag(API_KEY, ["tag1"])
    job_tag2 = create_job_with_tag(API_KEY, ["tag2"])
    job_tag_1_2 = create_job_with_tag(API_KEY, ["tag1", "tag2"])
    assert job_tag1 and job_tag2 and job_tag_1_2, "Test data (jobs) has not been created!!!"

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()

    app_test.workflow.fill_up_wf_name(wf_name)
    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Canvas")

    app_test.verification.text_present_on_page("Add Operator")
    time.sleep(3)
    app_test.workflow.select_operator.filter_jobs_by_tag("tag1")
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_tag1)
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_tag_1_2)

    app_test.workflow.select_operator.filter_jobs_by_tag("tag2")
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_tag1, mode=False)
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_tag2)
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_tag_1_2)


def test_filter_jobs_by_project(app_test):
    """
    As a customer, I can filter my jobs by project
    """
    job_id = create_job_with_tag(API_KEY, [])
    job_id2 = create_job_with_tag(API_KEY, [])

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()

    app_test.job.search_jobs_by_id(job_id)
    app_test.job.add_job_to_project(job_id, "test")

    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()

    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)
    app_test.navigation.click_link("Canvas")

    app_test.verification.text_present_on_page("Add Operator")
    time.sleep(3)
    app_test.workflow.select_operator.filter_jobs_by_project("test")
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_id2, mode=False)
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job_id)