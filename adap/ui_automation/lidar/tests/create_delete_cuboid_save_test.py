"""
https://appen.atlassian.net/browse/QED-1418
Cover below cases:
1.create multiple cuboids and save them
2.delete cuboids and save them
"""
import os
import time
import pytest
from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar
from adap.ui_automation.services_config.application import Application

# lidar.click_coordinates(700, 700) not working on Jenkins

USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['normal_job1']
ONTOLOGY_URL = 'https://client.%s.cf3.us/jobs/%s/ontology_manager' % (pytest.env, job_id)
LIDAR_URL = 'https://view.%s.cf3.io/channels/cf_internal/jobs/%s/editor_preview?token=88f0wWq7nIf87QNiFV67pw' % (pytest.env, job_id)


@pytest.fixture(scope="module")
def app():
    app = Application(pytest.env)
    app.user.login_as_customer(user_name=USER, password=PASSWORD)
    app.driver.get(ONTOLOGY_URL)
    app.user.close_guide()
    return app


@pytest.mark.dependency()
@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_create_first_cuboid(app):
    app.driver.get(LIDAR_URL)
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)
    original_count = lidar.get_cuboids_counts()

    # add 1nd cuboid
    lidar.toolbar.click_btn('create')
    lidar.click_coordinates(700, 700)
    lidar.toolbar.click_btn('save')
    time.sleep(2)
    app.navigation.refresh_page()
    time.sleep(10)
    lidar.activate_iframe_by_index(0)
    new_count = lidar.get_cuboids_counts()
    assert new_count - original_count == 1


@pytest.mark.dependency(depends=["test_create_first_cuboid"])
@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_create_second_cuboid(app):
    app.driver.get(LIDAR_URL)
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    original_count = lidar.get_cuboids_counts()
    # add 2nd cuboid
    lidar.toolbar.click_btn('create')
    lidar.sidepanel.select_ontology('Truck')
    time.sleep(2)
    lidar.click_coordinates(150, 150)
    lidar.toolbar.click_btn('save')
    time.sleep(2)
    app.navigation.refresh_page()
    time.sleep(10)
    lidar.activate_iframe_by_index(0)

    new_count = lidar.get_cuboids_counts()
    assert new_count - original_count == 1


@pytest.mark.dependency(depends=["test_create_second_cuboid"])
@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_delete_cuboid(app):
    # cover delete all cuboids case
    app.driver.get(LIDAR_URL)
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    cuboids_count = lidar.get_cuboids_counts()
    for i in range(0, cuboids_count):
        lidar.sidepanel.select_shape_label()
        time.sleep(2)
        lidar.toolbar.click_btn('delete')

    lidar.toolbar.click_btn('save')
    app.navigation.refresh_page()
    time.sleep(10)
    lidar.activate_iframe_by_index(0)

    delete_save_count = lidar.get_cuboids_counts()
    assert delete_save_count == 0

