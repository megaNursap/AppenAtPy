import datetime

from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name, tomorrow_date
from adap.api_automation.utils.data_util import *

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_ui_new_project, pytest.mark.ac_ui_project_recruitment]


@pytest.fixture(scope="module")
def login_and_create_project(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    project_name = generate_project_name()
    app.ac_project.create_new_project()
    customer = app.ac_project.identify_customer(pytest.env)

    app.ac_project.overview.fill_out_fields(data={
        "Project Title": "Recrutment_"+project_name[0],
        "Project Alias": "Recrutment_"+project_name[1],
        "Project Description": "New Project Description",
        "Customer": customer,
        "Project Type": "Express",
        "Task Type": "Express",
        "Task Volume": "Very Low"
    })

    app.navigation.click_btn('Next: Registration and Qualification')

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


# local tenant
def test_add_tenant_required_fields(app, login_and_create_project):
    """
    03.01 Recruitment: Locale Tenants: verify required field
    """
    app.navigation.click_btn('Add Tenant')
    app.verification.text_present_on_page("Country is a required field.", is_not=False)
    app.verification.text_present_on_page("Tenant is a required field.", is_not=False)

    app.ac_project.recruitment.click_save_add_tenant()
    app.verification.text_present_on_page("Country is a required field.")
    app.verification.text_present_on_page("Tenant is a required field.")

    app.ac_project.recruitment.click_cancel_add_tenant()


def test_add_tenant_cancel(app, login_and_create_project):
    """
    03.01 Recruitment: Locale Tenants
    """
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Russian Federation", tenant='Appen Ltd. (Contractor)', action=None)
    app.ac_project.recruitment.click_cancel_add_tenant()

    assert app.ac_project.recruitment.get_locale_tenant_count() == 0
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Russian Federation", "Appen Ltd.", "Contractor", is_not=False)


def test_add_tenant_save(app, login_and_create_project):
    """
    03.01 Recruitment: Locale Tenants
    """
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Russian Federation", tenant='Appen Ltd. (Contractor)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Russian Federation", "Appen Ltd.", "Contractor")


def test_edit_locale_tenant(app, login_and_create_project):
    """
    03.01 Recruitment: Locale Tenants
    """
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Brazil", tenant='Appen Ltd. (Contractor)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Brazil", "Appen Ltd.", "Contractor")

    app.ac_project.recruitment.edit_tenant("Brazil", "Appen Ltd.", "Contractor", "Bulgaria", 'Appen Ltd. (Contractor)')

    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Bulgaria", "Appen Ltd.", "Contractor")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Brazil", "Appen Ltd.", "Contractor", is_not=False)


def test_delete_locale_tenant(app, login_and_create_project):
    """
    03.01 Recruitment: Locale Tenants
    """
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="Albania", tenant='Appen Ltd. (Contractor)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Albania", "Appen Ltd.", "Contractor")

    app.ac_project.recruitment.delete_tenant("Albania", "Appen Ltd.", "Contractor")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("Albania", "Appen Ltd.", "Contractor", is_not=False)


def test_add_hiring_target_required_field(app, login_and_create_project):
    """
    03.02 Recruitment: Actions for Hiring Targets
    """
    app.navigation.click_btn('Add Target')
    app.ac_project.recruitment.click_save_ht()
    app.verification.text_present_on_page("Locale Language is a required field.")
    app.verification.text_present_on_page("Locale Region is a required field.")
    app.verification.text_present_on_page("Restrict to Country is a required field.")
    app.verification.text_present_on_page("Hiring Deadline is a required field.")
    app.verification.text_present_on_page("Target Contributors is a required field.")
    app.verification.text_present_on_page("Target Hours/Tasks is a required field.")
    app.ac_project.recruitment.click_cancel_hiring_target()


def test_add_hiring_target_no_locale_tenant(app, login_and_create_project):
    """
    03.02 Recruitment: Actions for Hiring Targets
    """
    app.ac_project.recruitment.add_target(language='Bosnian', region='All Countries',
                                          restrict_country='All Countries',
                                          deadline=tomorrow_date(), target='12', action="Save")
    app.verification.text_present_on_page("You must have a Locale Tenant for this country.")
    app.ac_project.recruitment.click_cancel_hiring_target()


@pytest.mark.dependency()
def test_add_tenant_all_countries(app, login_and_create_project):
    """
    03.01 Recruitment: Locale Tenants
    """
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="All Countries", tenant='Appen Ltd. (Contractor)')
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("All Countries", "Appen Ltd.", "Contractor")


@pytest.mark.dependency(depends=["test_add_tenant_all_countries"])
def test_add_hiring_target_ui(app, login_and_create_project):
    """
    03.02 Recruitment: Actions for Hiring Targets
    """
    app.navigation.click_btn('Add Tenant')
    app.ac_project.recruitment.add_tenant(country="India", tenant="Appen Ltd. (Contractor)")
    app.ac_project.recruitment.verify_locale_tenant_is_displayed("India", "Appen Ltd.", "Contractor")

    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    app.ac_project.recruitment.add_target(language='Hindi', region='India',
                                          restrict_country='India',
                                          deadline='', target='12')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Hindi', loc_dialect_from='India',
                                                                        rest_to_country='India', deadline= formatted_date, target='12')


    app.ac_project.recruitment.add_target(language='Marathi', region='India',
                                          restrict_country='India',
                                          deadline=tomorrow_date(), target='12')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Marathi', loc_dialect_from='India', rest_to_country='India',
                                                                        deadline=formatted_date, target='12')


@pytest.mark.dependency(depends=["test_add_hiring_target_ui"])
def test_copy_ht_error(app, login_and_create_project):
    app.ac_project.recruitment.click_copy_target("Hindi", "India", "India")
    app.ac_project.recruitment.click_save_ht()

    app.verification.text_present_on_page("You have a very similar target already included. If you need to increase a target, consider editing it.")
    app.ac_project.recruitment.close_error_msg()

@pytest.mark.dependency(depends=["test_copy_ht_error"])
def test_edit_ht(app, login_and_create_project):
    app.ac_project.recruitment.fill_out_fields({"Locale Language": "Kashmiri",
                             "Language Region": "India"})
    app.ac_project.recruitment.click_save_ht()

    formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kashmiri', loc_dialect_from='India',
                                                                        rest_to_country='India',
                                                                        deadline=formatted_date, target='12')


@pytest.mark.dependency(depends=["test_edit_ht"])
def test_delete_ht(app, login_and_create_project):
   app.ac_project.recruitment.delete_target("Kashmiri", "India", "India")
   formatted_date = (custom_strftime('%b {S}, %Y', (datetime.date.today() + datetime.timedelta(days=1))))
   app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kashmiri', loc_dialect_from='India',
                                                                       rest_to_country='India', deadline=formatted_date,
                                                                       target='12', row_is_present=False)

# Blocking Rules
@pytest.mark.dependency()
def test_blocking_rules_required_fields(app, login_and_create_project):
    app.ac_project.recruitment.fill_out_fields({"Blocking Rules": "1"})
    app.navigation.click_btn("Next: Invoice & Payment")

    app.verification.text_present_on_page("Project is a required field.")


@pytest.mark.dependency(depends=["test_blocking_rules_required_fields"])
def test_add_blocking_rules(app, login_and_create_project):
    app.ac_project.recruitment.add_block_project("testFigure8")
    app.ac_project.recruitment.click_permanent_btn("testFigure8")

    app.navigation.click_btn("Add Other Project")

    projects = app.ac_project.recruitment.get_list_of_available_block_projects()
    assert "testFigure8" not in projects

    app.ac_project.recruitment.add_block_project("Project NameQATest")

    app.verification.text_present_on_page("Project NameQATest")


@pytest.mark.dependency(depends=["test_add_blocking_rules"])
def test_delete_blocking_rules(app, login_and_create_project):
    app.ac_project.recruitment.delete_block_project("Project NameQATest")
    app.verification.text_present_on_page("Project NameQATest", is_not=False)

# TODO add blocking rules via API

# Linked Projects
@pytest.mark.dependency()
def test_linked_projects_required_fields(app, login_and_create_project):
    app.ac_project.recruitment.fill_out_fields({"Linked Projects": "1"})
    app.navigation.click_btn("Save")

    app.verification.text_present_on_page("Project is a required field.")


@pytest.mark.dependency(depends=["test_linked_projects_required_fields"])
def test_add_linked_project(app, login_and_create_project):
    app.ac_project.recruitment.add_linked_project("Figure-Eight Testing")

    app.ac_project.recruitment.click_add_other_linked_project()

    projects = app.ac_project.recruitment.get_list_of_available_linked_projects()
    assert "Figure-Eight Testing" not in projects

    app.ac_project.recruitment.add_linked_project("Appen Automation Express Project")

    app.verification.text_present_on_page("Appen Automation Express Project")


@pytest.mark.dependency(depends=["test_add_linked_project"])
def test_delete_linked_project(app, login_and_create_project):
    app.ac_project.recruitment.delete_linked_project("Appen Automation Express Project")
    app.verification.text_present_on_page("Appen Automation Express Project", is_not=False)

@pytest.mark.dependency()
def test_recruting_team_notes_required_field(app, login_and_create_project):
    app.ac_project.recruitment.fill_out_fields({"Add Notes to Recruiting Team": "1"})
    app.navigation.click_btn("Save")
    app.verification.text_present_on_page('When \"Add Notes to Recruiting Team\" is checked this is a required field.')


@pytest.mark.dependency(depends=["test_recruting_team_notes_required_field"])
def test_add_recruting_team_notes(app, login_and_create_project):
    app.ac_project.recruitment.fill_out_fields({"Recruiting Notes": "Test Notes to Recruiting Team"})
    app.verification.text_present_on_page('When \"Add Notes to Recruiting Team\" is checked this is a required field.', is_not=False)

# TODO sorting
@pytest.mark.dependency(depends=["test_add_recruting_team_notes"])
def test_add_all_macro(app, login_and_create_project):

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Arbëreshë Albanian', new_region='Albania',
                                           new_restrict_country='Albania',
                                           new_owner='Michalac (Fatima)',  new_deadline=None, new_target='101')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Võro', new_region='Estonia',
                                           new_restrict_country='Estonia',
                                           new_owner='Michalac (Fatima)',  new_deadline=None, new_target='102')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Standard Latvian', new_region='Latvia',
                                           new_restrict_country='Latvia',
                                           new_owner='Senyutina (Marina)',  new_deadline=None, new_target='103')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Southern Betsimisaraka Malagasy', new_region='Madagascar',
                                           new_restrict_country='Latvia',
                                           new_owner='Senyutina (Marina)',  new_deadline=None, new_target='104')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Cocos Islands Malay', new_region='Cocos (Keeling) Islands',
                                           new_restrict_country='Cocos (Keeling) Islands',
                                           new_owner='Pajjuri (Shashirekha)',  new_deadline=None, new_target='105')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Dotyali', new_region='Nepal',
                                           new_restrict_country='Nepal',
                                           new_owner='Pajjuri (Shashirekha)',  new_deadline=None, new_target='106')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Norwegian Bokmål', new_region='Norway',
                                           new_restrict_country='Norway',
                                           new_owner='Yu (Tracy)',  new_deadline=None, new_target='107')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Iranian Persian', new_region='Iran',
                                           new_restrict_country='Iran',
                                           new_owner='Yu (Tracy)',  new_deadline=None, new_target='108')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Kiswahili', new_region='Tanzania',
                                           new_restrict_country='Tanzania',
                                           new_owner='Yu (Tracy)',  new_deadline=None, new_target='109')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Fanti', new_region='Ghana',
                                           new_restrict_country='Ghana',
                                           new_owner='Yu (Tracy)',  new_deadline=None, new_target='110')

    app.ac_project.recruitment.copy_target(language='Hindi', dialect='India', rest_country='India',
                                           new_language='Eastern Egyptian Bedawi Arabic', new_region='Egypt',
                                           new_restrict_country='Egypt',
                                           new_owner='Yu (Tracy)',  new_deadline=None, new_target='111')


    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Kiswahili', loc_dialect_from='Tanzania',
                                                                        rest_to_country='Tanzania', deadline=None, target='109')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Iranian Persian', loc_dialect_from='Iran',
                                                                        rest_to_country='Iran', deadline=None, target='108')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Norwegian Bokmål', loc_dialect_from='Norway',
                                                                        rest_to_country='Norway', deadline=None, target='107')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Dotyali', loc_dialect_from='Nepal',
                                                                        rest_to_country='Nepal', deadline=None, target='106')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Cocos Islands Malay', loc_dialect_from='Cocos (Keeling) Islands',
                                                                        rest_to_country='Cocos (Keeling) Islands', deadline=None, target='105')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Southern Betsimisaraka Malagasy', loc_dialect_from='Madagascar',
                                                                        rest_to_country='Latvia', deadline=None, target='104')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Standard Latvian', loc_dialect_from='Latvia',
                                                                        rest_to_country='Latvia', deadline=None, target='103')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Võro', loc_dialect_from='Estonia',
                                                                        rest_to_country='Estonia', deadline=None, target='102')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Arbëreshë Albanian', loc_dialect_from='Albania',
                                                                        rest_to_country='Albania', deadline=None, target='101')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Fanti', loc_dialect_from='Ghana',
                                                                        rest_to_country='Ghana', deadline=None, target='110')

    app.ac_project.recruitment.verify_hiring_target_row_present_on_page(loc_lang_from='Eastern Egyptian Bedawi Arabic', loc_dialect_from='Egypt',
                                                                        rest_to_country='Egypt', deadline=None, target='111')

    app.navigation.click_btn("Save")