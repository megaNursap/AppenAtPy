"""
https://appen.spiraservice.net/5/TestCase/4686.aspx
This test covers that taxonomy tools correct works with other annotation tools
"""
import time

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_taxonomy]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def set_job(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job = Builder(API_KEY)
    resp = job.create_job_with_cml(data.taxonomy_shape_cml)
    assert resp.status_code == 200
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/taxonomy/taxonomy_annotation_data.csv")
    app.job.data.upload_file(data_file)
    return job_id


@pytest.fixture(autouse=True)
def change_job(app, set_job):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])

def test_taxonomy_tool_with_shape_tool(app, set_job):
    """
    Verify Taxonomy link and Image anotation appears in Design page
    """
    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")

    app.verification.text_present_on_page("Manage Taxonomies")
    app.verification.text_present_on_page("Manage Image Annotation Ontology")

    app.verification.wait_untill_text_present_on_the_page("Job saved successfully", 10)
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")

    app.job.open_tab('DESIGN')

    app.navigation.click_link("Manage Taxonomies")
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")
    taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    app.job.preview_job()
    time.sleep(4)

    app.annotation.activate_iframe_by_index(0)
    app.taxonomy.select_taxonomy_item(['DAIRY', 'Milk', 'Goat'])
    app.annotation.deactivate_iframe()

    app.annotation.activate_iframe_by_index(1)
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 3})
    app.image_annotation.deactivate_iframe()
    app.image_annotation.submit_test_validators()
    app.verification.text_present_on_page('Validation succeeded')


def test_taxonomy_tool_with_text_annotation_tool(app, set_job):
    """
    Verify Taxonomy link and Image anotation appears in Design page
    """
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.taxonomy_text_annotation_cml
        }
    }
    job = Builder(API_KEY)
    job.job_id = set_job
    job.update_job(payload=updated_payload)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")

    app.verification.text_present_on_page("Manage Taxonomies")
    app.verification.text_present_on_page("Manage Text Annotation Ontology")

    app.verification.wait_untill_text_present_on_the_page("Job saved successfully", 10)
    app.navigation.click_link('Manage Text Annotation Ontology')

    ontology_file = get_data_file("/text_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created", "//span[text()='3']")
    time.sleep(2)

    app.job.open_tab('DESIGN')

    app.navigation.click_link("Manage Taxonomies")
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_2")
    taxonomy_csv_file = get_data_file("/taxonomy/tax_category_id.csv")
    app.taxonomy.upload_taxonomy(taxonomy_csv_file)

    app.job.preview_job()
    time.sleep(4)

    app.text_annotation.activate_iframe_by_index(0)
    # add span
    app.text_annotation.click_token('cream')
    app.text_annotation.click_span('name')
    app.text_annotation.deactivate_iframe()

    app.annotation.activate_iframe_by_index(1)
    app.taxonomy.select_taxonomy_item(['DAIRY', 'Milk', 'Goat'])
    app.annotation.deactivate_iframe()

    app.image_annotation.submit_test_validators()
    app.verification.text_present_on_page('Validation succeeded')