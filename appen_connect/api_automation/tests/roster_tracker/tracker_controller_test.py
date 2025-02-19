import datetime

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.roster_tracker import RosterTracker

pytestmark = [pytest.mark.regression_ac_roster_tracker,
              pytest.mark.regression_ac,
              pytest.mark.ac_api_v2,
              pytest.mark.ac_api_v2_roster_tracker]

# tracker_id is project ID and this project is used with valid test data
TRACKER_ID = 6821
TODAY = (datetime.datetime.today() + datetime.timedelta(days=0)).isoformat()
NEXT_WEEK = (datetime.datetime.today() + datetime.timedelta(days=7)).isoformat()


def get_project_market(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
    }
    res_markets = api.get_tracker_markets(TRACKER_ID, payload=params)
    markets = res_markets.json_response
    return markets


@pytest.mark.ac_api_uat
def test_get_tracker_by_id_controler(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['projectId'] == TRACKER_ID


def test_get_tracker_with_not_existing_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(11111)
    res.assert_response_status(200)
    assert len(res.json_response) == 1


def test_get_tracker_with_not_no_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id()
    res.assert_response_status(500)
    assert res.json_response['message'] == "Failed to convert value of type \'java.lang.String\' to required type " \
                                           "\'long\'; nested exception is java.lang.NumberFormatException: For " \
                                           "input string: \"None\""


def test_get_get_tracker_by_id_empty_cookies():
    api = RosterTracker()
    res = api.get_trackers_by_id(TRACKER_ID)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_get_tracker_markets(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
    }
    res = api.get_tracker_markets(TRACKER_ID, payload=params)
    res.assert_response_status(200)
    assert len(res.json_response) > 0


def test_get_tracker_markets_missing_params(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "startDate": TODAY
    }
    res = api.get_tracker_markets(TRACKER_ID, payload=params)
    res.assert_response_status(500)
    assert res.json_response['message'] == "Required LocalDateTime parameter 'endDate' is not present"


@allure.issue("https://appen.atlassian.net/browse/ACE-17467", 'Bug: ACE-17467')
def test_get_productivity_metrics_by_metric_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    metric_id = res.json_response[0]['productivityMetrics'][0]['metricId']
    params = {
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
        "numberWeeks": 1
    }
    res1 = api.get_productivity_metrics_by_id(TRACKER_ID, metric_id, params)
    res1.assert_response_status(200)
    assert len(res.json_response) > 0


@allure.issue("https://appen.atlassian.net/browse/ACE-17467", 'Bug: ACE-17467')
def test_get_quality_metrics_by_metric_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    metric_id = res.json_response[0]['qualityMetrics'][0]['metricId']
    params = {
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
        "numberWeeks": 1
    }
    res1 = api.get_quality_metrics_by_id(TRACKER_ID, metric_id, params)
    res1.assert_response_status(200)
    assert len(res.json_response) > 0


@pytest.mark.ac_api_uat
def test_get_workers_for_market(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    project_markets = get_project_market(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "market": project_markets[1],
        "startDate": TODAY,
        "endDate": NEXT_WEEK

    }
    res1 = api.get_workers_of_market(TRACKER_ID, project_markets[1], payload=params)
    res1.assert_response_status(200)
    assert len(res.json_response) > 0


@pytest.mark.ac_api_uat
@allure.issue("https://appen.atlassian.net/browse/ACE-17467", 'Bug: ACE-17467')
def test_get_metrics_for_market(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    project_markets = get_project_market(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "market": project_markets[1],
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
        "numberWeeks": 1

    }
    res1 = api.get_metrics_of_market(TRACKER_ID, project_markets[1], payload=params)
    res1.assert_response_status(200)
    assert len(res.json_response) > 0


@allure.issue("https://appen.atlassian.net/browse/ACE-17467", 'Bug: ACE-17467')
def test_export_workers(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    project_markets = get_project_market(ac_api_cookie)
    payload = {
        "trackerId": TRACKER_ID,
        "market": project_markets[1],
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
        "page": 1,
        "pageSize": 10,
        "sortMetricType": "PRODUCTIVITY",
        "sortDirection": "ASC"

    }
    res1 = api.post_export_workers(TRACKER_ID, project_markets[1], payload=payload)
    res1.assert_response_status(200)


@allure.issue("https://appen.atlassian.net/browse/ACE-17467", 'Bug: ACE-17467')
def test_export_all_workers(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    project_markets = get_project_market(ac_api_cookie)
    payload = {
        "trackerId": TRACKER_ID,
        "market": project_markets[1],
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
        "page": 1,
        "pageSize": 10,
        "sortMetricType": "PRODUCTIVITY",
        "sortDirection": "ASC"

    }
    res1 = api.post_export_all_workers(TRACKER_ID, project_markets[1], payload=payload)
    res1.assert_response_status(200)


@allure.issue("https://appen.atlassian.net/browse/ACE-17467", 'Bug: ACE-17467')
def test_export_all_workers_invalid_tracker_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    project_markets = get_project_market(ac_api_cookie)
    payload = {
        "trackerId": 111111,
        "market": project_markets[1],
        "startDate": TODAY,
        "endDate": NEXT_WEEK,
        "page": 1,
        "pageSize": 10,
        "sortMetricType": "PRODUCTIVITY",
        "sortDirection": "ASC"

    }
    res1 = api.post_export_all_workers(111111, project_markets[1], payload=payload)
    res1.assert_response_status(500)
    assert res1.json_response['message'] == "There are no required metrics: []"
