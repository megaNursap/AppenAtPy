"""
Create a project with specific "Experiment Groups" configuration using API
and the tests validates the Project Experiment Group configuration when newly created project is being viewed and editing
"""
import time

import pytest

from adap.api_automation.utils.data_util import get_test_data
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project


pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_experiment_groups, pytest.mark.ac_ui_project_view_n_edit]

#
USER_NAME = get_test_data('test_ui_account', 'user_name')
PASSWORD = get_test_data('test_ui_account', 'password')


_country = "*"
_country_ui = "United States of America"
_locale  = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

project_config_ui = {
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "qualificationProcessTemplateId": 1386,
    "registrationProcessTemplateId": 764,
    "externalSystemId": "",
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
        "spokenFluency": _fluency.upper().replace(" ","_"),
        "writtenFluency": _fluency.upper().replace(" ","_"),
        "rateValue": _pay_rate,
        "taskType": "Default",
        "language": _lan,
        "languageCountry": "*",
        "restrictToCountry": _country
    }
}


@pytest.fixture(scope="module")
def exp_gr_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    _project = api_create_simple_project(project_config_ui, ac_api_cookie)

    return _project


@pytest.mark.dependency()
def test_experiment_group_no_access(app, exp_gr_project):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(exp_gr_project['name'])
    app.project_list.open_project_by_name(exp_gr_project['name'])

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    # TODO add view verification
    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Resume Setup")

    # app.navigation.switch_to_frame("page-wrapper")
    # app.ac_project.click_on_step('Project Access')
    #
    # app.verification.text_present_on_page("Access Configuration")
    # app.verification.text_present_on_page("1 - Go to “View Experiment” on the project list")
    # app.verification.text_present_on_page("2 - Create a new experiment based on project parameters")
    # app.verification.text_present_on_page("3 - Add user groups to the experiment created")


@pytest.mark.dependency(depends=["test_experiment_group_no_access"])
def test_experiment_group_add_external_system(app):
    app.ac_project.click_on_step('Project Tools')

    app.verification.text_present_on_page("Project Tools")
    app.verification.text_present_on_page("External System")

    app.ac_project.tools.fill_out_fields(data={
        "External System": "ADAP"
    })
    app.navigation.click_btn('Save')

    app.ac_project.click_on_step('Project Access')
    assert app.ac_project.tools.get_current_user_groups() == ['ALL USERS']


@pytest.mark.dependency(depends=["test_experiment_group_add_external_system"])
def test_add_experiment_group_add(app):
    app.navigation.click_btn("Add Other User Group")
    app.ac_project.tools.add_user_group("Cavite Raters")
    app.navigation.click_btn('Save')
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Project Access')
    assert sorted(app.ac_project.tools.get_current_user_groups()) ==  sorted(['Cavite Raters', 'ALL USERS'])


@pytest.mark.dependency(depends=["test_add_experiment_group_add"])
def test_edit_experiment_group_add(app):
    app.ac_project.tools.edit_user_group('Cavite Raters', 'Figure Eight Exeter')
    app.navigation.click_btn('Save')
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Project Access')
    assert  sorted(app.ac_project.tools.get_current_user_groups()) == sorted(['Figure Eight Exeter', 'ALL USERS'])


@pytest.mark.dependency(depends=["test_edit_experiment_group_add"])
def test_delete_experiment_group_add(app):
    app.ac_project.tools.add_user_group("Cavite Raters")
    app.navigation.click_btn('Save')
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Project Access')
    assert 'Cavite Raters' in app.ac_project.tools.get_current_user_groups()

    app.ac_project.tools.delete_user_group('Figure Eight Exeter')
    app.navigation.click_btn('Save')
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Project Access')
    assert sorted(app.ac_project.tools.get_current_user_groups()) ==  sorted(['Cavite Raters', 'ALL USERS'])


@pytest.mark.dependency(depends=["test_delete_experiment_group_add"])
def test_user_group_project_view(app, exp_gr_project):
    app.ac_project.click_on_step('Preview')
    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")
    app.verification.current_url_contains('/project_setup/view')
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step("Project Access")

    # app.verification.text_present_on_page("Access Configuration 1")
    # app.verification.text_present_on_page("Enable or add groups that will be able to view and work on this project.")
    app.verification.text_present_on_page(exp_gr_project['name'])

    assert sorted(app.ac_project.tools.get_current_user_groups_view()) == sorted(['Cavite Raters', 'ALL USERS'])


@pytest.mark.dependency(depends=["test_user_group_project_view"])
def test_edit_user_group_project_view(app, exp_gr_project):
    app.navigation.click_btn("Edit")

    app.ac_project.tools.add_user_group('Figure Eight Cavite')
    app.navigation.click_btn('Save Changes')

    assert 'Figure Eight Cavite' in app.ac_project.tools.get_current_user_groups_view()


@pytest.mark.dependency(depends=["test_edit_user_group_project_view"])
def test_delete_user_group_project_view(app, exp_gr_project):
    app.navigation.click_btn("Edit")

    app.ac_project.tools.delete_user_group('Figure Eight Cavite')
    app.navigation.click_btn('Save Changes')

    assert 'Figure Eight Cavite' not in app.ac_project.tools.get_current_user_groups_view()


@pytest.mark.dependency(depends=["test_delete_user_group_project_view"])
def test_user_group_view_experiment_list(app, exp_gr_project):
    app.navigation.click_link("Experiment List")
    app.verification.current_url_contains('partners/experiments')