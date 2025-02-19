"""
This test covers:
1. check all toolbar buttons enable/disable
2. check all video control buttons and play them, next frame, previous frame
"""

import time

import allure

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_annotation import create_video_annotation_job
from adap.data import annotation_tools_cml as data

pytestmark = pytest.mark.regression_video_annotation

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/video_annotation/video_withoutannotation.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_video_annotation_job(app, API_KEY, data.video_annotation_linear_interpolation_cml, USER_EMAIL, PASSWORD, DATA_FILE)
    return job_id


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@allure.issue("https://appen.atlassian.net/browse/AT-5027", "BUG AT-5027")
def test_toolbar_video(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    time.sleep(2)
    app_test.job.preview_job()
    time.sleep(8)
    app_test.video_annotation.activate_iframe_by_index(0)
    assert not app_test.video_annotation.button_is_disable('boxes')
    assert not app_test.video_annotation.button_is_disable('polygons')
    assert not app_test.video_annotation.button_is_disable('lines')
    assert not app_test.video_annotation.button_is_disable('dots')
    assert not app_test.video_annotation.button_is_disable('point_box')
    assert app_test.video_annotation.button_is_disable('pan')
    assert not app_test.video_annotation.button_is_disable('zoom_in')
    assert not app_test.video_annotation.button_is_disable('zoom_out')
    assert app_test.video_annotation.button_is_disable('reframe')
    assert not app_test.video_annotation.button_is_disable('cross_hair')
    assert not app_test.video_annotation.button_is_disable('map')
    assert not app_test.video_annotation.button_is_disable('show_label')
    assert not app_test.video_annotation.button_is_disable('help')
    assert not app_test.video_annotation.button_is_disable('full_screen')

    # verify labels menu
    app_test.video_annotation.click_toolbar_button('show_label')
    app_test.verification.text_present_on_page('Show labels for')
    app_test.verification.text_present_on_page('All')
    app_test.verification.text_present_on_page('Selected Class')
    app_test.verification.text_present_on_page('Selected Shape')
    app_test.verification.text_present_on_page('None')

    # verify help menu
    app_test.video_annotation.click_toolbar_button('help')
    app_test.verification.text_present_on_page('Using this tool')
    app_test.verification.text_present_on_page('Bounding Box')
    app_test.verification.text_present_on_page('Polygon')
    app_test.verification.text_present_on_page('Line')
    app_test.verification.text_present_on_page('Dot')
    app_test.verification.text_present_on_page('Add points to polygons and lines')
    app_test.video_annotation.close_help_menu()
    app_test.verification.text_present_on_page('Using This Tool', is_not=False)

    # get current frame and total frame
    current_frames = app_test.video_annotation.get_num_of_current_frame()
    assert current_frames == 1
    num_frames = app_test.video_annotation.get_num_of_frames_for_video()
    assert num_frames == 25
    # click next and previous
    app_test.video_annotation.next_frame()
    current_frames = app_test.video_annotation.get_num_of_current_frame()
    assert current_frames == 2
    app_test.video_annotation.previous_frame()
    current_frames = app_test.video_annotation.get_num_of_current_frame()
    assert current_frames == 1
    # click play and pause button
    app_test.video_annotation.play_pause()
    # time.sleep(5)
    # app_test.video_annotation.play_pause()
    # current_frames = app_test.video_annotation.get_num_of_current_frame()
    # assert current_frames in range(2, 25)
    app_test.video_annotation.deactivate_iframe()
    app_test.driver.close()