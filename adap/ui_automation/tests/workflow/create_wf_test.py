"""
create Workfow tests
"""
import time
import pytest

from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.workflow_e2e_test import payload1, payload2, payload3

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def create_wf(app):
    global WF_ID, _JOBS

    _JOBS = []

    job_id = create_job_from_config_api({"job": payload1["job"]}, pytest.env, API_KEY)
    _JOBS.append(job_id)

    job_id = create_job_from_config_api({"job": payload2["job"]}, pytest.env, API_KEY)
    _JOBS.append(job_id)

    job_id = create_job_from_config_api({"job": payload3["job"]}, pytest.env, API_KEY)
    _JOBS.append(job_id)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.workflows_page()
    app.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()
    app.workflow.fill_up_wf_name(wf_name)

    WF_ID = app.workflow.grab_wf_id()
    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app.job.data.upload_file(sample_file)



@pytest.mark.dependency()
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_add_operator_to_wf_side_panel(app, create_wf):
    """
    test_add_operator_to_wf_side_panel
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Canvas")

    app.verification.current_url_contains("connect")
    app.verification.text_present_on_page("Add Operator")
    app.verification.text_present_on_page("Jobs can be created and managed on your")

    app.workflow.select_operator.search_job_into_side_bar(_JOBS[0])

    app.workflow.select_operator.verify_job_is_present_on_the_list(_JOBS[0])
    app.workflow.select_operator.verify_job_status_on_the_list(_JOBS[0], "Available")
    app.workflow.select_operator.verify_job_is_present_on_the_list(_JOBS[1], mode=False)

    app.workflow.select_operator.connect_job_to_wf(_JOBS[0], 580, 370)

    app.verification.text_present_on_page("Add Operator", is_not=False)
    app.verification.text_present_on_page("Jobs can be created and managed on your", is_not=False)


@pytest.mark.dependency(depends=["test_add_operator_to_wf_side_panel"])
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_job_can_be_connected_only_once(app, create_wf):
    """
    test_job_can_be_connected_only_once
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)
    app.navigation.click_link("Canvas")
    # connect second job
    app.workflow.click_on_canvas_coordinates(app.workflow.x_add_first_job, app.workflow.y_add_first_job)

    app.workflow.select_operator.search_job_into_side_bar(_JOBS[0])
    app.workflow.select_operator.verify_job_status_on_the_list(_JOBS[0], "Currently Unavailable")


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/QED-2916")
# @pytest.mark.dependency(depends=["test_add_operator_to_wf_side_panel"])
# @pytest.mark.ui_uat
# def test_set_route_by_column_headers(app, create_wf):
#     """
#     test_set_route_by_column_headers
#     """
#     app.mainMenu.workflows_page()
#     app.workflow.open_wf_by_id(WF_ID)
#     app.navigation.click_link("Canvas")
#
#     # connect second job
#     app.workflow.click_on_canvas_coordinates(416, 324)
#     app.workflow.select_operator.search_job_into_side_bar(_JOBS[1])
#     app.workflow.select_operator.connect_job_to_wf(_JOBS[1], 580, 570)
#
#     app.verification.text_present_on_page("Routing")
#     # app.verification.text_present_on_page(
#     #     "Set up routing by selecting a column header from your output operator. Input the value from that column and "
#     #     "how the route will match on that value.")
#
#     #      todo verify jobs name
#     app.workflow.routing.select_routing_method("Route by Column Headers")
#     app.workflow.routing.add_filter("video_found_yn", "Equals", "")
#     app.verification.element_is("disabled", "Save & Close")
#
#     app.workflow.routing.add_filter("video_found_yn", "Equals", "Yes")
#     app.verification.element_is("disabled", "Save & Close", is_not=True)


# @pytest.mark.dependency(depends=["test_set_route_by_column_headers"])
# @pytest.mark.ui_uat
# def test_delete_job_from_wf(app, create_wf):
#  """
#  test_delete_job_from_wf
#  """
#     app.mainMenu.workflows_page()
#     app.workflow.open_wf_by_id(WF_ID)
#
#     # delete second job
#     app.workflow.click_on_canvas_coordinates(490, 455)
#     try:
#        app.navigation.click_link("Delete")
#     except:
#        app.workflow.click_on_canvas_coordinates(490, 465)
#        app.navigation.click_link("Delete")
#
#     wf_name = app.workflow.find_wf_name_for_job(_JOBS[1])
#     assert wf_name == None


