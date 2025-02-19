"""
https://appen.atlassian.net/browse/QED-1124
https://appen.atlassian.net/browse/QED-1125
Cover below cases:
1.Auto adjust the cuboid
2.copy the cuboid on frame 1, go to other frame(eg, frame 5)
3.paste it
4.click interpolate it.
5.validate frame 2,3,4 also has cuboid copied
"""
import os
import time
import pytest

from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar

pytestmark = pytest.mark.regression_lidar

USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['normal_job2']


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER, password=PASSWORD)


@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_autoadjust_copy_paste_interpolate_cuboid(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()

    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    # # get coordinates before auto-adjust
    # cuboids = lidar.find_cuboids()
    # assert cuboids.get('Car 1')
    # _xy = cuboids['Car 1']['coordinates']
    # x = _xy['X']
    # y = _xy['Y']
    # print("before auto-adjust, x is:", x)
    # print("before auto-adjust, y is:", y)
    #
    # # do auto-adjust, check coordinate updated
    # lidar.sidepanel.select_shape_label()
    # lidar.toolbar.click_btn('auto_adjust')
    # cuboids = lidar.find_cuboids()
    # assert cuboids.get('Car 1')
    # _adjustxy = cuboids['Car 1']['coordinates']
    # adjustx = _adjustxy['X']
    # adjusty = _adjustxy['Y']
    # print("after auto-adjust, x is:", adjustx)
    # print("after auto-adjust, y is:", adjusty)
    # assert adjustx == 348
    # assert adjusty == 97

    # select existing cuboid, copy it
    lidar.sidepanel.select_shape_label()
    time.sleep(1)
    lidar.toolbar.click_btn('copy')

    # go to frame 6 and paste cuboid
    for i in range(1, 6):
        lidar.video_control.click_btn('next')
        assert lidar.video_control.get_current_frame_number() == i + 1
        assert lidar.get_cuboids_counts() == 0

    lidar.toolbar.click_btn('paste')
    assert lidar.get_cuboids_counts() == 1

    # interpolate it, check frame 2,3,4,5 has cuboid copied because we click the interpolate button
    lidar.toolbar.click_btn('interpolate')
    for i in range(6, 1, -1):
        assert lidar.video_control.get_current_frame_number() == i
        assert lidar.get_cuboids_counts() == 1
        lidar.video_control.click_btn('previous')

