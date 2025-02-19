import datetime
import os
import time

import allure
import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject, QualityFlowApiWork
from adap.api_automation.utils.data_util import get_test_data, get_data_file
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page
from adap.data.annotation_tools_cml import quiz_work_mode_switch_cml

from adap.ui_automation.services_config.quality_flow.components import login_and_open_qf_page,  feedback_judgements_qa_job

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()


@pytest.fixture(scope="module")
def qf_login(app):
    login_and_open_qf_page(app, 'qf_user_ui')


@allure.issue("https://appen.atlassian.net/browse/QED-4453", "BUG")
def test_qf_e2e_smoke(app, qf_login):
    """
    E2E test:
       - create new project
       - upload data
       - create Lead job
       - send data to Lead job
       - create QA job
       - launch Lead job
       - create crowd
       - submit judgments for Lead job
       - launce QA Job
       - submit judgments for QA job
       - check results on Dashboard
    """
    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    project_name = f"Smoke E2E test {_today} {faker.zipcode()}"

    job_name_scratch = "Lead job 1"
    qa_job_name = "Job qa 1"

    # create project
    try:
        app.navigation.click_link('Create Project')
    except Exception as r:
        if "is not clickable at point" in str(r):
            time.sleep(10)
            app.navigation.click_link('Create Project')

    app.quality_flow.fill_out_project_details(name=project_name, description='E2E test', action="Confirm")
    app.mainMenu.quality_flow_page()
    assert app.quality_flow.find_project(by='name', value=project_name)
    app.quality_flow.open_project(by='name', value=project_name)

    project_id = app.quality_flow.get_project_id_from_url()

    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')
    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']
    app.quality_flow.add_project_to_tear_down_collection(project_id, username, password, team_id)

    # upload data
    data_file = get_data_file("/quiz_work_mode_switch/whatisgreater.csv")
    app.quality_flow.data.all_data.upload_data(data_file)
    time.sleep(20)
    app.navigation.refresh_page()

    # check units status
    all_units = app.quality_flow.data.all_data.get_all_units_on_page()
    assert len(all_units.loc[all_units['STATUS'] == 'NEW']) == 19

    # create lead job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='data_source')

    app.quality_flow.jobs.fill_out_job_name(job_name=job_name_scratch, action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Work Job', template='scratch')

    job_id_scratch = app.quality_flow.job.grab_job_id_from_url()

    # update cml - use api
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')
    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)
    # res = api.get_cml(team_id=team_id, job_id=job_id_scratch)
    # assert res.status_code == 200
    # assert res.json_response['message'] == 'success'

    # initial_job_config = res.json_response.get('data')
    # initial_job_config['cml'] = quiz_work_mode_switch_cml
    res = api.get_job_with_cml(team_id, job_id_scratch)
    job_with_cml = res.json_response['data']
    initial_job_config = {
        "id": job_with_cml["cmlId"],
        "version": job_with_cml["cmlVersion"],
        "teamId": team_id,
        "jobId": job_with_cml["id"],
        "flowId": job_with_cml["flowId"],
        "instructions": job_with_cml["instructions"],
        "cml": quiz_work_mode_switch_cml,
        "js": job_with_cml["js"],
        "css": job_with_cml["css"],
        "tags": job_with_cml["tags"],
        "validators": job_with_cml["validators"],
        "isValid": job_with_cml["isValid"]
    }

    res = api.put_cml(team_id=team_id, payload=initial_job_config)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    app.navigation.refresh_page()
    app.quality_flow.job.open_job_tab('design')
    app.navigation.switch_to_frame(0)
    app.verification.text_present_on_page('Step 1: Design your job')
    app.navigation.click_btn('Save')
    app.driver.switch_to.default_content()

    # preview lead job
    # app.navigation.click_link('Jobs')
    # app.quality_flow.jobs.open_job_by(by='name', value=job_name_scratch)
    # time.sleep(2)
    app.quality_flow.job.open_job_tab('settings')
    time.sleep(2)
    app.quality_flow.job.launch.select_crowd_settings(internal=True, external=False)

    internal_link = app.quality_flow.job.launch.grab_internal_link()

    time.sleep(2)
    app.navigation.click_link('Save Contributor Settings')
    time.sleep(2)
    app.quality_flow.job.launch.fill_out_price_and_row_settings(row_per_page=19)
    app.navigation.click_link('Save Prices & Rows Settings')

    time.sleep(2)
    app.navigation.click_link('Switch To Preview Mode')

    app.quality_flow.job.return_to_jobs()

    # send data to lead job
    app.navigation.click_link('Dataset')
    app.quality_flow.data.all_data.select_all_units()
    app.quality_flow.data.all_data.click_actions_menu('Send Selected Units to a Job')
    app.quality_flow.data.all_data.send_units_to_job(job_name=job_name_scratch, action='Send Selected Units to a Job')
    time.sleep(10)

    app.navigation.refresh_page()

    all_units = app.quality_flow.data.all_data.get_all_units_on_page()
    all_units_of_unit_category = all_units.iloc[:, :5]

    assert len(all_units_of_unit_category.loc[all_units_of_unit_category['STATUS'] == 'JUDGABLE']) == 19

    # open Lead job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=job_name_scratch)
    app.quality_flow.job.open_job_tab('data')
    time.sleep(3)
    data_info = app.quality_flow.job.data.get_job_dataset_info()
    assert data_info['total_units'] == 19

    app.quality_flow.job.return_to_jobs()

    # create qa job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='job_id', value=job_id_scratch)
    app.verification.text_present_on_page("Create a following QA job")

    app.quality_flow.jobs.fill_out_job_name(job_name=qa_job_name, action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Quality Assurance (QA) Job')

    # create  crowd
    app.quality_flow.job.return_to_jobs()

    # app.driver.get('https://client.integration.cf3.us/quality/projects/923456d9-4ef5-49c0-8d91-6a8dc1b93d64/curatedCrowd')
    app.navigation.click_link('Curated Contributors')
    app.verification.text_present_on_page('Copy Custom Contributors are skilled contributors we source, screen and '
                                          'recruit to match your project requirements.')

    app.navigation.click_link('Add Project')
    app.quality_flow.crowd.send_ac_project_id(project_id=86, action='Check ID')
    app.quality_flow.crowd.select_project_targeting_settings("Target all Appen Connect contributors")
    assert not app.verification.link_is_disable('Save And Add Project', method='cursor_property')
    app.navigation.click_link('Save And Add Project')
    time.sleep(10)

    # open 1 job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=job_name_scratch)
    time.sleep(2)
    app.quality_flow.job.open_job_tab('settings')

    # add external channel
    app.quality_flow.job.launch.select_crowd_settings(internal=True, external=True)
    app.navigation.click_link("Set up project ID")

    # add 86 project
    app.quality_flow.job.launch.set_up_project_id(86, action="Save And Add Project")

    # verify "Google Aztec Ads, 0 contributors assigned"
    app.verification.text_present_on_page("Google Aztec Ads, 0 contributors assigned")
    app.navigation.click_link("Save Contributor Settings")
    app.quality_flow.job.launch.fill_out_price_and_row_settings(pay_rate="DEFAULT")
    app.navigation.click_btn(btn_name="Save Prices & Rows Settings")


    # add 86 project to qa job
    app.quality_flow.job.return_to_jobs()
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=qa_job_name)
    time.sleep(3)

    app.quality_flow.job.open_job_tab('settings')
    app.quality_flow.job.launch.select_crowd_settings(internal=True, external=True)
    app.navigation.click_link("Set up project ID")

    # add 86 project
    app.quality_flow.job.launch.set_up_project_id(86, action="Save And Add Project")
    app.verification.text_present_on_page("Google Aztec Ads, 0 contributors assigned")
    app.navigation.click_link("Save Contributor Settings")
    app.quality_flow.job.launch.fill_out_price_and_row_settings(pay_rate="DEFAULT")
    app.navigation.click_btn(btn_name="Save Prices & Rows Settings")

    app.quality_flow.job.return_to_jobs()
    app.navigation.click_link('Curated Contributors')

    # assign 2 cont to job
    all_projects = app.quality_flow.crowd.get_all_curated_contributors_projects()
    print("all---",all_projects)
    app.quality_flow.crowd.select_action_for_project(by='id', value=86, action='Manage')

    all_units = app.quality_flow.crowd.get_all_units_on_page()
    units_to_select = [x[0] for x in all_units.loc[[0, 1], ['EMAIL AND AC USER ID']].values]
    app.quality_flow.crowd.select_data_units_by(by='EMAIL AND AC USER ID', values=units_to_select)
    app.quality_flow.crowd.click_actions_menu('Assign Or Unassign To A Job')
    app.quality_flow.crowd.assign_contributor_to_jobs(units_to_select[0], [job_name_scratch, qa_job_name])
    app.quality_flow.crowd.assign_contributor_to_jobs(units_to_select[1], [job_name_scratch, qa_job_name])
    app.navigation.click_link('Close')

    # launch lead job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=job_name_scratch)
    time.sleep(2)

    app.quality_flow.job.open_job_tab('settings')
    app.verification.text_present_on_page("Google Aztec Ads, 2 contributors assigned")

    app.navigation.click_link('Run Job')

    # submit judgements lead job
    qf_job_link = app.driver.current_url
    app.navigation.open_page(internal_link)
    app.user.task.wait_until_job_available_for_contributor(internal_link)
    answer_questions_on_page(app.driver, tq_dict='', mode='radio_button', values=['col1', 'col2', 'equals'])
    app.job.judgements.click_submit_judgements()

    # return to monitor page
    app.navigation.open_page(qf_job_link)

    # launch qa job
    app.quality_flow.job.return_to_jobs()
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=qa_job_name)
    time.sleep(2)
    app.quality_flow.job.open_job_tab('settings')

    app.quality_flow.job.launch.select_crowd_settings(internal=True)

    qa_internal_link = app.quality_flow.job.launch.grab_internal_link()

    time.sleep(2)
    app.navigation.click_link('Save Contributor Settings')
    app.quality_flow.job.launch.fill_out_price_and_row_settings(row_per_page=19)
    app.quality_flow.job.launch.allow_contributor_qa_their_own_work(allow=True)
    time.sleep(2)
    app.navigation.click_link('Save Prices & Rows Settings')

    time.sleep(2)
    app.navigation.click_link('Switch To Preview Mode')

    time.sleep(2)
    app.navigation.click_link('Run Job')

    # submit qa job
    qf_job_link = app.driver.current_url
    app.navigation.open_page(qa_internal_link)
    app.user.task.wait_until_job_available_for_contributor(qf_job_link, max_attempts=720)
    feedback_judgements_qa_job(app, random_reject=5)
    app.job.judgements.click_submit_judgements()

    app.navigation.open_page(qf_job_link)

    # check project dataset
    app.quality_flow.job.return_to_jobs()
    time.sleep(60)

    app.navigation.click_link('Dataset')

    app.quality_flow.data.all_data.customize_data_table_view(select_fields=['unit'])
    all_units = app.quality_flow.data.all_data.get_all_units_on_page()
    assert len(all_units.loc[all_units['STATUS'] == 'SUBMITTED']) == 19

    app.quality_flow.data.all_data.customize_data_table_view(select_fields=['latest'])
    all_units = app.quality_flow.data.all_data.get_all_units_on_page()
    assert len(all_units.loc[all_units['REVIEW RESULT'] == 'REJECTED']) == 5
    assert len(all_units.loc[all_units['REVIEW RESULT'] == 'ACCEPTED']) == 14

    dataset_info = app.quality_flow.data.get_dataset_info(judgments=False)
    assert dataset_info['total_units'] == 19
    assert dataset_info['new_units'] == 0

    # check dashboard
    app.navigation.click_link('Dashboards')
    app.quality_flow.dashboard.open_tab('quality')
    # TODO add dashboard verification - number of judgements

    time.sleep(180)
    app.navigation.refresh_page()
    summary = app.quality_flow.dashboard.project_quality.get_quality_flow_summary()
    assert summary['REJECTED'] == 5
    assert summary['ACCEPTED'] == 14

    summary = app.quality_flow.dashboard.project_quality.get_leading_job_statistics()
    assert summary['TOTAL UNITS SUBMITTED'] == 19
    assert summary['TOTAL QAED UNITS'] == 19
    assert summary['REJECTED'] == 5
    assert summary['ACCEPTED'] == 14

    app.quality_flow.dashboard.open_tab('productivity')
    progress = app.quality_flow.dashboard.project_productivity.get_progress_details()
    assert len(progress) == 2
    assert progress['Lead job 1'] == {'completed': '100%',
                                      'total_units': 19,
                                      'not_started': 0,
                                      'working': 0,
                                      'submitted': 19,
                                      'resolving': 0}

    assert progress['Job qa 1'] == {'completed': '100%',
                                    'total_units': 19,
                                    'not_started': 0,
                                    'working': 0,
                                    'submitted': 19,
                                    'resolving': 0}


