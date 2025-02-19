"""
https://appen.atlassian.net/browse/QED-1126
Cover below cases:
1. check all toolbar buttons.
2. check help menu content
"""
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
@pytest.mark.checklidarissue
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_verify_toolbar_id_present(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)
    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)
    # when no cuboid - create, save, fullscreen buttons should enabled
    assert not lidar.toolbar.button_is_disable('create')
    assert not lidar.toolbar.button_is_disable('save')
    assert not lidar.toolbar.button_is_disable('full_screen')

    assert lidar.toolbar.button_is_disable('move')
    assert lidar.toolbar.button_is_disable('rotate')
    assert lidar.toolbar.button_is_disable('resize')
    assert lidar.toolbar.button_is_disable('delete')
    assert lidar.toolbar.button_is_disable('copy')
    assert lidar.toolbar.button_is_disable('paste')

    # create one cuboid and verify: move, rotate, resize, delete and copy are enabled
    lidar.toolbar.click_btn('create')
    lidar.click_coordinates(700, 600)
    time.sleep(3)
    lidar.sidepanel.select_shape_label()
    time.sleep(3)
    assert not lidar.toolbar.button_is_disable('move')
    assert not lidar.toolbar.button_is_disable('rotate')
    assert not lidar.toolbar.button_is_disable('resize')
    assert not lidar.toolbar.button_is_disable('delete')
    assert not lidar.toolbar.button_is_disable('copy')
    assert lidar.toolbar.button_is_disable('paste')

    # paste is enabled after copy was clicked
    lidar.toolbar.click_btn('copy')
    assert not lidar.toolbar.button_is_disable('paste')

    # verify labels menu
    lidar.toolbar.click_btn('label')
    app.verification.text_present_on_page('Show labels for')
    app.verification.text_present_on_page('All')
    app.verification.text_present_on_page('Selected Class')
    app.verification.text_present_on_page('None')

    lidar.toolbar.click_btn('help')
    app.verification.text_present_on_page('Using This Tool')
    app.verification.text_present_on_page('Interaction with the Main View')
    app.verification.text_present_on_page(' to next frame')
    app.verification.text_present_on_page(' to previous frame')
    app.verification.text_present_on_page(' to increase point size in the point cloud')
    app.verification.text_present_on_page(' to paste copied shape')
    app.verification.text_present_on_page(' to unbind the selected cuboid with projection')
    app.verification.text_present_on_page('Interaction with asynchronous mode')
    app.verification.text_present_on_page('Interaction with attributes modal')
    # verify help menu can be closed
    lidar.toolbar.close_help_menu()
    app.verification.text_present_on_page('Using This Tool', is_not=False)
    app.driver.close()




