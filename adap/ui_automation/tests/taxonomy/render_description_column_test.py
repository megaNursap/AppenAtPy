"""
 https://appen.spiraservice.net/5/TestCase/4688.aspx
This test covers rendering of colum description in Taxonomy tool
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
taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")

ITEMS_TEXT_DATA = {
    1: ['DAIRY', 'Cheese', 'Soft, medium-soft'],
    2: ['VEGETABLE', 'Red and orange vegetables', 'Tomato']
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
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    return job_id


def test_render_description_on_column(app, set_job):
    """
       Verify that description rendering in a column
    """
    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)

    actual_description_list = read_csv_file(taxonomy_csv_file, 'description')

    app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[1])
    expected_description = app.taxonomy.get_description_of_column()
    assert expected_description in actual_description_list, f"The actual: {expected_description} not the same as " \
                                                            f"expected: {actual_description_list} "

    app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[2])
    expected_description = app.taxonomy.get_description_of_column()
    assert expected_description in actual_description_list, f"The actual: {expected_description} not the same as " \
                                                            f"expected: {actual_description_list} "
