"""
This test covers below area for linear interpolation:
1. annotate video frame with different shapes, boxes, polygons, dots, lines etc.
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
    job_id = create_video_annotation_job(app, API_KEY, data.video_annotation_linear_interpolation_cml, USER_EMAIL, PASSWORD, DATA_FILE)
    return job_id


@pytest.mark.dependency()
def test_annotate_frame_with_different_shape(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    job_window = app_test.driver.window_handles[0]
    app_test.job.preview_job()
    time.sleep(5)
    app_test.video_annotation.activate_iframe_by_index(0)
    time.sleep(5)
    app_test.video_annotation.full_screen()
    time.sleep(5)
    shapelabel_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert shapelabel_count == 0
    app_test.video_annotation.click_toolbar_button('boxes')
    time.sleep(5)

    app_test.video_annotation.annotate_frame(mode='ontology', value={"Left Hand": 1}, annotate_shape='box')
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count == 1

    app_test.video_annotation.click_toolbar_button('dots')
    app_test.video_annotation.click_classes_or_objects_tab('CLASSES')
    app_test.video_annotation.annotate_frame(mode='ontology', value={"Right Hand": 2}, annotate_shape='dot')

    app_test.video_annotation.click_toolbar_button('lines')
    app_test.video_annotation.click_classes_or_objects_tab('CLASSES')
    app_test.video_annotation.annotate_frame(mode='ontology', value={"Right Hand": 1}, annotate_shape='line')

    app_test.video_annotation.click_toolbar_button('polygons')
    app_test.video_annotation.click_classes_or_objects_tab('CLASSES')
    app_test.video_annotation.annotate_frame(mode='ontology', value={"Right Hand": 1}, annotate_shape='polygon')

    app_test.video_annotation.click_classes_or_objects_tab('CLASSES')
    app_test.video_annotation.click_toolbar_button('ellipses')
    app_test.video_annotation.annotate_frame(mode='ontology', value={"Right Hand": 1}, annotate_shape='ellipse')

    app_test.video_annotation.click_classes_or_objects_tab('OBJECTS')
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count > 1

    app_test.video_annotation.deactivate_iframe()
    app_test.driver.close()
    app_test.navigation.switch_to_window(job_window)


@pytest.mark.dependency(depends=["test_annotate_frame_with_different_shape"])
def test_copy_paste_delete_annotation(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    login = app_test.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app_test.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)
    # tx_job = 2264194
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    app_test.job.preview_job()
    time.sleep(5)
    app_test.video_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app_test.video_annotation.full_screen()
    time.sleep(5)
    original_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert original_count == 0

    app_test.video_annotation.click_classes_or_objects_tab('CLASSES')
    app_test.video_annotation.click_toolbar_button('boxes')
    app_test.video_annotation.annotate_frame(mode='ontology', value={"Left Hand": 1}, annotate_shape='box')
    app_test.video_annotation.click_ontology_item('Left Hand 1')
    app_test.video_annotation.press_combine_hotkey(Keys.COMMAND, 'c')
    time.sleep(2)
    app_test.video_annotation.press_combine_hotkey(Keys.COMMAND, 'v')
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert new_count == 2

    app_test.video_annotation.single_hotkey(Keys.DELETE)
    new_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    # unable to delete using hotkey on the first frame,as it is linear interpolation
    assert new_count == 1

    # go to next frame to check
    app_test.video_annotation.next_frame()
    next_frame_count = app_test.video_annotation.get_sidepanel_shapelabel_count()
    assert next_frame_count == 1





