"""
https://appen.spiraservice.net/5/TestCase/4793.aspx
This test covers  cases for peer review Job
"""
import time

import pytest
from allure_commons.types import AttachmentType

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = pytest.mark.regression_taxonomy

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')

taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")
data_file = get_data_file("/taxonomy/taxonomy_review_data.csv")
expected_result_selected_list = read_csv_file(data_file, 'my_taxonomy')
list_of_items = []


@pytest.fixture(scope="module")
def set_job(app):
    app.user.login_as_customer(USER_EMAIL, PASSWORD)
    job = Builder(API_KEY)
    job.create_job_with_cml(data.taxonomy_peer_review)
    job_id = job.job_id

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    app.job.data.upload_file(data_file)
    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Taxonomies")
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    app.job.open_action("Settings")

    time.sleep(2)
    app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
    app.navigation.click_link('Save')

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    res = job.get_json_job_status()
    res.assert_response_status(200)

    return job_id

def test_tool_work_with_correct_task_type(app, set_job):
    app.job.preview_job()
    time.sleep(4)

    app.annotation.activate_iframe_by_index(0)
    app.verification.wait_untill_text_present_on_the_page("DAIRY", 10)
    assert len(app.taxonomy.get_taxonomy_selected_list()) == len(
        expected_result_selected_list[0].split('\n')), "The length of actual taxonomy selected " \
                                                       "item not the same as expected "
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])
    app.user.logout()


@pytest.mark.dependency()
def test_contributor_access_to_taxonomy_peer_review_job(app, set_job):
    job_link = generate_job_link(set_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)

    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)

    app.annotation.activate_iframe_by_index(0)
    app.taxonomy.select_taxonomy_item(['FRUIT', 'Pomes', 'Apple'])
    app.annotation.deactivate_iframe()

    app.annotation.activate_iframe_by_index(3)
    app.taxonomy.select_taxonomy_item(['FRUIT', 'Drupes', 'Cherry'])
    app.annotation.deactivate_iframe()
    expected_result_selected_list.reverse()

    for index in range(0, len(expected_result_selected_list)):
        app.annotation.activate_iframe_by_index(index)
        actual_selected_list_length = len(app.taxonomy.get_taxonomy_selected_list())
        expected_selected_list_length = len(expected_result_selected_list[index].split('\n'))
        allure.attach(app.driver.get_screenshot_as_png(), name="Screenshot", attachment_type=AttachmentType.PNG)
        if index == 0 or index == 3:
            assert actual_selected_list_length == expected_selected_list_length + 1, "The length of actual taxonomy selected " \
                                                                                     "item not the same as expected "
        else:

            assert actual_selected_list_length == expected_selected_list_length, "The length of actual taxonomy selected " \
                                                                                 "item not the same as expected "
        list_of_items.append(app.taxonomy.get_taxonomy_selected_list())
        app.annotation.deactivate_iframe()
        time.sleep(2)

    app.text_annotation.submit_page()
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.logout()


@pytest.mark.dependency(depends=["test_contributor_access_to_taxonomy_peer_review_job"])
def test_judgment_loading_unit_page(app, set_job):
    """
    Verify requestor can see submitted judgment on unit page
    """
    app.user.customer.open_home_page()
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job = Builder(API_KEY)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(set_job)

    app.job.open_tab("DATA")

    job_row = job.get_rows_in_job(set_job)
    list_job_row = list(job_row.json_response.keys())
    app.navigation.click_link(list_job_row[len(list_job_row) - 1])
    app.annotation.activate_iframe_by_name("unit_page")
    app.annotation.activate_iframe_by_index(1)
    list_an = app.taxonomy.taxonomy_answers(list_job_row[len(list_job_row) - 1])
    assert list_an in list_of_items, "In the unit page the answer not displayed"
