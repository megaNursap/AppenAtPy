"""
https://appen.spiraservice.net/5/TestCase/4677.aspx
This test covers positive cases to create taxonomy job
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_taxonomy]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module", autouse=True)
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


def test_valid_source_type_cml(app, login):
    """
    Verify Taxonomy link appears in Design page
    """
    job = Builder(API_KEY)
    resp = job.create_job_with_cml(data.taxonomy_cml)
    assert resp.status_code == 200
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/taxonomy/data_for_taxonomy.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_btn("Save")
    app.verification.text_present_on_page("Manage Taxonomies")

