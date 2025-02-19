import time
from datetime import datetime as dt

import pytest
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.workflow import Workflow

pytestmark = [pytest.mark.wf_ui,
              pytest.mark.regression_wf
              ]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
USER_NAME = get_user_name('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


def login_and_create_new_wf(app_test):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")

    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)
    return wf_name


@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui_smoke_wf
def test_no_access_to_wf(app):
    """
    As a customer, when workflows are not enabled for my team, I do not have access to a workflows tab
    """
    _user = get_user_info('test_predefined_jobs')['email']
    _password = get_user_password('test_predefined_jobs')

    app.user.login_as_customer(user_name=_user, password=_password)
    # for fed, workflow is always enabled
    if pytest.env == 'fed':
        app.mainMenu.menu_item_is_disabled('workflow', is_not=True)
    else:
        app.mainMenu.menu_item_is_disabled('workflow')


@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui_smoke_wf
def test_workflow_name(app_test):
    """
    As a customer, I cannot create a workflow if the name is blank
    As a customer, I can cancel creating a workflow
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    app_test.verification.element_is("disabled", "Create")
    app_test.workflow.fill_up_wf_name(" ")

    # app_test.navigation.click_link("Create")
    app_test.verification.text_present_on_page("There was an error creating workflow.")

    app_test.verification.text_present_on_page("Workflow Name")
    # app_test.navigation.close_modal_window()
    app_test.verification.text_present_on_page("Create Workflow")


@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
def test_workflow_sorted_by_created_at(app_test):
    """
    As a customer, my workflows should be sorted by the created at column
    As a customer, I should see 30 workflows on a single page
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()

    wf_on_the_page = app_test.workflow.count_wf_on_page()
    assert wf_on_the_page <= 30

    wf = Workflow(API_KEY)
    res = wf.get_list_of_wfs()
    total_count = res.json_response['total_count']
    if total_count >= 30:
        app_test.verification.pagination_is_displayed()

        app_test.workflow.verify_wf_sorted_by('DATE CREATED')


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
@pytest.mark.fed_ui_smoke_wf
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.workflow_deploy
def test_user_can_create_workflow(app_test):
    """
    user_can_create_workflow
    As a customer, I should be able to search for a workflow by title
    As a customer, when workflows are enabled for my team, I have access to a workflows tab
    As a customer, I can go to my jobs page from the "Add Operator" panel
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app_test.mainMenu.menu_item_is_disabled('workflow', is_not=True)

    app_test.mainMenu.workflows_page()
    app_test.verification.current_url_contains("workflows")
    app_test.verification.text_present_on_page("Workflows")

    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)
    app_test.verification.current_url_contains('/data')
    app_test.verification.element_is('active', 'Data')

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)
    app_test.navigation.click_link("Data")
    app_test.verification.text_present_on_page("customer_01_sample_22.csv")

    app_test.verification.text_present_on_page("Canvas")
    app_test.navigation.click_link("Canvas")
    app_test.verification.current_url_contains('/connect')
    app_test.verification.text_present_on_page("Operator")

    wf_window = app_test.driver.window_handles[0]
    app_test.navigation.click_link("job listings page")
    window_after = app_test.driver.window_handles[1]
    app_test.navigation.switch_to_window(window_after)
    app_test.verification.current_url_contains("/jobs")

    app_test.navigation.switch_to_window(wf_window)

    app_test.mainMenu.workflows_page()
    app_test.verification.text_present_on_page(wf_name)
    app_test.workflow.open_wf_with_name(wf_name)
    app_test.navigation.click_link("Canvas")
    app_test.verification.current_url_contains('/connect')
    app_test.verification.text_present_on_page("Operator")


@pytest.mark.workflow_deploy
@pytest.mark.prod_bug
@pytest.mark.ui_uat
@pytest.mark.adap_uat
def test_user_can_upload_datafile_with_symbols(app_test):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app_test.mainMenu.menu_item_is_disabled('workflow', is_not=True)

    app_test.mainMenu.workflows_page()
    app_test.verification.current_url_contains("workflows")
    app_test.verification.text_present_on_page("Workflows")

    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)
    app_test.verification.current_url_contains('/data')
    app_test.verification.element_is('active', 'Data')

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/special_symbols_file.csv")
    app_test.job.data.upload_file(sample_file)
    app_test.navigation.click_link("Data")
    app_test.verification.text_present_on_page("special_symbols_file.csv")


@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui_smoke_wf
def test_user_can_rename_workflow(app_test):
    """
    As a customer, I can see the workflow ID, Owner, and date created
    As a customer, I can rename a workflow
    """
    wf_name = login_and_create_new_wf(app_test)
    wf_id = app_test.workflow.grab_wf_id()
    wf_data = dt.now().strftime("%b %d, %Y")

    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(wf_name)

    app_test.workflow.click_on_gear_for_wf(wf_name)
    # TODO fix https://appen.atlassian.net/browse/CW-8154
    # app_test.workflow.verify_wf_details(["Workflow ID: %s" % wf_id, "Owner: %s" % USER_NAME, "Created: %s" % wf_data])

    app_test.workflow.pick_wf_by_name(wf_name)
    app_test.verification.text_present_on_page(wf_name)

    new_wf_name = generate_random_wf_name()

    app_test.workflow.click_btn_rename_wf()
    app_test.workflow.rename_wf(new_wf_name)

    app_test.navigation.close_modal_window()
    app_test.verification.text_present_on_page(wf_name)

    app_test.workflow.click_btn_rename_wf()
    app_test.workflow.rename_wf(new_wf_name)
    app_test.navigation.click_link("Rename")
    app_test.verification.text_present_on_page(new_wf_name)

    new_wf_name2 = generate_random_wf_name()

    # # user can cancel renaming WF
    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(new_wf_name)
    app_test.workflow.click_on_gear_for_wf(new_wf_name, sub_menu='Rename Workflow')
    app_test.workflow.rename_wf(new_wf_name2)
    app_test.navigation.close_modal_window()
    app_test.workflow.pick_wf_by_name(new_wf_name)
    app_test.verification.text_present_on_page(new_wf_name)

    # user can rename WF
    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(new_wf_name)
    app_test.workflow.click_on_gear_for_wf(new_wf_name, sub_menu='Rename Workflow')
    app_test.workflow.rename_wf(new_wf_name2)
    app_test.navigation.click_link("Rename")
    time.sleep(5)
    app_test.workflow.clean_wf_search_field()
    app_test.mainMenu.workflows_page()
    app_test.verification.text_present_on_page(new_wf_name2)
    app_test.workflow.open_wf_with_name(new_wf_name2)


@pytest.mark.ui_uat
@pytest.mark.skip_hipaa
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.fed_ui_smoke_wf
def test_user_can_delete_workflow(app_test):
    """
    As a customer, I can cancel deleting a workflow
    As a customer, I can delete an unlaunced workflow
    """
    wf_name = login_and_create_new_wf(app_test)

    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(wf_name)
    app_test.workflow.click_on_gear_for_wf(wf_name, sub_menu='Delete Workflow')

    #  user can cancel deleting a workflow
    app_test.verification.text_present_on_page("Confirm Delete Workflow")
    app_test.verification.text_present_on_page("Any jobs or models used in this workflow will remain unchanged.")

    app_test.navigation.click_link("Cancel")

    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(wf_name)
    app_test.workflow.pick_wf_by_name(wf_name)

    #  user can  delete a workflow
    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(wf_name)
    app_test.workflow.click_on_gear_for_wf(wf_name, sub_menu='Delete Workflow')
    app_test.navigation.click_link("Delete")

    app_test.mainMenu.workflows_page()
    app_test.workflow.search_wf_by_name(wf_name)
    # app_test.verification.text_present_on_page("No data available in table")
