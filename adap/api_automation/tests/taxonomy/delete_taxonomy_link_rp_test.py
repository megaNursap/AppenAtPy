"""
JIRA:https://appen.atlassian.net/browse/QED-3685
Documentation: https://github.com/CrowdFlower/requestor-proxy/blob/master/config/endpoints/paths/taxonomy.yaml
"""
import uuid

import pytest
import requests

from adap.api_automation.utils.data_util import get_data_file

pytestmark = [pytest.mark.regression_taxonomy, pytest.mark.taxonomy_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('job_id',"")
TEAM_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('teamId', "")
TAXONOMY_TEST_DATA = get_data_file('/taxonomy_data.json')
CUSTOM_UUID = str(uuid.uuid4())


@pytest.fixture(scope="module")
def taxonomy_job(rp_adap):
    rp_adap.upload_taxonomy_file(TAXONOMY_TEST_DATA, JOB_ID, TEAM_ID, CUSTOM_UUID)


def test_delete_taxonomy_link_rp(rp_adap, taxonomy_job):
    """
    Verify DELETE v1/refs/delete_link?path=jobs/%s/shared/taxonomy/%s.json&teamId=%s is successful with valid parameters
    """

    res = rp_adap.delete_taxonomy_link_bucket_uuid(JOB_ID, TEAM_ID, CUSTOM_UUID)
    res.assert_response_status(200)
    url = res.json_response.get('url')

    response = requests.delete(url)
    assert response.status_code == 204, 'Content not deleted from taxonomy Job'
    res_get = rp_adap.get_taxonomy_link_to_cds_bucket(JOB_ID, TEAM_ID, CUSTOM_UUID)
    res_get.assert_response_status(200)
    url = res_get.json_response.get('url')

    response = requests.get(url)
    assert response.status_code == 404, 'Content present in taxonomy manager'


def test_delete_without_path_parameter_taxonomy_link_rp(rp_adap, taxonomy_job):
    """
    Verify DELETE v1/refs/delete_link?teamId=%s is error without parameters
    """

    res = rp_adap.delete_taxonomy_link_bucket_uuid(JOB_ID, TEAM_ID, CUSTOM_UUID, None)
    res.assert_response_status(400)
    error_msg_team_id = res.json_response['errors'][0]['message']
    error_msg_path = res.json_response['errors'][1]['message']
    assert 'Invalid parameter (teamId)' in error_msg_team_id, 'TeamId  not present error message'
    assert 'Invalid parameter (path)' in error_msg_path, 'Path  not present error message'


@pytest.mark.parametrize('team_id, path_param, error_message',
                         [(TEAM_ID, 'path', "Invalid parameter (path)"),
                          ("", "teamId", "Invalid parameter (teamId)")
                          ])
def test_delete_without_one_of_parameter_taxonomy_link_rp(rp_adap, team_id, path_param, error_message):
    """
    Verify DELETE v1/refs/delete_link is error without one of parameters
    """

    res = rp_adap.delete_taxonomy_link_bucket_uuid(JOB_ID, team_id, CUSTOM_UUID, path_param)
    res.assert_response_status(400)
    error_msg = res.json_response['errors'][0]['message']

    assert error_message in error_msg, '%s not present error message' % path_param


