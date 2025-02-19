import datetime
import pytest
from faker import Faker

from adap.api_automation.services_config.qf_api_logic import faker
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_data_file, get_test_data
from adap.ui_automation.utils.selenium_utils import sleep_for_seconds

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              mark_env]

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']
icm_name = faker.name()
filter_name = f"Filter_{faker.zipcode()}"


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)


""" This setup is used for creating project through the API call """


@pytest.fixture(scope="module")
def qf_create_project():
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


@pytest.mark.regression_qf
def test_qf_save_filter_data(app, qf_create_project, qf_login):
    app.quality_flow.navigate_to_dataset_page_by_project_id(qf_create_project['project_id'])
    sample_file = get_data_file("/test_questions/image-annotation-source-for-ADAP-TQ-1.csv")
    app.quality_flow.data.all_data.upload_data(sample_file)
    app.navigation.refresh_page()

    initial_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    initial_num_rows = initial_units_on_page.shape[0]

    app.quality_flow.data.all_data.select_filter('unit', 'Unit ID', 'Equals', '1_1', 'Apply')

    app.verification.text_present_on_page('1 Filter')
    filtered_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    assert len(filtered_units_on_page.loc[filtered_units_on_page['UNIT ID'] == '1_1']) == 1

    app.navigation.click_btn_by_text('1 Filter')

    app.quality_flow.data.all_data.save_filters(filter_name, 'Save')

    app.verification.text_present_on_page(f'Saved {filter_name} as filter set name successfully')

    filtered_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    assert len(filtered_units_on_page.loc[filtered_units_on_page['UNIT ID'] == '1_1']) == 1

    app.quality_flow.data.all_data.clear_filters(filter_name)
    sleep_for_seconds(5)

    current_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    current_units_rows = current_units_on_page.shape[0]
    assert current_units_rows == initial_num_rows


@pytest.mark.regression_qf
def test_qf_select_saved_filter(app, qf_login):
    app.quality_flow.data.all_data.apply_saved_filter(filter_name, 'Apply')
    sleep_for_seconds(5)

    filtered_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    filtered_num_rows = filtered_units_on_page.shape[0]

    assert len(filtered_units_on_page.loc[filtered_units_on_page['UNIT ID'] == '1_1']) == 1
    assert filtered_num_rows == 1


@pytest.mark.regression_qf
def test_qf_delete_saved_filter(app, qf_login):
    filtered_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    filtered_num_rows = filtered_units_on_page.shape[0]

    app.quality_flow.data.all_data.delete_saved_filter(filter_name, 'Delete')
    app.verification.text_present_on_page(f'Deleted {filter_name} filter set Successfully')
    sleep_for_seconds(5)

    after_deleted_filter_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    after_deleted_filter_rows = after_deleted_filter_units_on_page.shape[0]
    assert after_deleted_filter_rows != filtered_num_rows
