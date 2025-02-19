import time
"""
https://appen.atlassian.net/browse/AT-5426
This test covers the possibility of copy taxonomy job
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_taxonomy]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
NAME_CSV_FILE = 'tax_csv'
NAME_JSON_FILE = 'tax_json'

USER_EMAIL_2 = get_user_email('test_account')
PASSWORD_2 = get_user_password('test_account')
API_KEY_2 = get_user_api_key('test_account')


@pytest.fixture(scope="module")
def set_job(app):
    app.user.login_as_customer(USER_EMAIL, PASSWORD)
    api_v2 = Builder(api_key=API_KEY, api_version='v2')
    job = Builder(API_KEY)
    job.create_job_with_cml(data.taxonomy_cml)
    job_id = job.job_id
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    api_v2.upload_taxonomy_file_via_public(job_id, API_KEY, name=NAME_CSV_FILE,
                                           file=get_data_file('/taxonomy/tax_category_id.csv'),
                                           type_of_file='text/csv')
    api_v2.upload_taxonomy_file_via_public(job_id, API_KEY, name=NAME_JSON_FILE,
                                           file=get_data_file('/taxonomy/correct_tax.json'),
                                           type_of_file='application/json')
    data_file = get_data_file("/taxonomy/data_for_taxonomy.csv")
    app.job.data.upload_file(data_file)
    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Taxonomies")
    return job_id


@pytest.fixture(autouse=True)
def taxonomy_job(app, set_job):
    yield
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])


def test_copy_taxonomy_job(app, set_job):
    app.job.open_action("Copy,All Rows")
    app.navigation.click_btn("Copy")

    new_job = app.driver.window_handles[1]
    app.navigation.switch_to_window(new_job)

    time.sleep(4)
    app.user.close_guide()
    app.job.open_tab("DESIGN")
    app.navigation.refresh_page()

    app.navigation.click_link("Manage Taxonomies")

    app.verification.text_present_on_page(NAME_CSV_FILE, 10)
    app.verification.text_present_on_page(NAME_JSON_FILE, 10)


def test_user_not_the_same_team_copy_taxonomy_job(app, set_job):
    app.user.logout()
    app.user.login_as_customer(USER_EMAIL_2, PASSWORD_2)

    app.taxonomy.open_taxonomy_page(set_job)

    app.job.open_action("Copy,All Rows")
    app.navigation.click_btn("Copy")

    new_job = app.driver.window_handles[1]
    app.navigation.switch_to_window(new_job)

    time.sleep(4)
    app.user.close_guide()
    app.job.open_tab("DESIGN")
    app.navigation.refresh_page()

    app.navigation.click_link("Manage Taxonomies")

    app.verification.text_present_on_page(NAME_CSV_FILE, 10)
    app.verification.text_present_on_page(NAME_JSON_FILE, 10)