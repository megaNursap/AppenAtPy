"""
swagger - https://api-kepler.integration.cf3.us/metrics/swagger-ui/index.html#/
"""
import random

from adap.api_automation.services_config.quality_flow import QualityFlowApiMetrics
import pytest
import time
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, sorted_list_of_dict_by_value
import logging
logger = logging.getLogger('faker')
logger.setLevel(logging.INFO)  # Quiet faker locale messages down in testself.

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiMetrics()
    cookies = api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project
    }


def test_query_metrics_productivity_job_throughput(setup):
    api = setup['api']
    project_id = setup["default_project"]["dashboard"]["throughput"]["projectId"]
    team_id = setup['team_id']
    job_type = setup["default_project"]["dashboard"]["throughput"]["jobType"]
    start_time = setup["default_project"]["dashboard"]["throughput"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["throughput"]["endTime"]
    time_slot = setup["default_project"]["dashboard"]["throughput"]["timeSlot"]

    res = api.post_metrics_productivity_job_throughput(team_id, payload={
        "projectId": project_id,
        "jobId": "",
        "jobType": job_type,
        "startTime": start_time,
        "endTime": end_time,
        "timeSlot": time_slot
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data['workRate'] == setup["default_project"]["dashboard"]["throughput"]["workRate"]
    assert data['numOfContributors'] == setup["default_project"]["dashboard"]["throughput"]["numOfContributors"]
    assert data['workingHours'] == setup["default_project"]["dashboard"]["throughput"]["workingHours"]
    assert data['judgments'] == setup["default_project"]["dashboard"]["throughput"]["judgments"]
    assert data['efficiency'] == setup["default_project"]["dashboard"]["throughput"]["efficiency"]
    assert data['items'][51]['avgItems'] == setup["default_project"]["dashboard"]["throughput"]["items"]["avgItems"]
    assert data['items'][51]['efficiency'] == setup["default_project"]["dashboard"]["throughput"]["items"]["efficiency"]
    assert data['items'][51]['maxItems'] == setup["default_project"]["dashboard"]["throughput"]["items"]["maxItems"]
    assert data['items'][51]['medianItems'] == setup["default_project"]["dashboard"]["throughput"]["items"]["medianItems"]
    assert data['items'][51]['slice'] == setup["default_project"]["dashboard"]["throughput"]["items"]["slice"]
    assert data['items'][51]['totalItems'] == setup["default_project"]["dashboard"]["throughput"]["items"]["totalItems"]


def test_query_metrics_quality_project_quality(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']

    res = api.post_metrics_quality_project_quality(team_id, project_id)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data['accuracyRate'] == setup["default_project"]["dashboard"]["overallProjectQuality"]["accuracyRate"]
    assert data['approved'] == setup["default_project"]["dashboard"]["overallProjectQuality"]["approved"]
    assert data['modified'] == setup["default_project"]["dashboard"]["overallProjectQuality"]["modified"]
    assert data['rejected'] == setup["default_project"]["dashboard"]["overallProjectQuality"]["rejected"]
    assert data['totalQAedUnits'] == setup["default_project"]["dashboard"]["overallProjectQuality"]["totalQAedUnits"]
    assert data['totalSubmittedUnits'] == setup["default_project"]["dashboard"]["overallProjectQuality"]["totalSubmittedUnits"]


def test_query_metrics_quality_leading_job_statistic(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    start_time = setup["default_project"]["dashboard"]["leadingJobStatistics"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["leadingJobStatistics"]["endTime"]
    job_list = setup["default_project"]["dashboard"]["leadingJobStatistics"]["jobList"]
    job_statistic_name = list(job_list[0].keys())
    job_statistic_name.remove('jobTagSummaryList')
    job_statistic_list = []
    for i in range(len(job_list)):
        job_statistic_list.append({head: job_list[i][head] for head in job_statistic_name})
    job_ids = [x["jobId"] for x in job_list]

    res = api.post_metrics_quality_leading_job_statistic(team_id, payload={
        "projectId": project_id,
        "startTime": start_time,
        "endTime": end_time,
        "jobIds": job_ids
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    for job in rsp['data']:
        assert job in job_statistic_list


def test_query_metrics_contributor_performance(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    start_time = setup["default_project"]["dashboard"]["performance"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["performance"]["endTime"]
    contributor_list = setup["default_project"]["dashboard"]["performance"]["contributorList"]

    res = api.post_metrics_contributor_performance(team_id, payload={
        "projectId": project_id,
        "pageNum": 1,
        "pageSize": 4,
        "searchText": "",
        "startTime": start_time,
        "endTime": end_time,
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data['pageNumber'] == 1
    assert data['pageSize'] == 4
    assert data['totalElements'] == 8
    assert data['totalPages'] == 2
    assert data['content'] == contributor_list


def test_query_metrics_contributor_qachecker_performance(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    start_time = setup["default_project"]["dashboard"]["QaCheckerBehavior"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["QaCheckerBehavior"]["endTime"]
    contributor_list = setup["default_project"]["dashboard"]["QaCheckerBehavior"]["contributorList"]

    res = api.post_metrics_contributor_qachecker_performance(team_id, payload={
        "projectId": project_id,
        "pageNum": 1,
        "pageSize": 4,
        "searchText": "",
        "startTime": start_time,
        "endTime": end_time,
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data['pageNumber'] == 1
    assert data['pageSize'] == 4
    assert data['totalElements'] == 4
    assert data['totalPages'] == 1
    assert data['content'] == contributor_list


def test_query_metrics_project_job_statistic_progress(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    progress_list = random.sample(setup["default_project"]["dashboard"]["progress"], 4)
    payload = []
    for job in progress_list:
        payload.append({head: job[head] for head in ['jobId', 'flowId', 'cycleNum']})
    res = api.post_metrics_project_job_statistic_progress(team_id, project_id, payload)

    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data_list = []
    for job in progress_list:
        data_list.append({head: job[head] for head in ['jobId', 'notStarted', 'underReview', 'submitted', 'auditing', 'total', 'complete']})
    assert rsp['data'] == data_list


def test_query_metrics_project_job_statistic_breakdown_word_error_rate(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["endTime"]
    word_error_list = setup["default_project"]["dashboard"]["breakdown"]["wordErrorList"]
    word_error_rate_list = []
    word_error_list_name = list(word_error_list[0].keys())
    word_error_list_name.remove('wordDetailList')
    for i in range(len(word_error_list)):
        word_error_rate_list.append({head: word_error_list[i][head] for head in word_error_list_name})

    res = api.post_metrics_project_job_statistic_breakdown_word_error_rate(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "startTime": start_time,
        "endTime": end_time
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    for data in rsp['data']:
        assert data in word_error_rate_list


def test_query_metrics_project_job_statistic_breakdown_word_detail(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["endTime"]
    word_error_list = setup["default_project"]["dashboard"]["breakdown"]["wordErrorList"]
    for word_detail in word_error_list:
        payload = {
            "projectId": project_id,
            "startTime": start_time,
            "endTime": end_time,
            "jobId": job_id,
            "changeType": word_detail["changeType"],
            "original": word_detail["original"],
            "modification": word_detail["modification"]
        }
        res = api.post_metrics_project_job_statistic_breakdown_word_detail(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        assert rsp['data'] == word_detail["wordDetailList"]



def test_query_metrics_project_job_statistic_breakdown_tag_summary(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    start_time = setup["default_project"]["dashboard"]["leadingJobStatistics"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["leadingJobStatistics"]["endTime"]
    job_list = setup["default_project"]["dashboard"]["leadingJobStatistics"]["jobList"]
    job_ids = [x["jobId"] for x in job_list]
    job_tag_summary_dict = {}
    for i in range(len(job_list)):
        job_tag_summary_dict[job_list[i]["jobId"]] = job_list[i]["jobTagSummaryList"]

    res = api.post_metrics_project_job_statistic_breakdown_tag_summary(team_id, payload={
        "projectId": project_id,
        "startTime": start_time,
        "endTime": end_time,
        "jobIds": job_ids
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    for data in rsp['data']:
        for job_tag in data["jobTagSummaryList"]:
            assert job_tag in job_tag_summary_dict[data["jobId"]]


def test_query_metrics_project_job_statistic_breakdown_tag_error_rate(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["endTime"]
    tag_error_list = setup["default_project"]["dashboard"]["breakdown"]["tagErrorList"]
    tag_error_rate_list = []
    tag_error_list_name = list(tag_error_list[0].keys())
    tag_error_list_name.remove('tagDetailList')
    for i in range(len(tag_error_list)):
        tag_error_rate_list.append({head: tag_error_list[i][head] for head in tag_error_list_name})

    res = api.post_metrics_project_job_statistic_breakdown_tag_error_rate(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "startTime": start_time,
        "endTime": end_time
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    assert sorted_list_of_dict_by_value(rsp['data'],'tagValue') \
           == sorted_list_of_dict_by_value(tag_error_rate_list, 'tagValue')


def test_query_metrics_project_job_statistic_breakdown_tag_detail(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["endTime"]
    tag_error_list = setup["default_project"]["dashboard"]["breakdown"]["tagErrorList"]
    for tag_detail in tag_error_list:
        payload = {
            "projectId": project_id,
            "startTime": start_time,
            "endTime": end_time,
            "jobId": job_id,
            "changeType": tag_detail["changeType"],
            "tagValue": tag_detail["tagValue"]
        }
        res = api.post_metrics_project_job_statistic_breakdown_tag_detail(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        assert rsp['data'] == tag_detail["tagDetailList"]


def test_query_metrics_project_job_statistic_breakdown_label_error_rate(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["endTime"]
    label_error_list = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["labelErrorList"]
    label_error_rate_list = []
    label_error_list_name = list(label_error_list[0].keys())
    label_error_list_name.remove('labelDetailList')
    for i in range(len(label_error_list)):
        label_error_rate_list.append({head: label_error_list[i][head] for head in label_error_list_name})

    res = api.post_metrics_project_job_statistic_breakdown_label_error_rate(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "startTime": start_time,
        "endTime": end_time
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    for data in rsp['data']:
        assert data in label_error_rate_list


def test_query_metrics_project_job_statistic_breakdown_label_detail(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["endTime"]
    label_error_list = setup["default_project"]["dashboard"]["breakdown"]["labelErrorRate"]["labelErrorList"]
    for label_detail in label_error_list:
        payload = {
            "projectId": project_id,
            "startTime": start_time,
            "endTime": end_time,
            "jobId": job_id,
            "changeType": label_detail["changeType"],
            "original": label_detail["original"],
            "modification": label_detail["modification"]
        }
        res = api.post_metrics_project_job_statistic_breakdown_label_detail(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        assert rsp['data'] == label_detail["labelDetailList"]

def test_get_metrics_feedback_statistics_valid(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    statistics = setup["default_project"]["dashboard"]["feedback"]["summary"]
    res = api.get_metrics_project_feedback_statistics(team_id, project_id)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['disputedUnits'] == statistics["disputedUnits"]
    assert rsp['data']['pendingUnits'] == statistics["pendingUnits"]
    assert rsp['data']['resolvedUnits'] == statistics["resolvedUnits"]
    assert rsp['data']['totalFeedbackUnits'] == statistics["totalFeedbackUnits"]

def test_get_metrics_feedback_statistics_invalid_cookies(setup):
    api = QualityFlowApiMetrics()
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    res = api.get_metrics_project_feedback_statistics(team_id, project_id)
    rsp = res.json_response
    assert rsp['code'] == 401
    assert rsp['message'] == 'Please login'

@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_metrics_feedback_statistics_invalid_team_id(setup, name, team_id, message):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    res = api.get_metrics_project_feedback_statistics(team_id, project_id)
    rsp = res.json_response
    assert res.status_code == 203
    assert rsp['message'] == message

@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_get_metrics_feedback_statistics_invalid_project_id(setup, name, project_id):
    api = setup["api"]
    team_id = setup['team_id']
    res = api.get_metrics_project_feedback_statistics(team_id, project_id)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'

def test_get_metrics_feedback_columns(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    column_expect_list = ['Unit ID', 'Status', 'job Title', 'Contributor External ID', 'QA Checker External ID', 'updated At', 'feedback Status']
    column_actual_list = []
    res = api.get_metrics_project_feedback_columns(team_id, project_id)
    rsp = res.json_response
    assert rsp['code'] == 200
    for column_group in rsp['data']['columnDefs']:
        for column_name in column_group['children']:
            column_actual_list.append(column_name['displayName'])
    assert column_actual_list == column_expect_list

def test_post_metrics_feedback_list(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    units = setup["default_project"]["dashboard"]["feedback"]["units"]

    res = api.post_metrics_project_feedback_list(team_id, project_id, payload={
        "startRow": 0,
        "endRow": 100,
        "filterModel": {
            "latest.lastAnnotatorExternalId": {
                "filter": units["units_filter"]["items"]["lastAnnotatorExternalId"],
                "filterType": "text",
                "type": "equals"
            },
            "latest.feedbackStatus": {
                "values": [units["units_filter"]["items"]["feedbackStatus"]],
                "filterType": "set"
            },
            "unitDisplayId": {
                "filter": units["units_filter"]["items"]["unitDisplayId"][-1],
                "filterType": "text",
                "type": "contains"
            },
            "jobStatus": {
                "values": [units["units_filter"]["items"]["jobStatus"]],
                "filterType": "set"
            },
            "latest.jobTitle": {
                "filter": units["units_filter"]["items"]["jobTitle"],
                "filterType": "text",
                "type": "equals"
            }
        },
        "queryString": "",
        "sortModel": []
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    row_id = units["units_filter"]["items"]["rowId"]
    assert rsp['data']['totalElements'] == units["units_filter"]["totalElements"]
    assert rsp['data']['secondaryColumnFields'] == units["units_filter"]["secondaryColumnFields"]
    assert rsp['data']['lastRow'] == units["units_filter"]["lastRow"]
    assert rsp['data']['units'][row_id]['unitId'][0]['value'] == units["units_filter"]["items"]["unitId"]
    assert rsp['data']['units'][row_id]['jobAlias'][0]['value'] == units["units_filter"]["items"]["jobAlias"]
    assert rsp['data']['units'][row_id]['jobStatus'][0]['value'] == units["units_filter"]["items"]["jobStatus"]

    res = api.post_metrics_project_feedback_list(team_id, project_id, payload={
        "startRow": 0,
        "endRow": 100,
        "filterModel": {},
        "queryString": units["units_query"]["items"]["lastAnnotatorExternalId"][:5]+"*",
        "sortModel": [
            {
                "sort": "desc",
                "colId": "unitDisplayId"
            }
        ]
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    row_id = units["units_query"]["items"]["rowId"]
    assert rsp['data']['totalElements'] == units["units_query"]["totalElements"]
    assert rsp['data']['secondaryColumnFields'] == units["units_query"]["secondaryColumnFields"]
    assert rsp['data']['lastRow'] == units["units_query"]["lastRow"]
    assert rsp['data']['units'][row_id]['unitId'][0]['value'] == units["units_query"]["items"]["unitId"]
    assert rsp['data']['units'][row_id]['jobAlias'][0]['value'] == units["units_query"]["items"]["jobAlias"]
    assert rsp['data']['units'][row_id]['jobStatus'][0]['value'] == units["units_query"]["items"]["jobStatus"]

    contributor_id = units["units_invalid"]["lastAnnotatorExternalId"]
    res = api.post_metrics_project_feedback_list(team_id, project_id, payload={
        "startRow": 0,
        "endRow": 100,
        "filterModel": {
            "latest.lastAnnotatorExternalId": {
                "filter": contributor_id[:6],
                "filterType": "text",
                "type": "equals"
            }
        },
        "queryString": "",
        "sortModel": []
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['totalElements'] == units["units_invalid"]["totalElements"]
    assert rsp['data']['secondaryColumnFields'] == units["units_invalid"]["secondaryColumnFields"]
    assert rsp['data']['lastRow'] == units["units_invalid"]["lastRow"]
    assert rsp['data']['units'] == units["units_invalid"]["items"]


def test_query_metrics_project_job_statistic_review_breakdown_word_error_rate(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["ReviewBreakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["endTime"]
    word_error_list = setup["default_project"]["dashboard"]["ReviewBreakdown"]["wordErrorList"]
    word_error_rate_list = []
    word_error_list_name = list(word_error_list[0].keys())
    word_error_list_name.remove('wordDetailList')
    for i in range(len(word_error_list)):
        word_error_rate_list.append({head: word_error_list[i][head] for head in word_error_list_name})

    res = api.post_metrics_project_job_statistic_review_breakdown_word_error_rate(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "startTime": start_time,
        "endTime": end_time
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    for data in rsp['data']:
        assert data in word_error_rate_list


def test_query_metrics_project_job_statistic_review_breakdown_word_detail(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["ReviewBreakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["endTime"]
    word_error_list = setup["default_project"]["dashboard"]["ReviewBreakdown"]["wordErrorList"]
    for word_detail in word_error_list:
        payload = {
            "projectId": project_id,
            "startTime": start_time,
            "endTime": end_time,
            "jobId": job_id,
            "changeType": word_detail["changeType"],
            "original": word_detail["original"],
            "modification": word_detail["modification"]
        }
        res = api.post_metrics_project_job_statistic_review_breakdown_word_detail(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        for data in rsp['data']:
            assert data in word_detail["wordDetailList"]


def test_query_metrics_quality_review_job_statistic(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    start_time = setup["default_project"]["dashboard"]["ReviewJobStatistics"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewJobStatistics"]["endTime"]
    job_list = setup["default_project"]["dashboard"]["ReviewJobStatistics"]["jobList"]
    job_statistic_name = list(job_list[0].keys())
    job_statistic_name.remove('jobTagSummaryList')
    job_statistic_list = []
    for i in range(len(job_list)):
        job_statistic_list.append({head: job_list[i][head] for head in job_statistic_name})
    job_ids = [x["jobId"] for x in job_list]

    res = api.post_metrics_quality_review_job_statistic(team_id, payload={
        "projectId": project_id,
        "startTime": start_time,
        "endTime": end_time,
        "jobIds": job_ids
    })

    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    for job in rsp['data']:
        assert job in job_statistic_list

def test_query_metrics_project_job_statistic_review_breakdown_tag_summary(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    start_time = setup["default_project"]["dashboard"]["ReviewJobStatistics"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewJobStatistics"]["endTime"]
    job_list = setup["default_project"]["dashboard"]["ReviewJobStatistics"]["jobList"]
    job_ids = [x["jobId"] for x in job_list]
    job_tag_summary_dict = {}
    for i in range(len(job_list)):
        job_tag_summary_dict[job_list[i]["jobId"]] = job_list[i]["jobTagSummaryList"]

    res = api.post_metrics_project_job_statistic_review_breakdown_tag_summary(team_id, payload={
        "projectId": project_id,
        "startTime": start_time,
        "endTime": end_time,
        "jobIds": job_ids
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    for data in rsp['data']:
        for job_tag in data["jobTagSummaryList"]:
            assert job_tag in job_tag_summary_dict[data["jobId"]]


def test_query_metrics_project_job_statistic_review_breakdown_tag_error_rate(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["breakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["breakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["breakdown"]["endTime"]
    tag_error_list = setup["default_project"]["dashboard"]["breakdown"]["tagErrorList"]
    tag_error_rate_list = []
    tag_error_list_name = list(tag_error_list[0].keys())
    tag_error_list_name.remove('tagDetailList')
    for i in range(len(tag_error_list)):
        tag_error_rate_list.append({head: tag_error_list[i][head] for head in tag_error_list_name})

    res = api.post_metrics_project_job_statistic_review_breakdown_tag_error_rate(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "startTime": start_time,
        "endTime": end_time
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    for data in rsp['data']:
        assert data in tag_error_rate_list


def test_query_metrics_project_job_statistic_review_breakdown_tag_detail(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["ReviewBreakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["endTime"]
    tag_error_list = setup["default_project"]["dashboard"]["ReviewBreakdown"]["tagErrorList"]
    for tag_detail in tag_error_list:
        payload = {
            "projectId": project_id,
            "startTime": start_time,
            "endTime": end_time,
            "jobId": job_id,
            "changeType": tag_detail["changeType"],
            "tagValue": tag_detail["tagValue"]
        }
        res = api.post_metrics_project_job_statistic_review_breakdown_tag_detail(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        for data in rsp['data']:
            assert data in tag_detail["tagDetailList"]


def test_query_metrics_project_job_statistic_review_breakdown_label_error_rate(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["ReviewBreakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["endTime"]
    label_error_list = setup["default_project"]["dashboard"]["ReviewBreakdown"]["labelErrorList"]
    label_error_rate_list = []
    label_error_list_name = list(label_error_list[0].keys())
    label_error_list_name.remove('labelDetailList')
    for i in range(len(label_error_list)):
        label_error_rate_list.append({head: label_error_list[i][head] for head in label_error_list_name})

    res = api.post_metrics_project_job_statistic_review_breakdown_label_error_rate(team_id, payload={
        "projectId": project_id,
        "jobId": job_id,
        "startTime": start_time,
        "endTime": end_time
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    for data in rsp['data']:
        assert data in label_error_rate_list


def test_query_metrics_project_job_statistic_review_breakdown_label_detail(setup):
    api = setup["api"]
    project_id = setup["default_project"]["dashboard"]["projectId"]
    team_id = setup['team_id']
    job_id = setup["default_project"]["dashboard"]["ReviewBreakdown"]["jobId"]
    start_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["startTime"]
    end_time = setup["default_project"]["dashboard"]["ReviewBreakdown"]["endTime"]
    label_error_list = setup["default_project"]["dashboard"]["ReviewBreakdown"]["labelErrorList"]
    for label_detail in label_error_list:
        payload = {
            "projectId": project_id,
            "startTime": start_time,
            "endTime": end_time,
            "jobId": job_id,
            "changeType": label_detail["changeType"],
            "original": label_detail["original"],
            "modification": label_detail["modification"]
        }
        res = api.post_metrics_project_job_statistic_review_breakdown_label_detail(team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200
        for data in rsp['data']:
            assert data in label_detail["labelDetailList"]
