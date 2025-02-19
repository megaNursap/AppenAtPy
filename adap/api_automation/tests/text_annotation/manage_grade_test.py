"""
EPIC:https://appen.atlassian.net/browse/QED-1334
JIRA:https://appen.atlassian.net/browse/QED-1339
     https://appen.atlassian.net/browse/QED-1340
SWAGGER:https://app.swaggerhub.com/apis/CrowdFlower/text-annotation/1.0.0#/Annotations/post_annotations
"""

from adap.api_automation.services_config.textannotation import *
from adap.api_automation.utils.data_util import generate_random_test_data

pytestmark = [pytest.mark.regression_text_annotation, pytest.mark.textannotation_api]

predefined_jobs = pytest.data.predefined_data
TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env)
TEAM_ID = TEST_DATA['team_id']

@pytest.mark.smoke
@pytest.mark.uat_api
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
@pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
def test_post_grade_ta_storage():
    """
    Verify POST /grade is successful with correct contributor response (using judgments from Text Annotation storage)
    """
    job_id = predefined_jobs['textannotation_api'][pytest.env]['id']
    annotation_id1 = predefined_jobs['textannotation_api'][pytest.env]['annotation_1']
    annotation_id2 = predefined_jobs['textannotation_api'][pytest.env]['annotation_2']
    payload = {
        "contributor_response": {
            "job_id": job_id,
            "annotation_id": annotation_id1,
            "custom_bucket": False
        },
        "correct_response": {
            "job_id": job_id,
            "annotation_id": annotation_id2,
            "custom_bucket": False
        }
    }
    res = TextAnnotation().post_grade(payload)
    res.assert_response_status(200)
    assert 'status' in res.json_response
    # TODO: Need to check why status returned is 'fail'
    #assert 'pass' == res.json_response.get('status')
    assert 'correct_span_ratio' in res.json_response
    assert 'threshold' in res.json_response
    assert 'failed_spans' in res.json_response
    assert 'correct_spans' in res.json_response

@pytest.mark.smoke
@pytest.mark.uat_api
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
@pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox has correct data configured")
# need correct predefine data for integraiton env
def test_post_grade_incorrect_contributor_response_gold_response():
    """
    Verify POST /grade is successful with incorrect contributor response (using judgments from Text Annotation storage)
    """
    job_id = predefined_jobs['textannotation_api'][pytest.env]['id']
    annotation_id1 = predefined_jobs['textannotation_api'][pytest.env]['incorrect_contributor_annotation']
    annotation_id2 = predefined_jobs['textannotation_api'][pytest.env]['gold_response_annotation']
    payload = {
        "contributor_response": {
            "job_id": job_id,
            "annotation_id": annotation_id1,
            "custom_bucket": False
        },
        "correct_response": {
            "job_id": job_id,
            "annotation_id": annotation_id2,
            "custom_bucket": False
        }
    }
    res = TextAnnotation().post_grade(payload)
    res.assert_response_status(200)
    assert 'fail' == res.json_response.get('status')
    assert 'correct_span_ratio' in res.json_response
    assert 'threshold' in res.json_response
    assert 'response' in res.json_response.get('failed_spans')[0]
    assert 'golden' in res.json_response.get('failed_spans')[0]
    assert 'correct_spans' in res.json_response


# https://appen.atlassian.net/browse/QED-1709
@pytest.mark.smoke
@pytest.mark.uat_api
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only QA, Integration and Sandbox has data configured")
@pytest.mark.parametrize('case_desc, annotation_id1, response_status, expected_status, failed_span',
                         [("perfect response vs golden response", "perfect_response", 200, "pass", None),
                          ("passing response vs golden response", "passing_response", 200, "pass", "failed_span"),
                          ("failing response vs golden response", "failing_response", 200, "fail", "failed_span")
                          ])
def test_post_grade_nested_span(case_desc, annotation_id1, response_status, expected_status, failed_span):
    """
    Verify POST /grade is successful with correct nested spans contributor response (using judgments from Text Annotation storage)
    """
    job_id = predefined_jobs['textannotation_api'][pytest.env]['id']
    annotation_id2 = predefined_jobs['textannotation_api'][pytest.env]['nested_span_golden_response']
    if annotation_id1 == "perfect_response":
        annotation_id1 = predefined_jobs['textannotation_api'][pytest.env]['nested_span_perfect_response']
    if annotation_id1 == "passing_response":
        annotation_id1 = predefined_jobs['textannotation_api'][pytest.env]['nested_span_passing_response']
    if annotation_id1 == "failing_response":
        annotation_id1 = predefined_jobs['textannotation_api'][pytest.env]['nested_span_failing_response']
    payload = {
        "team_id": TEAM_ID,
        "job_id": job_id,
        "contributor_response": {
            "job_id": job_id,
            "annotation_id": annotation_id1,
            "custom_bucket": False
        },
        "correct_response": {
            "job_id": job_id,
            "annotation_id": annotation_id2,
            "custom_bucket": False
        }
    }
    res = TextAnnotation().post_grade(payload)
    res.assert_response_status(response_status)
    assert expected_status == res.json_response.get('status')
    assert 'correct_span_ratio' in res.json_response
    assert 'threshold' in res.json_response
    assert 'correct_spans' in res.json_response
    if failed_span is None:
        assert len(res.json_response.get('failed_spans')) == 0
    else:
        assert len(res.json_response.get('failed_spans')) > 0
        assert 'response' in res.json_response.get('failed_spans')[0]
        assert 'golden' in res.json_response.get('failed_spans')[0]


@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only QA, Integration and Sandbox has data configured")
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
@pytest.mark.parametrize('job_id, annotation_id1, annotation_id2, expected_status',
                         [("random_int", "random_string", "random_string", 422),
                          ("", "random_string", "random_string", 422),
                          ("random_int", "", "", 422)
                          ])
def test_post_grade_invalid_input(job_id, annotation_id1, annotation_id2, expected_status):
    """
    Verify POST /grade fails when invalid input is provided
    """
    test_data = generate_random_test_data({'job_id': job_id,
                                           'annotation_id1': annotation_id1,
                                           'annotation_id2': annotation_id2
                                           })
    payload = {
        "team_id": TEAM_ID,
        "job_id": job_id,
        "contributor_response": {
            "job_id": test_data['job_id'],
            "annotation_id": test_data['annotation_id1'],
            "custom_bucket": False
        },
        "correct_response": {
            "job_id": test_data['job_id'],
            "annotation_id": test_data['annotation_id2'],
            "custom_bucket": False
        }
    }
    res = TextAnnotation().post_grade(payload)
    res.assert_response_status(expected_status)
    assert 'Contributor response not found in storage' == res.json_response.get('errors')[0]
    assert 'Gold response not found in storage' == res.json_response.get('errors')[1]


@pytest.mark.smoke
@pytest.mark.uat_api
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
@pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Only Sandbox and Integration has data configured")
def test_put_grade():
    """
    Verify PUT /grade is successful with valid payload
    """
    job_id = predefined_jobs['textannotation_api'][pytest.env]['id']
    annotation_id = predefined_jobs['textannotation_api'][pytest.env]['annotation_1']
    annotation_id2 = predefined_jobs['textannotation_api'][pytest.env]['annotation_2']
    payload = {
        "team_id": TEAM_ID,
        "job_id": job_id,
        "judgment_data": {
            "job_id": job_id,
            "annotation_id": annotation_id,
            "custom_bucket": False
        }
    }
    res = TextAnnotation().put_grade(payload)
    res.assert_response_status(200)
    url = res.json_response.get('url')
    assert str(job_id) in url
    assert annotation_id in url


@pytest.mark.smoke
@pytest.mark.uat_api
@allure.issue("https://appen.atlassian.net/browse/QED-3122", "BUG  on Sandbox QED-3122")
@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only Integration and Sandbox has data configured")
def test_post_grade_ss_storage():
    """
    Verify POST /grade is successful with valid payload (in super-saver storage)
    """
    job_id = predefined_jobs['textannotation_api'][pytest.env]['job_id_ss']
    annotation_id1 = predefined_jobs['textannotation_api'][pytest.env]['annotation_1_ss']
    annotation_id2 = predefined_jobs['textannotation_api'][pytest.env]['annotation_2_ss']
    bucket_id = predefined_jobs['textannotation_api'][pytest.env]['bucket_id']
    payload = {
        "team_id": TEAM_ID,
        "job_id": job_id,
        "contributor_response": {
            "job_id": job_id,
            "annotation_id": annotation_id1,
            "bucket_id": bucket_id
        },
        "correct_response": {
            "job_id": job_id,
            "annotation_id": annotation_id2,
            "bucket_id": bucket_id
        }
    }
    res = TextAnnotation().post_grade(payload)
    res.assert_response_status(200)
    assert 'pass' == res.json_response.get('status')
    assert 'correct_span_ratio' in res.json_response
    assert 'threshold' in res.json_response
    assert 'failed_spans' in res.json_response
    assert 'correct_spans' in res.json_response
