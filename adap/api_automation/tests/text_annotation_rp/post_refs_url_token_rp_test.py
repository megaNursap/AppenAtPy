"""
https://appen.atlassian.net/browse/QED-1713
Covers text annotation get judgment link request proxy test
"""

from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

PREDEFINED_JOBS = pytest.data.predefined_data
JOB_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['id']
ANNOTATION_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_1']

JOB_ID_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['job_id_ss']
ANNOTATION_ID1_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_1_ss']
ANNOTATION_ID2_SS = PREDEFINED_JOBS['textannotation_api'][pytest.env]['annotation_2_ss']
BUCKET_ID = PREDEFINED_JOBS['textannotation_api'][pytest.env]['bucket_id']
# JWT_TOKEN = get_test_data('test_ui_account', 'jwt_token')
# REFS_TOKEN = get_test_data('test_ui_account', 'refs_token')

# Converting this to a negative test as per changed made in AT-3487. TODO: https://appen.atlassian.net/browse/QED-2243
# @allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Test data available only in sandbox & integration")
def test_post_ref_url_ss_invalid_input(rp_adap):
    """
    Verify POST /refs/url endpoint fails when refs-token is not provided in headers
    """
    # rp = RP(cookies=valid_cookies_adap)
    payload = {"ref": {"job_id": JOB_ID_SS,
                       "annotation_id": ANNOTATION_ID1_SS,
                       "bucket_id": BUCKET_ID}}
    res = rp_adap.post_refs_url(payload)
    res.assert_response_status(403)
    # url = res.json_response.get('url')
    # assert BUCKET_ID in url
    # assert str(JOB_ID_SS) in url
    # assert ANNOTATION_ID1_SS in url


# https://appen.atlassian.net/browse/QED-2243
# @allure.issue("https://appen.atlassian.net/browse/QED-3135", "BUG  on Sandbox QED-3135")
# @pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
def test_post_ref_url_ss_valid_input(rp_adap):
    """
    Verify POST /refs/url endpoint when refs-token is provided in headers
    """
    refs_token = get_test_data('test_ui_account', 'x_storage_refs_token')
    payload = {"ref": {"job_id": JOB_ID_SS,
                       "annotation_id": ANNOTATION_ID1_SS,
                       "bucket_id": BUCKET_ID}}
    res = rp_adap.post_refs_url(payload, refs_token)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert BUCKET_ID in url
    assert str(JOB_ID_SS) in url
    assert ANNOTATION_ID1_SS in url