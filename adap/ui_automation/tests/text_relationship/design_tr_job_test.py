"""
This is test setup, prerequisite tests cover:
1.create a text relationship job based on predefined text annotation job
(test annotation job result will be input for text relationship job)
2.upload ontology

<cml:text_relationships label="Your annotation:" validates="required" data-url="{{my_annotations}}" name="text relationship"/>
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.text_relationship import create_text_relationship_job

pytestmark = [pytest.mark.text_relationship,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.regression_text_relationship]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
predefined_jobs = pytest.data.predefined_data


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Text relationship job using the output of a predefined Text Annotation job
    """
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_text_relationship_job(tmpdir, API_KEY, predefined_jobs)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    return job_id


@pytest.mark.text_relationship
def test_upload_ontology(app, tx_job):
    """
    Verify requestor can successfully upload ontology json
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')

    ontology_file = get_data_file('/text_relationship/ontology.json')
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")

