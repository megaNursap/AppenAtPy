"""
JIRA:https://appen.atlassian.net/browse/QED-1129
Cover below cases:
1. check cuboid display on front,top,side view
"""
import time
import pytest
from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['normal_job2']
USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER, password=PASSWORD)


@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_multiple_view(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()

    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    lidar.sidepanel.select_shape_label()
    lidar.multiview.cuboid_displayed_on_front_view()
    lidar.multiview.cuboid_displayed_on_top_view()
    lidar.multiview.cuboid_displayed_on_side_view()
    app.driver.close()
