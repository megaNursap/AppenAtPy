import time
from random import random

import pytest

from adap.api_automation.utils.data_util import get_user_email, get_user_password, get_data_file
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom

pytestmark = [pytest.mark.ac_ui_uat, pytest.mark.regression_ac, pytest.mark.ac_client_mapping, pytest.mark.regression_ac_client_mapping]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    app.navigation.click_link('Client Data Mappings')
    app.navigation.click_btn('Client Data Mappings')
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency()
def test_user_mapping_table(app, login):
    """Verify Client Mapping list page UI"""
    app.verification.text_present_on_page("Client Data Mappings")
    app.verification.text_present_on_page("ID")
    app.verification.text_present_on_page("CLIENT")
    app.verification.text_present_on_page("TOOL NAME")
    app.verification.text_present_on_page("CLIENT ID & CREDENTIAL")
    app.verification.text_present_on_page("AC USER ID")
    app.verification.text_present_on_page("CREATED AT")
    app.verification.element_is_visible_on_the_page("//input[@id='filterByText']")
    app.verification.element_is_visible_on_the_page("//input[@id='filterByMapping']")
    app.verification.element_is_visible_on_the_page("//div[contains(text(),'All Clients')]")


def test_sort_by_client(app, login):
    """Verify Internal user can sort the client mappings by different Client values"""
    app.verification.text_present_on_page("Client Data Mappings")
    app.client_data_mapping.get_client_mapping_info_by(client='')
    for _client in ['Falcon', 'Bluebird']:
        app.client_data_mapping.get_client_mapping_info_by(client=_client)
        mappings_by_client = app.client_data_mapping.get_all_client_mappings_list()
        time.sleep(3)
        assert len(mappings_by_client) > 0
        for i in range(len(mappings_by_client)):
            assert (mappings_by_client[i]['client_name'] == _client.upper())


def test_filter_by_mapping_type(app, login):
    """Verify user can see the client mappings when filtered by Mapping type """
    app.verification.text_present_on_page("Client Data Mappings")
    app.client_data_mapping.get_client_mapping_info_by(mapping_type='')
    for _mapping_type in ['Project Mapping', 'User Mapping']:
        app.client_data_mapping.get_client_mapping_info_by(mapping_type=_mapping_type)
        mappings = app.client_data_mapping.get_all_client_mappings_list()
        time.sleep(3)
        assert len(mappings) > 0

        if _mapping_type == 'User Mapping':
            app.verification.text_present_on_page("TOOL NAME")
            app.verification.text_present_on_page("AC USER ID")
            app.verification.text_present_on_page("CLIENT ID & CREDENTIAL")
            app.verification.text_present_on_page("User Mapping")

        else:
            app.verification.text_present_on_page("MARKET")
            app.verification.text_present_on_page("CLIENT ID")
            app.verification.text_present_on_page("AC ID")
            app.verification.text_present_on_page("Project Mapping")


def test_filter_user_mapping_by_clientId_and_userId(app, login):
    """Verify that user can filter user client mappings when search by internal user id"""
    app.verification.text_present_on_page("Client Data Mappings")
    user_id = '1294877'
    app.client_data_mapping.get_client_mapping_info_by(mapping_type='User Mapping')
    app.client_data_mapping.get_client_mapping_info_by(client='All Clients')
    app.client_data_mapping.find_client_mappings(user_id=user_id)
    time.sleep(2)
    _mappings = app.client_data_mapping.get_user_client_mapping_data(search_field='index', value=0)
    assert user_id in _mappings['ac_user_id'], f'AC User ID {user_id} not found'


def test_filter_project_mapping_by_projectId(app, login):
    """Verify that user can filter project client mappings by project id"""
    app.verification.text_present_on_page("Client Data Mappings")
    app.navigation.click_btn("Bulk Upload Mappings")
    app.verification.text_present_on_page("Bulk Upload Mapping Data")
    sample_file = get_data_file("/project_mapping_automation_new.csv")
    app.client_data_mapping.enter_data({
        "Mapping Type": "Project Mapping",
        "Client": "Falcon",
        "Upload File": sample_file
    })
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload and Validate")
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload & Validate Data")
    time.sleep(3)
    app.navigation.click_btn("Finish Bulk Upload")
    project_id = '166'
    app.client_data_mapping.get_client_mapping_info_by(mapping_type='Project Mapping')
    app.client_data_mapping.find_client_mappings(project_id=project_id)
    _mappings = app.client_data_mapping.get_project_client_mapping_data(search_field='index', value=0)
    assert project_id in _mappings['ac_id'], f'Project ID {project_id} not found'
