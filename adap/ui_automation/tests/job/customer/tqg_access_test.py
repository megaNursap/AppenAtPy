"""
Test Questions Generator
"""
import time

from selenium.webdriver.common.alert import Alert

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.judgments_util import create_screenshot

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
    time.sleep(3)
    # app.navigation.click_btn("Save")


@pytest.fixture(scope="module")
def new_job_tqg(app):
    global job_id
    job_id = create_job(API_KEY)
    login_as_customer_and_open_job(app, job_id)


# TODO SDA
@pytest.mark.tqg
@pytest.mark.tqg_wip
@pytest.mark.parametrize('user_name', ['test_nda'])
def test_tqg_prevented_for_user(app_test, user_name):
    _user = get_user_email(user_name)
    _password = get_user_password(user_name)
    _api_key = get_user_api_key(user_name)

    new_job = create_job(_api_key)
    app_test.user.login_as_customer(user_name=_user, password=_password)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(new_job)
    app_test.job.open_tab("DESIGN")
    app_test.job.open_tab("DATA")
    time.sleep(1)
    # app_test.navigation.click_btn("Save")

    app_test.job.open_tab("QUALITY")
    app_test.verification.text_present_on_page("Order Test Questions by sending your job to a")
    app_test.verification.text_present_on_page("Build your own Test Questions manually by creating one at a time")

    app_test.verification.text_present_on_page("Currently Unavailable")


@pytest.mark.tqg
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui
def test_tqg_is_disable(app_test):
    _user = get_user_email('test_predefined_jobs')
    _password = get_user_password('test_predefined_jobs')
    _api_key = get_user_api_key('test_predefined_jobs')

    new_job = create_job(_api_key)
    app_test.user.login_as_customer(user_name=_user, password=_password)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(new_job)
    app_test.job.open_tab("DESIGN")
    app_test.navigation.click_btn("Save")
    # app_test.job.open_tab("QUALITY")
    app_test.navigation.click_link('Next: Create Test Questions')
    app_test.user.close_guide()
    app_test.verification.text_present_on_page("Order Test Questions by sending your job to a", is_not=False)
    app_test.verification.text_present_on_page("Build your own Test Questions manually by creating one at a time")

    app_test.job.quality.create_random_tqs(2)
    app_test.job.open_tab("QUALITY")
    app_test.verification.text_present_on_page('Add More', is_not=False)
    app_test.verification.text_present_on_page('Create More')


@pytest.mark.tqg
@pytest.mark.fed_ui
def test_tqg_access(app, new_job_tqg):
    app.job.open_tab("DESIGN")
    app.job.open_tab("QUALITY")
    app.verification.text_present_on_page("Add Test Questions")
    app.verification.text_present_on_page("Build your own Test Questions manually by creating one at a time")
    app.verification.text_present_on_page("Order Test Questions by sending your job to a", is_not=True)

    # verify help content
    app.navigation.click_link("Learn more about other quality control methods")
    app.verification.text_present_on_page("Redundancy")
    app.verification.text_present_on_page(
        "To ensure accuracy and find agreement, we recommend having multiple contributors review every row of data.")
    app.verification.text_present_on_page("You can set the number of judgments for your job on the")
    app.navigation.click_link("Next")
    app.verification.text_present_on_page("Contributor Levels")
    app.verification.text_present_on_page("We keep an audit trail of every contributor and bucket them into three")

    app.verification.text_present_on_page("quickest, while Level Three can handle more complex tasks. You can set the")
    app.verification.text_present_on_page("level of contributors for your job on the")

    app.navigation.click_link("Finish")



@pytest.mark.tqg
def test_order_tq_with_custom_channel(app_test):
    """
    As a customer, I can order test questions with a custom channel
    """
    new_job = create_job(API_KEY)
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(new_job)

    app_test.job.open_action("Settings")
    current_channels = app_test.job.get_all_custom_channels()
    ch_name = ''
    if not current_channels:
        print("create new channel")
        # TODO
    else:
        ch_name = current_channels[0]

    app_test.job.select_custom_channel(ch_name)
    app_test.navigation.click_link("Save")
    app_test.navigation.refresh_page()
    try:
        Alert(app_test.driver).accept()
    except:
        pass

    app_test.job.open_tab("DATA")
    app_test.job.open_tab("DESIGN")
    app_test.job.open_tab("LAUNCH")
    app_test.job.open_tab("QUALITY")
    app_test.job.quality.click_generate_tq()
    app_test.job.quality.order_tq(4, ch_name)
    app_test.navigation.click_link('Order')
    # TODO add verification


@pytest.mark.tqg
def test_tqg_job_design(app_test):
    """
    As a customer, if I change the job design the subsequent TQ orders the TQ job should follow the new design
    """
    _current_job = create_job(API_KEY)
    # _current_job = 1567304

    login_as_customer_and_open_job(app_test, _current_job)

    app_test.job.open_tab("QUALITY")
    app_test.job.quality.create_random_tqs(2)

    job = Builder(API_KEY)
    job.job_id = _current_job

    cml_sample = """
    <div class="html-element-wrapper"></div>
    <cml:radios label="Ask question here:" validates="required" name="ask_question_here" gold="true">
      <cml:radio label="First option Updated" value="first_option" />
      <cml:radio label="Second option Updated" value="second_option" />
    </cml:radios>
    """
    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Updated",
            'instructions': "Updated",
            'cml': cml_sample
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    app_test.job.open_tab("QUALITY")
    app_test.job.quality.click_generate_tq()
    app_test.job.quality.order_tq(5, "Appen Trusted Contributors")
    app_test.navigation.click_link('Order')
    app_test.navigation.refresh_page()

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

    tqg_cml = res.json_response['cml']
    assert "First option Updated" in tqg_cml
    assert "Second option Updated" in tqg_cml

# TODO As a customer, if I change the job design the subsequent TQ orders the TQ job should follow the new design
# TODO  As a customer, I can order a second TQG when the first has completed
