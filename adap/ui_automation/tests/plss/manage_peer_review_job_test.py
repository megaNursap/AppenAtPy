"""
https://appen.atlassian.net/browse/QED-1515
This test covers:
1. create peer review job
2. test validator peer review job
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.annotation import create_peer_review_job
from adap.data import annotation_tools_cml as data


pytestmark = pytest.mark.regression_plss

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
PREDEFINED_JOB_ID = pytest.data.predefined_data['plss'].get(pytest.env)


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, PREDEFINED_JOB_ID, data.plss_peer_review_cml)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    #AT-5911 is fixed, uncommenting the line below
    app.user.customer.go_to_specific_page(f"jobs/{job_id}/ontology_manager")
    # app.navigation.click_link('Manage Image Segmentation Ontology')

    ontology_file = get_data_file("/plss/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")
    return job_id


# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_peer_review(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    app_test.job.preview_job()
    time.sleep(15)
    app_test.plss.submit_test_validators()
    time.sleep(8)
    app_test.verification.text_present_on_page("Validation succeeded")
