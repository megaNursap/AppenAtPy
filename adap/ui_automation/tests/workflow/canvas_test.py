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


def test_remove_first_operator(app_test):
    """
     As a customer, if I remove an operator, all operators and routing below will also be deleted
    """
    job_id = create_job_with_tag(API_KEY, [])
    job2_id = create_job_with_tag(API_KEY, [])

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()

    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Canvas")
    app_test.workflow.select_operator.search_job_into_side_bar(job_id)
    app_test.workflow.select_operator.connect_job_to_wf(job_id, 580, 370)

    # connect second job
    app_test.workflow.click_on_canvas_coordinates(app_test.workflow.x_add_first_job, app_test.workflow.y_add_first_job)
    app_test.workflow.select_operator.search_job_into_side_bar(job2_id)
    app_test.workflow.select_operator.connect_job_to_wf(job2_id, 580, 570)

    app_test.workflow.routing.select_routing_method("Route All Rows")
    app_test.navigation.click_link("Save & Close")
    time.sleep(3)

    # delete 1st job
    app_test.workflow.click_on_canvas_coordinates(app_test.workflow.x_add_first_job+100, app_test.workflow.y_add_first_job-100, mode='canvas')
    app_test.verification.text_present_on_page("Remove Operator")
    app_test.navigation.click_link("Delete")

    time.sleep(10)
    app_test.verification.text_present_on_page("Add Operator")


def test_user_is_not_able_add_launched_job_to_wf(app_test):
    """
    As a customer, only jobs that are in an unlaunched state can be added to a workflow
    """
    job = Builder(API_KEY)
    job.create_simple_job_with_test_questions()

    job.launch_job()
    job.wait_until_status("running", max_time=60 * 5)

    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()

    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()

    app_test.workflow.fill_up_wf_name(wf_name)
    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Canvas")

    app_test.workflow.select_operator.search_job_into_side_bar(job.job_id)
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job.job_id)
    app_test.workflow.select_operator.verify_job_status_on_the_list(job.job_id, "Currently Unavailable")

    job.pause_job()
    job.wait_until_status("paused", max_time=60 * 5)

    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'paused' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "paused")

    app_test.navigation.refresh_page()

    app_test.workflow.select_operator.search_job_into_side_bar(job.job_id)
    app_test.workflow.select_operator.verify_job_is_present_on_the_list(job.job_id)
    app_test.workflow.select_operator.verify_job_status_on_the_list(job.job_id, "Currently Unavailable")


def test_job_can_be_linked_to_one_wf_only(app_test):
    """
    As a customer, I should see a "workflows" indicator on any job associated to a workflow
    As a customer, I cannot add the same job to multiple workflows or twice within the same workflow
    """
    _job_id1 = create_job_with_tag(API_KEY, [])
    time.sleep(5)
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()

    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name1 = generate_random_wf_name()

    app_test.workflow.fill_up_wf_name(wf_name1)
    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Canvas")

    app_test.workflow.select_operator.search_job_into_side_bar(_job_id1)
    app_test.workflow.select_operator.connect_job_to_wf(_job_id1, 580, 370)
    app_test.verification.text_present_on_page("Add Operator", is_not=False)

    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name2 = generate_random_wf_name()

    app_test.workflow.fill_up_wf_name(wf_name2)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Canvas")

    app_test.workflow.select_operator.search_job_into_side_bar(_job_id1)
    app_test.workflow.select_operator.verify_job_status_on_the_list(_job_id1, "Currently Unavailable")

    app_test.mainMenu.jobs_page()
    app_test.job.search_jobs_by_id(_job_id1)

    wf_indicator = app_test.job.get_wf_indicator_for_job(_job_id1)
    assert wf_indicator is not None, "Job %s is associated with WF"
    assert wf_indicator['wf_name'] == "Workflow: "+wf_name1
