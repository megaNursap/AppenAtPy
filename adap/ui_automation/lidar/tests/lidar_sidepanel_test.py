"""
JIRA:https://appen.atlassian.net/browse/QED-1419
Cover below cases:
https://appen.spiraservice.net/5/TestCase/1151.aspx
https://appen.spiraservice.net/5/TestCase/1152.aspx
https://appen.spiraservice.net/5/TestCase/1154.aspx
https://appen.spiraservice.net/5/TestCase/1170.aspx
1.check ontology display in sidepanel
2.check search feature
3.check description panel
"""

import time
import pytest
from adap.api_automation.utils.data_util import *
from adap.ui_automation.lidar.service_config.lidar import Lidar

pytestmark = pytest.mark.regression_lidar

TEST_DATA = pytest.data.predefined_data['lidar_ui'].get(pytest.env)
if TEST_DATA:
    job_id = TEST_DATA['normal_job1']
USER = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
API_KEY = get_user_api_key('test_lidar')


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER, password=PASSWORD)


@pytest.mark.lidar
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
def test_sidepanel(app, login):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.preview_job()

    lidar = Lidar(app)
    lidar.activate_iframe_by_index(0)

    time.sleep(2)
    lidar.wait_until_video_load(interval=5, max_wait_time=100)
    lidar.toolbar.click_btn('full_screen')
    time.sleep(2)

    assert lidar.sidepanel.ontology_class_is_displayed('Car')
    assert lidar.sidepanel.ontology_class_is_displayed('Truck')
    assert lidar.sidepanel.ontology_class_is_displayed('SUV')
    assert lidar.sidepanel.ontology_class_is_displayed('Pedestrian')
    assert lidar.sidepanel.ontology_class_is_displayed('Mini van')
    assert lidar.sidepanel.ontology_class_is_displayed('Sign')
    assert lidar.sidepanel.ontology_class_is_displayed('Pickup truck')

    # search 'T', it will filter 4 ontology
    lidar.sidepanel.search_ontology_class('T')
    assert lidar.sidepanel.ontology_class_is_displayed('Truck')
    assert lidar.sidepanel.ontology_class_is_displayed('Pedestrian')
    assert lidar.sidepanel.ontology_class_is_displayed('Pickup truck')
    assert not lidar.sidepanel.ontology_class_is_displayed('Car')
    assert not lidar.sidepanel.ontology_class_is_displayed('SUV')
    assert not lidar.sidepanel.ontology_class_is_displayed('Mini van')
    assert not lidar.sidepanel.ontology_class_is_displayed('Sign')

    # search 'Ca', it will just show Car
    lidar.sidepanel.clear_ontology_search()
    lidar.sidepanel.search_ontology_class('Ca')
    assert lidar.sidepanel.ontology_class_is_displayed('Car')
    assert not lidar.sidepanel.ontology_class_is_displayed('Truck')
    assert not lidar.sidepanel.ontology_class_is_displayed('SUV')
    assert not lidar.sidepanel.ontology_class_is_displayed('Pedestrian')
    assert not lidar.sidepanel.ontology_class_is_displayed('Mini van')
    assert not lidar.sidepanel.ontology_class_is_displayed('Sign')
    assert not lidar.sidepanel.ontology_class_is_displayed('Pickup truck')

    # search 'H', nothing will show
    lidar.sidepanel.clear_ontology_search()
    lidar.sidepanel.search_ontology_class('H')
    assert lidar.sidepanel.no_search_result_found()

    # clear search, all ontology will be back
    lidar.sidepanel.clear_ontology_search()
    assert lidar.sidepanel.ontology_class_is_displayed('Car')
    assert lidar.sidepanel.ontology_class_is_displayed('Truck')
    assert lidar.sidepanel.ontology_class_is_displayed('SUV')
    assert lidar.sidepanel.ontology_class_is_displayed('Pedestrian')
    assert lidar.sidepanel.ontology_class_is_displayed('Mini van')
    assert lidar.sidepanel.ontology_class_is_displayed('Sign')
    assert lidar.sidepanel.ontology_class_is_displayed('Pickup truck')

    # info icon will display when description is available
    title = lidar.sidepanel.get_ontology_instruction_title('Car')
    assert title == 'Car'
    content = lidar.sidepanel.get_ontology_instruction_content()
    assert content == 'It is a car'
    lidar.sidepanel.close_ontology_instruction()
    app.driver.close()
