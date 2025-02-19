import datetime
import time

import allure
import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file
from conftest import app_test

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_ui_smoke,
              mark_env]

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']
job_name_template = 'Leading job 2 (template)'
job_name_scratch = 'Leading job 1 (scratch)'
qa_job_name = 'QA job 1 (template)'


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)


@pytest.fixture(scope="module")
def new_project(app):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)
    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    faker = Faker()

    project_name = f"automation project {_today} {faker.zipcode()} for job test"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    return {
        "project_id": data['id']
    }


@pytest.fixture(scope="module")
def upload_dataset(new_project):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_id = new_project['project_id']
    dataset_id = '00000000-0000-0000-0000-000000000000'

    res = api.get_upload_dataset(project_id=project_id, team_id=team_id, dataset_id=dataset_id)
    assert res.status_code == 200
    time.sleep(5)


@pytest.mark.regression_qf
def test_qf_access_project_jobs_page(app, qf_login, new_project, upload_dataset):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    app.verification.text_present_on_page("ALL DATA")
    app.verification.text_present_on_page("units")


@pytest.mark.regression_qf
def test_qf_add_new_lead_job_from_scratch(app, qf_login, new_project, upload_dataset):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='data_source')
    app.verification.text_present_on_page("Create a leading job")

    assert app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.jobs.fill_out_job_name(job_name=job_name_scratch, action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Work Job', template='scratch')

    app.verification.text_present_on_page("return to jobs")
    app.verification.text_present_on_page("JOB ID")
    app.verification.text_present_on_page(job_name_scratch)

    global job_id_scratch
    job_id_scratch = app.quality_flow.job.grab_job_id_from_url()

    app.job.design.dc.switch_to_questions_tab()
    app.navigation.switch_to_frame(0)
    app.verification.text_present_on_page('Design your job')
    app.navigation.click_btn('Save Design')
    app.driver.switch_to.default_content()

    app.quality_flow.job.open_job_tab('quality')
    app.verification.text_present_on_page('Ensure Quality')

    app.quality_flow.job.open_job_tab('job settings')
    app.verification.text_present_on_page('Customize your job settings')

    app.quality_flow.job.setting.start_data_routing()

    app.quality_flow.job.return_to_jobs()


@pytest.mark.regression_qf
def test_qf_add_new_lead_job_from_template(app, qf_login, new_project, upload_dataset):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='data_source')

    app.quality_flow.jobs.fill_out_job_name(job_name=job_name_template, action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Work Job', template='Sentiment Analysis')

    app.verification.text_present_on_page("return to jobs")
    app.verification.text_present_on_page("JOB ID")

    global job_id_template
    job_id_template = app.quality_flow.job.grab_job_id_from_url()

    app.navigation.switch_to_frame(0)
    app.verification.text_present_on_page('Design your job')
    app.navigation.click_btn('Save')
    app.driver.switch_to.default_content()

    app.quality_flow.job.open_job_tab('quality')
    app.verification.text_present_on_page('Ensure Quality')

    app.quality_flow.job.open_job_tab('job settings')
    app.verification.text_present_on_page('Customize your job settings')

    app.quality_flow.job.setting.start_data_routing()

    app.quality_flow.job.return_to_jobs()


@pytest.mark.regression_qf
def test_qf_add_units_to_lead_job(app, qf_login, new_project, upload_dataset):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.quality_flow.data.all_data.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3'])

    app.quality_flow.data.all_data.click_actions_menu('Send Selected Units to a Job')
    app.quality_flow.data.all_data.send_units_to_job(job_name=job_name_scratch, action='Send Selected Units to a Job')
    time.sleep(5)

    app.navigation.refresh_page()

    # check unints status in job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=job_name_scratch)
    app.quality_flow.job.open_job_tab('data')
    time.sleep(3)
    data_info = app.quality_flow.job.data.get_job_dataset_info()
    assert data_info['sample_units'] == 0
    assert data_info['total_units'] == 3
    assert data_info['advanced_filter'] == 0

    data_job = app.quality_flow.job.data.get_all_units_on_page()
    units = [x[0] for x in data_job.loc[[0, 1, 2], ['STATUS']].values]

    assert set(units) == {'JUDGABLE'}
    assert (data_job.shape[0] == 3)
    app.quality_flow.job.return_to_jobs()


@pytest.mark.regression_qf
def test_qf_create_new_qa_job(app, qf_login, new_project, upload_dataset):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='job_id', value=job_id_scratch)
    app.verification.text_present_on_page("Create a following QA job")

    app.quality_flow.jobs.fill_out_job_name(job_name=qa_job_name, action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Quality Assurance (QA) Job')

    # app.verification.text_present_on_page('You can add items in PROJECT DATA MANAGEMENT page by clicking "Go to '
    #                                       'Project Data Management" button above')

    app.quality_flow.job.open_job_tab('design')
    app.navigation.switch_to_frame(0)
    app.verification.text_present_on_page('Design your job')
    app.navigation.click_btn('Save Design')
    app.driver.switch_to.default_content()

    app.quality_flow.job.open_job_tab('quality')
    app.verification.text_present_on_page('Judgment Modification')
    app.verification.text_present_on_page("Allow the QA contributor to modify the original contributor's judgments")
    app.verification.text_present_on_page("Do not allow QA Contributor to modify judgments and ...")
    app.verification.text_present_on_page(
        "Automatically send rejected units back to the original contributor to be redone")
    app.verification.text_present_on_page("Do not automatically send rejected units back to be redone")
    app.verification.text_present_on_page("When enabled, feedback will be provided to the original contributor and "
                                          "they must acknowledge the feedback before they can receive new tasks")
    app.verification.text_present_on_page("Require Original Contributor To Respond To Feedback")

    app.quality_flow.job.return_to_jobs()


@pytest.mark.regression_qf
def test_qf_remove_units_from_job(app, qf_login, new_project, upload_dataset):

    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    # app.navigation.click_link('Jobs')
    app.navigation.click_link('Dataset')

    app.quality_flow.data.all_data.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3'])

    app.quality_flow.data.all_data.click_actions_menu('Remove Selected Units from a Job')

    app.navigation.refresh_page()

    all_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    print("all_units_on_page ", all_units_on_page)

    # assert all_units_on_page.iloc[0, 1] == job_name_scratch
    # assert all_units_on_page.iloc[0, 8] ==
    # assert all_units_on_page.iloc[0, 11] == 'ASSIGNED'
    # assert all_units_on_page.iloc[0, 12] == contributor_email_1
    # assert all_units_on_page.iloc[0, 14] == 'ASSIGNED'
    # assert all_units_on_page.iloc[0, 15] == contributor_email_1

    # verify job data
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=job_name_scratch)
    app.quality_flow.job.open_job_tab('data')
    time.sleep(3)
    job_data_info_updated = app.quality_flow.job.data.get_job_dataset_info()
    print("job_data_info_updated ", job_data_info_updated)
    # assert job_data_info_updated['sample_units'] == 0
    # assert job_data_info_updated['total_units'] == 2
    # assert job_data_info_updated['advanced_filter'] == 0
