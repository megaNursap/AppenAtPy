"""
https://appen.atlassian.net/browse/QED-1585
This test covers:
1. create box annotation
2. create ellipse annotation
3. create line annotation
4. create dot annotation
5. create polygon annotation
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


def test_create_box_annotation(app, tx_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.image_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.image_annotation.full_screen()
    time.sleep(5)
    app.image_annotation.search_ontology_class("*(}]")
    app.verification.text_present_on_page("No Results")
    app.image_annotation.clear_search_ontology_result()
    time.sleep(2)
    app.image_annotation.click_toolbar_button('boxes')
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 1}, annotate_shape='box')
    app.image_annotation.deactivate_iframe()
    value = app.image_annotation.get_annotation_value()
    assert len(value) == 1
    assert value[0].get("class") == 'cat'
    assert value[0].get("type") == 'box'
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_create_ellipse_annotation(app, tx_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.image_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.image_annotation.full_screen()
    time.sleep(5)
    app.image_annotation.click_toolbar_button('ellipses')
    app.image_annotation.annotate_image(mode='ontology', value={"dog": 1}, annotate_shape='box')
    app.image_annotation.deactivate_iframe()
    value = app.image_annotation.get_annotation_value()
    assert len(value) == 1
    assert value[0].get("class") == 'dog'
    assert value[0].get("type") == 'ellipse'
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_create_line_and_dot_annotation(app, tx_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.image_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.image_annotation.full_screen()
    time.sleep(5)
    app.image_annotation.click_toolbar_button('lines')
    app.image_annotation.annotate_image(mode='ontology', value={"dog": 1}, annotate_shape='line')
    time.sleep(2)
    app.image_annotation.click_toolbar_button('dots')
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 1}, annotate_shape='dot')
    time.sleep(2)
    app.image_annotation.deactivate_iframe()
    value = app.image_annotation.get_annotation_value()
    assert len(value) == 2
    assert value[0].get("class") == 'dog'
    assert value[0].get("type") == 'line'
    assert value[1].get("class") == 'cat'
    assert value[1].get("type") == 'dot'
    app.driver.close()
    app.navigation.switch_to_window(job_window)


def test_create_polygon_annotation(app, tx_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.image_annotation.activate_iframe_by_index(0)
    time.sleep(2)
    app.image_annotation.full_screen()
    time.sleep(5)
    app.image_annotation.click_toolbar_button('polygons')
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 1}, annotate_shape='polygon')
    app.image_annotation.deactivate_iframe()
    value = app.image_annotation.get_annotation_value()
    assert len(value) == 1
    assert value[0].get("class") == 'cat'
    assert value[0].get("type") == 'polygon'
    app.driver.close()
    app.navigation.switch_to_window(job_window)






