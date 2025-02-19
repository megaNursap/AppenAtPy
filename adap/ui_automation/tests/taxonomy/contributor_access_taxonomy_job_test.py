import time

from allure_commons.types import AttachmentType

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.builder import Builder as JobAPI

pytestmark = [pytest.mark.regression_taxonomy]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
ITEMS_TEXT_DATA = {
    1: ['DAIRY', 'Milk', 'Goat'],
    2: ['FAT', 'Trans', 'Frozen pizza'],
    3: ['DAIRY', 'Cheese', 'Medium'],
    4: ['VEGETABLE', 'Dark green vegetables', 'Beet'],
    5: ['PROTEIN FOODS', 'Meat', 'Beef, pork']
}


@pytest.fixture(scope="module")
def taxonomy_job(app):
    app.user.login_as_customer(USER_EMAIL, PASSWORD)
    job = Builder(API_KEY)
    job.create_job_with_cml(data.taxonomy_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/taxonomy/data_for_taxonomy.csv")
    app.job.data.upload_file(data_file)
    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Taxonomies")

    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")

    taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")
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
    app.user.logout()

    return job_id


def test_contributor_access_to_taxonomy_job(app, taxonomy_job):
    job_link = generate_job_link(taxonomy_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)

    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)

    for k, v in ITEMS_TEXT_DATA.items():
        app.text_annotation.activate_iframe_by_index(k - 1)
        actual_selected_list = app.taxonomy.select_taxonomy_item(v)
        app.text_annotation.deactivate_iframe()
        time.sleep(2)
        expected_selected_list = ' > '.join(v)
        allure.attach(app.driver.get_screenshot_as_png(), name="Screenshot", attachment_type=AttachmentType.PNG)
        assert actual_selected_list == expected_selected_list, f"The actual: {actual_selected_list} not the same as " \
                                                               f"expected: {expected_selected_list} "
    app.text_annotation.submit_page()
    app.verification.text_present_on_page('There is no work currently available in this task.')
