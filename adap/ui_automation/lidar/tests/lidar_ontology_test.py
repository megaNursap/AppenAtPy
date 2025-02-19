"""
EPIC:https://appen.atlassian.net/browse/QED-1121
JIRA:https://appen.atlassian.net/browse/QED-1127
Cover below cases:
1. create ontology class, verify it on lidar page
2. update ontology class
3. delete ontology class
"""
import os
import time
import pytest

from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar
from adap.ui_automation.services_config.application import Application

pytestmark = pytest.mark.regression_lidar

USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['normal_job2']
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
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_create_new_class(app):
    app.ontology.add_class(title='Bus', color='#0036FF')
    app.navigation.click_link('Save')

    # verify new class is displayed on Lidar
    app.driver.get(LIDAR_URL)
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)
    time.sleep(5)

    assert lidar.sidepanel.ontology_class_is_displayed('Bus')
    assert lidar.sidepanel.get_ontology_class_color('Bus') == '#0036FF'

    assert not lidar.sidepanel.ontology_class_is_displayed('New Bus')


@pytest.mark.dependency(depends=["test_create_new_class"])
@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_change_class_name(app):
    app.driver.get(ONTOLOGY_URL)

    app.ontology.edit_class('Bus', new_title='Bus Updated')
    app.navigation.click_link('Save')

    app.driver.get(LIDAR_URL)
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)
    time.sleep(5)

    assert not lidar.sidepanel.ontology_class_is_displayed('Bus')
    assert lidar.sidepanel.ontology_class_is_displayed('Bus Updated')


@pytest.mark.dependency(depends=["test_change_class_name"])
@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_delete_class(app):
    app.driver.get(ONTOLOGY_URL)

    app.ontology.delete_class('Bus Updated')
    app.navigation.click_link('Save')

    app.driver.get(LIDAR_URL)
    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)
    time.sleep(5)

    assert not lidar.sidepanel.ontology_class_is_displayed('Bus Updated')
