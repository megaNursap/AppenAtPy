import time

from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from appen_connect.api_automation.services_config.new_project_support import api_create_simple_project
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_list, pytest.mark.regression_ac, pytest.mark.ac_project_list]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
PROJECT_NAME = generate_project_name()
PROJECT_ALIAS = generate_project_name()



@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    app.navigation.switch_to_frame("page-wrapper")


def create_project(ac_cookie):
    api = AC_API(ac_cookie)
    project_details = {}
    payload = {
        "alias": PROJECT_ALIAS[1],
        "name": PROJECT_NAME[0],
        "taskVolume": "VERY_LOW",
        "workType": "LINGUISTICS",
        "description": PROJECT_NAME[0],
        "projectType": "Regular"

    }
    res = api.create_project(payload=payload)
    res.assert_response_status(201)
    project_details['name'] = res.json_response['name']
    project_details['alias'] = res.json_response['alias']
    project_details['description'] = res.json_response['description']
    return project_details


@pytest.mark.ac_ui_uat
def test_project_list_show_items(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    all_reports = app.project_list.get_num_of_all_reports()

    for reports_num in [15, 20, 30, 50]:
        app.project_list.set_up_show_items(reports_num)
        time.sleep(2)
        expected_reports = min(reports_num, all_reports)
        reports_on_page = app.project_list.count_projects_on_page()
        assert reports_on_page == expected_reports


@pytest.mark.ac_ui_uat
def test_expand_project_details(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name='Instagram Truckee')

    app.verification.text_present_on_page('Project description', is_not=False)

    app.project_list.click_toggle_for_project_details(search_field='name',
                                                      search_value='Instagram Truckee')

    app.verification.text_present_on_page('Project description')

    # close
    app.project_list.click_toggle_for_project_details(search_field='name',
                                                      search_value='Instagram Truckee')
    app.verification.text_present_on_page('Project description', is_not=False)

    app.project_list.click_more_less_for_project(search_field='name',
                                                 search_value='Instagram Truckee',
                                                 click_type='More')
    app.verification.text_present_on_page('Project description')

    details = app.project_list.get_project_expanded_details(search_field='name',
                                                            search_value='Instagram Truckee')

    assert details['description'] == "Help improve ads quality for one of the world's largest image sharing " \
                                     "sites.REQUIRED: An active Facebook and Instagram account (Instagram account " \
                                     "must be connected to your Facebook account). A smartphone device (iOS or " \
                                     "Android preferred)."

    app.project_list.click_more_less_for_project(search_field='name',
                                                 search_value='Instagram Truckee',
                                                 click_type='Less')

    app.verification.text_present_on_page('Project description', is_not=False)

    app.project_list.filter_project_list_by(program='All programs', status='All Statuses', name='')


# def test_clone_project(app, login):
#     app.navigation.refresh_page()
#     app.navigation.switch_to_frame("page-wrapper")
#
#     app.project_list.filter_project_list_by(customer='Appen Internal', status='Enabled')
#
#     _project = random.choice(app.project_list.get_projects_on_page())
#
#     app.project_list.click_action_for_project(search_field='id', search_value=_project['id'], action='Clone Project')
#
#     app.verification.current_url_contains('/partners/project/edit')
#
#     new_project_info = app.project_old_ui.get_current_project_info()
#     assert _project['name'] in new_project_info['project.name']
#     assert 'clone' in new_project_info['project.name']
#
#     app.navigation.browser_back()
#     app.project_list.filter_project_list_by(customer='', status='')


# @pytest.mark.ac_ui_uat
# def test_view_experiments_project(app, login):
#     app.navigation.refresh_page()
#     app.navigation.switch_to_frame("page-wrapper")
#
#     app.project_list.filter_project_list_by(name='Figure Eight integration')
#
#     _project = random.choice(app.project_list.get_projects_on_page())
#
#     app.project_list.click_action_for_project(search_field='id', search_value=_project['id'], action='View Experiments')
#
#     app.verification.current_url_contains('/partners/experiments')
#
#     app.navigation_old_ui.click_input_btn("Go")
#     time.sleep(2)
#
#     # app.verification.text_present_on_page('Figure Eight integration')
#     app.navigation.browser_back()
#
#     app.verification.current_url_contains('/partners/projects')


def test_resume_project(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.project_list.filter_project_list_by(status='Draft')

    _project = random.choice(app.project_list.get_projects_on_page())

    app.project_list.click_action_for_project(search_field='id', search_value=_project['id'],
                                              action='Resume Project Setup')

    app.verification.current_url_contains('/partners/project/editNewProject')
    app.navigation.switch_to_frame("page-wrapper")

    app.verification.text_present_on_page('Project Setup')
    app.ac_project.click_on_step('Project Overview')
    app.ac_project.overview.load_project(data={
        "Project Name": _project['name']
    })
    app.navigation.browser_back()

    app.verification.current_url_contains('/partners/projects')


@pytest.mark.ac_ui_uat
@pytest.mark.parametrize('status, context_menu',
                         [
                         ('Draft', {'User Project Page': False, 'Resume Project Setup': True, 'View Experiments': True,
                                     'Open Tracker': True, 'Clone Project': True, 'Delete': False}),
                          ('Ready', {'User Project Page': False, 'View Experiments': True, 'Open Tracker': True,
                                     'Clone Project': True, 'Delete': False}),
                          ('Enabled', {'User Project Page': False, 'View Experiments': True, 'Open Tracker': True,
                                       'Clone Project': True, 'Delete': False}),
                          ('Disabled', {'User Project Page': False, 'View Experiments': True, 'Open Tracker': True,
                                        'Clone Project': True,'Delete': False})
                          ])
def test_project_list_context_menu_options(app, login, status, context_menu):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(program='All programs', status=status)
    random_project = random.choice(app.project_list.get_projects_on_page())
    assert app.project_list.open_context_menu_for_project(search_field='id',
                                                          search_value=random_project['id']) == context_menu


@pytest.mark.parametrize('column, project_field',
                         [
                             ('ID', 'id'),
                          ('PROJECT', 'name'),
                          ('TYPE OF TASK', 'type'),
                          ('PROGRAM', 'program'),
                          ('STATUS', 'status')
                          ])
def test_project_order_by(app, login, column, project_field):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    if column == 'PROJECT':
        app.project_list.filter_project_list_by(status='Enabled')

    app.project_list.order_project_list_by(column)
    _projects = app.project_list.get_projects_on_page()

    if project_field == 'id':
        _ = [int(x[project_field]) for x in _projects]
    else:
        _ = [x[project_field].lower() for x in _projects]
    assert _ == sorted(_)

    app.project_list.order_project_list_by(column)
    _projects = app.project_list.get_projects_on_page()
    if project_field == 'id':
        _ = [int(x[project_field]) for x in _projects]
    else:
        _ = [x[project_field].lower() for x in _projects]
    assert _ == sorted(_, reverse=True)


@pytest.mark.ac_ui_uat
@pytest.mark.parametrize('program',
                         [
                             ("Arogorn_NER"),
                             ("A9"),
                             ("Facebook"),

                         ])
def test_project_list_filter_by_customer(app, login, program):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(program=program)
    time.sleep(5)
    all_projects = app.project_list.get_projects_on_page()
    if all_projects:
        for x in all_projects:
            assert program == x['program']
    else:
        print("There are no projects under this customer : %s" % program)


@pytest.mark.ac_ui_uat
@pytest.mark.parametrize('status',
                         [
                             ("Enabled"),
                             ("Disabled"),
                             ("Draft"),
                             ("Ready")
                         ])
def test_project_list_by_status(app, login, status):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(status=status)
    time.sleep(2)
    all_projects = app.project_list.get_projects_on_page()
    time.sleep(2)
    for x in all_projects:
        assert status == x['status']



@pytest.mark.parametrize('alias_or_name',
                         [("google"), ("facebook")])
def test_project_list_filter_by_partial_alias_or_name(app, login, alias_or_name):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=alias_or_name)
    _projects = app.project_list.get_projects_on_page()
    for i in range(len(_projects)):
        app.project_list.click_toggle_for_project_details(search_field='id', search_value=_projects[i]['id'])
        project_details = app.project_list.get_project_expanded_details(search_field='id',
                                                                        search_value=_projects[i]['id'])
        time.sleep(2)
        assert project_details['name'].lower().find(alias_or_name) > -1
        app.project_list.click_toggle_for_project_details(search_field='id', search_value=_projects[i]['id'])


@pytest.mark.ac_ui_uat
def test_project_list_filter_by_full_name_and_alias(app, login):
    app.navigation.refresh_page()
    # app.navigation.click_link('View previous list page')
    # app.ac_user.select_customer('Appen Internal')
    _api_cookie = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                            app.driver.get_cookies()}

    _country = "*"
    _country_ui = "United States of America"
    _locale = "English (United States)"
    _fluency = "Native or Bilingual"
    _lan = "eng"
    _lan_ui = "English"
    _lan_country = "*"
    _pay_rate = 6

    project_config = {
        "projectType": 'Regular',
        "workType": "LINGUISTICS",
        "externalSystemId": 15,
        "qualificationProcessTemplateId": 1386,
        "registrationProcessTemplateId": 764,
        "locale": {
            "country": _country
        }
    }
    input_project_details = api_create_simple_project(project_config, _api_cookie)

    app.navigation.click_link("Projects")
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name=input_project_details['name'])
    time.sleep(2)
    projects = app.project_list.get_projects_on_page()
    assert (len(projects) == 1)
    assert (input_project_details['name'] == projects[0]['name'])
    # app.project_list.click_toggle_for_project_details(search_field='id', search_value=projects[0]['id'])
    # projects_expanded_details = app.project_list.get_project_expanded_details(search_field='id', search_value=projects[0]['id'])
    # assert (input_project_details['alias'] == projects_expanded_details['alias'])

    #Test to filter the search by Alias of the project
    # app.navigation.refresh_page()
    # app.navigation.switch_to_frame("page-wrapper")
    # app.project_list.filter_project_list_by(name=input_project_details['alias'])
    # time.sleep(2)
    # projects = app.project_list.get_projects_on_page()
    # app.project_list.click_toggle_for_project_details(search_field='id', search_value=projects[0]['id'])
    # projects_expanded_details = app.project_list.get_project_expanded_details(search_field='id', search_value=projects[0]['id'])
    # assert (len(projects) == 1)
    # assert (input_project_details['alias'] == projects_expanded_details['alias'])


@pytest.mark.ac_ui_uat
def test_project_list_search_filter_by_name_not_present(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.project_list.filter_project_list_by(name='sajfklsjflksdjfsl')
    time.sleep(2)
    projects = app.project_list.get_projects_on_page()
    assert (len(projects) == 0)
    assert (app.verification.text_present_on_page("No Results Found"))
