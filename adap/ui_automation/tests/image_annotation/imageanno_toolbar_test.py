"""
This test covers:
1. check all toolbar buttons enable/disable
2. when annotation is created, change to toolbar button, requester is able to delete annotation
"""

import time
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_annotation_cml,
                                        job_title="Testing create image annotation job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')
    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")
    return job_id


def test_toolbar_image_annotation(app, tx_job):
    app.job.preview_job()
    time.sleep(5)
    app.image_annotation.activate_iframe_by_index(0)
    time.sleep(8)
    assert not app.image_annotation.button_is_disable('boxes')
    assert not app.image_annotation.button_is_disable('ellipses')
    assert not app.image_annotation.button_is_disable('polygons')
    assert not app.image_annotation.button_is_disable('lines')
    assert not app.image_annotation.button_is_disable('dots')
    assert app.image_annotation.button_is_disable('delete')
    assert app.image_annotation.button_is_disable('undo')
    assert app.image_annotation.button_is_disable('redo')
    assert app.image_annotation.button_is_disable('pan')
    assert not app.image_annotation.button_is_disable('zoomin')
    assert not app.image_annotation.button_is_disable('zoomout')
    assert app.image_annotation.button_is_disable('reframe')
    assert not app.image_annotation.button_is_disable('crosshair')
    assert app.image_annotation.button_is_disable('focus_mode')
    assert app.image_annotation.button_is_disable('hide_mode')
    assert not app.image_annotation.button_is_disable('show_label')
    assert not app.image_annotation.button_is_disable('auto_enhance')
    assert not app.image_annotation.button_is_disable('help')
    assert not app.image_annotation.button_is_disable('full_screen')

    # verify labels menu
    app.image_annotation.click_toolbar_button('show_label')
    app.verification.text_present_on_page('Show labels for')
    app.verification.text_present_on_page('All')
    app.verification.text_present_on_page('Selected Class')
    app.verification.text_present_on_page('Selected Shape')
    app.verification.text_present_on_page('None')

    # verify help menu
    app.image_annotation.click_toolbar_button('help')
    app.verification.text_present_on_page('Using this tool')
    app.verification.text_present_on_page('Bounding Box')
    app.verification.text_present_on_page('Ellipse')
    app.verification.text_present_on_page('Polygon')
    app.verification.text_present_on_page('Line')
    app.verification.text_present_on_page('Dot')
    app.verification.text_present_on_page('Change the class of a shape')
    app.verification.text_present_on_page('Add points to polygons and lines')
    app.verification.text_present_on_page('Shortcuts')
    app.verification.text_present_on_page('to enable/disable hide mode')
    app.image_annotation.close_help_menu()
    app.verification.text_present_on_page('Using This Tool', is_not=False)

    # create an annotation and delete button will be enabled, delete the annotation
    app.image_annotation.click_toolbar_button('boxes')
    assert app.image_annotation.button_is_disable('hide_mode')
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 1}, annotate_shape='box')
    attemts = 0
    while app.image_annotation.button_is_disable('hide_mode') and attemts < 3:
        time.sleep(1)
        attemts += 1
        if not app.image_annotation.button_is_disable('hide_mode'):
            break

    assert not app.image_annotation.button_is_disable('hide_mode')
    assert not app.image_annotation.button_is_disable('delete')
    assert not app.image_annotation.button_is_disable('undo')
    assert not app.image_annotation.button_is_disable('focus_mode')

    app.image_annotation.click_toolbar_button('delete')
    app.image_annotation.deactivate_iframe()
    value = app.image_annotation.get_annotation_value()
    assert len(value) == 0
    app.driver.close()

