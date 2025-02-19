"""
https://appen.atlassian.net/browse/QED-2665
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom

pytestmark = [pytest.mark.ac_ui_uat, pytest.mark.regression_ac, pytest.mark.ac_client_mapping]

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
def test_user_mapping(app, login):
    app.verification.text_present_on_page("Client Data Mappings")
    app.navigation.click_btn("Bulk Upload Mappings")
    app.verification.text_present_on_page("Bulk Upload Mapping Data")
    sample_file = get_data_file("/user_mapping_data_file.csv")
    app.client_data_mapping.enter_data({
        "Mapping Type": "User Mapping",
        "Client": "Falcon",
        "Tool Name": "SRT",
        "Upload File": sample_file
    })
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload and Validate")
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload & Validate Data")
    app.navigation.hover_over_meta_tag()
    time.sleep(1)
    assert app.driver.find_element('xpath',"//div[text()='Rejected rows could be rows that are already mapped with the same external_value/ac_id combination, or an error with mapping column selections. Please download the rejected data file to learn more.']").is_displayed()
    assert (app.client_data_mapping.get_accepted_rows() == '0')
    assert (app.client_data_mapping.get_rejected_rows() == '2')


