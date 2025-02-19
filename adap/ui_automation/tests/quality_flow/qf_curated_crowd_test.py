import datetime
import time
import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowExternalApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file
from adap.ui_automation.services_config.quality_flow.components import login_and_open_qf_page, create_new_project_qf_api

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              mark_env]

ACCOUNT = 'qf_user_ui'
faker = Faker()


@pytest.fixture(scope="module")
def qf_login(app):
    login_and_open_qf_page(app, ACCOUNT)


def new_simple_project():
    team_id = get_test_data(ACCOUNT, 'teams')[0]['id']
    api_key = get_test_data(ACCOUNT, 'api_key')

    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    project_name = f"automation project Curated Crowd {_today} {faker.zipcode()}"

    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    api = QualityFlowExternalApiProject(api_key=api_key)

    res = api.post_create_project(team_id=team_id, payload=payload, headers=api.headers)
    response = res.json_response
    assert res.status_code == 200
    assert response.get('message', False) == 'success'

    project_id = response.get('data').get('id', False)

    return {"id": project_id,
            "name": project_name,
            "team": team_id}


@pytest.fixture(scope="module")
def new_project(app):
    details = create_new_project_qf_api('qf_user_ui', prefix="automation project Crowd")

    time.sleep(5)
    app.navigation.refresh_page()

    app.quality_flow.open_project(by='name', value=details['name'])

    # upload data
    app.navigation.click_link('Dataset')
    app.verification.current_url_contains('/dataset')

    sample_file = get_data_file("/sentiment_of_this_content_5_rows.csv")
    app.quality_flow.data.all_data.upload_data(sample_file)
    time.sleep(3)

    app.navigation.click_link('Jobs')
    app.quality_flow.jobs.click_add_new_job_to(connection_type='data_source')

    time.sleep(1)
    app.quality_flow.jobs.fill_out_job_name(job_name="Lead Job", action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Work Job', template='scratch')
    job_id_scratch = app.quality_flow.job.grab_job_id_from_url()

    app.quality_flow.job.return_to_jobs()
    app.navigation.click_link('Jobs')
    time.sleep(2)
    app.quality_flow.jobs.click_add_new_job_to(connection_type='job_id', value=job_id_scratch)

    app.verification.text_present_on_page("Create a following QA job")

    app.quality_flow.jobs.fill_out_job_name(job_name="QA Job", action='Confirm')
    app.quality_flow.jobs.select_new_job_property(job_type='Quality Assurance (QA) Job')
    job_id = app.quality_flow.job.grab_job_id_from_url()
    app.quality_flow.job.return_to_jobs()

    return {
        "id": details['id'],
        "name": details['name'],
        "team_id": details['teamId'],
        "version": details['version']
    }


@pytest.mark.qf_ui_smoke
def test_qf_access_curated_crowd_page(app, qf_login, new_project):
    """
     verify: user has access to "Curated Crowd" tab
             if AC project ID is empty - Save button is disabled
             able to set up AC project ID
             select Project targeting settings
    """
    app.navigation.click_link('Curated Contributors')
    app.verification.text_present_on_page("What is Curated Crowd?")
    app.verification.text_present_on_page("If you already have access")
    app.verification.text_present_on_page("It's a experienced team curated by us. We recruit and source custom groups "
                                          "of skilled contributors and match them to a customer’s specific project "
                                          "requirements. To hire our crowd management capabilities contact your "
                                          "Customer Success Manager.")
    app.verification.text_present_on_page("Enter your Appen Connect project ID below to access project settings and "
                                          "launch jobs to our Appen Connect contributors.")
    app.verification.text_present_on_page("Appen connect project id")

    assert app.verification.link_is_disable('Save', method='cursor_property')

    app.quality_flow.crowd.send_ac_project_id(project_id=86)
    assert not app.verification.link_is_disable('Save', method='cursor_property')
    app.navigation.click_link('Save')

    app.verification.text_present_on_page("Target all Appen Connect contributors")
    app.verification.text_present_on_page("Target specific Appen Connect Locales")
    app.verification.text_present_on_page("Target specific Appen Connect User Groups")

    assert app.verification.link_is_disable('Save settings', method='cursor_property')


@pytest.mark.qf_ui_smoke
@pytest.mark.dependency()
def test_qf_target_all_ac_contributors(app, qf_login, new_project):
    """
    verify user can select all contributors as projects target
    """
    app.navigation.click_link('Curated Contributors')
    app.quality_flow.crowd.select_project_targeting_settings("Target all Appen Connect contributors")
    assert not app.verification.link_is_disable('Save settings', method='cursor_property')
    app.navigation.click_link('Save settings')

    time.sleep(15)
    app.navigation.refresh_page()
    all_units = app.quality_flow.crowd.get_all_units_on_page()
    assert all_units.shape[0] > 0, "No contributors found"


@pytest.mark.qf_ui_smoke
@pytest.mark.dependency(depends=["test_qf_target_all_ac_contributors"])
def test_qf_create_contributor_group(app, qf_login, new_project):
    """
    verify user is able to create contributor group
    """
    app.navigation.refresh_page()
    app.navigation.click_link('Curated Contributors')
    all_units = app.quality_flow.crowd.get_all_units_on_page()
    units_to_select = [x[0] for x in all_units.loc[[0, 1], ['EMAIL AND AC USER ID']].values]
    app.quality_flow.crowd.select_data_units_by(by='EMAIL AND AC USER ID', values=units_to_select)

    app.quality_flow.crowd.click_actions_menu('Create A New Group')
    assert app.verification.link_is_disable('Create Group', method='cursor_property')

    app.quality_flow.crowd.fill_out_contributor_group_details("Group 1", description="Group 1 test",
                                                              action='Create Group')

    app.navigation.click_link('contributor groups')
    time.sleep(3)
    all_units = app.quality_flow.crowd.get_all_units_on_page()
    assert all_units.shape[0] > 0, "No contributor groups found"

    assert all_units['GROUP NAME'].values[0] == 'Group 1'
    assert all_units['CONTRIBUTORS'].values[0] == '2 members'


@pytest.mark.qf_ui_smoke
@pytest.mark.dependency(depends=["test_qf_create_contributor_group"])
def test_qf_assign_contributor_to_job(app, qf_login, new_project):
    """
    verify user is able to assign contributors to jobs
    """
    app.navigation.click_link('Curated Contributors')
    all_units = app.quality_flow.crowd.get_all_units_on_page()
    units_to_select = [x[0] for x in all_units.loc[[2, 3], ['EMAIL AND AC USER ID']].values]
    app.quality_flow.crowd.select_data_units_by(by='EMAIL AND AC USER ID', values=units_to_select)

    app.quality_flow.crowd.click_actions_menu('Assign Or Unassign To A Job')
    app.quality_flow.crowd.assign_contributor_to_jobs(units_to_select[0], ["Lead Job", "QA Job"])
    app.quality_flow.crowd.assign_contributor_to_jobs(units_to_select[1], ["Lead Job", "QA Job"])
    app.navigation.click_link('Close')

    all_units = app.quality_flow.crowd.get_all_units_on_page()
    assert all_units.loc[all_units['EMAIL AND AC USER ID'] == units_to_select[0]].values[0][-1] == '2 jobs'
    assert all_units.loc[all_units['EMAIL AND AC USER ID'] == units_to_select[1]].values[0][-1] == '2 jobs'


@pytest.mark.qf_uat_ui
def test_qf_curated_crowd_invalid_ac_project(app_test):
    """
    verify user can not use invalid AC project id - project is not exist
                                                    or contains of char's instead of number
    verify user can cansel Curated Crowd settings
    """

    new_project = new_simple_project()

    username = get_test_data(ACCOUNT, 'email')
    password = get_test_data(ACCOUNT, 'password')

    app_test.user.login_as_customer(username, password)

    app_test.mainMenu.quality_flow_page()
    time.sleep(5)
    app_test.navigation.refresh_page()

    app_test.quality_flow.open_project(by='name', value=new_project['name'])
    app_test.navigation.click_link('Curated Contributors')

    app_test.verification.text_present_on_page("To launch jobs to our Appen Connect contributors, click on the Add Project button on the top right.")
    app_test.verification.text_present_on_page("Custom Contributors are skilled contributors we source, screen and recruit to match your project requirements.")
    app_test.verification.text_present_on_page(" Contact your Customer Success Manager, or visit our website.")
    app_test.verification.text_present_on_page("Learn more at our website and talk to an expert ↗")

    app.navigation.click_link('Add Project')
    app_test.verification.text_present_on_page('Appen connect project id')

    assert app_test.verification.link_is_disable('Save And Add Project', method='cursor_property')

    app_test.quality_flow.crowd.send_ac_project_id(project_id=31231243412)
    app_test.navigation.click_link('Check ID')
    assert app_test.verification.link_is_disable('Save And Add Project', method='cursor_property')
    # app_test.verification.text_present_on_page('Please enter a valid project ID')

    app_test.quality_flow.crowd.send_ac_project_id(project_id='vldfklk')
    app_test.navigation.click_link('Check ID')
    assert app_test.verification.link_is_disable('Save And Add Project', method='cursor_property')
    # app_test.verification.text_present_on_page('Please enter a valid project ID')

    app_test.quality_flow.crowd.send_ac_project_id(project_id=86)
    app_test.navigation.click_link('Check ID')
    app_test.verification.text_present_on_page('Please enter a valid project ID', is_not=False)
    app_test.verification.text_present_on_page('Target all Appen Connect contributors')
    app_test.navigation.click_link('Target all Appen Connect contributors')
    assert not app_test.verification.link_is_disable('Save And Add Project', method='cursor_property')


@pytest.mark.dependency()
@pytest.mark.qf_uat_ui
def test_qf_curated_crowd_target_specific_locale(app_test):
    new_project = new_simple_project()

    username = get_test_data(ACCOUNT, 'email')
    password = get_test_data(ACCOUNT, 'password')

    app_test.user.login_as_customer(username, password)

    app_test.mainMenu.quality_flow_page()
    time.sleep(5)
    app_test.navigation.refresh_page()

    global project_filter_test
    project_filter_test = new_project['name']

    app_test.quality_flow.open_project(by='name', value=new_project['name'])
    app_test.navigation.click_link('Curated Contributors')

    app_test.quality_flow.crowd.send_ac_project_id(project_id='01')
    app_test.navigation.click_link('Save')
    time.sleep(5)

    app_test.quality_flow.crowd.select_project_targeting_settings("Target specific Appen Connect Locales")
    app_test.navigation.click_link('Add')

    app_test.verification.text_present_on_page('Target specific Appen Connect Locales')
    app_test.verification.text_present_on_page('Target specific users within a combination of language and country.')

    app_test.quality_flow.crowd.select_project_locale('hin_ind,ita_ita', action='Save And Close')
    app_test.verification.text_present_on_page('2 locales selected')

    app_test.navigation.click_link('Save settings')
    app_test.verification.wait_untill_text_present_on_the_page('Country', max_time=120)

    time.sleep(10)
    all_units_on_page = app_test.quality_flow.crowd.get_all_units_on_page()


    print("---", all_units_on_page)

    assert set(all_units_on_page['COUNTRY'].values).issubset(set(['ITA','IND']))
    assert len(all_units_on_page.loc[all_units_on_page['COUNTRY'] == 'ITA']) > 0
    assert len(all_units_on_page.loc[all_units_on_page['COUNTRY'] == 'IND']) > 0
    assert len(all_units_on_page.loc[all_units_on_page['COUNTRY'] == 'USA']) == 0

@pytest.mark.qf_uat_ui
@pytest.mark.dependency(depends=["test_qf_curated_crowd_target_specific_locale"])
def test_qf_curated_crowd_filter_by_country(app_test):
    """
    verify crowd filters list
    verify contributor can be filtered by country
    verify filter cam be removed
    """
    username = get_test_data(ACCOUNT, 'email')
    password = get_test_data(ACCOUNT, 'password')

    app_test.user.login_as_customer(username, password)

    app_test.mainMenu.quality_flow_page()
    time.sleep(5)
    app_test.navigation.refresh_page()

    app_test.quality_flow.open_project(by='name', value=project_filter_test)
    time.sleep(5)
    app_test.navigation.click_link('Curated Contributors')

    all_filters = app_test.quality_flow.crowd.get_all_filters()
    assert all_filters == ['Contributor Information', 'Country', 'Gender', 'Age', 'Language', 'Locale', 'Dialect', 'Mobile OS', 'Project Statistics', 'Pay Rate', 'Total Units', 'Total Judgments', 'Efficiency', 'Accuracy']

    app_test.navigation.refresh_page()
    time.sleep(5)

    all_units_on_page_no_filter = app_test.quality_flow.crowd.get_all_units_on_page()
    assert set(all_units_on_page_no_filter['COUNTRY'].values).issubset(set(['ITA', 'IND']))
    assert len(all_units_on_page_no_filter.loc[all_units_on_page_no_filter['COUNTRY'] == 'ITA']) > 0
    assert len(all_units_on_page_no_filter.loc[all_units_on_page_no_filter['COUNTRY'] == 'IND']) > 0
    assert len(all_units_on_page_no_filter.loc[all_units_on_page_no_filter['COUNTRY'] == 'USA']) == 0

    app_test.quality_flow.crowd.select_filter('Country', 'Equals', 'ITA', 'Apply')
    app_test.verification.text_present_on_page('1 Filter')

    all_units_on_page_filter_country = app_test.quality_flow.crowd.get_all_units_on_page()
    assert len(all_units_on_page_filter_country.loc[all_units_on_page_filter_country['COUNTRY'] == 'ITA']) > 0
    assert len(all_units_on_page_filter_country.loc[all_units_on_page_filter_country['COUNTRY'] == 'IND']) == 0

    app_test.quality_flow.data.all_data.remove_current_filter()
    app_test.verification.text_present_on_page('1 Filter', is_not=False)

    all_units_on_page_no_filter = app_test.quality_flow.crowd.get_all_units_on_page()
    assert set(all_units_on_page_no_filter['COUNTRY'].values).issubset(set(['ITA', 'IND']))
    assert len(all_units_on_page_no_filter.loc[all_units_on_page_no_filter['COUNTRY'] == 'ITA']) > 0
    assert len(all_units_on_page_no_filter.loc[all_units_on_page_no_filter['COUNTRY'] == 'IND']) > 0
    assert len(all_units_on_page_no_filter.loc[all_units_on_page_no_filter['COUNTRY'] == 'USA']) == 0


#
# TODO
# def test_qf_curated_crowd_target_user_group(qf_login, new_simple_project):
#     pass
#
#
# def test_qf_curated_crowd_filter_contributors(qf_login, new_simple_project):
#     pass


