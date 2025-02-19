"""
https://appen.spiraservice.net/5/TestCase/4778.aspx

This test covers functionality for Taxonomy, when data for Taxonomy comes from url and cds source
and also verify if attribute source correct read liquid data

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
taxonomy_json_file = get_data_file("/taxonomy/correct_tax.json")
taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")

@pytest.fixture(scope="module")
def set_job(app):
    app.user.login_as_customer(USER_EMAIL, PASSWORD)
    job = Builder(API_KEY)
    job.create_job_with_cml(data.taxonomy_source_url_liquid)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/taxonomy/taxonomy_with_url_refer.csv")
    app.job.data.upload_file(data_file)
    app.job.open_tab('DESIGN')

    return job_id

@pytest.fixture(autouse=True)
def taxonomy_job(app, set_job):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])


def test_taxonomy_job_with_source_url_ref(set_job, app):
    """
       Verify Taxonomy with attribute source that ref to liquid data
    """
    app.navigation.click_btn("Save")
    app.verification.text_present_on_page("Manage Taxonomies")

    app.job.preview_job()
    time.sleep(4)
    app.annotation.activate_iframe_by_index(0)

    list_output = app.taxonomy.get_taxonomy_nodes_name()
    list_name_input = read_json_file(taxonomy_json_file, 'topLevel', False)
    for number in range(1, len(list_output) + 1):
        assert input_list_contains_output_list(list_name_input, list_output, True, f'{number}_'), "The incorrect data displays for url ref"

    app.annotation.deactivate_iframe()

    app.annotation.activate_iframe_by_index(1)
    assert set(app.taxonomy.get_taxonomy_nodes_name()) == set(read_csv_file(taxonomy_csv_file, 'category_1')), "The incorrect data displays for CDS ref"


def test_taxonomy_job_with_url_in_source(set_job, app):
    """
           Verify Taxonomy tool with attribute source that ref to data from url
    """
    app.job.preview_job()
    time.sleep(4)
    app.annotation.deactivate_iframe()

    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_source_url_ref
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.annotation.activate_iframe_by_index(1)

    list_output = app.taxonomy.get_taxonomy_nodes_name()
    list_name_input = read_json_file(taxonomy_json_file, 'topLevel', False)

    for number in range(1, len(list_output) + 1):
        assert input_list_contains_output_list(list_name_input, list_output, True, f'{number}_'), "The incorrect data displays for url ref"
