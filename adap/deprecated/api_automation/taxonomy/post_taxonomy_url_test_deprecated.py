"""
JIRA:https://appen.atlassian.net/browse/QED-3685
Documentation: https://github.com/CrowdFlower/requestor-proxy/blob/master/config/endpoints/paths/taxonomy.yaml
"""

import pytest
from adap.api_automation.utils.data_util import get_data_file

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('job_id',  "")
TEAM_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('teamId',"")
TAXONOMY_TEST_DATA = get_data_file('/taxonomy_data.json')


def test_post_taxonomy_url(rp_adap):
    """
    Verify POST /v1/taxonomy/%s/url?teamId=%s is successful with valid parameters
    """

    res = rp_adap.post_taxonomy_url(JOB_ID, TEAM_ID)
    res.assert_response_status(200)
    header_location = res.headers['location']

    assert TEAM_ID in header_location, "TeamId missed in response header location URI %s" % header_location
    assert JOB_ID in header_location, "JobId missed in response header location URI %s" % header_location
    assert "https://appen-managed-integration-shared.s3.amazonaws.com" in header_location, "Schema and authority " \
                                                                                           "incorrect in response " \
                                                                                           "header location URI %s" %\
                                                                                           header_location
    assert "taxonomy.json" in header_location, "Taxonomy.json missed in response header location URI %s" % header_location


def test_post_without_team_id_parameter_taxonomy_url_rp(rp_adap):
    """
    Verify POST/v1/taxonomy/%s/url? is error without TeamId
    """

    res = rp_adap.post_taxonomy_url(JOB_ID, "", None)
    res.assert_response_status(400)
    error_msg_team_id = res.json_response['errors'][0]['message']
    assert 'Invalid parameter (teamId)' in error_msg_team_id, 'TeamId  not present error message'


def test_post_with_incorrect_team_id_parameter_taxonomy_url_rp(rp_adap):
    """
    Verify POST /v1/taxonomy/%s/url?teamId=%s is error with incorrect TeamId value
    """

    res = rp_adap.post_taxonomy_url(JOB_ID, "ga7409b8-9ca8-497d-837e-120f0287a6b7")
    res.assert_response_status(404)


def test_post_with_incorrect_job_id_parameter_taxonomy_url_rp(rp_adap):
    """
    Verify POST /v1/taxonomy/%s/url?teamId=%s is error with incorrect JobId value
    """
    res = rp_adap.post_taxonomy_url(123, TEAM_ID)
    res.assert_response_status(404)
    res.assert_job_message('Not Found')