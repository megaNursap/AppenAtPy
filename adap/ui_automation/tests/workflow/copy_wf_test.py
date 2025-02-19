import allure

from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api
from adap.api_automation.services_config.mlapi import *
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, get_akon_id
from adap.e2e_automation.workflow_e2e_test import payload1, payload2, payload3
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.builder import *
from adap.ui_automation.services_config.user import *

pytestmark = [pytest.mark.wf_ui,
              pytest.mark.regression_wf]

API_KEY = get_user_api_key('test_ui_account')
USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
TEAM_ID = get_user_team_id('test_ui_account')
AKON_ID = get_akon_id('test_ui_account')


@pytest.fixture(scope="function")
def new_wf(request):
    wf = Workflow(API_KEY, AKON_ID)
    wf_name = generate_random_wf_name()
    payload = {'name': wf_name, 'description': 'API create new wf'}
    wf.create_wf(payload=payload)
    return wf.wf_id


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.user.contributor.alert_window()


def create_jobs():
    _jobs = []
    _job_titles = []

    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)
    _job_titles.append(payload1["job"]["title"])

    job_id = create_job_from_config_api({"job": payload2["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)
    _job_titles.append(payload2["job"]["title"])

    job_id = create_job_from_config_api({"job": payload3["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)
    _job_titles.append(payload3["job"]["title"])
    return _jobs, _job_titles


def create_model(num=2):
    model = MLAPI(AKON_ID, team_id=TEAM_ID)
    _model_ids = []
    _model_names = []
    for i in range(num):
        response = model.create_model(model_type='f8-coherence-detection')
        _model_ids.append(model.model_id)
        _model_names.append(response.json_response.get('name'))
    return _model_ids, _model_names


@pytest.mark.wf_ui
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui_smoke_wf
@allure.issue("https://appen.atlassian.net/browse/ADAP-2255", "BUG  on Integration ADAP-2255")
def test_copy_empty_wf_from_copy_icon(app, new_wf, login):
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(new_wf)
    app.workflow.click_copy_icon(new_wf)

    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)
    app.navigation.click_link("Copy")
    time.sleep(5)

    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/" + new_copied_wf_id + "/data")
    app.navigation.switch_to_window(app.driver.window_handles[1])
    app.verification.text_present_on_page(wf_name)
    app.driver.close()
    app.navigation.switch_to_window(app.driver.window_handles[0])


@pytest.mark.wf_ui
@pytest.mark.fed_ui_smoke_wf
def test_copy_empty_wf_from_gear_icon(app, new_wf, login):
    app.mainMenu.workflows_page()
    app.workflow.click_on_gear_for_wf(new_wf, "Copy Workflow")

    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)
    app.navigation.click_link("Copy")
    time.sleep(2)

    app.workflow.open_wf_with_name(wf_name)
    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/" + new_copied_wf_id + "/data")
    app.verification.text_present_on_page(wf_name)


@pytest.mark.wf_ui
@pytest.mark.fed_ui_smoke_wf
@pytest.mark.workflow_deploy
@pytest.mark.flaky(reruns=2)
@allure.issue("https://appen.atlassian.net/browse/ADAP-2255", "BUG  on Integration ADAP-2255")
def test_copy_wf_with_job_with_data_from_copy_icon(app, new_wf, login):
    api_job_id, api_job_title = create_jobs()

    wf = Workflow(API_KEY)
    wf.create_job_step(api_job_id, new_wf)

    # opening API created WF and copying it from copy icon
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(new_wf)
    # app.navigation.click_link("Next: Upload Data")
    app.verification.element_is('disabled', 'Next: Add Steps')

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app.job.data.upload_file(sample_file)
    app.navigation.click_link("Data")
    app.verification.text_present_on_page("customer_01_sample_22.csv")

    app.workflow.click_copy_icon(new_wf)

    # providing random name for copy WF
    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)
    app.navigation.click_link("Copy")
    time.sleep(7)

    # grabbing ID and verifying the correct url
    new_wf_window = app.driver.window_handles[1]
    app.navigation.switch_to_window(new_wf_window)
    time.sleep(2)


    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/workflows/" + new_copied_wf_id)
    app.verification.text_present_on_page(wf_name)

    copied_job_ids = wf.get_job_id_from_wf(new_copied_wf_id)
    copied_job_titles = wf.get_title_of_job(copied_job_ids)

    assert len(api_job_id) == len(copied_job_ids), "Number of copied jobs are not matching with original jobs"

    assert sorted(api_job_title) == sorted(
        copied_job_titles), "Title of copied jobs are not matching with title of original jobs"

    app.navigation.click_link("Data")
    app.verification.text_present_on_page('Supported Formats')
    app.verification.text_present_on_page('.csv, .tsv, .xls, .xlsx, .ods')


@pytest.mark.wf_ui
@pytest.mark.fed_ui_smoke_wf
def test_copy_wf_with_job_from_gear_icon(app, new_wf, login):
    api_job_id, api_job_title = create_jobs()

    wf = Workflow(API_KEY)
    wf.create_job_step(api_job_id, new_wf)

    # opening API created WF and copying it from gear icon
    app.mainMenu.workflows_page()
    app.workflow.click_on_gear_for_wf(new_wf, "Copy Workflow")

    # providing random name for copied job
    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)
    app.navigation.click_link("Copy")
    time.sleep(10)

    # grabbing ID and verifying the correct url
    app.workflow.open_wf_with_name(wf_name)
    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/" + new_copied_wf_id + "/data")
    app.verification.text_present_on_page(wf_name)

    copied_job_ids = wf.get_job_id_from_wf(new_copied_wf_id)
    copied_job_titles = wf.get_title_of_job(copied_job_ids)

    assert len(api_job_id) == len(copied_job_ids), "Number of copied jobs are not matching with original jobs"
    assert sorted(api_job_title) == sorted(
        copied_job_titles), "Title of copied jobs are not matching with title of original jobs"

    for i in range(len(copied_job_ids)):
        app.mainMenu.jobs_page()
        app.job.open_job_with_id(copied_job_ids[i])
        app.job.open_tab('DATA')
        app.verification.text_present_on_page("Data upload is not allowed because this job is part of a Workflow")
        app.verification.text_present_on_page("You can add more data using")


@pytest.mark.wf_ui
#@allure.issue("https://appen.atlassian.net/browse/ADAP-2255", "BUG  on Integration ADAP-2255")
@allure.issue("https://appen.atlassian.net/browse/ADAP-2921", "BUG on Integration/Staging ADAP-2921")
def test_copy_wf_with_model_from_copy_icon(app, new_wf, login):
    api_model_id, api_model_names = create_model()
    wf = Workflow(API_KEY)
    ml = MLAPI(AKON_ID)

    wf.create_model_step(api_model_id, new_wf)

    # opening API created WF and copying it from copy icon
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(new_wf)
    app.workflow.click_copy_icon(new_wf)

    # providing random name for copy WF
    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)

    current_windows = len(app.driver.window_handles)
    app.navigation.click_link("Copy")
    time.sleep(7)

    new_wf_window = app.driver.window_handles[current_windows]
    app.navigation.switch_to_window(new_wf_window)

    # grabbing ID and verifying the correct url
    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/" + new_copied_wf_id + "/data")
    app.verification.text_present_on_page(wf_name)


    # getting model id of copied model
    copied = wf.get_model_id_from_wf(new_copied_wf_id)
    copied_model_ids = [int(x) for x in copied]

    copied_model_names = ml.get_names_of_model(copied_model_ids)

    assert sorted(api_model_id) == sorted(copied_model_ids), "Copied model ID is not matching with original model ID"
    assert sorted(api_model_names) == sorted(
        copied_model_names), "Copied model name is not matching with original model name"


@pytest.mark.wf_ui
@allure.issue("https://appen.atlassian.net/browse/ADAP-2921", "BUG on Integration/Staging ADAP-2921")
def test_copy_wf_with_model_from_gear_icon(app, new_wf, login):
    api_model_id, api_model_names = create_model()
    wf = Workflow(API_KEY)
    ml = MLAPI(AKON_ID)

    wf.create_model_step(api_model_id, new_wf)

    # opening API created WF and copying it from gear icon
    app.mainMenu.workflows_page()
    app.workflow.click_on_gear_for_wf(new_wf, "Copy Workflow")

    # providing random name for copy WF
    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)
    app.navigation.click_link("Copy")
    time.sleep(2)

    # grabbing ID and verfiying the correct url
    app.workflow.open_wf_with_name(wf_name)
    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/" + new_copied_wf_id + "/data")
    app.verification.text_present_on_page(wf_name)

    # getting model id of copied model
    copied = wf.get_model_id_from_wf(new_copied_wf_id)
    copied_model_ids = [int(x) for x in copied]

    copied_model_names = ml.get_names_of_model(copied_model_ids)

    assert api_model_id.sort() == copied_model_ids.sort(), "Copied model ID is not matching with original model ID"
    assert sorted(api_model_names) == sorted(
        copied_model_names), "Copied model name is not matching with original model name"
