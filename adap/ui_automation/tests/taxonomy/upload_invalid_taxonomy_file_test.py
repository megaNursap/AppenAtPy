"""
https://appen.spiraservice.net/5/TestCase/4680.aspx
This test covers negative cases to upload taxonomy file
"""

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
    app.taxonomy.add_taxonomy()
    app.taxonomy.input_name_of_taxonomy("taxonomy_1")


@pytest.mark.parametrize('file_name, error_msg',
                         [('tax_file_with_forbidden_character>.csv', 'contains illegal character >'),
                          ('tax_file_with_incorrect_symbol_|.csv', 'contains illegal character |'),
                          ('tax_with_incorrect_header_name.csv', 'Invalid header name category_4'),
                          ('tax_with_empty_field.csv', 'the field value represented by column 2 is empty'),
                          ('illegal_field_|_graph.json', 'contains illegal character |')])
def test_taxonomy_job_with_upload_invalid_data_csv(app, set_job, file_name, error_msg):
    """
       Verify that data in file for taxonomy cannot consist '<' and '|', empty field in the middle column,
       the header name should be represented category_1, category_2, category_3....
    """
    taxonomy_csv_file = get_data_file(f"/taxonomy/{file_name}")
    app.job.data.upload_file(taxonomy_csv_file)
    alert_message = app.taxonomy.get_error_msg()
    assert error_msg in alert_message, "Error message doesn't contain proper message: %s" % error_msg