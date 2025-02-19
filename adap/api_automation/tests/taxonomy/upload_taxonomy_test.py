"""
JIRA:https://appen.atlassian.net/browse/AT-5579

"""
import random

import allure
import pytest
import requests

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_data_file, get_test_data, get_user_team_id
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_taxonomy, pytest.mark.taxonomy_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('job_id', "")
TAXONOMY_TEST_DATA = get_data_file('/taxonomy/tax_category_id.csv')
API_KEY_NO_ADMIN = get_test_data('test_predefined_jobs', 'api_key')

api_key = get_test_data('test_account', 'api_key')
password = get_test_data('test_account','password')
user = get_test_data('test_account', 'email')
team_id = get_user_team_id('test_account')


@pytest.fixture(scope="module")
def set_job():
    job = Builder(api_key)
    job.create_job_with_cml(data.taxonomy_cml)
    job_id = job.job_id

    return job_id


@pytest.mark.parametrize('file_data, type_of_file, name',
                         [(TAXONOMY_TEST_DATA, 'text/csv', 'tax_1'),
                          (get_data_file('/taxonomy/correct_tax.json'), "application/json", 'tax_2')
                          ])
def test_upload_taxonomy_file(file_data, type_of_file, name, rp_adap, set_job):
    api = Builder(api_key=api_key, api_version='v2')

    response = api.upload_taxonomy_file_via_public(set_job, api_key, name=name, file=file_data,
                                                   type_of_file=type_of_file)
    property_msg = response.text
    assert property_msg == 'Taxonomy successfully uploaded',  f"Uploading failed in the reason with {property_msg}"
    response.assert_response_status(200)

    res = rp_adap.get_taxonomy_link_shared_file(set_job, team_id)
    res.assert_response_status(200)
    url = res.json_response.get('url')

    response = requests.get(url)
    assert response.status_code == 200, 'URL created incorrect from endpoint GET v1/refs/get_link'
    res_content = response.json()
    assert name in str(res_content), "The uploaded file not present in bucket"


def test_upload_taxonomy_file_unique_name(set_job):
    api = Builder(api_key=api_key, api_version='v2')
    name = 'tax_3'
    api.upload_taxonomy_file_via_public(set_job, api_key, name=name, file=TAXONOMY_TEST_DATA,
                                        type_of_file="text/csv")
    response = api.upload_taxonomy_file_via_public(set_job, api_key, name=name, file=TAXONOMY_TEST_DATA,
                                                   type_of_file="text/csv")

    actual_error_msg = response.text
    expected_error_msg = "Provided taxonomy name is not unique"

    response.assert_response_status(400)
    assert actual_error_msg == expected_error_msg, f"The expected msg: {expected_error_msg } not the same as actual: {actual_error_msg} "


@pytest.mark.parametrize('file_data, type_of_file, expected_error_msg',
                         [(get_data_file('/taxonomy/tax_file_with_forbidden_character>.csv'), 'text/csv',
                           'contains illegal character >'),
                          (get_data_file('/taxonomy/tax_file_with_incorrect_symbol_|.csv'), "text/csv",
                           'contains illegal character |'),
                          (get_data_file('/taxonomy/empty_file'), "text/plain",
                           'Only these file types are supported: csv, json')
                          ])
def test_upload_incorrect_taxonomy_file(file_data, type_of_file, expected_error_msg, set_job):
    api = Builder(api_key=api_key, api_version='v2')
    name = "tax_" + str(random.randint(1, 100))

    response = api.upload_taxonomy_file_via_public(set_job, api_key, name=name, file=file_data,
                                                   type_of_file=type_of_file)
    actual_error_msg = response.text

    response.assert_response_status(400)
    assert expected_error_msg in actual_error_msg, f"The {expected_error_msg}, not present in {actual_error_msg}"


@pytest.mark.parametrize('name, file_data, type_of_file, file_param',
                         [(None, TAXONOMY_TEST_DATA, "text/csv", 'file'),
                          ("tax_1", TAXONOMY_TEST_DATA, "text/csv", None)
                          ])
@allure.issue("https://appen.atlassian.net/browse/AT-5636", "BUG  on Sandbox, Integration  AT-5636")
def test_upload_taxonomy_file_without_one_parameters(name, file_data, type_of_file, file_param, set_job):
    api = Builder(api_key=api_key, api_version='v2')

    response = api.upload_taxonomy_file_via_public(set_job, api_key, name=name, file=file_data,
                                                   type_of_file=type_of_file, file_param=file_param)
    actual_error_msg = response.text
    expected_error_msg = "Parameters 'file' and 'name' are required"

    response.assert_response_status(400)
    assert actual_error_msg == expected_error_msg, f"The expected msg: {expected_error_msg } not the same as actual: {actual_error_msg} "


@allure.issue("https://appen.atlassian.net/browse/AT-5636", "BUG  on Sandbox, Integration  AT-5636")
def test_upload_taxonomy_file_no_admin_user():
    api = Builder(api_key=api_key, api_version='v2')

    name = 'tax_' + str(random.randint(1, 1000))

    response = api.upload_taxonomy_file_via_public(JOB_ID, API_KEY_NO_ADMIN, name=name, file=TAXONOMY_TEST_DATA,
                                                   type_of_file='text/csv')

    property_msg = response.text
    assert property_msg == 'Taxonomy successfully uploaded', f"Uploading failed in the reason with {property_msg}"
    response.assert_response_status(200)



