"""
https://appen.atlassian.net/browse/QED-2664
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
def test_project_mapping(app, login):
    app.verification.text_present_on_page("Client Data Mappings")
    app.navigation.click_btn("Bulk Upload Mappings")
    app.verification.text_present_on_page("Bulk Upload Mapping Data")
    sample_file = get_data_file("/project_mapping_data_file.csv")
    app.client_data_mapping.enter_data({
        "Mapping Type": "Project Mapping",
        "Client": "Falcon",
        "Upload File": sample_file
    })
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload and Validate")
    app.navigation.click_btn("Cancel")
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload and Validate")
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Upload & Validate Data")
    time.sleep(3)
    assert (app.client_data_mapping.get_accepted_rows() == '0')
    assert (app.client_data_mapping.get_rejected_rows() == '9')

