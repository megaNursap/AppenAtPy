import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor, QualityFlowApiWork, \
    QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file

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
        "job_names": ['New  WORK job'],
        "project_name": project_name,
    }


@pytest.mark.regression_qf
def test_upload_test_question(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])
    sample_file = get_data_file("/test_questions/image-annotation-source-for-ADAP-TQ-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)
    app.quality_flow.navigate_to_design_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.open_job_tab('quality')
    app.verification.text_present_on_page('Ensure Quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-for-upload-part-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units == 4


@pytest.mark.regression_qf
def test_upload_more_test_question(app, setup, qf_login):
    app.navigation.click_link('Add Test Questions')
    app.quality_flow.job.quality.select_action_from_popup('Upload Test Questions')
    app.navigation.click_link('Select')

    sample_file = get_data_file("/test_questions/tq-for-upload-part-2.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units == 8












