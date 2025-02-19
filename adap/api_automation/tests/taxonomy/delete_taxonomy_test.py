"""
JIRA:https://appen.spiraservice.net/5/TestCase/4839.aspx
Documentation: https://github.com/CrowdFlower/requestor-proxy/blob/master/config/endpoints/paths/taxonomy.yaml
"""
import uuid

import allure
import pytest
import requests

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_data_file, get_test_data, get_user_api_key

pytestmark = [pytest.mark.regression_taxonomy, pytest.mark.taxonomy_api]

PREDEFINED_JOBS = pytest.data.predefined_data
job_id = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('job_id_delete', "")
team_id = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('teamId',"")

taxonomy_test_data = get_data_file('/taxonomy_data.json')
custom_uuid = str(uuid.uuid4())
api_key = get_test_data('test_predefined_jobs', 'api_key')
api_key_other = get_user_api_key('test_ui_account')
name = "Taxonomy_3"


@pytest.fixture(autouse=True)
def set_job(rp_adap):
    rp_adap.upload_taxonomy_file(taxonomy_test_data, job_id, team_id, custom_uuid, name)
    api = Builder(api_key=api_key, api_version='v2')
    return api


def test_delete_taxonomy_file(rp_adap, set_job):
    """
    Verify DELETE /v2/jobs/$s/taxonomy?key=%s is successful with valid parameters
    """

    response = set_job.delete_taxonomy_file_via_public(job_id, api_key, name=name)
    response.assert_response_status(200)

    res = rp_adap.get_taxonomy_link_shared_file(job_id, team_id)
    res.assert_response_status(200)
    url = res.json_response.get('url')

    response = requests.get(url)
    assert response.status_code == 200, 'URL created incorrect from endpoint GET v1/refs/get_link'
    res_content = response.json()

    assert name not in str(res_content), f"The name of Taxonomy: {res_content} not as expected"


def test_delete_no_exist_taxonomy_file(set_job):
    """
       Verify DELETE /v2/jobs/$s/taxonomy?key=%s is return error with invalid taxonomy name
    """

    response = set_job.delete_taxonomy_file_via_public(job_id, api_key, name="Taxonomy_123444")
    response.assert_response_status(404)

    assert "No taxonomy found by this name" == response.text, "The incorrect error message"


def test_delete_without_name_parameter_taxonomy_file(set_job):
    """
           Verify DELETE /v2/jobs/$s/taxonomy?key=%s is return error without parameter 'name'
    """

    response = set_job.delete_taxonomy_file_via_public(job_id, api_key, name=None)
    response.assert_response_status(400)

    assert "Parameter 'name' is required" == response.text, "The incorrect error message"


@allure.issue("https://appen.atlassian.net/browse/AT-5955", "BUG  on Integration  AT-5955")
def test_delete_taxonomy_file_by_other_user(set_job):
    """
           Verify DELETE /v2/jobs/$s/taxonomy?key=%s is successful with api_key of other cf_internal api_key
    """
    response = set_job.delete_taxonomy_file_via_public(job_id, api_key_other, name=name)
    response.assert_response_status(200)

    assert "Taxonomy successfully deleted" == response.text, "The incorrect error message"
