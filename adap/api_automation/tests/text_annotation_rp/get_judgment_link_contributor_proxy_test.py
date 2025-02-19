"""
https://appen.atlassian.net/browse/QED-1713
Covers text annotation get judgment link contributor proxy test
Info from dev:
It seems that we use /v1/text_annotation/${job_id}/judgment_link?annotationId=${annotation_id} in the unit mode and /contributor_proxy/v1/text_annotation/${job_id}/judgment_link?annotationId=${annotation_id} in the contributor missed and work modes
So we create job, fail the quiz mode and go to the test questions page to check the call.
But this api will be deprecated soon to super saver.
"""
import pytest
import requests
from adap.api_automation.utils.data_util import get_test_data,generate_random_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['text_annotation'].get(pytest.env)['tq_flat']
ANNOTATION_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['contributor_proxy_annotation_id']
JWT_TOKEN = get_test_data('test_contributor_task', 'jwt_token')

# TODO: Tests are not working for predefined Integration job_id=1580339 ("tq_flat"), hence not enabled in INT env

@pytest.mark.skip(reason="Need jwt_token for contributor account, as this endpoint is accessed by contributor only ")
@pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
def test_get_judgment_link_rp_contributor(rp_adap):
    """
    Verify GET /contributor_proxy/v1/text_annotation/%s/judgment_link?annotationId=%s is successful with valid parameters
    """
    # rp = RP(JWT_TOKEN)
    res = rp_adap.get_judgment_link_contributor_proxy_text_annotation(JOB_ID, ANNOTATION_ID)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert ANNOTATION_ID in url
    assert str(JOB_ID) in url
    assert "f8-text-annotation" in url
    url_res = requests.get(url)
    assert url_res.status_code == 200
    assert 'spans' in url_res.json()
    assert 'tokens' in url_res.json()
    assert len(url_res.json().get('text')) > 0


@pytest.mark.skipif(pytest.env != "sandbox", reason="Only sandbox has annotation id configured")
@pytest.mark.parametrize('case_desc, job_id, annotation_id, expected_status',
                         [("missing job id", "", "predefine_annotation", 404),
                          ("missing annotation id", "predefine_job", "", 404),
                          ("random job id and annotation id", "random_int", "random_string", 404)
                          ])
def test_get_judgment_link_invalid_input_contributor(case_desc, job_id, annotation_id, expected_status, rp_adap):
    """
    Verify GET /contributor_proxy/v1/text_annotation/%s/judgment_link?annotationId=%s fails with invalid parameters
    """
    if job_id == "predefine_job":
        job_id = JOB_ID
    if annotation_id == "predefine_annotation":
        annotation_id = ANNOTATION_ID

    test_data = generate_random_test_data({'annotation_id': annotation_id,
                                           'job_id': job_id
                                           })

    # rp = RP(cookies=valid_cookies_adap)
    res = rp_adap.get_judgment_link_text_annotation(test_data['job_id'], test_data['annotation_id'])
    res.assert_response_status(expected_status)
