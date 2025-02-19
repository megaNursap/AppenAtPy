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
JOB_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('job_id_taxonomies', "")
TEAM_ID = PREDEFINED_JOBS['taxonomy_api'].get(pytest.env, {}).get('teamId', "")
TAXONOMY_TEST_DATA = get_data_file('/taxonomy_data.json')
NO_ADMIN_TEAM_ID = get_user_team_id('test_account')


def test_get_all_taxonomies(rp_adap):
    """
       Verify GET v1/refs/get_link?path=jobs/%s/shared/taxonomies.json  is successful with valid parameters
    """
    custom_uuid = str(uuid.uuid4())
    name = "taxonomy_2"

    rp_adap.upload_taxonomy_file(TAXONOMY_TEST_DATA, JOB_ID, TEAM_ID, custom_uuid, name)
    res = rp_adap.get_taxonomy_link_shared_file(JOB_ID, TEAM_ID)
    res.assert_response_status(200)
    url = res.json_response.get('url')

    response = requests.get(url)
    assert response.status_code == 200, 'URL created incorrect from endpoint GET v1/refs/get_link'
    res_content = response.json()

    assert custom_uuid in res_content, f"The uuid: of response {res_content} doesn't contain expected uuid: {custom_uuid} "
    assert name == res_content[custom_uuid], f"The name of Taxonomy: {res_content[custom_uuid]} not as expected"