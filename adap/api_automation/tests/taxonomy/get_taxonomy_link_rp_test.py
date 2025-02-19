"""
JIRA:https://appen.atlassian.net/browse/QED-3685
Documentation: https://github.com/CrowdFlower/requestor-proxy/blob/master/config/endpoints/paths/taxonomy.yaml
"""
import uuid

import pytest
import requests

from adap.api_automation.utils.data_util import get_data_file, get_user_team_id

pytestmark = [pytest.mark.regression_taxonomy, pytest.mark.taxonomy_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('job_id', "")
TEAM_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('teamId', "")
TAXONOMY_TEST_DATA = get_data_file('/taxonomy_data.json')
NO_ADMIN_TEAM_ID = get_user_team_id('test_account')
CUSTOM_UUID = str(uuid.uuid4())


@pytest.fixture(scope="module")
def taxonomy_job(rp_adap):
    rp_adap.upload_taxonomy_file(TAXONOMY_TEST_DATA, JOB_ID, TEAM_ID, CUSTOM_UUID)


def test_get_taxonomy_link_rp(rp_adap, taxonomy_job):
    """
    Verify GET v1/refs/get_link?path=jobs/%s/shared/taxonomy/%s.json&teamId=%s  is successful with valid parameters
    """
    res = rp_adap.get_taxonomy_link_to_cds_bucket(JOB_ID, TEAM_ID, CUSTOM_UUID)
    res.assert_response_status(200)
    url = res.json_response.get('url')

    response = requests.get(url)
    assert response.status_code == 200, 'URL created incorrect from endpoint GET v1/refs/get_link'
    res_content = response.json()
    assert 'taxonomyItems' in res_content, 'Json file does not contain one of the main key topLevel'
    assert 'taxonomyItems' in res_content, 'Json file does not contain one of the main key taxonomyItems'


@pytest.mark.parametrize('team_id, path_param, error_message',
                         [(TEAM_ID, 'path', "Invalid parameter (path)"),
                          ("", "teamId", "Invalid parameter (teamId)")
                          ])
def test_get_without_path_parameter_taxonomy_link_rp(rp_adap, taxonomy_job, team_id, path_param, error_message):
    """
    Verify GET v1/refs/get_link is error without parameters
    """

    res = rp_adap.get_taxonomy_link_to_cds_bucket(JOB_ID, team_id, CUSTOM_UUID, path_param)
    res.assert_response_status(400)
    error_msg_job = res.json_response['errors'][0]['message']
    assert error_message in error_msg_job, '%s  not present error message' % error_msg_job


@pytest.mark.parametrize('job_id, team_id, status_code',
                         [(JOB_ID, NO_ADMIN_TEAM_ID, 200),
                          (' ', TEAM_ID, 200)
                          ])
def test_get_invalid_path_parameter_taxonomy_link_rp(rp_adap, taxonomy_job, job_id, team_id, status_code ):
    """
    Verify GET v1/refs/get_link?path=jobs//shared/%s.json&teamId=%s without JobId in path create incorrect url

    In this test we check that user who doesn't have admin role or not a part of the team whose requestor create the Job
    and other case when we send empty Job_Id
    """

    res = rp_adap.get_taxonomy_link_to_cds_bucket(job_id, team_id, CUSTOM_UUID)

    res.assert_response_status(200)
    url = res.json_response.get('url')
    response = requests.get(url)
    assert response.status_code == 404, f'The status code for URL incorrect should be 404 but {response.status_code}'


