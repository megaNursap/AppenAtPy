"""
https://appen.atlassian.net/browse/QED-1417
Cover below cases:
https://appen.spiraservice.net/5/TestCase/1155.aspx
https://appen.spiraservice.net/5/TestCase/1156.aspx
https://appen.spiraservice.net/5/TestCase/1157.aspx
https://appen.spiraservice.net/5/TestCase/1158.aspx
https://appen.spiraservice.net/5/TestCase/1159.aspx
https://appen.spiraservice.net/5/TestCase/1160.aspx
1. check the play button
2. check next/previous frame buttons
3. check next10/previous10 frame buttons and others
"""
import time
import pytest

from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['26_frame_job']
USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER, password=PASSWORD)


@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_video_control_is_displayed(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()

    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    num_frames = lidar.video_control.get_total_frames_number()

    assert lidar.video_control.get_current_frame_number() == 1
    assert lidar.video_control.get_total_frames_number() == 26
    assert lidar.video_control.get_current_progress_bar_status() == float(0)
    lidar.video_control.click_btn('next')
    assert lidar.video_control.get_current_frame_number() == 2
    assert str(lidar.video_control.get_current_progress_bar_status()) == format(float(100/(num_frames-1)))

    lidar.video_control.click_btn('next10')
    assert lidar.video_control.get_current_frame_number() == 12
    assert str(lidar.video_control.get_current_progress_bar_status()) == format(float(100/(num_frames-1)*11))

    lidar.video_control.click_btn('previous10')
    assert lidar.video_control.get_current_frame_number() == 2
    assert str(lidar.video_control.get_current_progress_bar_status()) == format(float(100/(num_frames-1)))

    lidar.video_control.click_btn('previous')
    assert lidar.video_control.get_current_frame_number() == 1
    assert lidar.video_control.get_current_progress_bar_status() == float(0)

    lidar.video_control.click_btn('play')
    time.sleep(5)
    app.driver.close()


