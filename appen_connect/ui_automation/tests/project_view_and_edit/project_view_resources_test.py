
import time

from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

"""
Create a project with specific "Resources" configuration using API
and the tests validates the Project Resources configuration when newly created project is being viewed and tests while editing the configuration
"""

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = [pytest.mark.regression_ac_project_view, pytest.mark.regression_ac, pytest.mark.ac_ui_project_resources, pytest.mark.ac_ui_project_view_n_edit]

config = {}

_project = generate_project_name()

_country = "*"
_country_ui = "United States of America"
_locale  = "English (United States)"
_fluency = "Native or Bilingual"
_lan = "eng"
_lan_ui = "English"
_lan_country = "*"
_pay_rate = 6

existing_academy01 = "Needs Met Academy" #APPLE TEST
existing_academy02 = "Your Side By Side Academy" #CATS
existing_academy03 = "The E-A-T Academy" #Got Academy
existing_academy04 = "Project Nile Academy" #The Start line

up_existing_academy01 = existing_academy01.upper()
up_existing_academy02 = existing_academy02.upper()
up_existing_academy03 = existing_academy03.upper()
up_existing_academy04 = existing_academy04.upper()

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
        "restrictToCountry": _country
    },
    "pay_rates": {
        "create": False
    }
}


@pytest.fixture(scope="module")
def user_project_page(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    time.sleep(2)
    ac_api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                     app.driver.get_cookies()}

    global _project
    _project = api_create_simple_project(project_config, ac_api_cookie)

    return _project


@pytest.mark.dependency()
def test_user_project_page_access(app, user_project_page):
    app.navigation.click_link('Projects')
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(user_project_page['name'])
    app.project_list.open_project_by_name(user_project_page['name'])

    app.driver.switch_to.default_content()
    try:
        app.navigation.click_btn("View new experience")
        time.sleep(2)
    except:
        print("new UI")

    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Resume Setup")

    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('User Project Page')

    app.verification.text_present_on_page("All Types")
    app.verification.text_present_on_page("No Resources Added")


@pytest.mark.dependency(depends=["test_user_project_page_access"])
def test_academy_resource_required_field(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Academy")

    app.verification.text_present_on_page("Allow Qualifying Applicants Access")
    app.verification.text_present_on_page("Allow Active Users Access")

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("Academy is a required field.")


@pytest.mark.dependency(depends=["test_academy_resource_required_field"])
def test_academy_resource_add(app, user_project_page):

    app.ac_project.user_project.fill_out_fields({
        # "Academy":"Apple Test",
        "Academy":existing_academy01,
        "Allow Active Users Access": 1
    })

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page(existing_academy01)

    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Academy")
    app.ac_project.user_project.fill_out_fields({
        "Academy": existing_academy03,
        "Allow Qualifying Applicants Access": 1
    })

    app.ac_project.user_project.save_project_resource()
    _current_resources = app.ac_project.user_project.get_project_resources()
    assert _current_resources[0] == {'name': f'ACADEMY | {up_existing_academy01}', 'access': 'Access: Active users and Qualifying applicants'}
    assert _current_resources[1] == {'name': f'ACADEMY | {up_existing_academy03}', 'access': 'Access: Active users'}


@pytest.mark.dependency(depends=["test_academy_resource_add"])
def test_academy_resource_add_duplicate(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Academy")
    app.ac_project.user_project.fill_out_fields({
        "Academy": existing_academy03,
        "Allow Qualifying Applicants Access": 1
    })

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("There is already a resource with this academy.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_academy_resource_add_duplicate"])
def test_academy_resource_edit_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('ACADEMY', existing_academy01, 'Edit')

    app.ac_project.user_project.fill_out_fields({
            "Academy": existing_academy03
        })

    app.ac_project.user_project.save_project_resource()

    # app.verification.text_present_on_page("There is already a resource with this academy.")
    app.verification.text_present_on_page("Something went wrong, please try again soon")
    app.ac_project.user_project.save_project_resource(is_not=False)
#  TODO add edit


@pytest.mark.dependency(depends=["test_academy_resource_edit_duplicate"])
def test_academy_resource_copy_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('ACADEMY', existing_academy01, 'Copy')

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("There is already a resource with this academy.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_academy_resource_copy_duplicate"])
def test_academy_resource_copy(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('ACADEMY', existing_academy01, 'Copy')

    app.ac_project.user_project.fill_out_fields({
                "Academy": existing_academy02
            })

    app.ac_project.user_project.save_project_resource()

    _current_resources =  app.ac_project.user_project.get_project_resources()
    assert find_dict_in_array_by_value(_current_resources, 'name', f'ACADEMY | {up_existing_academy01}') == {'name': f'ACADEMY | {up_existing_academy01}', 'access': 'Access: Active users and Qualifying applicants'}

    assert find_dict_in_array_by_value(_current_resources, 'name', f'ACADEMY | {up_existing_academy03}') == {'name': f'ACADEMY | {up_existing_academy03}', 'access': 'Access: Active users'}
    assert find_dict_in_array_by_value(_current_resources, 'name', f'ACADEMY | {up_existing_academy01}') == {'name': f'ACADEMY | {up_existing_academy01}', 'access': 'Access: Active users and Qualifying applicants'}


@pytest.mark.dependency(depends=["test_academy_resource_copy"])
def test_academy_resource_edit(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('ACADEMY', existing_academy02, 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Academy": existing_academy04,
        "Allow Qualifying Applicants Access": 1
    })

    app.ac_project.user_project.save_project_resource()

    _current_resources = app.ac_project.user_project.get_project_resources()
    assert find_dict_in_array_by_value(_current_resources, 'name', f'ACADEMY | {up_existing_academy01}') == {'name': f'ACADEMY | {up_existing_academy01}',
                                                                      'access': 'Access: Active users and Qualifying applicants'}

    assert find_dict_in_array_by_value(_current_resources, 'name', f'ACADEMY | {up_existing_academy03}') == {'name': f'ACADEMY | {up_existing_academy03}',
                                                                      'access': 'Access: Active users'}
    assert find_dict_in_array_by_value(_current_resources, 'name', f'ACADEMY | {up_existing_academy04}') == {'name': f'ACADEMY | {up_existing_academy04}',
                                                                      'access': 'Access: Active users'}


@pytest.mark.dependency(depends=["test_academy_resource_edit"])
def test_academy_resource_delete(app, user_project_page):
    _current_resources = app.ac_project.user_project.get_project_resources()
    app.ac_project.user_project.click_context_menu_project_resource('ACADEMY', existing_academy04, 'Delete')

    _new_resources = app.ac_project.user_project.get_project_resources()
    assert len(_current_resources)-1 == len(_new_resources)


# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# ---------------------------------DOCUMENT--------------------------------------
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------


@pytest.mark.dependency(depends=["test_academy_resource_delete"])
def test_document_resource_required_field(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Document")

    app.verification.text_present_on_page("Upskilling")
    app.verification.text_present_on_page("Guideline")
    app.verification.text_present_on_page("Allow Qualifying Applicants Access")
    app.verification.text_present_on_page("Add Notes To Raters")

    app.ac_project.user_project.fill_out_fields({
        "Guideline": 1,
        "Add Notes To Raters": 1
    })
    app.verification.text_present_on_page("REQUIRE ACKNOWLEDGEMENT")

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page('When "Add Notes to Raters" is checked this is a required field.')
    app.verification.text_present_on_page("Document is a required field.")


@pytest.mark.dependency(depends=["test_document_resource_required_field"])
def test_document_resource_add(app, user_project_page):

    app.ac_project.user_project.fill_out_fields({
        "Document":"Ads Doc",
        "Allow Qualifying Applicants Access": 1,
        "Add Notes To Raters": 1
    })

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page("Ads Doc")

    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Document")
    app.ac_project.user_project.fill_out_fields({
        "Document": "Platte Product Rating",
        "Upskilling": 1
    })

    app.ac_project.user_project.save_project_resource()
    _current_resources = app.ac_project.user_project.get_project_resources()
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | PLATTE PRODUCT RATING') == \
           {'name': 'DOCUMENT | PLATTE PRODUCT RATING', 'access': 'Document type: Upskilling'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | ADS DOC') ==\
           {'name': 'DOCUMENT | ADS DOC', 'access': 'Document type: Guideline\nAccess: Active users and Qualifying applicants'}


@pytest.mark.dependency(depends=["test_document_resource_add"])
def test_document_resource_add_duplicate(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Document")
    app.ac_project.user_project.fill_out_fields({
        "Document": "Platte Product Rating",
        "Upskilling": 1
    })

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page("Document mapping already exists.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_document_resource_add_duplicate"])
def test_document_resource_edit_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('DOCUMENT', 'Ads Doc', 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Document": "Platte Product Rating",
        "Upskilling": 1
    })

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("Document mapping already exists.")
    # app.verification.text_present_on_page("Something went wrong, please try again soon")
    app.ac_project.user_project.save_project_resource(is_not=False)
#  TODO add edit


@pytest.mark.dependency(depends=["test_document_resource_edit_duplicate"])
def test_document_resource_copy_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('DOCUMENT', 'Ads Doc', 'Copy')

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("Document mapping already exists.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_document_resource_copy_duplicate"])
def test_document_resource_copy(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('DOCUMENT', 'Ads Doc', 'Copy')

    app.ac_project.user_project.fill_out_fields({
                "Document": "Social FAQ"
            })

    app.ac_project.user_project.save_project_resource()

    _current_resources =  app.ac_project.user_project.get_project_resources()
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | PLATTE PRODUCT RATING') == \
           {'name': 'DOCUMENT | PLATTE PRODUCT RATING', 'access': 'Document type: Upskilling'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | SOCIAL FAQ') == \
           {'name': 'DOCUMENT | SOCIAL FAQ', 'access': 'Document type: Guideline\nAccess: Active users and Qualifying applicants'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | ADS DOC') == \
           {'name': 'DOCUMENT | ADS DOC', 'access': 'Document type: Guideline\nAccess: Active users and Qualifying applicants'}


@pytest.mark.dependency(depends=["test_document_resource_copy"])
def test_document_resource_edit(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('DOCUMENT', 'Ads Doc', 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Document": "User Instruction Test"
    })

    app.ac_project.user_project.save_project_resource()

    _current_resources = app.ac_project.user_project.get_project_resources()

    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | PLATTE PRODUCT RATING') == \
          {'name': 'DOCUMENT | PLATTE PRODUCT RATING', 'access': 'Document type: Upskilling'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | SOCIAL FAQ') == \
          {'name': 'DOCUMENT | SOCIAL FAQ', 'access': 'Document type: Guideline\nAccess: Active users and Qualifying applicants'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'DOCUMENT | USER INSTRUCTION TEST') == \
          {'name': 'DOCUMENT | USER INSTRUCTION TEST', 'access': 'Document type: Guideline\nAccess: Active users and Qualifying applicants'}


@pytest.mark.dependency(depends=["test_document_resource_edit"])
def test_document_resource_delete(app, user_project_page):
    _current_resources = app.ac_project.user_project.get_project_resources()
    app.ac_project.user_project.click_context_menu_project_resource('DOCUMENT', 'Platte Product Rating', 'Delete')

    _new_resources = app.ac_project.user_project.get_project_resources()
    assert len(_current_resources)-1 == len(_new_resources)


@pytest.mark.dependency(depends=["test_document_resource_delete"])
def test_document_resource_guideline_delete(app, user_project_page):
    _current_resources = app.ac_project.user_project.get_project_resources()
    app.ac_project.user_project.click_context_menu_project_resource('DOCUMENT', 'User Instruction Test', 'Delete')

    # app.verification.text_present_on_page("Cannot delete an Active Guideline.") #Absolete
    app.navigation.refresh_page()
    time.sleep(2)
    app.navigation.switch_to_frame("page-wrapper")
    app.ac_project.click_on_step('User Project Page')


# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# -------------------------------------QUIZ--------------------------------------
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------


@pytest.mark.dependency(depends=["test_document_resource_guideline_delete"])
def test_quiz_resource_required_field(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Quiz")

    app.verification.text_present_on_page("Shuffle Questions")
    app.verification.text_present_on_page("Show Question Feedback")
    app.verification.text_present_on_page("Maximum attempts")
    app.verification.text_present_on_page("Subset size")
    app.verification.text_present_on_page("Passing score")
    app.verification.text_present_on_page("UNLIMITED")
    app.verification.text_present_on_page("ALL QUESTIONS")

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page('Quiz is a required field.')
    app.verification.text_present_on_page("Maximum Attemps is a required field.")
    app.verification.text_present_on_page("Subset size is a required field.")
    app.verification.text_present_on_page("Passing Score is a required field.")


@pytest.mark.dependency(depends=["test_quiz_resource_required_field"])
def test_quiz_resource_add(app, user_project_page):

    app.ac_project.user_project.fill_out_fields({
        "Quiz": "Delta Japanese",
        "Shuffle Questions": 1,
        "Show Question Feedback": 1,
        "Maximum Attempts": 4,
        "Subset Size" : 1,
        "Passing Score": 70
    })

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page("Delta Japanese")

    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Quiz")
    app.ac_project.user_project.fill_out_fields({
        "Quiz": "IGS Qualification",
        "UNLIMITED": 1,
        "ALL QUESTIONS": 1,
        "Passing Score": 50
    })

    app.ac_project.user_project.save_project_resource()
    _current_resources = app.ac_project.user_project.get_project_resources()

    assert find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | DELTA JAPANESE') ==  {'name': 'QUIZ | DELTA JAPANESE', 'access': 'Max attempts: 4, Subset size: 1, Passing score: 70%'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | IGS QUALIFICATION') == {'name': 'QUIZ | IGS QUALIFICATION', 'access': 'Max attempts: Unlimited, Subset size: All questions, Passing score: 50%'}


#  TODO unlimited verification
# TODO ERROR  errorThe size of subset of question pages to be shown to the user must be less than the number of available question pages in the quiz (or survey)

@pytest.mark.dependency(depends=["test_quiz_resource_add"])
def test_quiz_resource_add_duplicate(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Quiz")
    app.ac_project.user_project.fill_out_fields({
        "Quiz": "IGS Qualification",
        "UNLIMITED": 1,
        "ALL QUESTIONS": 1,
        "Passing Score": 50
    })

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page("There is already a resource with this quiz.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_quiz_resource_add_duplicate"])
def test_quiz_resource_edit_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('QUIZ', 'Delta Japanese', 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Quiz": "IGS Qualification"
    })

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("There is already a resource with this quiz.")
    app.ac_project.user_project.save_project_resource(is_not=False)
#  TODO add edit


@pytest.mark.dependency(depends=["test_quiz_resource_edit_duplicate"])
def test_quiz_resource_copy_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('QUIZ', 'Delta Japanese', 'Copy')

    app.ac_project.user_project.save_project_resource()

    app.verification.text_present_on_page("There is already a resource with this quiz.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_quiz_resource_copy_duplicate"])
def test_quiz_resource_copy(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('QUIZ', 'Delta Japanese', 'Copy')

    app.ac_project.user_project.fill_out_fields({
                "Quiz": "M-Test"
            })

    app.ac_project.user_project.save_project_resource()

    _current_resources =  app.ac_project.user_project.get_project_resources()

    assert find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | DELTA JAPANESE') ==  {'name': 'QUIZ | DELTA JAPANESE', 'access': 'Max attempts: 4, Subset size: 1, Passing score: 70%'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | M-TEST') == {'name': 'QUIZ | M-TEST', 'access': 'Max attempts: 4, Subset size: 1, Passing score: 70%'}


@pytest.mark.dependency(depends=["test_quiz_resource_copy"])
def test_quiz_resource_edit(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('QUIZ', 'M-Test', 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Quiz": "Social and Chat Dynamics"
    })

    app.ac_project.user_project.save_project_resource()

    _current_resources = app.ac_project.user_project.get_project_resources()

    assert not find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | M-TEST')
    assert find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | SOCIAL AND CHAT DYNAMICS') == {'name': 'QUIZ | SOCIAL AND CHAT DYNAMICS', 'access': 'Max attempts: 4, Subset size: 1, Passing score: 70%'}


@pytest.mark.dependency(depends=["test_quiz_resource_edit"])
def test_quiz_resource_delete(app, user_project_page):
    _current_resources = app.ac_project.user_project.get_project_resources()
    app.ac_project.user_project.click_context_menu_project_resource('QUIZ', 'Social and Chat Dynamics', 'Delete')

    _new_resources = app.ac_project.user_project.get_project_resources()
    assert len(_current_resources)-1 == len(_new_resources)


# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# ------------------------------------SURVEY-------------------------------------
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------


@pytest.mark.dependency(depends=["test_quiz_resource_delete"])
def test_survey_resource_required_field(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Survey")

    app.verification.text_present_on_page("Shuffle Questions")
    app.verification.text_present_on_page("Show Question Feedback", is_not=False)
    app.verification.text_present_on_page("Maximum attempts")
    app.verification.text_present_on_page("Subset size")


    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page('Survey is a required field.')
    app.verification.text_present_on_page("Maximum Attemps is a required field.")
    app.verification.text_present_on_page("Subset size is a required field.")



@pytest.mark.dependency(depends=["test_survey_resource_required_field"])
def test_survey_resource_add(app, user_project_page):

    app.ac_project.user_project.fill_out_fields({
        "Survey": "Arrow Date Test",
        "Shuffle Questions": 1,
        "Maximum Attempts": 4,
        "Subset Size" : 1
    })

    app.ac_project.user_project.save_project_resource()
    app.verification.text_present_on_page("Arrow Date Test")

    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Survey")
    app.ac_project.user_project.fill_out_fields({
        "Survey": "CU test",
        "UNLIMITED": 1,
        "ALL QUESTIONS": 1
    })

    app.ac_project.user_project.save_project_resource()
    _current_resources = app.ac_project.user_project.get_project_resources()

    assert find_dict_in_array_by_value(_current_resources, 'name', 'SURVEY | ARROW DATE TEST') ==  \
           {'name': 'SURVEY | ARROW DATE TEST', 'access': 'Max attempts: 4, Subset size: 1'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'SURVEY | CU TEST') ==\
           {'name': 'SURVEY | CU TEST', 'access': 'Max attempts: Unlimited, Subset size: All questions'}


 # TODO unlimited verification

@pytest.mark.dependency(depends=["test_survey_resource_add"])
def test_survey_resource_add_duplicate(app, user_project_page):
    app.navigation.click_btn("Add Resource")
    app.ac_project.user_project.select_resource_type("Survey")
    app.ac_project.user_project.fill_out_fields({
                "Survey": "CU test",
                "UNLIMITED": 1,
                "ALL QUESTIONS": 1
            })

    app.ac_project.user_project.save_project_resource()
    # bug - redirects on quiz page
    # app.verification.text_present_on_page("There is already a resource with this survey.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_survey_resource_add_duplicate"])
def test_survey_resource_edit_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('SURVEY', 'CU test', 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Survey": "Arrow Date Test"
    })

    app.ac_project.user_project.save_project_resource()
    #  bug -  There is already a resource with this quiz.
    # app.verification.text_present_on_page("There is already a resource with this survey.")
    app.ac_project.user_project.save_project_resource(is_not=False)
#  TODO add edit


@pytest.mark.dependency(depends=["test_survey_resource_edit_duplicate"])
def test_survey_resource_copy_duplicate(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('SURVEY', 'CU test', 'Copy')

    app.ac_project.user_project.save_project_resource()
    #  bug -  There is already a resource with this quiz.
    # app.verification.text_present_on_page("There is already a resource with this quiz.")
    app.ac_project.user_project.save_project_resource(is_not=False)


@pytest.mark.dependency(depends=["test_survey_resource_copy_duplicate"])
def test_survey_resource_copy(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('SURVEY', 'CU test', 'Copy')

    app.ac_project.user_project.fill_out_fields({
                "Survey": "Jackson Survey"
            })

    app.ac_project.user_project.save_project_resource()

    _current_resources =  app.ac_project.user_project.get_project_resources()

    assert find_dict_in_array_by_value(_current_resources, 'name', 'SURVEY | ARROW DATE TEST') ==  \
           {'name': 'SURVEY | ARROW DATE TEST', 'access': 'Max attempts: 4, Subset size: 1'}
    assert find_dict_in_array_by_value(_current_resources, 'name', 'SURVEY | JACKSON SURVEY') ==\
           {'name': 'SURVEY | JACKSON SURVEY', 'access': 'Max attempts: Unlimited, Subset size: All questions'}
    assert  find_dict_in_array_by_value(_current_resources, 'name', 'SURVEY | CU TEST') ==  \
            {'name': 'SURVEY | CU TEST', 'access': 'Max attempts: Unlimited, Subset size: All questions'}


@pytest.mark.dependency(depends=["test_survey_resource_copy"])
def test_survey_resource_edit(app, user_project_page):
    app.ac_project.user_project.click_context_menu_project_resource('SURVEY', 'Jackson Survey', 'Edit')

    app.ac_project.user_project.fill_out_fields({
        "Survey": "Domain Expertise"
    })

    app.ac_project.user_project.save_project_resource()

    _current_resources = app.ac_project.user_project.get_project_resources()

    assert not find_dict_in_array_by_value(_current_resources, 'name', 'QUIZ | JACKSON SURVEY')


@pytest.mark.dependency(depends=["test_survey_resource_edit"])
def test_survey_resource_delete(app, user_project_page):
    _current_resources = app.ac_project.user_project.get_project_resources()
    app.ac_project.user_project.click_context_menu_project_resource('SURVEY', 'Domain Expertise', 'Delete')

    _new_resources = app.ac_project.user_project.get_project_resources()
    assert len(_current_resources)-1 == len(_new_resources)

@pytest.mark.dependency(depends=["test_survey_resource_delete"])
def test_resources_filter(app, user_project_page):
    _all_resources = app.ac_project.user_project.get_project_resources()
    _count = 0
    for res_type, res_value in {'Quizzes':'QUIZ', 'Surveys':'SURVEY', 'Academies': 'ACADEMY', 'Documents':'DOCUMENT'}.items():
        app.ac_project.user_project.fill_out_fields({"Filter resources": res_type})
        _current_resources = app.ac_project.user_project.get_project_resources()

        _count += len(_current_resources)
        for _res in _current_resources:
            assert _res['name'].startswith(res_value)

    assert len(_all_resources) == _count






