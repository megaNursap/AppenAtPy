import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.data import annotation_tools_cml as data
from adap.ui_automation.utils.selenium_utils import find_elements

# we leverage below user as it won't impact lidar feature
USER_EMAIL = get_user_email('test_lidar')
PASSWORD = get_user_password('test_lidar')
API_KEY = get_user_api_key('test_lidar')
TEAM_ID = get_user_team_id('test_lidar')
TEAM_NAME = get_user_team_name('test_lidar')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")

pytestmark = [pytest.mark.regression_ontology_attribute]


# @pytest.mark.skipif(pytest.env not in ['sandbox'], reason="Sandbox have switch configured")
def test_on_off_switch_for_ontology_attributes(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_annotation_cml,
                                        job_title="Testing ontology attribute ON OFF switch", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")
    # for the job created, see if ontology attribute is there, set the expected switch on off value
    app.ontology.click_edit_class('dog')
    is_switch_on = False
    ontology_attribute_link = find_elements(app.driver, "//span[(normalize-space(text())='Ontology Attributes')]")
    if len(ontology_attribute_link) > 0:
        is_switch_on = True
        app.navigation.click_btn('Cancel')
    app.navigation.click_btn('Cancel')
    if pytest.env == 'fed':
        app.mainMenu.account_menu("Users")
    else:
        app.mainMenu.account_menu("Customers")
    app.navigation.click_link("Users")
    app.user.search_user_and_go_to_team_page(USER_EMAIL, TEAM_ID)
    app.user.click_edit_team()
    # verify on team edit page, switch is as expected, name needs to be confirmed
    if is_switch_on:
        app.verification.checkbox_by_text_is_selected('Ontology Attributes')
    else:
        assert not app.verification.checkbox_by_text_is_selected('Ontology Attributes')
    # update switch
    app.user.update_feature_flag_or_additional_role('Ontology Attributes')
    app.navigation.click_btn('Save Changes')
    time.sleep(2)
    # go to job again, verify switch update takes effect
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    # if original value is on, we have turned it off, so verify 'onotlogy attribute' is not showing  there. Else, verify it is showing
    _c = 0
    while _c < 30:
        app.navigation.refresh_page()
        app.ontology.click_edit_class('dog')
        ontology_attribute_link = find_elements(app.driver, "//span[(normalize-space(text())='Ontology Attributes')]")
        if is_switch_on:
            if len(ontology_attribute_link) == 0:
                break
            else:
                app.navigation.click_btn('Cancel')
                app.navigation.click_btn('Cancel')
                time.sleep(10)
                _c += 1
        else:
            if len(ontology_attribute_link) > 0:
                break
            else:
                app.navigation.click_btn('Cancel')
                time.sleep(10)
                _c += 1
    else:
        msg = f'Switch does not take effect, please check'
        raise Exception(msg)

