"""
Workflow Routing tests
"""
import time

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import create_screenshot
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api
from adap.e2e_automation.workflow_e2e_test import payload1, payload2, payload3

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
USER_ID = get_akon_id('test_ui_account')
USER_TEAM_ID = get_user_team_id('test_ui_account')


@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.workflow_engine_deploy
@pytest.mark.flaky(reruns=2)
@pytest.mark.dependency()
def test_set_route_all_rows(app_test):
    """
    test_set_route_all_rows
    As a customer, clicking a route node opens the panel and puts the route path in a highlighted state
    As a customer, clicking 'X' on the panel or saving the routing logic, closes the panel
    As a customer, I can select from the following routing options using a dropdown: "Route all rows" (default) and "Route by column headers"
    """
    _jobs = []

    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)

    job_id = create_job_from_config_api({"job": payload2["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    global WF_ID
    WF_ID = app_test.workflow.grab_wf_id()
    app_test.mainMenu.workflows_page()
    app_test.workflow.open_wf_by_id(WF_ID)
    app_test.navigation.click_link("Canvas")

    app_test.workflow.select_operator.search_job_into_side_bar(_jobs[0])
    app_test.workflow.select_operator.connect_job_to_wf(_jobs[0], 580, 370)

    # connect second job
    app_test.workflow.click_on_canvas_coordinates(app_test.workflow.x_add_first_job, app_test.workflow.y_add_first_job)
    # user is able to close routing panel
    time.sleep(3)
    app_test.workflow.routing.close_routing_panel()
    app_test.verification.text_present_on_page("Add Operator", is_not=False)

    app_test.workflow.click_on_canvas_coordinates(app_test.workflow.x_add_first_job, app_test.workflow.y_add_first_job)
    app_test.workflow.select_operator.search_job_into_side_bar(_jobs[1])
    app_test.workflow.select_operator.connect_job_to_wf(_jobs[1], 580, 570)

    # app_test.workflow.routing.select_routing_method("Route by Column Headers")
    # app_test.workflow.routing.select_routing_method("Route a Random Sample")
    app_test.workflow.routing.select_routing_method("Route All Rows")

    app_test.navigation.click_link("Save & Close")

    wf_name = app_test.workflow.find_wf_name_for_job(_jobs[1])
    assert wf_name is not None

@pytest.mark.skip("https://appen.atlassian.net/browse/QED-4440")
@pytest.mark.workflow_engine_deploy
@pytest.mark.dependency(depends=["test_set_route_all_rows"])
def test_change_routing(app_test):
    """
    As a customer, I can switch the routing option back to "Route: All Rows" from "Route by column headers" or vice versa
    As a customer, I can not use branching and "Route All Rows"
    As a customer, I can not use "Route All Rows" and "Route by Column headers" in same branch
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()
    app_test.workflow.open_wf_by_id(WF_ID)
    app_test.navigation.click_link("Canvas")

    # open saved rout
    app_test.workflow.click_on_canvas_coordinates(830, 420, mode='body')
    app_test.verification.text_present_on_page("Routing")
    app_test.workflow.routing.select_routing_method("Route by Column Headers")

    app_test.workflow.routing.add_filter("video_found_yn", "Equals", "Yes")
    app_test.navigation.click_link("Save & Close")
    time.sleep(3)

    app_test.workflow.click_on_canvas_coordinates(830, 420, mode='body')
    app_test.verification.text_present_on_page("Routing")
    app_test.workflow.routing.select_routing_method("Route All Rows")
    app_test.navigation.click_link("Save & Close")

    # try to connect new job
    app_test.workflow.click_on_canvas_coordinates(830, 575)
    app_test.verification.text_present_on_page("Add Operator", is_not=False)

@pytest.mark.workflow_engine_deploy
def test_route_by_columns(app_test):
    """
    As a customer, when using "Route by column headers", I must configure 1 condition before saving the rule
    Routing rules should be unique
    As a customer, I can delete individual conditions but cannot delete the first rule
    As a customer, if I remove the second condition, the third condition becomes the second condition with an AND/OR dropdown and so on.
    As a customer, I can switch the entire set of conditions in the routing rule from ANDs to ORs, or vice versa
    As a customer, when I select a column header to route, I can select the following parameters: Equals, Does not Equal, Contains, Is less than, Is less than or equal to, Is greater then, Is greater than or equal to
    User is able to use confidence rule
    """
    _jobs = []

    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)

    job_id = create_job_from_config_api({"job": payload2["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()

    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)
    app_test.navigation.click_link("Canvas")

    app_test.workflow.select_operator.search_job_into_side_bar(_jobs[0])
    app_test.workflow.select_operator.connect_job_to_wf(_jobs[0], 580, 370)

    # connect second job
    app_test.workflow.click_on_canvas_coordinates(app_test.workflow.x_add_first_job, app_test.workflow.y_add_first_job)
    app_test.workflow.select_operator.search_job_into_side_bar(_jobs[1])
    app_test.workflow.select_operator.connect_job_to_wf(_jobs[1], 580, 570)

    app_test.workflow.routing.select_routing_method("Route by Column Headers")
    app_test.verification.element_is('disabled', 'Save & Close')

    app_test.workflow.routing.add_filter("video_found_yn", "Equals", "Yes")
    app_test.verification.element_is('disabled', 'Save & Close', is_not=True)

    app_test.workflow.routing.add_condition()
    app_test.workflow.routing.add_filter("video_found_yn", "Equals", "No", index=1, connector='AND')

    app_test.workflow.routing.add_condition()
    app_test.workflow.routing.add_filter("video_found_yn", "Equals", "No", index=2)

    app_test.navigation.click_link('Save & Close')

    all_rules = app_test.workflow.routing.get_all_routing_rules()

    assert all_rules[1]['error'] == 'Cannot set identical routing rules'
    assert all_rules[2]['error'] == 'Cannot set identical routing rules'

    app_test.workflow.routing.delete_rule_by_index(1)
    app_test.navigation.click_link('Save & Close')

    # This part of the test failing due to ("https://appen.atlassian.net/browse/QED-4440")

    # open saved rout
    # app_test.navigation.refresh_page()
    # time.sleep(4)
    # app_test.workflow.click_on_canvas_coordinates(416, 340)
    # app_test.verification.text_present_on_page("Routing")
    # app_test.verification.wait_untill_text_present_on_the_page("Routing method", 30)
    # all_rules = app_test.workflow.routing.get_all_routing_rules()
    #
    # assert len(all_rules) == 2
    # assert not all_rules[0]['error']
    # assert not all_rules[1]['error']
    # assert all_rules[1]['connector'] == 'AND'
    #
    # app_test.workflow.routing.select_connector("OR")
    # all_rules = app_test.workflow.routing.get_all_routing_rules()
    #
    # assert len(all_rules) == 2
    # assert all_rules[1]['connector'] == 'OR'
    #
    # all_rules = app_test.workflow.routing.get_all_routing_rules()
    # assert len(all_rules) == 2
    #
    # app_test.workflow.routing.add_condition()
    # app_test.workflow.routing.add_filter("video_found_yn:confidence", "Is less than", 20, index=2, connector='AND')
    #
    # all_rules = app_test.workflow.routing.get_all_routing_rules()
    # assert len(all_rules) == 3


@pytest.mark.workflow_engine_deploy
def test_random_route(app_test):
    """
    Customer us able to use 'Route a Random Sample'
    Number of random rows - integer between 1 and 99
    """
    _jobs = []

    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)

    job_id = create_job_from_config_api({"job": payload2["job"]}, pytest.env, API_KEY)
    _jobs.append(job_id)

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.workflows_page()

    app_test.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)
    app_test.navigation.click_link("Canvas")

    app_test.workflow.select_operator.search_job_into_side_bar(_jobs[0])
    app_test.workflow.select_operator.connect_job_to_wf(_jobs[0], 580, 370)

    # connect second job
    app_test.workflow.click_on_canvas_coordinates(app_test.workflow.x_add_first_job, app_test.workflow.y_add_first_job)
    app_test.workflow.select_operator.search_job_into_side_bar(_jobs[1])
    app_test.workflow.select_operator.connect_job_to_wf(_jobs[1], 580, 570)

    app_test.workflow.routing.select_routing_method("Route a Random Sample")
    app_test.verification.text_present_on_page("The final number of rows routed may vary.")
    app_test.verification.text_present_on_page("% of total rows to be routed")

    for num in [200, 100, 0]:
        app_test.workflow.routing.set_random_rows(num)
        time.sleep(5)
        app_test.verification.text_present_on_page("The numeric value must be an integer between 1 and 99, inclusive.")

    app_test.workflow.routing.set_random_rows(99)
    app_test.verification.text_present_on_page("The numeric value must be an integer between 1 and 99, inclusive.", is_not=False)

    app_test.workflow.routing.set_random_rows(20)
    app_test.verification.text_present_on_page("The numeric value must be an integer between 1 and 99, inclusive.", is_not=False)