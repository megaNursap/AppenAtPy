import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor, QualityFlowApiWork, \
    QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)


@pytest.fixture(scope="module")
def setup():
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    project_name = f"automation project {_today} {faker.zipcode()}: copy job -ui"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    # create job
    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)
    payload = {"title": "New  WORK job",
               "teamId": team_id,
               "projectId": data['id'],
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "",
                       "css": "",
                       "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                       "instructions": "Test CML API update"}
               }

    res = job_api.post_create_job(team_id=team_id, payload=payload)
    assert res.status_code == 200

    print("project_id ", data['id'])
    print("job_id ", [res.json_response['data']['id']])

    return {
        "project_id": data['id'],
        "team_id": data['teamId'],
        "job_id": [res.json_response['data']['id']],
        "job_name": ['New  WORK job'],
        "project_name": project_name,
    }


@pytest.mark.regression_qf
def test_job_setting_in_quiz_mode_only(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])
    sample_file = get_data_file("/test_questions/image-annotation-source-for-ADAP-TQ-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.quality_flow.navigate_to_design_page_by_project_id(setup['project_id'], setup['job_id'][0])
    app.driver.implicitly_wait(20)
    app.navigation.switch_to_frame(0)
    app.quality_flow.job.design.delete_multiple_choices()
    app.driver.implicitly_wait(5)
    app.navigation.click_link('OK')
    app.driver.implicitly_wait(10)
    app.quality_flow.job.design.close_dialog_message()
    app.navigation.click_link('Text Box (Single Line)')
    app.quality_flow.job.design.input_textbox_single_line_from_side_panel('What Doing')
    app.navigation.click_btn('Save & Close')
    app.navigation.click_btn_by_text('Save Design')
    app.driver.switch_to.default_content()

    app.quality_flow.job.open_job_tab('quality')
    app.driver.implicitly_wait(5)
    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3', '1_4', '1_5'])

    app.navigation.click_link('Next: Set up Test Questions')

    app.quality_flow.job.quality.set_minimum_matching_accuracy('80')

    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(0, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(1, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(2, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(3, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(4, None, None, None, None,
                                                                                      'Hello World', None)

    app.navigation.click_link('Save And Exit')

    app.quality_flow.navigate_to_job_setting_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.setting.start_data_routing()

    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])

    app.quality_flow.data.all_data.select_units_checkbox_by_unit_ids(['1_6', '1_7', '1_8', '1_9'])

    app.quality_flow.data.all_data.click_actions_menu('Send Selected Units to a Job')
    app.quality_flow.data.all_data.send_units_to_job(job_name=setup['job_name'][0],
                                                     action='Send Selected Units to a Job')

    app.quality_flow.navigate_to_job_setting_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.setting.select_job_mode('Quiz Mode Only')

    app.quality_flow.job.setting.configure_test_question_quiz_mode_only_settings('80', '5')

    app.quality_flow.job.setting.enable_public_link()

    internal_link = app.quality_flow.job.setting.get_public_link()

    app.navigation.click_link('Save settings')

    app.quality_flow.job.run_job()

    app.navigation.open_page(internal_link)

    app.user.task.wait_until_job_available_for_contributor(internal_link)

    app.user.task.wait_until_job_available_for_contributor(internal_link)

    answer_questions_on_page(app.driver, tq_dict='', mode='cml_text', values=['Hello World', 'Hello World', 'Hello World', 'Hello World', 'Hello World'])

    app.job.judgements.click_submit_judgements()


@pytest.mark.regression_qf
def test_job_setting_in_quiz_and_work_mode(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])
    sample_file = get_data_file("/test_questions/image-annotation-source-for-ADAP-TQ-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.quality_flow.navigate_to_design_page_by_project_id(setup['project_id'], setup['job_id'][0])
    app.driver.implicitly_wait(20)
    app.navigation.switch_to_frame(0)
    app.quality_flow.job.design.delete_multiple_choices()
    app.driver.implicitly_wait(5)
    app.navigation.click_link('OK')
    app.driver.implicitly_wait(10)
    app.quality_flow.job.design.close_dialog_message()
    app.navigation.click_link('Text Box (Single Line)')
    app.quality_flow.job.design.input_textbox_single_line_from_side_panel('What Doing')
    app.navigation.click_btn('Save & Close')
    app.navigation.click_btn_by_text('Save Design')
    app.driver.switch_to.default_content()

    app.quality_flow.job.open_job_tab('quality')
    app.driver.implicitly_wait(5)
    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3', '1_4', '1_5'])

    app.navigation.click_link('Next: Set up Test Questions')

    app.quality_flow.job.quality.set_minimum_matching_accuracy('80')

    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(0, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(1, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(2, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(3, None, None, None, None,
                                                                                      'Hello World', None)
    app.quality_flow.job.quality.configure_textbox_single_line_test_question_by_index(4, None, None, None, None,
                                                                                      'Hello World', None)

    app.navigation.click_link('Save And Exit')

    app.quality_flow.navigate_to_job_setting_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.setting.start_data_routing()

    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])

    app.quality_flow.data.all_data.select_units_checkbox_by_unit_ids(['1_6', '1_7', '1_8', '1_9'])

    app.quality_flow.data.all_data.click_actions_menu('Send Selected Units to a Job')
    app.quality_flow.data.all_data.send_units_to_job(job_name=setup['job_name'][0],
                                                     action='Send Selected Units to a Job')

    app.quality_flow.navigate_to_job_setting_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.setting.select_job_mode('Quiz + Work Mode')

    app.quality_flow.job.setting.configure_test_question_quiz_and_work_mode_settings('80', '5', '1', '5')

    app.quality_flow.job.setting.enable_public_link()

    internal_link = app.quality_flow.job.setting.get_public_link()

    app.navigation.click_link('Save settings')

    app.quality_flow.job.run_job()

    app.navigation.open_page(internal_link)

    app.user.task.wait_until_job_available_for_contributor(internal_link)

    answer_questions_on_page(app.driver, tq_dict='', mode='cml_text', values=['Hello World', 'Hello World', 'Hello World', 'Hello World', 'Hello World'])

    app.user.task.submit_quiz_answer_and_continue()

    answer_questions_on_page(app.driver, tq_dict='', mode='cml_text', values=['Hello World', 'Hello World', 'Hello World', 'Hello World', 'Hello World'])

    app.job.judgements.click_submit_judgements()
