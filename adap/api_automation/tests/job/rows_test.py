import pytest
import random
import time
import allure
import csv
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_data_file, get_user_api_key, get_headers_in_csv

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units:post')
@pytest.mark.woody2
@pytest.mark.jenkins
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.make
@pytest.mark.builder
@pytest.mark.devspace
def test_create_new_row():
    api_key = get_user_api_key('test_account')
    # create new job
    job = Builder(api_key)
    resp = job.create_job()
    resp.assert_response_status(200)

    # add one unit
    data = {"name": "new row", "url": "example.com/new_row"}
    res = job.add_new_row(data=data)

    assert 200 == res.status_code
    assert data == res.json_response['data']


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/units:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.devspace
def test_create_random_number_of_rows():
    """
    create random number of rows and verify GET rows
    """
    api_key = get_user_api_key('test_account')
    # create new job
    job = Builder(api_key)
    resp = job.create_job()
    resp.assert_response_status(200)

    num_rows = random.randint(5, 30)
    for i in range(num_rows):
        data = {"name": "row %s" % i, "url": "example.com/new_row%s" % i}
        job.add_new_row(data=data)

    rows_resp = job.get_rows_in_job()
    assert num_rows == len(rows_resp.json_response.items()), "Expected number of rows: %s \n Actual number: %s" % (
                                                              num_rows, len(rows_resp.json_response.items()))

    i = 0
    for v in rows_resp.json_response.values():
        data = {"name": "row %s" % i, "url": "example.com/new_row%s" % i}
        if pytest.env == 'fed':
            v = v.get("data")
        assert data == v, "Row %s does't match expected row: %s" % (v, data)
        i += 1


# todo more than 1000 rows for regression
@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units:get')
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.builder
@pytest.mark.make
@pytest.mark.devspace
def test_get_rows():
    api_key = get_user_api_key('test_account')
    # create new job
    job = Builder(api_key)
    resp = job.create_job()
    resp.assert_response_status(200)

    # add one unit
    data = {"name": "new row", "url": "example.com/new_row"}
    job.add_new_row(data=data)

    res = job.get_rows_in_job()
    res.assert_response_status(200)
    assert 1 == len(res.json_response.items()), "Expected number of rows: %s \n Actual number: %s" % (
                                                1, len(res.json_response.items()))
    actual_data = list(res.json_response.values())[0]
    if pytest.env == 'fed':
        actual_data = actual_data.get("data")
    assert data == actual_data, "Row %s does't match expected row: %s" % (actual_data, data)


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/units/ping:get')
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.devspace
def test_get_row_count():
    api_key = get_user_api_key('test_account')
    # create new job
    job = Builder(api_key)
    resp = job.create_job()
    resp.assert_response_status(200)

    count_res = job.count_rows()
    count_res.assert_response_status(200)

    assert 0 == count_res.json_response['count']

    num_rows = random.randint(1, 10)
    for i in range(num_rows):
        data = {"name": "row %s" % i, "url": "example.com/new_row%s" % i}
        job.add_new_row(data=data)
        count_res = job.count_rows()
        count_res.assert_response_status(200)
        assert i+1 == count_res.json_response['count']


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units/{unit_id}:delete')
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.devspace
def test_delete_a_unit():
    """
    You can only delete units on jobs that have not been launched or paused
    """
    api_key = get_user_api_key('test_account')
    sample_file = get_data_file("/sample_data.json")
    units = []

    job = Builder(api_key)
    resp = job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    time.sleep(5)
    res = job.get_rows_in_job()
    res.assert_response_status(200)

    # Adding only the unit ids to the list from the json response
    for key, value in res.json_response.items():
        units.append(key)

    # selecting a random unit_id within the list to cancel
    i = random.randint(0, len(units) - 1)

    # Will cancel a random unit within the list
    resp = job.delete_unit(units[i])
    resp.assert_response_status(200)

    # Verify that the unit is no longer available in the job
    resp = job.get_unit(units[i])
    resp.assert_response_status(404)


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units/{unit_id}:put')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('status',
                         ["hidden_gold", "golden",
                          "finalized", "new"])
@pytest.mark.devspace
def test_update_a_unit(status):
    api_key = get_user_api_key('test_account')
    sample_file = get_data_file("/sample_data.json")
    units = []

    job = Builder(api_key)
    resp = job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    time.sleep(5)
    res = job.get_rows_in_job()
    res.assert_response_status(200)

    # Adding only the unit ids to the list from the json response
    for key, value in res.json_response.items():
        units.append(key)

    # Picking a random unit to change it's status
    i = random.randint(0, len(units) - 1)

    # Will change a random unit within the list
    resp = job.change_state_of_row(units[i], status)
    resp.assert_response_status(200)

    resp = job.get_unit(units[i])
    assert resp.json_response['state'] == status


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units/{unit_id}/cancel:post')
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.devspace
def test_cancel_a_unit():
    """Rows is synonymous with units. This will cancel a unit in state 'New'. Units already launched can not
    be cancelled. """
    api_key = get_user_api_key('test_account')
    sample_file = get_data_file("/sample_data.json")
    units = []

    job = Builder(api_key)
    resp = job.create_job_with_json(sample_file)
    resp.assert_response_status(200)

    time.sleep(5)
    res = job.get_rows_in_job()
    res.assert_response_status(200)

    # Adding only the unit ids to the list from the json response
    for key, value in res.json_response.items():
        units.append(key)

    # selecting a random unit_id within the list to cancel
    i = random.randint(0, len(units)-1)

    # Will cancel a random unit within the list
    resp = job.cancel_unit(units[i])
    resp.assert_response_status(200)
    resp.assert_success_message('Unit %s has been canceled', str(units[i]))

    resp = job.get_unit(units[i])
    assert resp.json_response['state'] == 'canceled'


# test is deprecated
# @allure.parent_suite('/jobs/{job_id}/units/split:get')
# @pytest.mark.uat_api
# @pytest.mark.fed_api
# @pytest.mark.fed_api_smoke
# @allure.issue("https://appen.atlassian.net/browse/JW-1397", "BUG JW-1397")
# def test_split_unit_column():
#     api_key = get_user_api_key('test_account')
#     data_file = get_data_file("/authors.csv")
#
#     job = Builder(api_key)
#     resp = job.create_job_with_csv(data_file)
#     resp.assert_response_status(200)
#
#     time.sleep(5)
#     res = job.get_rows_in_job()
#     res.assert_response_status(200)
#
#     headers = get_headers_in_csv(data_file)
#     i = random.randint(0, len(headers)-1)
#
#     # Pass in the column header name and the delimiter
#     resp = job.split_column(headers[i], "|")
#     resp.assert_response_status(200)
