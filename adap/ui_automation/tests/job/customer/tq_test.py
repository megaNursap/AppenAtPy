import time

import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *

pytestmark = [
    pytest.mark.regression_tq
]

api_key = get_user_api_key('test_ui_account')
email = get_user_email('test_ui_account')
password = get_user_password('test_ui_account')


@pytest.fixture(scope="module")
def login(request, app):
    app.user.login_as_customer(user_name=email, password=password)


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui
@pytest.mark.fed_ui_smoke
# @allure.issue("https://appen.atlassian.net/browse/ADAP-3246", "BUG on Sandbox ADAP-3246")
# @allure.issue("https://appen.atlassian.net/browse/JW-122", "BUG  on Sandbox JW-122")
# @allure.issue("https://appen.atlassian.net/browse/ADAP-3165", "BUG  on Integration ADAP-3165")
def test_create_tq(app, login):
    """
    Customer is able to create test question
    """
    sample_file = get_data_file("/authors_add.csv")

    job = Builder(api_key)
    resp = job.create_job_with_csv(sample_file)
    job_id = job.job_id
    assert resp.status_code == 200, "Job was not created"
    time.sleep(10)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DESIGN")
    app.navigation.click_btn("Save")
    app.navigation.click_link("Next: Create Test Questions")
    app.user.close_guide()

    tq_num_rows = random.randint(1, 2)
    app.job.quality.create_random_tqs(tq_num_rows)
    app.job.open_tab("DATA")

    tq_units = app.job.data.find_all_units_with_status("golden")
    assert tq_num_rows == len(tq_units), "%s rows were found, expected - %s" %(len(tq_units), tq_num_rows)


@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_edit_tq(app, login):
    """
        Customer is able to edit test question
    """
    # create job with title, instructions, data and test questions
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    job_id = job.job_id

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("QUALITY")
    unit_id = app.job.quality.open_tq_unit_by_id("random")
    app.job.open_tab("QUALITY")

    app.job.quality.open_tq_unit_by_id(unit_id)

    current_tq_info = app.job.quality.grab_tq_info()

    app.job.quality.click_answer('funny')
    app.job.quality.click_answer('not_funny')

    new_tq_info = app.job.quality.grab_tq_info()

    assert current_tq_info['funny'] != new_tq_info['funny']
    assert current_tq_info['not_funny'] != new_tq_info['not_funny']

    app.job.quality.switch_to_tq_iframe()
    app.navigation.click_link("Save Changes")
    app.driver.switch_to.default_content()

    app.job.quality.open_tq_unit_by_id(unit_id)

    after_save_tq_info = app.job.quality.grab_tq_info()

    assert after_save_tq_info['funny'] == new_tq_info['funny']
    assert after_save_tq_info['not_funny'] == new_tq_info['not_funny']


@pytest.mark.ui_uat
@pytest.mark.fed_ui
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_disable_enable_tq(app, login):
    job = Builder(api_key)
    job.create_simple_job_with_test_questions()
    job_id = job.job_id

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("QUALITY")

    unit_id = app.job.quality.get_random_unit_id()
    num_tqs = app.job.quality.get_number_of_active_tq()

    app.job.quality.disable_tq(unit_id)
    new_num_tqs = app.job.quality.get_number_of_active_tq()
    assert num_tqs == new_num_tqs+1

    time.sleep(2)
    app.job.quality.enable_tq(unit_id)
    enable_num_tqs = app.job.quality.get_number_of_active_tq()

    assert num_tqs == enable_num_tqs


@pytest.mark.ui_uat
@pytest.mark.fed_ui
def test_upload_and_convert_tq_report(app, login):
    app.mainMenu.jobs_page()
    app.job.create_new_job_from_scratch()
    time.sleep(3)
    sample_file = get_data_file('/convertTestQuestions.csv')
    app.job.data.upload_file(sample_file)
    app.job.open_tab("DESIGN")
    app.navigation.click_link('Next: Create Test Questions')
    app.verification.text_present_on_page('Add Test Questions')
    app.verification.text_present_on_page('Test questions are rows with specified answers that are regularly inserted throughout your job.')
    app.job.open_tab("DATA")
    time.sleep(3)
    data_info = app.job.data.get_number_of_units_on_page()
    app.navigation.click_btn('Convert Uploaded Test Questions')
    time.sleep(10)
    app.job.open_tab("QUALITY")
    app.navigation.refresh_page()
    tq_info = app.job.data.get_number_of_units_on_page()
    assert data_info == tq_info
