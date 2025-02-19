import datetime
import pytest
from selenium.webdriver.common.by import By

from adap.api_automation.services_config.qf_api_logic import faker
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject, QualityFlowApiWork
from adap.api_automation.utils.data_util import get_data_file
from adap.ui_automation.tests.quality_flow.qf_create_jobs_test import job_name_scratch, job_name_template, qa_job_name

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]

username = 'integration+qa1qf@figure-eight.com'
password = 'Password@123'
team_id = 'f6c0b8cb-de69-495c-980b-2b0e0a6ca288'
icm_name = faker.name()


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)


@pytest.fixture(scope="module")
def setup():
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    payload = {"pageNumber": 1, "pageSize": 5, "sortModel": [], "filterModel": {}}
    res = api.get_list_of_projects(team_id=team_id, payload=payload)
    assert res.status_code == 200
    project_id = res.json_response['data']['list'][2]['id']
    project_name = res.json_response['data']['list'][2]['name']

    return {
        "project_id": project_id,
        "project_name": project_name
    }


@pytest.mark.regression_qf
def test_qf_create_project(app, qf_login):
    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    app.navigation.click_link_by_href('/quality')

    project_name = f"automation project {_today} {faker.zipcode()} for job test"
    app.verification.wait_untill_text_present_on_the_page('Create Project')
    app.navigation.click_link('Create Project')

    app.quality_flow.fill_out_project_details(name=project_name,
                                              description="Test read-only user",
                                              action="Confirm")

    app.verification.text_present_on_page('There was an error creating quality flow project.')


@pytest.mark.regression_qf
def test_qf_upload_dataset(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])

    app.navigation.click_link('Add More Data')

    sample_file = get_data_file("/authors.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.verification.text_present_on_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_add_new_lead_job_from_scratch(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='data_source')
    app.verification.text_present_on_page("Create a leading job")

    assert app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.jobs.fill_out_job_name(job_name=job_name_scratch, action='Confirm')

    assert app.verification.text_present_on_page("Access Denied")


@pytest.mark.regression_qf
def test_qf_add_new_lead_job_from_template(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])
    app.navigation.click_link('Jobs')

    app.quality_flow.jobs.click_add_new_job_to(connection_type='data_source')
    app.verification.text_present_on_page("Create a leading job")

    assert app.verification.link_is_disable('Confirm', method='cursor_property')

    app.quality_flow.jobs.fill_out_job_name(job_name=job_name_template, action='Confirm')

    assert app.verification.text_present_on_page("Access Denied")


@pytest.mark.regression_qf
def test_qf_action_menu(app, setup, qf_login):
    project_id = 'e6e49e80-31e0-40ed-abb0-21784ee42db8'

    app.quality_flow.navigate_to_dataset_page_by_project_id(project_id)

    app.quality_flow.data.all_data.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3'])

    app.quality_flow.data.all_data.click_actions_menu('Send Selected Units to a Job')
    app.quality_flow.data.all_data.send_units_to_job(job_name='Job', action='Send Selected Units to a Job')

    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_edit_design(app, qf_login):
    project_id = 'e6e49e80-31e0-40ed-abb0-21784ee42db8'
    job_id = '9381de69-ef4d-4b79-9a95-13cf73e12912'

    app.quality_flow.navigate_to_design_page_by_project_id(project_id, job_id)
    app.driver.implicitly_wait(10)
    app.navigation.switch_to_frame(0)
    app.quality_flow.job.design.delete_multiple_choices()
    app.driver.implicitly_wait(5)
    app.navigation.click_link('OK')
    app.driver.implicitly_wait(5)
    app.navigation.click_btn_by_text('Save Design')
    app.driver.switch_to.default_content()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id, job_id)
    app.driver.implicitly_wait(10)
    app.navigation.switch_to_frame(0)
    assert app.quality_flow.job.design.is_multiple_choice_visible() is True
    app.driver.switch_to.default_content()


@pytest.mark.regression_qf
def test_qf_edit_quality(app, qf_login):
    project_id = '1050ab6a-b47e-45c7-8e0a-b32aae3631b5'
    job_id = '77dbab3d-dcac-48bd-b942-62249a805695'

    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(project_id, job_id)

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_1'])

    app.navigation.click_link('Next: Set up Test Questions')

    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_edit_contributor_setting(app, qf_login):
    project_id = 'e6e49e80-31e0-40ed-abb0-21784ee42db8'
    job_id = '9381de69-ef4d-4b79-9a95-13cf73e12912'

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')

    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup('xyz@gmail.com')

    app.navigation.click_link('Assign')
    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_internal_link(app, qf_login):
    project_id = 'e6e49e80-31e0-40ed-abb0-21784ee42db8'
    job_id = '9381de69-ef4d-4b79-9a95-13cf73e12912'

    app.quality_flow.navigate_to_job_setting_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    # Having issue with the internal link


@pytest.mark.regression_qf
def test_qf_edit_price_row(app, qf_login):
    project_id = 'efe760f2-9e85-447e-97c6-5824bfad8efc'
    job_id = 'db8b9692-792d-4cff-8f3c-fb305851e2bc'

    app.quality_flow.navigate_to_job_setting_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(10)
    app.quality_flow.job.setting.configure_row_settings('2')
    app.navigation.click_link('Save settings')

    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_action_menu(app, qf_login):
    project_id = '788e7782-d3da-4777-a27c-33f796f84976'
    job_id = '4a2f7345-f0f6-4188-8274-d6f495be361e'

    app.quality_flow.navigate_to_data_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(20)
    app.quality_flow.job.data.select_units_checkbox_by_unit_ids(['1_9'])
    app.quality_flow.job.data.click_actions_menu('Assign Selected Units to Contributor(s)')
    app.quality_flow.job.data.assign_selected_units_to_contributors(['xyz@gmail.com'])

    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_result(app, qf_login):
    project_id = 'f3ca5112-ef50-4db4-8f9c-7b80cc094e57'
    job_id = '7f08371f-1ca3-434f-84b6-bba593b4c2ea'

    app.quality_flow.navigate_to_result_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.navigation.click_link('Download Report')

    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_copy_job(app, qf_login):
    project_id = '788e7782-d3da-4777-a27c-33f796f84976'
    job_id = '4a2f7345-f0f6-4188-8274-d6f495be361e'

    new_job_name = "Copy job 1"
    project_name = "WJ1"

    app.quality_flow.navigate_to_job_setting_page_by_project_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.click_copy_job("WJ1")
    app.quality_flow.job.copy_job(new_job_name=new_job_name,
                                  data_source=project_name,
                                  copy_job_design=True,
                                  launch_settings=True,
                                  contributors=True,
                                  action='Copy')

    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_delete_job(app, qf_login):
    project_id = '788e7782-d3da-4777-a27c-33f796f84976'
    job_id = '4a2f7345-f0f6-4188-8274-d6f495be361e'

    app.quality_flow.navigate_to_job_setting_page_by_project_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.click_delete_job("WJ1")
    app.driver.implicitly_wait(3)
    app.navigation.click_link('confirm')

    # assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_preview_job(app, qf_login):
    project_id = '788e7782-d3da-4777-a27c-33f796f84976'
    job_id = '4a2f7345-f0f6-4188-8274-d6f495be361e'

    app.quality_flow.navigate_to_job_setting_page_by_project_id(project_id, job_id)
    app.driver.implicitly_wait(10)
    app.quality_flow.job.click_preview_job("WJ1")
    original_window = app.driver.current_window_handle
    # Switch to the new tab
    new_window = [window for window in app.driver.window_handles if window != original_window][0]
    app.driver.switch_to.window(new_window)
    assert app.verification.wait_untill_text_present_on_the_page('WJ1')
    app.driver.switch_to.window(original_window)


@pytest.mark.regression_qf
def test_qf_add_new_contributor(app, qf_login):
    email = faker.email()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email(email)
    app.project_resource.icm.enter_name(icm_name)
    app.project_resource.icm.click_add_button()
    assert app.verification.wait_untill_text_present_on_the_page('Access Denied')


@pytest.mark.regression_qf
def test_qf_run_job(app, qf_login):
    project_id = '788e7782-d3da-4777-a27c-33f796f84976'
    job_id = '4a2f7345-f0f6-4188-8274-d6f495be361e'

    app.quality_flow.navigate_to_job_setting_page_by_project_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.run_job(False)
    assert app.verification.wait_untill_text_present_on_the_page('There was an error resuming job.')


@pytest.mark.regression_qf
def test_qf_edit_curated_contributor(app, qf_login):
    project_id = '788e7782-d3da-4777-a27c-33f796f84976'

    app.quality_flow.navigate_to_dataset_page_by_project_id(project_id)
    app.driver.implicitly_wait(10)
    app.navigation.click_link('Curated Contributors')
    app.quality_flow.crowd.select_action_by_project_name(project_name='Quality_Flow_005', action='Edit')
    app.navigation.click_link('Save And Add Project')
    assert app.verification.verify_error_is_visible_on_the_page()

