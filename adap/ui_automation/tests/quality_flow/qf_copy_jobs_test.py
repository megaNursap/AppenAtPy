import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject, QualityFlowApiWork
from adap.api_automation.utils.data_util import get_test_data

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]


@pytest.fixture(scope="module")
def qf_login(app):
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')

    app.user.login_as_customer(username, password)
    app.mainMenu.quality_flow_page()
    time.sleep(10)


@pytest.fixture(scope="module")
def new_project():
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)
    team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

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
    payload = {"title": "New WORK job",
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

    return {
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version'],
        "jobs": [res.json_response['data']['id']],
        "job_names": ['New WORK job'],
        "project_name": project_name,
        "job_api": job_api
    }


def test_qf_copy_lead_job(app, new_project, qf_login):
    """
    verify user is able to copy job
    """
    app.quality_flow.open_project(by='name', value=new_project['project_name'])

    # create lead job
    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.open_job_by(by='name', value=new_project['job_names'][0])

    parent_job = app.driver.window_handles[0]
    new_job_name = "Copy job 1"

    app.quality_flow.job.click_copy_job(new_project['job_names'][0])

    print('Job Name: ', new_project['job_names'][0])
    app.quality_flow.job.copy_job(new_job_name=new_job_name,
                                  data_source=None,
                                  copy_job_design=True,
                                  launch_settings=True,
                                  contributors=True,
                                  action='Copy')

    new_job = app.driver.window_handles[1]
    app.navigation.switch_to_window(new_job)

    time.sleep(5)
    app.quality_flow.job.open_job_tab('design')
    app.navigation.switch_to_frame(0)
    app.verification.text_present_on_page("Show data to contributors here")
    app.driver.switch_to.default_content()

    app.quality_flow.job.open_job_tab('settings')
    app.verification.text_present_on_page("Customize your job settings")
    # app.verification.text_present_on_page("Curated Crowd")
    # app.verification.text_present_on_page("Set up the Appen Connect Project ID")

    app.navigation.switch_to_window(parent_job)
    app.verification.text_present_on_page("New WORK job")

# TODO: copy job with/out different data sources
# TODO: copy job with/out launch settings
# TODO: copy job with/out contributors
