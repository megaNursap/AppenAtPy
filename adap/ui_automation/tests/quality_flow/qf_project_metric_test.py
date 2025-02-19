import pytest

from adap.api_automation.utils.data_util import get_test_data, get_data_file
from adap.ui_automation.lidar.support.image_diff import compare_images

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]


@pytest.fixture(scope="module")
def qf_login(app):
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    project = get_test_data('qf_user', 'default_project')['dashboard']
    project_id = project['projectId']

    app.user.login_as_customer(username, password)
    app.quality_flow.open_project_by_id(project_id)


def test_qf_verify_progress_data(app, qf_login):
    """
    verify user can see Progress data on project dashboard page
    """
    app.navigation.click_link('Dashboard')
    app.quality_flow.dashboard.open_tab('productivity')
    progress = app.quality_flow.dashboard.project_productivity.get_progress_details()

    assert progress == {
        "Metrics API automation test data (DON\u0027T USE THIS!) work job A1": {
            "completed": "89%",
            "total_units": 28,
            "not_started": 2,
            "working": 1,
            "submitted": 25,
            "resolving": 0
        },
        "Metrics API automation test data (DON\u0027T USE THIS!) QA job B2": {
            "completed": "100%",
            "total_units": 7,
            "not_started": 0,
            "working": 0,
            "submitted": 7,
            "resolving": 0
        },
        "Metrics API automation test data (DON\u0027T USE THIS!) QA job C2 FL": {
            "completed": "62%",
            "total_units": 16,
            "not_started": 3,
            "working": 0,
            "submitted": 10,
            "resolving": 3
        },
        "Metrics API automation test data (DON\u0027T USE THIS!) work job B1": {
            "completed": "33%",
            "total_units": 21,
            "not_started": 5,
            "working": 9,
            "submitted": 7,
            "resolving": 0
        }
    }


def test_qf_verify_throughput_data(app, qf_login):
    """
    verify user can see Progress data on project dashboard page
    """
    app.navigation.click_link('Dashboard')
    app.quality_flow.dashboard.open_tab('productivity')

    app.quality_flow.dashboard.project_productivity.set_throughput_filter(
        date_start='2022-11-01 00:00',
        date_end='2022-12-01 00:00',
        time_slot='1 Week',
        action='Apply Filters'
    )

    new_screenshot = app.quality_flow.dashboard.project_productivity.get_throughput_judgements_screenshot(
        app.temp_path_file,
        "/actual_metrics.png")

    expected_screenshot = get_data_file("/qf_data/metrics_1week.png")
    score = compare_images(expected_screenshot, new_screenshot)
    assert score > 0.8, f"Screenshot does not match the baseline"
