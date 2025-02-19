from adap.api_automation.services_config.mlapi import *
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, get_akon_id
from adap.api_automation.services_config.workflow import Workflow
from adap.ui_automation.services_config.user import *

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

API_KEY = get_user_api_key('test_ui_account')
USER_EMAIL = get_user_email('cf_internal_role')
PASSWORD = get_user_password('cf_internal_role')
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


@pytest.mark.wf_ui
@pytest.mark.fed_ui_smoke_wf
@pytest.mark.flaky(reruns=2)
@allure.issue("https://appen.atlassian.net/browse/ADAP-2255", "BUG  on Integration ADAP-2255")
def test_copy_wf_from_cross_team(app, new_wf, login):
    url = "https://client.%s.cf3.us/workflows/%s/connect" % (pytest.env, new_wf)
    go_to_page(app.driver, url)
    app.workflow.click_copy_icon(new_wf)

    wf_name = generate_random_wf_name()
    app.workflow.fill_up_copy_wf_name(wf_name)
    app.navigation.click_link("Copy")
    time.sleep(2)

    new_copied_wf_id = app.workflow.grab_wf_id()
    app.verification.current_url_contains("/" + new_copied_wf_id + "/connect")

    url = "https://client.%s.cf3.us/workflows" % (pytest.env)
    go_to_page(app.driver, url)
    app.verification.text_present_on_page(wf_name)
