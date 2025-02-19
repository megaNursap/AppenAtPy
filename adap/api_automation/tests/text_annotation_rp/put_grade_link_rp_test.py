"""
EPIC:https://appen.atlassian.net/browse/QED-1334
JIRA:https://appen.atlassian.net/browse/QED-1339
     https://appen.atlassian.net/browse/QED-1340
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/text-annotation/1.0.0#/Annotations/post_annotations
"""
import requests
from adap.api_automation.services_config.textannotation import *
from adap.api_automation.utils.data_util import generate_random_test_data, get_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

predefined_jobs = pytest.data.predefined_data
TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env)
TEAM_ID = TEST_DATA['team_id']


@pytest.mark.skipif(pytest.env not in ["sandbox", "qa", "integration"],
                    reason="Only QA, Integration and Sandbox has data configured")
@pytest.mark.parametrize('job_id, annotation_id, expected_status, error_message',
                         [("", "random_string", 404, "NoSuchKey"),
                          ("random_int", "", 404, "NoSuchKey"),
                          ("random_int", "random_string", 404, "NoSuchKey")
                          ])
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
def test_put_grade_invalid_input(rp_adap, job_id, annotation_id, expected_status, error_message):
    """
    Verify PUT /grade fails with invalid payload
    """
    # jwt_token = get_test_data('test_ui_account', 'jwt_token')
    # refs_token = get_test_data('test_ui_account', 'refs_token')
    storage_ref_token = get_test_data('test_ui_account', 'x_storage_refs_token')

    test_data = generate_random_test_data({'job_id': job_id,
                                           'annotation_id': annotation_id
                                           })
    payload = {
        "team_id": TEAM_ID,
        "job_id": test_data['job_id'],
        "judgment_data": {
            "job_id": test_data['job_id'],
            "annotation_id": test_data['annotation_id'],
            "custom_bucket": False
        }
    }
    res = TextAnnotation().put_grade(payload)
    res.assert_response_status(expected_status)
    # rp = RP(cookies=valid_cookies_adap, jwt_token=jwt_token, refs_token=refs_token)
    payload = {
        "ref": {
            "type": "text_annotation/agg_report",
            "valueRef": "jobs/%s/%s/grade" % (test_data['job_id'], test_data['annotation_id'])
        }
    }
    res = rp_adap.post_refs_url(payload, storage_ref_token)

    url = res.json_response.get('url')
    url_res = requests.get(url)
    assert url_res.status_code == expected_status
    if error_message is not None:
        assert error_message in url_res.text
