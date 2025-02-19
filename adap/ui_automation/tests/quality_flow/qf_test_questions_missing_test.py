import datetime
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject, QualityFlowApiWork
from adap.api_automation.utils.data_util import get_test_data, get_data_file
from adap.ui_automation.tests.quality_flow.qf_add_contributor_to_new_group_test import faker
from adap.ui_automation.utils.selenium_utils import find_elements

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_ui_smoke,
              mark_env]

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']

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
def upload_dataset(app, qf_login,new_project):

    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    sample_file = get_data_file("/test_questions/image-annotation-upload-dataset.csv")
    app.quality_flow.data.all_data.upload_data(sample_file)
    time.sleep(5)

@pytest.fixture(scope="function")
def create_job(new_project):
    api = QualityFlowApiWork()
    api.get_valid_sid(username, password)
    project_id = new_project['project_id']

    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    all_CML = '<cml:radios label="what doing" validates="required" gold="true"> <cml:radio label="RUNNING" /> <cml:radio label="JOGGING" /> </cml:radios>'

    payload = {"title": f"work {_today}{faker.zipcode()}", "projectId": project_id, "type": "WORK",
               "jobCml": {
    "id": "string",
    "version": 0,
    "teamId": "string",
    "jobId": "string",
    "instructions": "string",
    "cml": all_CML,
    "js": "string",
    "css": "string",
    "validators": [
      "string"
    ]}}
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
@pytest.mark.order(1)
@pytest.mark.dependency()
def test_change_column_order(app, new_project, upload_dataset, create_job, qf_login):
    """Testmo Test case ID: 134931"""

    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-shuffled-columns.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    time.sleep(5)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units > 0

@pytest.mark.regression_qf
@pytest.mark.dependency(depends=['test_change_column_order'])
def test_select_test_questions_list(app, new_project, upload_dataset, create_job, qf_login):
    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.navigation.click_checkbox_by_xpath(app.driver, "(//table[@role='table'])[1]/thead/tr/th/div/div")
    app.verification.text_present_on_page('units selected')


@pytest.mark.regression_qf
def test_multiple_correct_answers(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 130210
     1. Upload a CSV file with multiple answers in {fieldname_gold}.
     2. Verify that all answers are accepted as correct.
    """

    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-multiple_answer-golden-columns.csv") 

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >= 0


@pytest.mark.regression_qf
def test_empty_values_gold_field(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134440
    Steps:
    1. Upload a CSV file with empty values in {fieldname_gold}.
    2. Verify the system handles the empty values appropriately."""
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-empty-golden-columns.csv")  

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    assert all_units == 2



@pytest.mark.regression_qf
def test_empty_values_reason_field(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134921
    Steps:
    1. Upload a CSV file with empty values in {fieldname_gold_reason}.
    2. Verify the system processes the upload without issues."""
    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-empty-reason-columns.csv")  

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >= 0


@pytest.mark.regression_qf
def test_set_false_gold_column(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 130211
    Steps:
    1. Upload a CSV file with FALSE in the {_golden} column.
    2. Verify that the question is marked correctly."""
    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-false-golden-columns.csv")  

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units == 2


@pytest.mark.regression_qf
def test_empty_gold_column(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134441
    Steps:
    1. Upload a CSV file with an empty {_golden} column.
    2. Verify that the system handles the empty column correctly."""
    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-empty-golden-columns.csv")  

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >= 0


@pytest.mark.regression_qf
def test_duplicated_row(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134789
    Steps:
    1. Upload a CSV file with duplicated rows.
    2. Verify that the system identifies and handles duplicates."""
    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-duplicate-rows.csv")  

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >=2



@pytest.mark.regression_qf
def test_view_test_questions_list_after_upload(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134554
    Steps:
    1. Upload a CSV file.
    2. Navigate to the Quality tab.
    3. Verify that all test questions are listed."""
    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

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
def test_check_columns_in_uploaded_list(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134555
    Steps:
    1. Upload a CSV file.
    2. Check the columns displayed in the TQ list.
    3. Verify that all expected columns are present."""
    app.driver.refresh()
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-for-upload-part-1.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

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
def test_invalid_file_upload(app, create_new_project,create_new_job_segmented, qf_login):
    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(create_new_project['project_id'], create_new_job_segmented['job_id'])
    app.driver.implicitly_wait(10)
    app.navigation.click_bytext('Upload Test Questions')
    app.driver.implicitly_wait(5)
    app.verification.text_present_on_page(".csv")

@pytest.mark.regression_qf
# Delete test question functionality is not available in the UI
@pytest.mark.xfail()
def test_remove_uploaded_csv(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134508
    Steps:
    1. Upload a CSV file.
    2. Remove the uploaded CSV file.
    3. Verify it is no longer in the system."""
    pass

@pytest.mark.regression_qf
@pytest.mark.dependency()
def test_check_upload_progress(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134509
    Steps:
    1. Start uploading a CSV file.
    2. Verify the progress bar is displayed.
    3. Verify the progress bar updates as the upload progresses."""

    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')

    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-shuffled-columns.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)
    time.sleep(2)
    app.quality_flow.job.open_processes_running_in_backgroud()

    process = app.quality_flow.latest_process_running_background()

    assert process in ["UPLOAD_TEST_QUESTION_UPDATE","UPLOAD_TEST_QUESTION"]

@pytest.mark.regression_qf
@pytest.mark.dependency(depends=['test_check_upload_progress'])
def test_columns_and_filters_in_background(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134510"""
    app.verification.text_present_on_page("batch job id")
    app.verification.text_present_on_page("type")
    app.verification.text_present_on_page("status")
    app.verification.text_present_on_page("progress")
    app.verification.text_present_on_page("Filters")
    app.verification.text_present_on_page("Columns")
    app.verification.text_present_on_page("Processes Running In Background")

@pytest.mark.regression_qf
def test_check_all_columns_in_background(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134511"""
    headers = find_elements(app.driver,"//table[@role='table']/thead/tr/th/div/div")
    for header in headers:
        print(header.text,"1234567890selvam")
    expected_headers = [
    'failed',
    'unit id',
    'status',
    'created at',
    'question id',
    'batch job id',
    'type',
    'status',
    'progress',
    'job',
    'created at',
    'updated at',
    'active until',
    'actions',''
]
    for header in headers:
        assert header.text.strip().lower() in expected_headers, f"Unexpected header text: {header.text.strip()}"

@pytest.mark.regression_qf
def test_remove_mandatory_columns(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134442
    Steps:
    1. Attempt to upload a CSV without mandatory columns.
    2. Verify an error or warning is generated."""
    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.navigation.click_element_by_xpath(app.driver,
                                          "//*[text()='Processes Running In Background']/following-sibling::*/a")
    app.driver.implicitly_wait(5)
    app.mainMenu.quality_flow_page()
    app.quality_flow.navigate_to_design_page_by_project_id(project_id=new_project['project_id'],
                                                           job_id=create_job['job_id'])

    app.quality_flow.job.open_job_tab('quality')


    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-without-mandatory-column.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units == 0



@pytest.mark.regression_qf
def test_change_answers_only_column(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 130264
    Steps:
    1. Upload a CSV file with changes only in Answers column.
    2. Verify that only the answers are updated."""
    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.mainMenu.quality_flow_page()

    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'], create_job['job_id'])
    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-before-change-answer.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >= 1

    app.navigation.click_element_by_xpath(app.driver,"(//*[contains(text(), 'Reports')])[2]")
    app.navigation.click_bytext("Upload Test Question Report")

    sample_file = get_data_file("/test_questions/tq-after-change-answer.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >= 1


@pytest.mark.regression_qf
def test_change_reasons_column_only(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134424
    Steps:
    1. Upload a CSV file with changes only in Reasons column.
    2. Verify that only the reasons are updated."""
    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.mainMenu.quality_flow_page()

    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'],
                                                                           create_job['job_id'])
    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-before-change-reason.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units == 2

    app.navigation.click_element_by_xpath(app.driver,"(//*[contains(text(), 'Reports')])[2]")
    app.navigation.click_bytext("Upload Test Question Report")
    sample_file = get_data_file("/test_questions/tq-after-change-reason.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)

    app.driver.implicitly_wait(20)

    app.navigation.refresh_page()

    app.driver.implicitly_wait(10)

    all_units = app.quality_flow.job.quality.get_row_from_table()

    print('all_units ', all_units)

    assert all_units >= 1


@pytest.mark.regression_qf
@pytest.mark.dependency()
def test_enable_disable_tq(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134605"""

    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'], create_job['job_id'])
    app.driver.implicitly_wait(10)
    app.driver.implicitly_wait(10)
    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-enable_disable_tq.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)
    app.driver.implicitly_wait(10)
    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.quality_flow.job.quality.enable_all_test_questions()
    app.navigation.click_bytext("Confirm")
    app.driver.implicitly_wait(10)
    app.verification.text_present_on_page('You have successfully enabled the selected test questions.')
    app.quality_flow.job.quality.disable_all_test_questions()
    app.navigation.click_bytext("Confirm")
    app.driver.implicitly_wait(10)
    app.verification.text_present_on_page('You have successfully disabled the selected test questions.')

@pytest.mark.regression_qf
@pytest.mark.dependency(depends=["test_enable_disable_tq"])
def test_enable_disable_all_tq(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134606"""

    app.navigation.refresh_page()
    app.driver.implicitly_wait(10)
    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'],
                                                                           create_job['job_id'])
    app.driver.implicitly_wait(10)
    app.driver.implicitly_wait(10)
    app.quality_flow.job.quality.select_action('Upload Test Questions')

    sample_file = get_data_file("/test_questions/tq-enable_disable_all_tq.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)
    app.driver.implicitly_wait(10)
    app.driver.refresh()
    app.driver.implicitly_wait(10)
    app.quality_flow.job.quality.enable_all_test_questions()
    app.navigation.click_bytext("Confirm")
    app.driver.implicitly_wait(10)
    app.verification.text_present_on_page('You have successfully enabled the selected test questions.')
    app.quality_flow.job.quality.disable_all_test_questions()
    app.navigation.click_bytext("Confirm")
    app.driver.implicitly_wait(10)
    app.verification.text_present_on_page('You have successfully disabled the selected test questions.')

@pytest.mark.regression_qf
@pytest.mark.dependency(depends=['test_enable_disable_tq'])
def test_enable_disable_test_questions(app, new_project, upload_dataset, create_job, qf_login):
    """ Test case ID: 130203"""

    """Steps are same as test_enable_disable_tq"""
    pass


@pytest.mark.regression_qf
def test_mark_all_reviewed_tqs_without_changes(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134878"""
    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'], create_job['job_id'])
    app.driver.implicitly_wait(10)
    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_1', '1_2', '1_3'])

    app.navigation.click_link('Next: Set up Test Questions')
    app.driver.implicitly_wait(10)
    app.navigation.click_link('Save And Exit')
    app.driver.implicitly_wait(5)
    app.navigation.click_element_by_xpath(app.driver,"//a[text()='Confirm']")
    app.driver.implicitly_wait(10)
    app.navigation.click_element_by_xpath(app.driver,"//*[@id='app']/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div/table/tbody/tr[1]/td[2]/a")
    app.driver.implicitly_wait(5)
    app.verification.text_present_on_page("Pass Review")
    app.navigation.click_bytext("Pass Review")
    app.verification.text_present_on_page("Review Submitted Successfully")


@pytest.mark.regression_qf
def test_review_without_marking_with_changes(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134882
    1. Review TQs with changes.
    2. Do not mark them as reviewed.
    3. Verify they remain unmarked.
"""
    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'], create_job['job_id'])

    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_4', '1_5', '1_6'])

    app.navigation.click_link('Next: Set up Test Questions')
    app.driver.implicitly_wait(10)
    app.navigation.click_link('Save And Exit')
    app.driver.implicitly_wait(5)
    app.navigation.click_link("Confirm")
    app.driver.implicitly_wait(10)
    app.navigation.click_element_by_xpath(app.driver, "//*[@id='app']/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div/table/tbody/tr[1]/td[2]/a")
    app.driver.implicitly_wait(5)
    app.navigation.click_bytext("Edit test question")
    app.driver.implicitly_wait(5)
    app.navigation.click_element_by_xpath(app.driver, "//*[@id='app']/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/label[2]/div")
    app.navigation.click_bytext("Save Changes")
    assert app.verification.text_present_on_page("Your test questions have been saved.")
    


@pytest.mark.regression_qf
def test_review_without_marking_without_changes(app, new_project, upload_dataset, create_job, qf_login):
    """Test case ID: 134883
    Steps:
    1. Review TQs without changes.
    2. Do not mark them as reviewed.
    3. Verify they remain unmarked."""

    app.quality_flow.navigate_to_job_quality_page_by_project_id_and_job_id(new_project['project_id'],
                                                                           create_job['job_id'])
    app.quality_flow.job.quality.select_action('Add Test Questions')

    app.driver.implicitly_wait(10)

    app.quality_flow.job.quality.select_units_checkbox_by_unit_ids(['1_7', '1_8', '1_9'])

    app.navigation.click_link('Next: Set up Test Questions')
    app.driver.implicitly_wait(5)
    app.navigation.click_bytext('Save And Exit')
    app.driver.implicitly_wait(5)
    app.navigation.click_bytext('Confirm')
    app.driver.implicitly_wait(10)
    app.navigation.click_element_by_xpath(app.driver,
                                          "//*[@id='app']/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div/table/tbody/tr[1]/td[2]/a")
    app.driver.implicitly_wait(5)
    app.navigation.click_element_by_xpath(app.driver,"//*[@id='js-modal-overlay']/div/div[2]/div/div[2]/div[2]/div[1]/div")
    app.verification.text_present_on_page("Review Submitted Successfully")
