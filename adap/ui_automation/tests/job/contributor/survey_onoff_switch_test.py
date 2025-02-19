"""
https://appen.atlassian.net/browse/QED-2032
1. The exist survey ON/OFF switch is based on job.
2. We have 3 scenarios to test
   a. Disable the survey and contributor give up during annotation, no survey should show
   b. Disable the survey and contributor finish annotation and no survey should show there
   c. Enable the survey and contributor finish annotation and see the survey
"""
import time
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.ui_uat, pytest.mark.regression_core, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/text_annotation/multiplelinesdata.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module")
def exit_survey_jobs(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    _jobs = []
    for i in range(2):
        job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.text_annotation_cml,
                                            job_title="Testing text annotation tool", units_per_page=5)
        _jobs.append(job_id)
        app.mainMenu.jobs_page()
        app.job.open_job_with_id(job_id)
        time.sleep(2)

        app.job.open_action('Settings')
        app.job.open_settings_tab('Quality Control,Quality Control Settings')
        app.verification.current_url_contains('/settings/quality_control')
        app.verification.text_present_on_page('Satisfaction Exit Survey')
        app.verification.checkbox_by_text_is_selected('Enable satisfaction exit survey when contributors finish or exit their work')
        # we disable the survey for the first job
        if i == 0:
            app.navigation.click_checkbox_by_text('Enable satisfaction exit survey when contributors finish or exit their work')
            app.navigation.click_btn('Save')

        app.job.open_tab('DESIGN')
        app.navigation.click_link('Manage Text Annotation Ontology')
        ontology_file = get_data_file("/text_annotation/ontology.json")
        app.ontology.upload_ontology(ontology_file, rebrand=True)
        # app.verification.text_present_on_page("3/1000 Classes Created")
        time.sleep(3)

        if pytest.env == 'fed':
            app.job.open_action("Settings")
            app.navigation.click_link("Select Contributor Channels")
            app.job.select_hosted_channel_by_index(save=True)

        job = JobAPI(API_KEY, job_id=job_id)
        job.launch_job()

        job.wait_until_status('running', 120)
        res = job.get_json_job_status()
        res.assert_response_status(200)
        assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
            res.json_response['state'], "running")

    app.user.logout()
    return _jobs


@pytest.mark.skipif(not pytest.running_in_preprod_sandbox_fed, reason="Sandbox enable the feature")
def test_exit_survey_on_off_switch(app, exit_survey_jobs):
    # try scenario a: first job disable the survey, we checked the give up scenario, see survey will not show if contributor gives up during annotation
    job_link = generate_job_link(exit_survey_jobs[0], API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.navigation.click_link('Give up')
    app.navigation.click_link('Give up', index=-1)
    app.verification.text_present_on_page('Please help us improve by completing this optional survey.', is_not=False)

    # try scenario b and scenario c in the notes
    for i in range(2):
        job_link = generate_job_link(exit_survey_jobs[i], API_KEY, pytest.env)
        app.navigation.open_page(job_link)
        app.user.close_guide()
        time.sleep(2)
        app.user.task.wait_until_job_available_for_contributor(job_link)
        for j in range(5):
            app.text_annotation.activate_iframe_by_index(j)
            app.text_annotation.click_token('Google')
            app.text_annotation.click_span('company')
            app.text_annotation.deactivate_iframe()
            time.sleep(2)

        app.text_annotation.submit_page()
        time.sleep(5)
        app.verification.text_present_on_page('There is no work currently available in this task.')
        if i == 0:
            app.verification.text_present_on_page('Please help us improve by completing this optional survey.',
                                                  is_not=False)
        else:
            app.verification.text_present_on_page('Please help us improve by completing this optional survey.')

