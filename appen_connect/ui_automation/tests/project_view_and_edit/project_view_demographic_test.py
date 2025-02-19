"""
Create a project with specific "Hiring Targets & Metrics" configuration using API
and the tests validates the Project Hiring Target configuration when newly created project is being viewed and tests while editing the configuration
"""
import datetime
import time

from adap.ui_automation.utils.selenium_utils import find_elements
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *
from conftest import ac_api_cookie

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_demographics, pytest.mark.ac_ui_project_view_n_edit, pytest.mark.ac_ui_project_view_n_test]

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6
_tomorrow_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m/%d/%Y")

project_config = {
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 1386,
    "registrationProcessTemplateId": 764,
    "locale": {
        "country": _country
    },
    "hiring_target": {
        "language": _lan,
        "languageCountry": _lan_country,
        "restrictToCountry": _country,
        "target": 10
    },
    "pay_rates": {
        "spokenFluency": _fluency.upper().replace(" ", "_"),
        "writtenFluency": _fluency.upper().replace(" ", "_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    },
    "invoice": "default",
    "update_status": "READY"
}

@pytest.fixture(scope="module")
def create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)

    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)
    print(_project)

    status_payload = {
        "status": "ENABLED"
    }
    project_id = _project['id']
    api = AC_API(ac_api_cookie)
    status = api.update_project_status(project_id, status_payload)
    status.assert_response_status(200)

    project_status = status.json_response['status']
    _project['status'] = project_status
    return _project


# https://appen.atlassian.net/browse/QED-1816
# Edit Custom Demographic Requirements
@pytest.mark.dependency()
def test_demographics_required_fields(app, create_project):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(create_project['name'])
    app.project_list.open_project_by_name(create_project['name'])

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    assert not app.ac_project.checkbox_by_text_is_selected_ac('Add Custom Demographic Requirements')
    app.ac_project.recruitment.fill_out_fields(data={
        "Add Custom Demographic Requirements": "1"
    })
    app.navigation.click_btn('Set Demographics')
    app.verification.text_present_on_page('Demographic Requirements Setup')
    app.verification.text_present_on_page('DEMOGRAPHICS TYPE')
    app.verification.text_present_on_page('VIEW AS')
    app.verification.text_present_on_page('SELECT PARAMETERS')
    app.verification.text_present_on_page('Requirements by group')
    app.verification.text_present_on_page('Aggregated requirements', is_not=False)

    params_selected = app.ac_project.recruitment.get_current_num_of_selected_params_demographic()
    assert params_selected == '0'
    app.navigation.click_btn('Next: Distribution')
    app.verification.text_present_on_page('Select at least one requirement')


@pytest.mark.dependency(depends=["test_demographics_required_fields"])
def test_demographics_requirements_by_group_percentage(app, create_project):
    app.ac_project.recruitment.set_up_demographic_requirements(params=['Gender', 'Device'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '2'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender', 'Device']

    app.ac_project.recruitment.delete_selected_demographic_param('Device')
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.distribute_demograph({'Female': 60, 'Male': 40})
    app.navigation.click_btn('Save Requirements')
    assert app.ac_project.recruitment.get_saved_requirements() == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_requirements_by_group_percentage"])
def test_demographics_requirements_by_group_number(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_clear_saved_req()
    app.navigation.click_btn('Set Demographics')
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Requirements by group', view='NUMBER',
                                                               params=['Gender'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.click_distribute_evenly()
    app.navigation.click_btn('Save Requirements')
    assert app.ac_project.recruitment.get_saved_requirements() == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_requirements_by_group_number"])
def test_demographics_aggregated_requirements_percentage(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_clear_saved_req()
    app.navigation.click_btn('Set Demographics')
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Aggregated requirements', view='PERCENTAGE',
                                                               params=['Gender'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.distribute_demograph({'Female': 60, 'Male': 40})
    app.navigation.click_btn('Save Requirements')
    # seems bug here, it does not show aggregated requirement, https://appen.atlassian.net/browse/ACE-6158
    # assert app.ac_project.recruitment.get_saved_requirements(demographics_type='AGGREGATED REQUIREMENTS') == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_aggregated_requirements_percentage"])
def test_demographics_aggregated_requirements_number(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_clear_saved_req()
    app.navigation.click_btn('Set Demographics')
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Aggregated requirements', view='NUMBER',
                                                               params=['Gender'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.click_distribute_evenly()
    app.navigation.click_btn('Save Requirements')
    # bug https://appen.atlassian.net/browse/ACE-6158
    # assert app.ac_project.recruitment.get_saved_requirements(demographics_type='AGGREGATED REQUIREMENTS') == 'Gender'
    app.navigation.click_btn('Save Changes')


@pytest.mark.dependency(depends=["test_demographics_aggregated_requirements_number"])
def test_edit_demographics(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Edit')
    app.ac_project.close_error_msg()
    app.ac_project.recruitment.click_edit_saved_req()
    app.verification.text_present_on_page('Demographic Requirements Setup')
    app.verification.text_present_on_page('Save Requirements')

    app.ac_project.recruitment.distribute_demograph({'Female': 2, 'Male': 6})
    app.navigation.click_btn('Save Requirements')

    app.ac_project.recruitment.click_edit_saved_req()
    assert app.ac_project.recruitment.get_current_distribution() == {'GENDER': {'Female': '2', 'Male': '6'}}
    app.navigation.click_btn('Save Requirements')
    app.navigation.click_btn('Save Changes')


#comment it out due to https://appen.atlassian.net/browse/ACE-7318
# @pytest.mark.skip(reason='bug ACE-7318')
@pytest.mark.dependency(depends=["test_edit_demographics"])
def test_view_demographics(app, create_project):
    app.ac_project.click_on_step('Recruitment')
    app.navigation.click_btn('Demographic Distribution')
    app.verification.text_present_on_page('Demographic Distribution')
    app.verification.text_present_on_page('Requirements by group (Gender)')
    app.verification.text_present_on_page('CUSTOM DEMOGRAPHICS')
    # app.verification.text_present_on_page('TOTAL BY CATEGORY')
    app.ac_project.click_on_step('PERCENTAGE')
    app.ac_project.recruitment.verify_demografics_header_view(type="Gender", target='ALL > ENG (ALL)',
                                                              engaged='(0% of 100%)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Female", engaged='0% of 2%')
    app.ac_project.recruitment.verify_demografics_row_view(type="Male", engaged='0% of 6%')

    # # app.ac_project.recruitment.verify_demographics_select_view(view="TOTAL BY CATEGORY")
    # app.ac_project.click_on_step('NUMBER')
    # app.ac_project.recruitment.verify_demografics_header_view(type="Gender", target='ALL > ACE (ALL)',
    #                                                           engaged='(0 of 12)')
    # app.ac_project.recruitment.verify_demografics_row_view(type="Female", engaged='0%')
    # app.ac_project.recruitment.verify_demografics_row_view(type="Male", engaged='0%')
    #
    # app.ac_project.recruitment.verify_demografics_header_view(type="Age Range", target='ALL > ACE (ALL)',
    #                                                           engaged='(0 of 12)')
    # app.ac_project.recruitment.verify_demografics_row_view(type="18-24", engaged='0%')
    # app.ac_project.recruitment.verify_demografics_row_view(type="25-34", engaged='0%')
    # app.ac_project.recruitment.verify_demografics_row_view(type="35-44", engaged='0%')
    # app.ac_project.recruitment.verify_demografics_row_view(type="45-54", engaged='0%')
    # app.ac_project.recruitment.verify_demografics_row_view(type="55+", engaged='0%')
    #
    # app.ac_project.recruitment.verify_demografics_header_view(type="Device", target='ALL > ACE (ALL)',
    #                                                           engaged='(0 of 12)')
    # app.ac_project.recruitment.verify_demografics_row_view(type="Android", engaged='0%')
    # app.ac_project.recruitment.verify_demografics_row_view(type="iOS", engaged='0%')
    #
    # app.ac_project.recruitment.verify_demographics_select_view(view="CUSTOM DEMOGRAPHICS")
    # app.verification.text_present_on_page('Demographic Distribution')
    # app.ac_project.recruitment.close_modal_window()
