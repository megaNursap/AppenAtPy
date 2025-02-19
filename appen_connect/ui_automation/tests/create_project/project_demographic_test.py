import datetime
import time

from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name, tomorrow_date
from adap.api_automation.utils.data_util import *

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_ui_new_project, pytest.mark.ac_ui_project_demographics]



@pytest.fixture(scope="module")
def login_and_create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    project_name = generate_project_name()
    app.ac_project.create_new_project()
    customer = app.ac_project.identify_customer(pytest.env)

    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "Demo_" + project_name[0],
        "Project Alias": "Demo_" + project_name[1],
        "Project Description": "Demographics New Project Description",
        "Customer":customer,
        "Project Type": "Regular",
        "Task Type": "Express",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')
    time.sleep(3)

    if pytest.env == "prod":
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Agnew registration",
            "Select Qualification process": "Aliso Qualification"})
    else:
        app.ac_project.registration.fill_out_fields(data={
            "Select Registration process": "Acac Register",
            "Select Qualification process": "Apple NDA"
    })

    app.navigation.click_btn('Next: Recruitment')

    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Russian Federation", tenant='Appen Ltd. (Contractor)')

    app.ac_project.recruitment.add_target(language='Russian', region='Russian Federation', restrict_country='Russian Federation',
                                          deadline=tomorrow_date(), target='12')


@pytest.mark.dependency()
def test_demograph_default_value(app, login_and_create_project):
    app.verification.text_present_on_page('Add Custom Demographic Requirements')
    app.verification.text_present_on_page("Set Demographics", is_not=False)
    assert not app.ac_project.checkbox_by_text_is_selected_ac('Add Custom Demographic Requirements')

    app.ac_project.recruitment.fill_out_fields({"Add Custom Demographic Requirements": "1"})

    app.verification.text_present_on_page("Set Demographics")

    app.navigation.click_btn("Set Demographics")

    app.verification.text_present_on_page('Demographic Requirements Setup')
    app.verification.text_present_on_page('DEMOGRAPHICS TYPE')
    app.verification.text_present_on_page('VIEW AS')
    app.verification.text_present_on_page('SELECT PARAMETERS')
    app.verification.text_present_on_page('Requirements by group')
    app.verification.text_present_on_page('Aggregated requirements', is_not=False)

    params_selected = app.ac_project.recruitment.get_current_num_of_selected_params_demographic()
    assert params_selected == '0'


@pytest.mark.dependency(depends=["test_demograph_default_value"])
def test_demograph_requirements_by_group(app, login_and_create_project):
    app.ac_project.recruitment.set_up_demographic_requirements(params=['Gender', 'Device'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '2'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender', 'Device']

    app.ac_project.recruitment.delete_selected_demographic_param('Device')
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '1'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender']

    app.navigation.click_btn('Cancel')


@pytest.mark.dependency(depends=["test_demograph_requirements_by_group"])
def test_demograph_aggregated_requirements(app, login_and_create_project):
    app.navigation.click_btn("Set Demographics")
    app.ac_project.recruitment.set_up_demographic_requirements(d_type='Aggregated requirements', view='NUMBER', params=['Gender', 'Device', 'Age Range'])
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '3'
    assert app.ac_project.recruitment.get_current_selected_params_demographic() == ['Gender', 'Device', 'Age Range']

    app.ac_project.recruitment.delete_all_selected_demographic_param()
    assert app.ac_project.recruitment.get_current_num_of_selected_params_demographic() == '0'


@pytest.mark.dependency(depends=["test_demograph_requirements_by_group"])
def test_distribution_gender(app, login_and_create_project):
    app.ac_project.recruitment.set_up_demographic_requirements(params=['Gender'])
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.distribute_demograph({'Female': 60, 'Male': 40})
    app.navigation.click_btn('Save Requirements')
    assert app.ac_project.recruitment.get_saved_requirements() == 'Gender'


@pytest.mark.dependency(depends=["test_distribution_gender"])
def test_edit_requirements_by_group(app, login_and_create_project):
    app.ac_project.recruitment.click_edit_saved_req()
    app.verification.text_present_on_page('Demographic Requirements Setup')
    app.verification.text_present_on_page('Save Requirements')

    app.ac_project.recruitment.distribute_demograph({'Female': 70, 'Male': 30})
    app.navigation.click_btn('Save Requirements')

    app.ac_project.recruitment.click_edit_saved_req()
    assert app.ac_project.recruitment.get_current_distribution() == {'GENDER': {'Female': '70',
                                                                                'Male': '30',
                                                                                'Non-Binary / Other': '0'}}
    app.navigation.click_btn('Save Requirements')


@pytest.mark.dependency(depends=["test_edit_requirements_by_group"])
def test_clear_saved_requirements(app, login_and_create_project):
    app.ac_project.recruitment.click_clear_saved_req()
    app.verification.text_present_on_page('REQUIREMENTS BY GROUP', is_not=False)


@pytest.mark.dependency(depends=["test_clear_saved_requirements"])
def test_distribute_evenly(app, login_and_create_project):
    app.navigation.click_btn("Set Demographics")
    app.ac_project.recruitment.set_up_demographic_requirements(params=['Gender', 'Device'])
    app.navigation.click_btn('Next: Distribution')
    app.ac_project.recruitment.click_distribute_evenly()
    assert app.ac_project.recruitment.get_current_distribution() == {'GENDER': {'Female': '33', 'Male': '33', 'Non-Binary / Other': '33'},
                                                                     'DEVICE': {'Android': '50', 'iOS': '50'}}
    app.navigation.click_btn('Save Requirements')


@pytest.mark.dependency(depends=["test_distribute_evenly"])
def test_demographics_preview(app, login_and_create_project):

    app.navigation.click_btn("Next: Invoice & Payment")
    app.ac_project.payment.fill_out_fields({"PROJECT WORKDAY TASK ID": "P12345",
                                            "Rate Type": "By Task",
                                            "Project Business Unit": "CR"})

    app.navigation.click_btn("Add Pay Rate")
    app.ac_project.payment.fill_out_fields({"Custom Pay Rates": "1"})

    app.ac_project.payment.select_custom_pay_rates('Russian (Russian Federation)', 'Russian Federation')

    app.ac_project.payment.fill_out_fields({"Spoken Fluency": "Near Native",
                                            "Written Fluency": "Near Native",
                                            "User Group": "All users",
                                            "Task Type": "Default",
                                            "Rate": 1234
                                            }, action='Save')

    app.navigation.click_btn('Next: Project Tools')
    app.ac_project.tools.fill_out_fields(data={
        "External System": "Ampersand"
    })
    # app.navigation.click_btn("Next: Project Access")
    app.navigation.click_btn("Next: User Project Page")
    app.ac_project.user_project.fill_out_fields({"Default Page Task": "Tasks"})
    app.navigation.click_btn("Next: Support Team")
    app.ac_project.support.fill_out_fields({"Support User Role": "Quality",
                                            "Member Name": "Support (Ac)"})

    app.navigation.click_btn("Next: Preview")

    app.navigation.click_btn("Finish Project Setup")
    app.navigation.click_btn("Go to Project Page")


def test_demographics_view(app, login_and_create_project):
    # app.navigation.open_page("https://connect-stage.integration.cf3.us/qrp/core/partners/project_setup/view/6553")
    app.navigation.switch_to_frame("page-wrapper")

    app.ac_project.click_on_step('Recruitment')
    app.verification.text_present_on_page('Custom Demographic Requirements')
    app.verification.text_present_on_page('Recruiting team will use the parameters set as basis for recruitment.')
    app.verification.text_present_on_page('REQUIREMENTS BY GROUP')
    app.verification.text_present_on_page('Gender, Device')

    app.navigation.click_btn('Demographic Distribution')
    app.verification.text_present_on_page('Demographic Distribution')
    app.verification.text_present_on_page('Requirements by group (Gender, Device)')
    app.verification.text_present_on_page('Custom demographics')
    app.verification.text_present_on_page('NUMBER')
    app.verification.text_present_on_page('PERCENTAGE')

    app.ac_project.recruitment.verify_demografics_header_view(type="Gender", target='RUS > RUS (RUS)', engaged='(0 of 12)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Female", engaged='0')
    app.ac_project.recruitment.verify_demografics_row_view(type="Male", engaged='0')

    app.ac_project.recruitment.verify_demografics_header_view(type="Device", target='RUS > RUS (RUS)', engaged='(0 of 12)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Android", engaged='0')
    app.ac_project.recruitment.verify_demografics_row_view(type="iOS", engaged='0')

    app.ac_project.click_on_step('PERCENTAGE')

    app.ac_project.recruitment.verify_demografics_header_view(type="Gender", target='RUS > RUS (RUS)', engaged='(0% of 100%)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Female", engaged='0% of 33%')
    app.ac_project.recruitment.verify_demografics_row_view(type="Male", engaged='0% of 33%')
    app.ac_project.recruitment.verify_demografics_row_view(type="Non-Binary / Other", engaged='0% of 33%')

    app.ac_project.recruitment.verify_demografics_header_view(type="Device", target='RUS > RUS (RUS)', engaged='(0% of 100%)')
    app.ac_project.recruitment.verify_demografics_row_view(type="Android", engaged='0% of 50%')
    app.ac_project.recruitment.verify_demografics_row_view(type="iOS", engaged='0% of 50%')

    app.ac_project.recruitment.close_modal_window()






