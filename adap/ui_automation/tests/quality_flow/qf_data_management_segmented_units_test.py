import datetime
import os
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file, count_row_in_file

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              mark_env]

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']


# project creation was changed
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


@pytest.mark.qf_ui_smoke
@pytest.mark.dependency()
def test_qf_segmented_data_upload_csv_file(app, qf_login, new_project):
    """
    verify user can upload csv file
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.verification.text_present_on_page('all data')
    app.verification.text_present_on_page('data group')
    app.verification.text_present_on_page('deleted')

    app.verification.current_url_contains('/dataset')

    sample_file = get_data_file("/qf_data/audio_tx_sample_seg_2_segroup_3.csv")
    app.quality_flow.data.all_data.upload_data(sample_file)

    rows_in_file = count_row_in_file(sample_file)
    time.sleep(10)
    app.navigation.refresh_page()

    dataset_info = app.quality_flow.data.get_dataset_info(segmented=True)
    assert dataset_info['total_unit_groups'] == 3
    assert dataset_info['new_units'] == rows_in_file
    assert dataset_info['total_units'] == rows_in_file
    assert dataset_info['assigned_units'] == 0
    assert dataset_info['judgeable_units'] == 0

    app.navigation.click_link('Unit Groups')
    unit_groups_data = app.quality_flow.data.all_data.get_all_units_on_page(segmented_groups=True)
    assert unit_groups_data.shape[0] == 3

    app.navigation.click_link('Units')
    units_data = app.quality_flow.data.all_data.get_all_units_on_page()
    assert units_data.shape[0] == rows_in_file


@pytest.mark.dependency(depends=["test_qf_segmented_data_upload_csv_file"])
def test_qf_add_more_segmented_data(app, qf_login):
    file_name = get_data_file("/qf_data/audio_tx_sample_seg_2_segroup_add.csv")
    rows_in_file = count_row_in_file(file_name)

    if not app.verification.wait_untill_text_present_on_the_page('Add More Data', max_time=3):
        # no data, upload csv file
        app.quality_flow.data.all_data.upload_data(file_name)
        time.sleep(3)
        app.navigation.refresh_page()

    initial_dataset_info = app.quality_flow.data.get_dataset_info()

    app.navigation.click_link('Add More Data')
    app.quality_flow.data.all_data.upload_data(file_name)

    time.sleep(6)
    app.navigation.refresh_page()

    app.navigation.click_link('Unit Groups')
    dataset_info = app.quality_flow.data.get_dataset_info(segmented=True)
    assert dataset_info['total_unit_groups'] == 4
    assert dataset_info['new_units'] == initial_dataset_info['new_units'] + rows_in_file
    assert dataset_info['total_units'] == initial_dataset_info['total_units'] + rows_in_file
    assert dataset_info['assigned_units'] == 0
    assert dataset_info['judgeable_units'] == 0

    unit_groups_data = app.quality_flow.data.all_data.get_all_units_on_page(segmented_groups=True)
    assert unit_groups_data.shape[0] == 4

    app.navigation.click_link('units')
    units_data = app.quality_flow.data.all_data.get_all_units_on_page()
    assert units_data.shape[0] == initial_dataset_info['total_units'] + rows_in_file
