"""
Automate ADAP/AC integration
"""
from datetime import date
import time

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.judgments_util import answer_questions_on_page
from adap.api_automation.utils.service_util import delete_jobs

pytestmark = [pytest.mark.adap_ac_integration]

ADAP_REQUESTOR = get_test_data('adap_requestor', 'email')
ADAP_API_KEY = get_test_data('adap_requestor', 'api_key')
ADAP_PASSWORD = get_test_data('adap_requestor', 'password')

AC_CUSTOMER = get_test_data('ac_customer', 'email')
AC_CUSTOMER_PASSWORD = get_test_data('ac_customer', 'password')

VENDOR = get_test_data('ac_vendor_1', 'email')
VENDOR_PASSWORD = get_test_data('ac_vendor_1', 'password')
VENDOR_ID = get_test_data('ac_vendor_1', 'id')

VENDOR_DENIED = get_test_data('ac_vendor_pay_rate', 'email')
VENDOR_PASSWORD_DENIED = get_test_data('ac_vendor_pay_rate', 'password')
VENDOR_ID_DENIED = get_test_data('ac_vendor_pay_rate', 'id')

VENDOR_NO_ADAP = get_test_data('ac_vendor_no_adap', 'email')
VENDOR_NO_ADAP_ID = get_test_data('ac_vendor_no_adap', 'id')


# TODO https://appen.atlassian.net/browse/ADAP-3613
@pytest.fixture(scope="module", autouse=True)
def delete_adap_job():
    yield
    delete_jobs(pytest.data.job_collections, env='integration')


@pytest.fixture(scope="module")
def new_adap_job():
    job_name = "Integration Adap Job" + date.today().strftime("%m/%d/%Y")

    cml_sample = '''
               <div class="html-element-wrapper">
                 <span>{{text}}</span>
               </div>
               <cml:radios label="Is this funny or not?" validates="required" gold="true">
                 <cml:radio label="funny" value="funny" />
                 <cml:radio label="not funny" value="not_funny" />
               </cml:radios>
        '''

    payload = {
        'key': ADAP_API_KEY,
        'job': {
            'title': job_name,
            'instructions': "instructions",
            'project_number': 'PN000112',
            'cml': cml_sample
        }
    }
    job = Builder(ADAP_API_KEY, payload=payload, env='integration')
    job.create_job()

    sample_file = get_data_file('/simple_job/simple_data__tq_ex.json', env='integration')
    job.upload_data(sample_file)

    return {"id": job.job_id, "name": job_name}


@pytest.mark.dependency()
def test_create_integration_job(app_test, new_adap_job):
    app_test.adap.user.login_as_customer(user_name=ADAP_REQUESTOR, password=ADAP_PASSWORD)

    app_test.adap.mainMenu.jobs_page()
    app_test.adap.job.open_job_with_id(new_adap_job['id'])

    app_test.adap.job.open_tab('DESIGN')
    app_test.adap.job.open_tab('LAUNCH')

    app_test.adap.job.launch.click_edit_settings_section("Crowd Channel")
    app_test.adap.job.launch.select_crowd_channel('Managed Crowd')
    # app_test.adap.job.launch.select_crowd_channel('Internal')
    app_test.adap.navigation.click_link('Save & Close')

    app_test.adap.job.launch.click_edit_settings_section("Crowd Settings (Managed, Internal)")
    app_test.adap.job.click_edit_project_id()

    app_test.adap.job.launch.enter_ac_project_id('324', action='Save')
    app_test.adap.job.launch.select_job_targeting_settings('Target specific Appen Connect user groups')
    app_test.adap.navigation.click_link('Add')

    app_test.adap.navigation.click_checkbox_by_text('HC Group for Appen Internal')
    app_test.adap.navigation.click_link('Save')

    app_test.adap.navigation.click_link('Save & Close')

    app_test.adap.navigation.click_link('Launch Job')
    time.sleep(10)

    app_test.adap.user.logout()


# TODO create new vendor for test QED-2869
@pytest.mark.skip(reason='vendor is not valid')
def test_vendor_access_denied(app_test, new_adap_job):
    """
    Vendor:
    Add the rater on the ac project created (324)
    Do not add the user group created and that is set on the job in ADAP
    Add the user locale that will be set on the job in ADAP
    """
    app_test.ac.ac_user.login_as(user_name=AC_CUSTOMER, password=AC_CUSTOMER_PASSWORD)

    vendor_profile = "https://connect-stage.integration.cf3.us/qrp/core/vendor/view/{}".format(VENDOR_ID_DENIED)
    app_test.ac.driver.get(vendor_profile)
    time.sleep(3)

    app_test.ac.navigation.click_link('Impersonate')
    time.sleep(2)
    app_test.ac.navigation.switch_to_frame("page-wrapper")
    app_test.ac.vendor_pages.open_projects_tab("All projects")

    app_test.ac.project_list.filter_project_list_by("FigureEight")
    app_test.ac.vendor_pages.click_action_for_project('FigureEight', 'Work This')

    app_test.ac.internal_home_pages.click_on_adap_task_by_id(new_adap_job['id'])

    app_test.adap.user.task.login(VENDOR_DENIED, VENDOR_PASSWORD_DENIED)

    app_test.adap.verification.current_url_contains('/appen_connect/tasks/')
    app_test.adap.verification.text_present_on_page("Access Denied")


def test_vendor_not_register_in_adap(app_test):
    """
    Vendor: not registered in ADAP
    """
    app_test.ac.ac_user.login_as(user_name=AC_CUSTOMER, password=AC_CUSTOMER_PASSWORD)

    vendor_profile = "https://connect-stage.integration.cf3.us/qrp/core/vendor/view/{}".format(VENDOR_NO_ADAP_ID)
    app_test.ac.driver.get(vendor_profile)
    time.sleep(3)

    app_test.ac.navigation.click_link('Impersonate')
    time.sleep(2)
    app_test.ac.navigation.switch_to_frame("page-wrapper")
    app_test.ac.vendor_pages.open_projects_tab("All projects")

    app_test.ac.vendor_pages.search_project_by_name("FigureEight")
    app_test.ac.vendor_pages.click_action_for_project("FigureEight", 'Work This')

    app_test.ac.verification.text_present_on_page("We can not find your ADAP account")


@pytest.mark.dependency(depends=["test_create_integration_job"])
def test_vendor_access_job(app, new_adap_job):
    """
    Vendor :
    Add the rater on the project created (324)
    Add to the user group created and that is set on the job in ADAP
    Add the user locale that will be set on the job in ADAP
    """

    # app.ac.ac_user.login_as(user_name=AC_CUSTOMER, password=AC_CUSTOMER_PASSWORD)
    #
    # vendor_profile = "https://connect-stage.integration.cf3.us/qrp/core/vendor/view/{}".format(VENDOR_ID)
    # app.ac.driver.get(vendor_profile)
    # time.sleep(3)
    #
    # app.ac.navigation.click_link('Impersonate')

    app.ac.ac_user.login_as(user_name=VENDOR, password=VENDOR_PASSWORD)
    time.sleep(2)
    app.ac.navigation.switch_to_frame("page-wrapper")
    app.ac.vendor_pages.open_projects_tab("All projects")

    app.ac.vendor_pages.search_project_by_name("FigureEight")
    app.ac.vendor_pages.click_action_for_project("FigureEight", 'Work This')

    app.ac.internal_home_pages.click_on_adap_task_by_id(new_adap_job['id'])

    # app.adap.user.task.login(VENDOR, VENDOR_PASSWORD)

    app.adap.verification.current_url_contains('/assignments/')
    app.adap.verification.text_present_on_page(new_adap_job['name'])
    app.adap.verification.text_present_on_page("Access Denied", is_not=False)
    app.adap.verification.text_present_on_page("Email mismatch", is_not=False)


@pytest.mark.dependency(depends=["test_vendor_access_job"])
def test_submit_judgements_adap_job(app):
    answer_questions_on_page(app.driver, {})
    app.adap.job.judgements.click_submit_judgements()
    assert app.adap.job.judgements.get_num_completed_tasks() == '1 task completed'


@pytest.mark.dependency(depends=["test_submit_judgements_adap_job"])
def test_access_productivity_metrics(app_test, new_adap_job):

    app_test.ac.ac_user.login_as(user_name=AC_CUSTOMER, password=AC_CUSTOMER_PASSWORD)
    app_test.ac.navigation.click_link('Partner Home')
    time.sleep(15)
    app_test.ac.navigation.click_link('Partner Data')

    app_test.ac.navigation_old_ui.type_in_input_field_project_name('Figure Eight integration')

    app_test.ac.navigation_old_ui.click_input_btn("Go")

    app_test.ac.navigation.click_link('Completion Date')
    time.sleep(5)
    app_test.ac.navigation.click_link('Completion Date')
    time.sleep(10)

    partner_data = app_test.ac.partner_home.get_partner_data_info()

    assert partner_data[0]['User Email'] == VENDOR
    assert partner_data[0]['Project'] == 'Figure Eight integration'
    assert partner_data[0]['Items Reviewed'] == '5'
    assert partner_data[0]['Task Id'] == str(new_adap_job['id'])

    # TODO open project by id
    # TODO add verification that Manage crowd is selected
