"""
Test Questions Generator
"""
import time

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.utils.data_util import *

from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.job.job_quality import find_tq_job, generate_tq_for_job
from adap.ui_automation.utils.pandas_utils import collect_data_from_ui_table

pytestmark = pytest.mark.regression_tq

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


def create_job(api_key):
    """
    create new job by api
    """
    sample_file = get_data_file("/dod_data.csv")

    job = Builder(api_key)
    resp = job.create_job_with_csv(sample_file)
    _job_id = job.job_id
    assert resp.status_code == 200, "Job was not created"

    return _job_id


def login_as_customer_and_open_job(app, _id):
    """
    login as a customer and open job by ID
    """
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(_id)
    app.job.open_tab("DESIGN")
    app.job.open_tab("DATA")


@pytest.fixture(scope="module")
def new_job_tqg(app):
    global job_id
    job_id = create_job(API_KEY)
    login_as_customer_and_open_job(app, job_id)


@pytest.mark.tqg
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
@pytest.mark.dependency()
def test_order_tq(app, new_job_tqg):
    """
    As a customer with TQG enabled, I should see an "Add More" option on the quality page
    As a customer, I should be able to select the number of TQs to be ordered
    As a customer, I should be able to create TQs manually while a TQG order is in progress
    As a customer, I cannot order more than one TQ job at a time
    As a customer that has ordered TQs, I will see a test question status modal representing the order status
    """

    app.job.open_tab("QUALITY")
    time.sleep(2)
    app.job.quality.click_generate_tq()
    app.job.quality.order_tq(5, "Appen Trusted Contributors")
    app.navigation.click_link('Order')
    app.navigation.refresh_page()

    app.job.quality.create_random_tqs(2)
    app.job.open_tab("QUALITY")
    app.verification.text_present_on_page('Add More')
    app.job.quality.create_random_tqs(2)
    app.job.open_tab("QUALITY")
    # assert app.job.quality.order_more_tg_btn_is_disable()

    # app.verification.text_present_on_page('Lock Exists: Order Already In Progress.') ? msg


@pytest.mark.tqg
@pytest.mark.dependency(depends=["test_order_tq"])
def test_order_questions_with_level_x(app_test):
    """
    As a customer, I can order test questions with Level x
    """
    _api_key = get_user_api_key('test_tqg')
    _user = get_user_email('test_tqg')
    _password = get_user_password('test_tqg')

    wf = Workflow(_api_key)
    res = wf.get_list_of_wfs()

    tq_job_id = find_tq_job(job_id, res.json_response)

    app_test.user.login_as_customer(_user, _password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tq_job_id)

    app_test.job.open_action("Settings")
    app_test.job.open_settings_tab("Contributors")

    app_test.verification.text_present_on_page('Level X TQG')



@pytest.mark.slow
@pytest.mark.e2e
@pytest.mark.tqg
@pytest.mark.dependency(depends=["test_order_tq"])
def test_generate_tq(app, new_job_tqg):
    """
    As a customer, I should see TQs automatically converted and added to the original job as soon as they are created

    As a customer, I should be able to determine which rows were created manually and by a TQG job As a customer,
    once I ordered TQs, theTQ creation job instructions are copied from the origin job with appended additional
    instructions at the top

    As a customer, once I are order TQs, theTQ creation job should transform CM
    """
    _api_key = get_user_api_key('test_tqg')

    job = Builder(API_KEY)
    job.job_id = job_id
    wf = Workflow(_api_key)
    res = wf.get_list_of_wfs()
    tq_job_id = find_tq_job(job_id, res.json_response)

    _tq_job = Builder(_api_key)
    res = _tq_job.get_json_job_status(tq_job_id)
    instructions_tq_job = res.json_response['instructions']
    cml_tq_job = res.json_response['cml']

    assert '<cml:checkbox label="Skip This Question" value="skip_this_question"/>' in cml_tq_job
    assert '<cml:textarea label="Skip Question Reason" validates="required" class="cml-wrapper" only-if="skip_this_question"/>' in cml_tq_job
    assert '<cml:checkbox label="Confirm Completion" validates="required" value="tq_confirm_completion"/>' in cml_tq_job

    inst_tq = "In this job you will be creating test questions "
    assert inst_tq in instructions_tq_job
    job_link = generate_job_link(tq_job_id, _api_key, pytest.env)
    # add tq job to tear down (delete job)
    pytest.data.job_collections[tq_job_id] = _api_key

    generate_tq_for_job(job_link, "test_ui_account",
                        {"total_count": 5, "answers_by_index": [3, 2], "skipped": 0})

    job.wait_until_golds_count(count=9, max_time=60*30)
    res = job.get_json_job_status()
    assert res.json_response['golds_count'] == 9

    app.navigation.refresh_page()
    app.job.open_tab("QUALITY")

    time.sleep(3)
    assert app.job.quality.get_count_tqs_by_type("Generated") == '5 of 5'
    assert app.job.quality.get_count_tqs_by_type("Created") == '4'
    assert app.job.quality.get_count_tqs_by_type("Total Active") == '9'

    df = collect_data_from_ui_table(app.driver, False)

    created_df = df.loc[df.type == "Created"]
    generated_df = df.loc[df.type == "Generated"]

    assert len(created_df) == 4
    assert len(generated_df) == 5
    assert not app.job.quality.order_more_tg_btn_is_disable()

    app.driver.quit()


@pytest.mark.slow
@pytest.mark.e2e
@pytest.mark.tqg
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_skipped_questions(app_test):
    """
    As a customer, I will not be shown the skipped TQs
    As a customer, I can order test questions with Level x
    As a customer, once I are order TQs, the TQG job updates various settings to ensure it will run properly
    As a customer, once I are order TQs, the origin does not update various settings to ensure it will run properly
    As a customer, once I are order TQs, I will not be notified my job is associated with a workflow
    """
    _current_job = create_job(API_KEY)

    login_as_customer_and_open_job(app_test, _current_job)

    app_test.job.open_tab("QUALITY")

    app_test.job.quality.click_generate_tq()
    app_test.job.quality.order_tq(5, "Appen Trusted Contributors")
    app_test.navigation.click_link('Order')

    time.sleep(10)
    # current job is not associated with a workflow
    assert app_test.workflow.find_wf_name_for_job(_current_job) is None

    _job = Builder(API_KEY)
    _job.job_id = _current_job
    current_res = _job.get_json_job_status()

    assert current_res.json_response['alias'] is None
    assert current_res.json_response['judgments_per_unit'] == 3
    assert current_res.json_response['units_per_assignment'] == 5
    assert current_res.json_response['pages_per_assignment'] == 1
    assert current_res.json_response['max_judgments_per_worker'] is None
    assert current_res.json_response['payment_cents'] == 35
    assert current_res.json_response['units_remain_finalized'] is None
    assert current_res.json_response['send_judgments_webhook'] is None
    assert current_res.json_response['language'] == 'en'
    assert current_res.json_response['assignment_duration'] == 1800
    assert current_res.json_response['included_countries'] == []
    assert current_res.json_response['excluded_countries'] == []
    assert current_res.json_response['units_count'] == 5
    assert current_res.json_response['golds_count'] == 0

    # find TQ job id and get status for TQ job
    _api_key = get_user_api_key('test_tqg')

    wf = Workflow(_api_key)
    res = wf.get_list_of_wfs()

    _tq_job_id = find_tq_job(_current_job, res.json_response)

    _tq_job = Builder(_api_key)
    _tq_job.job_id = _tq_job_id
    _tq_job.wait_until_status('running', 300)
    res = _tq_job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    # add tq job to tear down (delete job)
    pytest.data.job_collections[_tq_job_id] = _api_key

    assert res.json_response['alias'] is None
    assert res.json_response['judgments_per_unit'] == 1
    assert res.json_response['units_per_assignment'] == 1
    assert res.json_response['pages_per_assignment'] == 1
    assert res.json_response['max_judgments_per_worker'] == 500
    assert res.json_response['payment_cents'] == int(
        current_res.json_response['payment_cents'] / current_res.json_response['units_per_assignment'] * 20)
    assert res.json_response['webhook_uri'] is None
    assert res.json_response['send_judgments_webhook'] is None
    assert res.json_response['language'] == 'en'
    assert res.json_response['assignment_duration'] == 7200
    assert res.json_response['included_countries'] == []
    assert res.json_response['excluded_countries'] == []
    assert res.json_response['units_count'] == 5

    tq_job_link = generate_job_link(_tq_job_id, _api_key, pytest.env)

    generate_tq_for_job(tq_job_link, "test_ui_account",
                        {"total_count": 5, "answers_by_index": [3], "skipped": 2})

    _job.wait_until_golds_count(count=3, max_time=300)
    time.sleep(10)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(_current_job)
    app_test.job.open_tab("QUALITY")
    assert app_test.job.quality.get_count_tqs_by_type("Generated") == '3 of 5'
    assert app_test.job.quality.get_count_tqs_by_type("Created") == '0'
    assert app_test.job.quality.get_count_tqs_by_type("Total Active") == '3'

    df = collect_data_from_ui_table(app_test.driver, False)

    created_df = df.loc[df.type == "Created"]
    generated_df = df.loc[df.type == "Generated"]

    assert len(created_df) == 0
    assert len(generated_df) == 3

