import time

import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data

pytestmark = pytest.mark.regression_taxonomy

API_KEY = get_user_api_key('test_ui_account')
USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")

ITEMS_TEXT_DATA = {
    1: ['DAIRY', 'Milk', 'Goat'],
    2: ['FAT', 'Trans', 'Frozen pizza'],
    3: ['DAIRY', 'Cheese', 'Medium'],
    4: ['VEGETABLE', 'Dark green vegetables', 'Beet'],
    5: ['PROTEIN FOODS', 'Meat', 'Beef, pork'],
    6: ['FAT', 'Trans', 'Frozen pizza'],
    7: ['DRINK', 'Natural Beverages', 'Kombucha'],
    8: ['VEGETABLE', 'Red and orange vegetables', 'Carrot']
}


@pytest.fixture(scope="module")
def set_job(app):
    app.user.login_as_customer(USER_EMAIL, PASSWORD)
    job = Builder(API_KEY)
    job.create_job_with_cml(data.taxonomy_cml)
    job_id = job.job_id
    # job_id = 1960452
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/taxonomy/data_for_taxonomy.csv")
    app.job.data.upload_file(data_file)
    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Taxonomies")
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    return job_id


def test_create_tq_for_taxonomy(app, set_job):
    """
    Customer is able to create test question for Taxonomy
    """
    app.job.open_tab('DESIGN')
    app.navigation.click_link("Next: Create Test Questions")
    app.user.close_guide()

    app.job.quality.create_random_tqs()
    tq_num = 0
    for i in range(0, 4):
        tq_num = i + 1
        app.job.quality.switch_to_tq_iframe()
        app.annotation.activate_iframe_by_index(0)
        app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[i + 1])
        app.annotation.deactivate_iframe()
        app.job.quality.switch_to_tq_iframe()
        app.navigation.click_link("Save & Create Another")

    time.sleep(2)
    app.navigation.refresh_page()
    app.job.open_tab("DATA")

    tq_units = app.job.data.find_all_units_with_status("golden")
    assert tq_num == len(tq_units), "%s rows were found, expected - %s" % (len(tq_units), tq_num)


def test_upload_tq_for_taxonomy(app, set_job):
    app.job.open_tab("DATA")
    tq_units = app.job.data.find_all_units_with_status("golden")

    app.navigation.click_link('Add More Data')

    tq_data_file = get_data_file("/taxonomy/tq_taxonomy_report.csv")
    app.job.data.upload_file(tq_data_file)
    app.navigation.click_link('Proceed Anyway')
    app.verification.wait_untill_text_present_on_the_page('Convert Uploaded Test Questions', 10)
    app.navigation.click_link('Convert Uploaded Test Questions')
    app.job.open_tab('QUALITY')
    num_tq = app.job.quality.get_number_of_active_tq()
    assert len(tq_units) + 4 == num_tq
