"""
Cover below cases:
 1. move cuboid left,right,forward,back
 2. rotate the cuboid

"""
import os
import time
import pytest
from selenium.webdriver.common.keys import Keys
from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar
from adap.ui_automation.lidar.support.image_diff import compare_images
from adap.ui_automation.services_config.application import Application

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['normal_job2']
USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
API_KEY = get_user_api_key('test_lidar')


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER, password=PASSWORD)


@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_move_rotate_cuboid(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()

    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)
    lidar.sidepanel.select_ontology('Car')
    # use hotkey to create cuboid
    lidar.single_hotkey(Keys.SPACE)
    lidar.click_coordinates(700, 700)

    lidar.sidepanel.select_shape_label('Car 1')
    cuboids = lidar.find_cuboids()

    assert cuboids.get('Car 1')
    _xy = cuboids['Car 1']['coordinates']
    x = _xy['X']
    y = _xy['Y']
    print("before move, x is:", x)
    print("before move, y is:", y)

    # move it left by hotkey
    _leftxy = lidar.move_cuboid('Car 1', 'a')
    leftx = _leftxy['X']
    lefty = _leftxy['Y']
    print("after move left, x is:", leftx)
    print("after move left, y is:", lefty)
    assert leftx < x
    assert lefty == y

    # move it right by hotkey
    _rightxy = lidar.move_cuboid('Car 1', 'd')
    rightx = _rightxy['X']
    righty = _rightxy['Y']
    print("after move right, x is:", rightx)
    print("after move right, y is:", righty)
    # move left, then move right make the x y go back to the original value
    assert rightx == x
    assert righty == y

    # move it back by hotkey
    _backxy = lidar.move_cuboid('Car 1', 'w')
    backx = _backxy['X']
    backy = _backxy['Y']
    print("after move back, x is:", backx)
    print("after move back, y is:", backy)
    assert backx >= x
    assert backy <= y
    assert not (backx ==x and backy == y)

    # move it forward by hotkey
    _forwardxy = lidar.move_cuboid('Car 1', 's')
    forwardx = _forwardxy['X']
    forwardy = _forwardxy['Y']
    print("after move forward, x is:", forwardx)
    print("after move forward, y is:", forwardy)
    # move back, then move forward make the x y go back to the original value
    assert forwardx == x
    assert forwardy == y

    # rotate selected cuboid left in local coordinates by hotkey, nothing changed in coordinate
    lidar.rotate_cuboid('Car 1', 'q')
    # rotate selected cuboid right in local coordinates by hotkey
    lidar.rotate_cuboid('Car 1', 'e')
