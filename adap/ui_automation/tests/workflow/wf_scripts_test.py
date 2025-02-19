from adap.api_automation.utils.data_util import *
from adap.ui_automation.tests.workflow.access_control_test import login_and_create_new_wf

pytestmark = [pytest.mark.wf_ui,
              pytest.mark.regression_wf
              ]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
USER_NAME = get_user_name('test_ui_account')


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_script_catalog_access(app_test):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.scripts_page()

    app_test.verification.current_url_contains('/scripts')

    app_test.verification.text_present_on_page('Base Scripts')

    app_test.scripts.open_scripts_tab("Base Scripts")
    assert app_test.scripts.get_page_header() == 'Base Scripts'

    app_test.scripts.open_scripts_tab("My Scripts")
    assert app_test.scripts.get_page_header() == 'My Scripts'

    app_test.scripts.open_script_by_name('Copy of Split Annotation')
    app_test.verification.text_present_on_page("Title")
    app_test.verification.text_present_on_page("Input Parameters")
    app_test.verification.text_present_on_page("Split column name")
    app_test.verification.text_present_on_page("Output")

    app_test.navigation.click_link('Cancel')


@pytest.mark.prod_bug
def test_add_script_as_first_operator(app_test):
    """
    prod bug https://appen.atlassian.net/browse/ADAP-1006
    verify user is able to add script as first operator in workflow
    """
    login_and_create_new_wf(app_test)

    app_test.navigation.click_link("Canvas")
    app_test.navigation.click_link("Scripts")

    app_test.workflow.select_operator.connect_job_to_wf('Diagnostics: Secure Dataline Logger', 580, 370)

    app_test.verification.text_present_on_page("Script Details")
    app_test.verification.text_present_on_page("Title")
    app_test.verification.text_present_on_page("dataline_id")

    app_test.navigation.click_link('Add Script')

    app_test.verification.text_present_on_page('You’ve selected parameters that match the parameters set for Script')
    app_test.verification.text_present_on_page('will be added to your Workflow instead of a duplicate.')



