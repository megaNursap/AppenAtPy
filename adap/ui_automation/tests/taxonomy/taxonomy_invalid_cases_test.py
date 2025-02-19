"""
https://appen.spiraservice.net/5/TestCase/4793.aspx
This test covers  cases for invalid cases
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
taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")
data_file=get_data_file("/taxonomy/taxonomy_review_data.csv")


@pytest.fixture(scope="module")
def set_job(app):
    app.user.login_as_customer(USER_EMAIL, PASSWORD)
    job = Builder(API_KEY)
    job.create_job_with_cml(data.taxonomy_peer_review_incorrect_task_type)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    app.job.data.upload_file(data_file)
    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Taxonomies")
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_3")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    return job_id


@pytest.fixture(autouse=True)
def taxonomy_job(app, set_job):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])


def test_tool_not_initialized_incorrect_task_type(app, set_job):
    app.job.preview_job()
    time.sleep(4)

    app.annotation.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable')
    app.verification.text_present_on_page('Tool cannot be initialized')
    app.navigation.click_link('Details')
    app.verification.text_present_on_page("Invalid task-type in payload. Provided task-type 'qas' is not supported by this tool.")


def test_tool_work_with_incorrect_source_ref(app, set_job):
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_cml
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Taxonomies")
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_2")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    app.job.preview_job()
    time.sleep(4)

    app.annotation.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable')
    app.verification.text_present_on_page('Tool cannot be initialized')
    app.navigation.click_link('Details')
    app.verification.text_present_on_page(
        "There is no taxonomy data uploaded with given source name: taxonomy_1 (Job designer should use Taxonomy "
        "Manager page to upload one with this name or update the 'source' attribute value in CML to match an existing "
        "taxonomy name.)")


def test_tool_with_absent_of_source_att(app, set_job):
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_cml_without_source
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.job.preview_job()
    time.sleep(4)

    app.annotation.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable')
    app.verification.text_present_on_page('Tool cannot be initialized')
    app.navigation.click_link('Details')
    app.verification.text_present_on_page(
    "There are more than one taxonomy available for this job. Job designer should specify which taxonomy to load via "
    "the 'source' attribute in CML.")