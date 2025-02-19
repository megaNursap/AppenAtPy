"""
https://appen.spiraservice.net/5/TestCase/4668.aspx
https://appen.spiraservice.net/5/TestCase/4667.aspx

This test covers positive cases to upload taxonomy file
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


@pytest.fixture(autouse=True)
def taxonomy_job(app, set_job):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])
    app.taxonomy.action_taxonomy('taxonomy_1', 'Delete')
    app.taxonomy.delete_submission()
    app.verification.wait_until_text_disappear_on_the_page("taxonomy_1", 10)


def test_taxonomy_job_with_valid_csv_data(app):
    """
       Verify Taxonomy upload csv file
    """
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")
    taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)
    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)
    assert set(app.taxonomy.get_taxonomy_nodes_name()) == set(read_csv_file(taxonomy_csv_file, 'category_1'))


def test_taxonomy_job_with_valid_graph_json_data(app):
    """
       Verify Taxonomy upload graph json file
    """
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")
    taxonomy_json_graph_file = get_data_file("/taxonomy/correct_tax_graph.json")
    app.taxonomy.upload_taxonomy(taxonomy_json_graph_file)
    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)
    list_name_input = read_json_file(taxonomy_json_graph_file, 'nodes', 'name')
    list_edges_input = read_json_file(taxonomy_json_graph_file, 'edges', 'to')
    list_output = app.taxonomy.get_taxonomy_nodes_name()
    assert input_list_contains_output_list(list_name_input, list_output), "The taxonomy nodes doesn't contains all ID"
    assert not input_list_contains_output_list(list_edges_input, list_output, True), "The taxonomy nodes contains " \
                                                                                     "incorrect ID value "


def test_taxonomy_job_with_valid_json_data(app):
    """
       Verify Taxonomy upload json file
    """
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")
    taxonomy_json_file = get_data_file("/taxonomy/correct_tax.json")
    app.taxonomy.upload_taxonomy(taxonomy_json_file)
    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)
    list_name_input = read_json_file(taxonomy_json_file, 'topLevel', False)
    list_output = app.taxonomy.get_taxonomy_nodes_name()
    for number in range(1, len(list_output) + 1):
        assert input_list_contains_output_list(list_name_input, list_output, True, f'{number}_'), "The taxonomy nodes " \
                                                                                                  "doesn't contains " \
                                                                                                  "all ID "
