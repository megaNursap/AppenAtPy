"""
https://appen.spiraservice.net/5/TestCase/4685.aspx
This test covers  cases to select/deselect taxonomy items
"""
import time

import pytest

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data


pytestmark = [pytest.mark.regression_taxonomy]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

ITEMS_TEXT_DATA = {
    1: ['DAIRY', 'Milk', 'Goat'],
    2: ['FAT', 'Trans', 'Frozen pizza'],
    3: ['DAIRY', 'Cheese', 'Medium'],
    4: ['VEGETABLE', 'Dark green vegetables', 'Beet'],
    5: ['PROTEIN FOODS', 'Meat', 'Beef, pork']
}


@pytest.fixture(scope="module")
def set_job(app):
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

    return job_id


def test_taxonomy_select_deselect_item(app, set_job):
    """
       Verify possibility select and deselect taxonomy items
    """
    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)

    actual_selected_list = app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[1])
    expected_selected_list = ' > '.join(ITEMS_TEXT_DATA[1])
    assert actual_selected_list == expected_selected_list, f"The actual: {actual_selected_list} not the same as " \
                                                           f"expected: {expected_selected_list} "
    app.taxonomy.deselect_taxonomy_item()
    app.verification.text_present_on_page(expected_selected_list, False)





