import time
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.api_automation.services_config.jobs_api import JobsApi
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get("radio_default", "")

api_key = get_test_data('test_ui_account', 'api_key')
email = get_test_data('test_ui_account', 'email')
password = get_test_data('test_ui_account', 'password')


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_delete_unordered_job(app):
    """
    Verify that user can delete "Unordered" job
    """
    job = JobAPI(api_key)
    resp = job.create_job()
    job_id = job.job_id
    assert resp.status_code == 200, "Job was not created"

    app.user.login_as_customer(user_name=email, password=password)

    app.mainMenu.jobs_page()
    time.sleep(5)

    app.job.click_on_gear_for_job(job_id=job_id, sub_menu_action="Delete Job")
    app.job.enter_job_id_delete_job_window(job_id)
    app.job.click_on_delete_this_job()
    app.verification.text_present_on_page("The deletion of job ID %s is processed and will be removed from Appen systems" % job_id )

    app.mainMenu.jobs_page()
    app.job.search_jobs_by_id(job_id)
    app.verification.text_present_on_page('No results found matching your search')

@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_delete_canceled_job(app):
    """
    Verify that user can delete "Canceled" job
    """
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    job_id = job.job_id
    job.launch_job()
    job.cancel_job()
    job.wait_until_status2(status='canceled')

    res = job.get_json_job_status()
    assert 'canceled' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "canceled")

    app.mainMenu.workflows_page()
    app.mainMenu.jobs_page()
    time.sleep(5)

    app.job.click_on_gear_for_job(job_id=job_id, sub_menu_action="Delete Job")
    app.job.enter_job_id_delete_job_window(job_id)
    app.job.click_on_delete_this_job()
    app.verification.text_present_on_page(
        "The deletion of job ID %s is processed and will be removed from Appen systems" % job_id)

    app.mainMenu.jobs_page()
    app.job.search_jobs_by_id(job_id)
    app.verification.text_present_on_page('No results found matching your search')


# Needs to be updated according to new UI and search for archived jobs https://appen.atlassian.net/browse/ADAP-3954
# @pytest.mark.ui_uat
# @pytest.mark.adap_ui_uat
# @pytest.mark.adap_uat
# def test_delete_archived_job(app):
#     """
#     Verify that user can delete "Archived" job
#     """
#     job = Builder(api_key)
#     job.create_job()
#     job_id = job.job_id
#
#     job_to_archive = JobsApi()
#     resp = job_to_archive.archive_job(job_id)
#     resp.assert_response_status(200)
#     job.wait_until_status2(status='archived', key='archive_state', state_key='state')
#
#     res = job.get_json_job_status()
#     assert res.json_response['archive_state']['state'] == 'archived'
#
#     app.user.login_as_customer(user_name=email, password=password)
#
#     app.mainMenu.jobs_page()
#     app.job.search_jobs_by_id(job_id)
#     time.sleep(5)
#
#     app.job.select_action_in_job_menu("Delete Job")
#     app.job.enter_job_id_delete_job_window(job_id)
#     app.job.click_on_delete_this_job()
#     app.job.verify_job_delete_successfully_message(job_id)
#
#     app.mainMenu.jobs_page()
#     app.job.verify_job_is_not_found()
#     app.user.logout()

@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_can_not_delete_paused_job(app):
    """
    Verify that user can not delete "Paused" job
    """
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    job_id = job.job_id
    job.launch_job()
    job.pause_job()
    job.wait_until_status2(status='paused')

    res = job.get_json_job_status()
    assert 'paused' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "paused")

    app.mainMenu.workflows_page()
    app.mainMenu.jobs_page()
    time.sleep(5)

    app.job.verify_job_action_not_in_dropdown_menu(job_id=job_id, sub_menu_action="Delete Job")

@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_can_not_delete_running_job(app):
    """
    Verify that user can not delete "Running" job
    """
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    job_id = job.job_id
    job.launch_job()
    job.wait_until_status2(status='running')

    res = job.get_json_job_status()
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app.mainMenu.workflows_page()
    app.mainMenu.jobs_page()
    time.sleep(5)

    app.job.verify_job_action_not_in_dropdown_menu(job_id=job_id, sub_menu_action="Delete Job")

@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_can_not_delete_job_that_part_of_workflow(app):
    """
    Verify that user can not delete job that part of Workflow
    """
    job = Builder(api_key)
    job.create_job()
    job_id = job.job_id

    wf = Workflow(api_key)
    payload = {'name': 'WF Test Job Deletion', 'description': 'WF Test Job Deletion'}
    wf.create_wf(payload=payload)
    wf_id = wf.wf_id
    wf.create_job_step([job_id], wf_id)

    app.mainMenu.workflows_page()
    app.mainMenu.jobs_page()
    time.sleep(5)

    app.job.verify_job_action_not_in_dropdown_menu(job_id=job_id, sub_menu_action="Delete Job")

@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_delete_finished_job(app):
    """
    Verify that user can delete "Finished" job
    """
    copied_job = Builder(api_key)

    copied_job_resp = copied_job.copy_job(TEST_DATA, "all_units")
    copied_job_resp.assert_response_status(200)

    job_id = copied_job_resp.json_response['id']
    copied_job.job_id = job_id
    copied_job.launch_job()
    copied_job.wait_until_status("running", max_time=60)

    job_link = generate_job_link(job_id, api_key, pytest.env)
    app.navigation.open_page(job_link)

    app.user.task.wait_until_job_available_for_contributor(job_link)
    answer_questions_on_page(app.driver, tq_dict='', mode='radio_button', values=['cat', 'dog', 'something_else'])
    app.job.judgements.click_submit_judgements()

    app.user.customer.open_home_page()
    time.sleep(40)
    copied_job.wait_until_status2(status='finished')
    app.mainMenu.jobs_page()
    time.sleep(5)

    app.job.click_on_gear_for_job(job_id=job_id, sub_menu_action="Delete Job")
    app.job.enter_job_id_delete_job_window(job_id)
    app.job.click_on_delete_this_job()
    app.verification.text_present_on_page(
        "The deletion of job ID %s is processed and will be removed from Appen systems" % job_id)

    app.mainMenu.jobs_page()
    app.job.search_jobs_by_id(job_id)
    app.verification.text_present_on_page('No results found matching your search')