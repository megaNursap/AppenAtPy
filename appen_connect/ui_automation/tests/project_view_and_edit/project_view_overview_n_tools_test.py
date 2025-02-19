"""
Create a project with specific "Overview and Tools" configuration using API
and the tests validates the Project Overview and Tools configuration when newly created project is being viewed and editing
"""
import datetime
import time

from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
FULL_NAME = get_test_data('test_ui_account', 'full_name')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac,
              pytest.mark.ac_ui_project_overview_n_tools, pytest.mark.ac_ui_project_view_n_edit]

config = {}

_project = generate_project_name()

_country = "*"
_country_ui = "United States of America"
_locale = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

faker = Faker()
IP_ADDR = faker.ipv4()
URL = 'https://gnx-stage.appen.com'
NEW_URL = 'https://connect-stage.integration.cf3.us/'

project_config = {
    "projectType": 'Regular',
    "workType": "LINGUISTICS",
    "externalSystemId": 15,
    "qualificationProcessTemplateId": 85,
    "registrationProcessTemplateId": 315,
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
    app.navigation.click_link('View previous list page')
    app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)

    return _project


# ---------- View and edit 'OVERVIEW & TOOLS' page ---------
@pytest.mark.dependency()
def test_view_overview_and_tools_page(app, create_project):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")
    project_name = create_project['name']

    app.project_list.filter_project_list_by(project_name)
    app.project_list.open_project_by_name(project_name)

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('Overview & tools')
    app.verification.current_url_contains('/project_setup/view')
    app.verification.text_present_on_page('Overview & Tools')
    app.verification.text_present_on_page('Project Setup')
    app.verification.text_present_on_page('Project Tools')
    # original_secure_ip = app.ac_project.get_project_info_for_section('Secure IP Access')
    app.ac_project.verify_project_info({
        "Project Description": "Test Project" + create_project['alias'],
        "Type of Project": project_config['projectType'],
        "Type of Task": 'Linguistics',
        "Task Volume": "Very Low",
        "External Project": "ADAP"
    })


def test_view_highlight_information(app, create_project):
    app.ac_project.click_on_step('Overview & tools')
    assert app.ac_project.get_project_info_for_section('Status') == 'Ready'
    assert app.verification.text_present_on_page(
        'Your project is ready to be enabled. Click on “Enable Project” to start recruitment.')
    type_of_task = 'Linguistics'
    type_of_project = project_config['projectType']
    task_volume = 'Very Low'
    task = app.ac_project.get_project_info_for_section(type_of_task)
    assert type_of_project + ' project' in task
    assert task_volume + ' task volume' in task
    customer = app.ac_project.get_project_info_for_section('Customer')
    assert 'Appen Internal' in customer

    formatted_date = custom_strftime('%B %d, %Y', datetime.date.today())
    app.verification.text_present_on_page(formatted_date)
    app.verification.text_present_on_page('Appen Connect')
    app.navigation.click_link(FULL_NAME)
    assert '/qrp/core/vendor/view/' in app.driver.current_url
    # need go back to new experience page for other test  cases
    app.navigation.click_link('Partner Home')
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=create_project['name'])
    app.project_list.open_project_by_name(create_project['name'])
    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency(depends=["test_view_overview_and_tools_page"])
def test_view_info_in_edit_mode(app, create_project):
    print(f"Projectid: {_project['id']}")
    print(f"PROJECT_TITLE: {_project['name']}")
    print(f"PROJECT_AlIAS: {_project['alias']}")

    app.navigation.click_btn('Edit')
    assert app.ac_project.checkbox_by_text_is_selected_ac('External System')
    customer = app.ac_project.identify_customer(pytest.env)

    app.ac_project.overview.load_project(data={
        "Project Title": create_project['name'],
        "Project Alias": create_project['alias'],
        "Project Description": "Test Project" + create_project['alias'],
        "Customer": customer,
        "Project Type": project_config['projectType'],
        "Task Type": "Linguistics",
        "Task Volume": "Very Low"
    })
    app.ac_project.tools.load_project(data={
        "External System": "ADAP"
    })
    app.navigation.click_btn('Cancel')
    app.ac_project.verify_project_info({
        "Project Description": "Test Project" + create_project['alias'],
        "Type of Project": project_config['projectType'],
        "Type of Task": 'Linguistics',
        "Task Volume": "Very Low",
        "External Project": "ADAP"
    })


# @pytest.mark.dependency(depends=["test_view_info_in_edit_mode"])
# def test_uncheck_external_system(app, create_project):
#     # uncheck external system checkbox and save the data
#     app.navigation.click_btn('Edit')
#     app.ac_project.tools.fill_out_fields(data={
#         "External System checkbox": "1"
#     })
#
#     app.navigation.click_btn('Save Changes')
#     # app.verification.text_present_on_page('Cannot set a project to non-external while it has external experiments.')
#     # app.ac_project.close_error_msg()

#
# @pytest.mark.dependency(depends=["test_view_info_in_edit_mode"])
# def test_edit_save_external_system(app, create_project):
#     app.navigation.click_btn('Edit')
#     app.ac_project.tools.fill_out_fields(data={
#         "External System checkbox": "1"
#     })
#     app.ac_project.tools.load_project(data={
#         "External System": "ADAP"
#     })
#     app.navigation.click_btn('Save Changes')
#     time.sleep(2)
#     app.ac_project.verify_project_info({
#         "External Project": "ADAP"
#     })


# ---------- View project header and action information ---------
@pytest.mark.dependency()
def test_view_header_information(app, create_project):
    app.ac_project.click_on_step('Overview & tools')
    app.verification.text_present_on_page(create_project['name'])
    current_url = app.driver.current_url
    index = current_url.find('view')
    global project_id
    project_id = current_url[index + 5:]
    print("ID", project_id)
    header_info = app.ac_project.get_header_info()
    print("HEADER INFO", header_info)
    assert 'ID' in header_info
    assert (create_project['alias']).lower() in header_info.lower()
    assert project_id in header_info


@pytest.mark.dependency(depends=["test_view_header_information"])
def test_view_actions_in_header(app, create_project):
    app.ac_project.click_on_step('Overview & tools')
    app.ac_project.get_action_in_header_info('Clone Project')
    app.ac_project.get_action_in_header_info('Delete')
    user_project = app.ac_project.get_action_in_header_info('User Project Page')
    user_project.click()
    time.sleep(2)
    current_url = app.driver.current_url
    assert '/qrp/core/vendors/project_site/' + project_id in current_url
    # need go back to new experience page for other test  cases
    # app.navigation.click_link('Partner Home')
    # app.navigation.switch_to_frame("page-wrapper")
    # app.project_list.filter_project_list_by(name=create_project['name'])
    # app.project_list.open_project_by_name(create_project['name'])
    # app.driver.switch_to.default_content()
    # app.navigation.click_btn("View new experience")
    # app.navigation.switch_to_frame("page-wrapper")
