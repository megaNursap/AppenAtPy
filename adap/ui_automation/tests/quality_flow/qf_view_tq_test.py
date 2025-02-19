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

@pytest.fixture(scope="function")
def create_new_project(app):
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

@pytest.fixture(scope="function")
def create_job(new_project):
    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)

    project_id = new_project['project_id']

    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    payload = {"title": f"work {_today}{faker.zipcode()}", "projectId": project_id, "type": "WORK"}
    res = api.post_create_job_v2(team_id=team_id, payload=payload)

    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Job is not is created"

    return {
        "job_id": data['id']
    }

@pytest.fixture(scope="function")
def create_new_job_segmented(create_new_project):
    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)

    project_id = create_new_project['project_id']

    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    payload = {"title": f"work {_today}{faker.zipcode()}", "projectId": project_id, "type": "WORK"}
    res = api.post_create_job_v2(team_id=team_id, payload=payload)

    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Job is not is created"

    return {
        "job_id": data['id']
    }


@pytest.mark.regression_qf
def test_view_test_question(app, setup, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(setup['project_id'])
    sample_file = get_data_file("/test_questions/image-annotation-source-for-ADAP-TQ-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)
    app.quality_flow.navigate_to_design_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.open_job_tab('quality')

    app.driver.implicitly_wait(5)

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-for-upload-part-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(30)

    all_units = app.quality_flow.job.quality.get_all_test_question_units_on_page()

    print("all_units ", all_units)

    question_id = all_units['QUESTION ID'].tolist()[0]

    print("question_id ", question_id)

    app.navigation.click_link(question_id)

    app.verification.text_present_on_page("Question ID " + question_id)
    app.verification.text_present_on_page("show Data")
    app.verification.text_present_on_page("show Statistics")
    app.verification.text_present_on_page("show Contributor Info")
    app.verification.text_present_on_page("Edit test question")

    app.navigation.click_btn_by_text("show Data")
    app.verification.text_present_on_page("Source Data")
    app.navigation.click_btn_by_text("hide Data")
    app.verification.text_present_on_page("Test Question Answer")

    app.navigation.click_btn_by_text("show Data")
    app.verification.text_present_on_page("Source Data")
    app.navigation.click_btn_by_text("hide Data")
    app.verification.text_present_on_page("Test Question Answer")

    app.navigation.click_btn_by_text("show Statistics")
    app.verification.text_present_on_page(
        "Choose a question from the list to display its distribution of answers. Stats are updated every 30 seconds.")
    app.verification.text_present_on_page("Question")
    app.navigation.click_btn_by_text("hide Statistics")
    app.verification.text_present_on_page("Test Question Answer")

    app.navigation.click_btn_by_text("show Contributor Info")
    app.verification.text_present_on_page("No Items")
    app.navigation.click_btn_by_text("hide Contributor Info")
    app.verification.text_present_on_page("Test Question Answer")

    app.navigation.click_btn_by_text("Edit test question")
    app.verification.text_present_on_page("Edit Answers & Reasons to your Test Questions")
    app.verification.text_present_on_page("Overall Test Question Settings")
    app.verification.text_present_on_page("Test Question Mode")
    app.verification.text_present_on_page("Quiz + Work Mode")
    app.verification.text_present_on_page("Quiz Mode Only")
    app.verification.text_present_on_page("Work Mode Only")
    app.verification.text_present_on_page("Hide Answer")
    app.verification.text_present_on_page("Cancel")
    app.verification.text_present_on_page("Save Changes")


@pytest.mark.regression_qf
def test_enable_disable_test_question(app, setup, qf_login):
    app.quality_flow.navigate_to_design_page_by_project_id(setup['project_id'], setup['job_id'][0])

    app.quality_flow.job.open_job_tab('quality')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_all_units()

    app.quality_flow.job.quality.click_actions_menu('Disable Selected')

    app.navigation.click_link('Confirm')

    app.driver.implicitly_wait(2)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(30)

    is_enabled = app.quality_flow.job.quality.is_all_test_questions_enabled()

    assert is_enabled == False, "Not all switches are 'false'"

############################################################################################################

@pytest.mark.regression_qf
@pytest.mark.dependency
def test_pagination_functionality(app, new_project, upload_dataset, create_job, qf_login):
    # Test case ID: 134504
    # Steps:
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')
    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3'])

    app.navigation.click_link('Next: Set up Test Questions')

    app.navigation.click_link('Save And Exit')

    all_units = app.quality_flow.job.quality.get_all_test_question_units_on_page()

    print('all_units ', all_units)

    app.verification.text_present_on_page("Show 30 Items")


def test_maximum_questions_limit(app, new_project, upload_dataset, create_job):
    # Need to Know the limit

    # Test case ID: 134505
    # Steps:
    # 1. Add Test Questions until the maximum limit is reached.
    # 2. Verify that no more questions can be added.
    pass


@pytest.mark.regression_qf
@pytest.mark.dependency(depends=['test_pagination_functionality'])
def test_dataset_marked_as_test_question(app, new_project, upload_dataset, create_job, qf_login):
    # Test case ID: 130223
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    app.driver.implicitly_wait(10)
    app.verification.text_present_on_page("GOLDEN")


@pytest.mark.regression_qf
def test_click_test_question_in_dataset(app, new_project, upload_dataset, create_job, qf_login):
    # Test case ID: 134437
    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'],
                                                                           create_job['job_id'])
    app.verification.text_present_on_page("Question ID")
    app.verification.text_present_on_page("Linked Unit Id")
    app.verification.text_present_on_page("Enable ?")
    app.verification.text_present_on_page("Contested %")
    app.verification.text_present_on_page("Missed %")
    app.verification.text_present_on_page("Judgments")
    app.verification.text_present_on_page("Last Updated")
    app.verification.text_present_on_page("Mode")
    app.verification.text_present_on_page("Hide Answer")


@pytest.mark.regression_qf
def test_dataset_unit_group_marked_as_test_question(app, create_new_project, create_new_job_segmented):
    # Test case ID: 134793
    # Steps:
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_dataset_page_by_project_id(create_new_project['project_id'])

    segmented_file = get_data_file("/qf_data/audio_tx_sample_seg_2_segroup_3.csv")
    app.quality_flow.data.all_data.upload_data(segmented_file)

    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(create_new_project['project_id'],
                                                                           create_new_job_segmented['job_id'])

    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3'])

    app.navigation.click_link('Next: Set up Test Questions')

    app.navigation.click_link('Save And Exit')

    all_units = app.quality_flow.job.quality.get_all_test_question_units_on_page()

    print('all_units ', all_units)

    assert len(all_units) >2 , "Test Question not added"