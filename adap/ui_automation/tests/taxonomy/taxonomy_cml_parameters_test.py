"""
https://appen.spiraservice.net/5/TestCase/4685.aspx
This test covers  cases to select/deselect taxonomy items
"""
import time

import pytest

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = pytest.mark.regression_taxonomy

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

taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")


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


@pytest.fixture(autouse=True)
def taxonomy_job(app, set_job):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])


def test_multi_select_category(app, set_job):
    app.job.preview_job()
    time.sleep(4)
    app.annotation.deactivate_iframe()

    # update cml and check regular peer review job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_cml_multi_select
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.annotation.activate_iframe_by_index(0)
    actual_selected_list = app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[1])
    actual_selected_list_1 = app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[2], index_of_select_list=1)
    expected_selected_list = ' > '.join(ITEMS_TEXT_DATA[1])
    assert actual_selected_list == expected_selected_list, f"The actual: {actual_selected_list} not the same as " \
                                                           f"expected: {expected_selected_list} "
    expected_selected_list_1 = ' > '.join(ITEMS_TEXT_DATA[2])
    assert actual_selected_list_1 == expected_selected_list_1, f"The actual: {actual_selected_list_1} not the same as " \
                                                               f"expected: {expected_selected_list_1} "


def test_select_all_category(app, set_job):
    app.job.preview_job()
    time.sleep(4)
    app.annotation.deactivate_iframe()

    # update cml and check regular peer review job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_cml_select_all
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.annotation.activate_iframe_by_index(0)

    actual_selected_list = app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[1])
    expected_selected_list = ITEMS_TEXT_DATA[1][0]
    assert actual_selected_list == expected_selected_list, f"The actual: {actual_selected_list} not the same as " \
                                                           f"expected: {expected_selected_list} "

    actual_selected_list_1 = app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[2], index_of_select=2)

    expected_selected_list_1 = ' > '.join(ITEMS_TEXT_DATA[2])
    assert actual_selected_list_1 == expected_selected_list_1, f"The actual: {actual_selected_list_1} not the same as " \
                                                               f"expected: {expected_selected_list_1} "

    actual_selected_list_2 = app.taxonomy.select_taxonomy_item(ITEMS_TEXT_DATA[4], index_of_select=1)

    expected_selected_list_2 = ' > '.join(ITEMS_TEXT_DATA[4][0:2])
    assert actual_selected_list_2 == expected_selected_list_2, f"The actual: {actual_selected_list_2} not the same as " \
                                                               f"expected: {expected_selected_list_2} "


def test_sort_category(app, set_job):
    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)

    app.annotation.deactivate_iframe()

    # update cml and check regular peer review job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_cml_sort
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.annotation.activate_iframe_by_index(0)

    assert sorted(app.taxonomy.get_taxonomy_nodes_name()) == app.taxonomy.get_taxonomy_nodes_name(), "The taxonomy " \
                                                                                                     "category_1 not " \
                                                                                                     "sorted "

    app.taxonomy.select_taxonomy_item(['DAIRY', 'Milk', 'Goat'])

    assert sorted(
        app.taxonomy.get_taxonomy_children_nodes_name()) == app.taxonomy.get_taxonomy_children_nodes_name(), "The taxonomy category_2 not sorted "
    assert sorted(app.taxonomy.get_taxonomy_children_nodes_name(2)) == app.taxonomy.get_taxonomy_children_nodes_name(2), "The taxonomy category_3 not sorted "
