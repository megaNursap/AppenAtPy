import json
import logging
import os
import time

import allure
import urllib3
import pytest

from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.customer_data_service import CDS
from adap.api_automation.services_config.requestor_proxy import RP
from adap.support.crp.api_crp import modify_report_crp, push_test_result_to_crp
from appen_connect.ui_automation.service_config.application import AC
from adap.api_automation.utils.data_util import DataTricks, load_key, get_user_name, get_user_password, get_test_data
from adap.api_automation.utils.service_util import delete_jobs, delete_wfs, delete_models, delete_qf_projects_index, \
    delete_qf_projects
from adap.settings import Config

from adap.ui_automation.services_config.application import Application
from adap.ui_automation.utils.selenium_utils import create_screenshot
from browserstack.local import Local

from gap.ui_automation.service_config.application import Gap
from integration.service_config.application import ADAP_AC

LOGGER = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ignore_collect = [
    'adap/perf_platform',
    'appen_connect/performance'
]


def pytest_ignore_collect(path, config):
    """return True to prevent considering this path for collection.
    This hook is consulted for all files and directories prior to calling
    more specific hooks.
    """
    if list(filter(lambda x: x in str(path), ignore_collect)):
        return True

    return False


def pytest_configure(config):
    pytest.env = config.getoption('--env')
    pytest.appen = 'false'
    pytest.env_fed = config.getoption('--env_fed')
    pytest.flaky = config.getoption('--flaky')
    pytest.set = config.getoption('--set')
    pytest.key = config.getoption('--key')
    pytest.browser_stack = config.getoption('--browser_stack')
    pytest.os_system = config.getoption('--os_system')
    pytest.browser = config.getoption('--browser')
    pytest.customize_fed_url = config.getoption('--customize_fed_url')
    pytest.customize_fed = config.getoption('--customize_fed')
    # pytest.service_tag = config.getoption('--service_tag')
    pytest.jenkins_test_url = config.getoption('--jenkins_test_url')
    pytest.deployment_url = config.getoption('--deployment_url')
    pytest.crp = config.getoption('--crp')
    pytest.jira = config.getoption('--jira')

    if pytest.env.startswith('ac_'):
        pytest.env = pytest.env[3:]
        pytest.appen = 'true'

    if pytest.env is not None:
        Config.ENV = pytest.env

    running_in_devspace = "devspace" in pytest.env
    pytest.running_in_devspace = running_in_devspace
    pytest.running_in_preprod = pytest.env in ["sandbox", "integration", "staging"] or running_in_devspace
    pytest.running_in_preprod_subset = pytest.env in ["sandbox", "integration"] or running_in_devspace
    pytest.running_in_preprod_sandbox = pytest.env in ["sandbox"] or running_in_devspace
    pytest.running_in_preprod_integration = pytest.env in ["integration"] or running_in_devspace
    pytest.running_in_preprod_sandbox_fed = pytest.env in ["sandbox", "fed"] or running_in_devspace
    pytest.running_in_preprod_adap_ac = pytest.env in ["adap_ac"] or running_in_devspace
    pytest.data = DataTricks()

    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is not None:
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=f"tests_{worker_id}.log",
            level=config.getini("log_file_level"),
        )


def pytest_addoption(parser):
    """"
    ENV:
        for AC: stage - ac_stage; qa - ac_qa; ac_integration;
        adap_ac - for integration tests,
        gap - gap
        adap production - live
    """
    parser.addoption("--env", action="store", default="integration")
    parser.addoption("--env_fed", action="store", default="qe60")
    parser.addoption("--flaky", action="store", default="true")
    parser.addoption("--set", action="store", default="all")
    parser.addoption("--key", action="store", default=None)
    parser.addoption("--browser_stack", action="store", default='false')
    parser.addoption("--os_system", action="store", default='Windows 10')
    parser.addoption("--browser", action="store", default='Chrome latest')
    parser.addoption("--customize_fed", action="store", default='false')
    parser.addoption("--customize_fed_url", action="store", default="qa.secure.cf3.io")
    # parser.addoption("--service_tag", action="store", default="smoke")
    parser.addoption("--jenkins_test_url", action="store", default='')
    parser.addoption("--deployment_url", action="store", default='')
    parser.addoption("--crp", action="store", default="false")
    parser.addoption("--jira", action="store", default="")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


@pytest.hookimpl(optionalhook=True)
def pytest_json_runtest_metadata(item, call):
    if call.when != 'call':
        return {}

    try:
        metadata = {'execution_count': item.keywords.node.execution_count}
    except:
        metadata = {'execution_count': 1}

    return metadata


@pytest.hookimpl(optionalhook=True)
def pytest_json_modifyreport(json_report):
    json_report = modify_report_crp(json_report)


def pytest_sessionfinish(session):
    try:
        plugin = session.config._json_report
        plugin.save_report(Config.PROJECT_ROOT +'/result/test_result.json')

        report = session.config._json_report.report

        if pytest.crp  == 'true':
            data_json = json.dumps(report)
            push_test_result_to_crp(data_json)
    except:
        LOGGER.error("Json Report has not been generated")


@pytest.fixture(scope='function', autouse=True)
def test_info(request):
    LOGGER.info(f"""BEGIN TEST CASE: {request.function.__name__}""")

    yield test_info

    if request.node.rep_call.failed:
        print(request.fspath)
        if 'ui_automation' in str(request.fspath):
            LOGGER.info("Making screenshot")
            try:
                create_screenshot(driver, request.function.__name__)
            except:
                LOGGER.info("SCREENSHOT HAS NOT BEEN CREATED")

        LOGGER.info("Test case FAILED")
    else:
        LOGGER.info("Test case PASSED")

    LOGGER.info(f"""END TEST CASE: {request.function.__name__}""")
    time.sleep(1)


@pytest.fixture(scope='session', autouse=True)
def job_collections(request):
    LOGGER.info(f"OS environ: {os.environ} ")
    #LOGGER.info(f"Current IP: {get_current_ip()} ")

    if pytest.browser_stack == 'true':
        bs_local = Local()
        bs_local_args = {"key": "Muq8tTy3eXd3erRF3WRY"}
        # starts the Local instance with the required arguments
        bs_local.start(**bs_local_args)
        # check if BrowserStack local instance is running
        print(bs_local.isRunning())

    from datetime import datetime
    pytest.session_id = datetime.now().strftime("%Y_%m_%d_%H_%M")

    pytest.data.job_collections = {}
    pytest.data.wfs_collections = {}
    pytest.data.models_collection = {}
    pytest.data.qf_project_collection = []

    if not pytest.key:
        # get key from file
        path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
        if os.path.isfile(path_key):
            pytest.key = load_key(path_key)
        else:
            LOGGER.error("Secret key has not been found!!!")


    yield job_collections

    if pytest.crp == 'true':
        LOGGER.info(f" Portal notification: finished testing!!")

    if pytest.browser_stack == 'true':
        bs_local.stop()

    if pytest.env not in ['adap_ac', 'ac_stage', 'ac_integration', 'fed', 'gap']:
        delete_wfs(pytest.data.wfs_collections)
        delete_jobs(pytest.data.job_collections)
        delete_models(pytest.data.models_collection)
        # delete_qf_projects(pytest.data.qf_project_collection, delete_index=False)

    try:
      with open('./allure_result_folder/environment.properties', 'w') as f_env:
        f_env.write('ENV={0}'.format(pytest.env) + '\r\n')
        f_env.write('MARKEREXPR={0}'.format(os.getenv('MARKEREXPR')) + '\r\n')
        f_env.write('NUMPROCESSES={0}'.format(os.getenv('NUMPROCESSES')) + '\r\n')
        f_env.write('TEST_SET={0}'.format(pytest.set) + '\r\n')
    except:
        LOGGER.error("Allure environment variables")

    # ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#                             UI fixtures
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def create_ui_fixture_for_test(request, temp_path_to_files=None):
    if pytest.appen == 'true':
        fixture = AC(pytest.env, temp_path_to_files)
    elif pytest.env == 'adap_ac':
        fixture = ADAP_AC(temp_path_to_files)
    elif pytest.env == 'gap':
        fixture = Gap(pytest.env, temp_path_to_files)
    else:
        driver_type = 'browser_stack' if pytest.browser_stack == 'true' else 'local'
        fixture = Application(env=pytest.env, temp_path_file=temp_path_to_files, request=request,
                              driver_type=driver_type)
    global driver

    driver = fixture.driver

    def fin():
        # check if a fixture contains specific destroy func and call it if so
        callable(getattr(fixture, 'destroy', None)) \
            and fixture.destroy()

        driver.quit()

    request.addfinalizer(fin)
    return fixture


@pytest.fixture(scope='function')
def app_test(request, tmpdir):
    return create_ui_fixture_for_test(request, tmpdir)


@pytest.fixture(scope='module')
def app(request, tmpdir_factory):
    return create_ui_fixture_for_test(request, tmpdir_factory.mktemp("data"))


@pytest.fixture(scope='session')
def ac_api_cookie(request):
    if pytest.appen == 'true':
        app = create_ui_fixture_for_test(request)
        USER_NAME = get_user_name('test_ui_account')
        USER_PASSWORD = get_user_password('test_ui_account')
        app.ac_user.login_as(user_name=USER_NAME, password=USER_PASSWORD)
        app.navigation.click_link('Partner Home')
        # app.navigation.click_link('View previous list page')
        # app.ac_user.select_customer('Appen Internal')
        flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                            app.driver.get_cookies()}
        return flat_cookie_dict
    return None


@pytest.fixture(scope='session')
def ac_api_cookie_no_customer(request):
    if pytest.appen == 'true':
        app = create_ui_fixture_for_test(request)
        USER_NAME = get_user_name('test_ui_account')
        USER_PASSWORD = get_user_password('test_ui_account')
        app.ac_user.login_as(user_name=USER_NAME, password=USER_PASSWORD)
        flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                            app.driver.get_cookies()}
        return flat_cookie_dict


@pytest.fixture(scope='session')
def ac_api_cookie_vendor(request):
    if pytest.appen == 'true':
        app = create_ui_fixture_for_test(request)
        USER_NAME = get_user_name('test_active_vendor_account')
        USER_PASSWORD = get_user_password('test_active_vendor_account')
        app.ac_user.login_as(user_name=USER_NAME, password=USER_PASSWORD)
        flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                            app.driver.get_cookies()}
        return flat_cookie_dict


@pytest.fixture(scope='session')
def valid_cookies_adap(request, account='test_ui_account'):
    driver = create_ui_fixture_for_test(request)
    username = get_test_data(account, 'email')
    password = get_test_data(account, 'password')

    driver.user.login_as_customer(user_name=username, password=password, close_guide=False)

    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        driver.driver.get_cookies()}

    return flat_cookie_dict

@pytest.fixture(scope="session")
def rp_adap():
    username = get_test_data('test_ui_account', 'email')
    password = get_test_data('test_ui_account', 'password')

    rp = RP()
    rp.get_valid_sid(username, password)

    return rp


@pytest.fixture(scope="module")
def adap_cds():
    api_key = get_test_data('test_account', 'api_key')
    jwt = AkonUser(api_key).get_appen_jwt_token()

    return CDS(jwt=jwt)
