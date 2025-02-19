"""
This test mainly focus on manage text relationship on long span cases, it covers:
https://appen.atlassian.net/browse/QED-1274
1. create text relationship on long from span, long to span, long text relationship type
verify they are being truncated
"""
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.text_relationship import create_text_relationship_job
import time

pytestmark = [pytest.mark.text_relationship,  pytest.mark.regression_text_relationship]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
predefined_jobs = pytest.data.predefined_data


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    1. Create Text Relationship job using output of a predefined Text Annotation job
    2. Upload ontology json
    """
    tmpdir = tmpdir_factory.mktemp('data')
    longspan_id = predefined_jobs['long_span'][pytest.env]
    job_id = create_text_relationship_job(tmpdir, API_KEY, predefined_jobs, job_id=longspan_id)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')

    ontology_file = get_data_file('/text_relationship/longspan_ontology.json')
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")
    print(job_id)
    return job_id


@pytest.mark.text_annotation
def test_long_span(app, tx_job):
    """
    1. Verify long relationship names are truncated
    2. Verify scroll is available when there are a lot of relationships
    3. Verify that long from and to span names are truncated in sidepanel
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    app.job.preview_job()
    time.sleep(5)
    app.text_relationship.activate_iframe_by_index(3)
    app.text_relationship.full_screen()
    time.sleep(5)
    app.text_relationship.click_word('RIBA', 'city')
    app.text_relationship.click_word('Department', 'name')
    app.text_relationship.select_relationship_type('test relationship8 - yet another long relationship name for testing purpose')
    app.text_relationship.long_span_truncate('RIBA International Prize', 'Department of Finance building')
    app.text_relationship.full_screen()
    app.driver.close()

