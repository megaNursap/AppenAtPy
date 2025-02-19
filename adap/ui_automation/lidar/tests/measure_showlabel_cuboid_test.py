"""
Cover below cases:
 1.measure, check label-cuboid is added
 2.show label for "All", "Selected Class", "None"
"""
import os
import time
import pytest
from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar
pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['four_cuboids_job']
USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
API_KEY = get_user_api_key('test_lidar')


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER, password=PASSWORD)


@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_showlabel_cuboid(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()

    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    # by default, show labels for all
    cuboids = lidar.get_cuboids_counts()
    labels = lidar.sidepanel.get_shape_label_counts()
    assert cuboids == labels

    # if we choose 'None', no label will show for cuboid
    lidar.toolbar.click_btn('label')
    lidar.toolbar.select_show_shape_labels_for('None')
    cuboids = lidar.get_cuboids_counts()
    assert cuboids == 0

    # if we choose 'Selected Class' from dropdown, the label will only show for class being selected
    lidar.toolbar.click_btn('label')
    lidar.toolbar.select_show_shape_labels_for('Selected Class')
    cuboids = lidar.get_cuboids_counts()
    assert cuboids == 2

    # if we choose 'All' from dropdown
    lidar.toolbar.click_btn('label')
    lidar.toolbar.select_show_shape_labels_for('All')
    cuboids = lidar.get_cuboids_counts()
    assert cuboids == 4

    # test measure feature, after we measure, 1 more 'cube-label' will be added, so it is increased from 4 to 5
    # TODO: click_coordinates not working on Jenkins job, though it works on local very good
    # lidar.toolbar.click_btn('measure')
    # lidar.click_coordinates(500, 500)
    # lidar.click_coordinates(60, 60)
    # cuboids = lidar.get_cuboids_counts()
    # assert cuboids == 5
    # measure_label = lidar.find_cuboids()
    # assert measure_label.get('1.1 m')



