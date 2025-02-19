"""
This test covers below area for object tracking:
1. create box annotation
2. copy and paste shapes.
3. delete shapes
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_annotation import create_video_annotation_job
from selenium.webdriver.common.keys import Keys
import time
from adap.data import annotation_tools_cml as data

pytestmark = pytest.mark.regression_video_annotation

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/video_annotation/video_withoutannotation.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_video_annotation_job(app, API_KEY, data.video_annotation_object_tracking_cml, USER_EMAIL, PASSWORD, DATA_FILE)
    return job_id


def test_object_tracking_annotation(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    job_window = app_test.driver.window_handles[0]
    app_test.job.preview_job()
    time.sleep(8)
    app_test.video_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app_test.video_annotation.full_screen()
    time.sleep(5)
    original_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert original_count == 0
    app_test.video_annotation.annotate_frame(mode='ontology', value={"Left Hand": 1}, annotate_shape='box')
    app_test.video_annotation.click_ontology_item('Left Hand 1')
    app_test.video_annotation.press_combine_hotkey(Keys.COMMAND, 'c')
    time.sleep(1)
    app_test.video_annotation.press_combine_hotkey(Keys.COMMAND, 'v')
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count == 2

    app_test.video_annotation.single_hotkey(Keys.DELETE)
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    # be able to delete annotation on first frame as it is object tracking
    assert new_count == 1

    # paste again
    app_test.video_annotation.press_combine_hotkey(Keys.COMMAND, 'v')
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count == 2

    # go to next frame, verify shape label count
    app_test.video_annotation.next_frame()
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count == 2

    # go back to previous frame, verify unable to delete single one using hotkey
    app_test.video_annotation.previous_frame()
    app_test.video_annotation.single_hotkey(Keys.DELETE)
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count == 1

    app_test.video_annotation.deactivate_iframe()
    app_test.driver.close()
    app_test.navigation.switch_to_window(job_window)
