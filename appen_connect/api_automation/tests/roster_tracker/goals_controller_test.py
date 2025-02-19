import datetime

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.roster_tracker import RosterTracker

pytestmark = [pytest.mark.regression_ac_roster_tracker,
              pytest.mark.regression_ac,
              pytest.mark.ac_api_v2,
              pytest.mark.ac_api_v2_roster_tracker]

#  project ID and this project is used with valid test data
PROJECT_ID = 6821
TRACKER_ID = 6821



def test_get_goals_history(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(PROJECT_ID)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['projectId'] == PROJECT_ID


def test_get_goals_history_no_content(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    project_id = 111111
    res = api.get_trackers_by_id(project_id)
    res.assert_response_status(204)
    assert len(res.json_response) == 0


def test_get_goals_history_invalid_project(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    project_id = None
    res = api.get_trackers_by_id(project_id)
    res.assert_response_status(500)
    assert res.json_response['message'] == "Failed to convert value of type \'java.lang.String\' to required type \'long\'; nested exception is java.lang.NumberFormatException: For input string: \"None\""

def get_project_market(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    _startDate = (datetime.datetime.today() + datetime.timedelta(days=0)).isoformat()
    _endDate = (datetime.datetime.today() + datetime.timedelta(days=7)).isoformat()
    params = {
        "trackerId": TRACKER_ID,
        "startDate": _startDate,
        "endDate": _endDate,
    }
    res_markets = api.get_tracker_markets(TRACKER_ID, payload=params)
    markets = res_markets.json_response
    return markets

def test_get_goal_filter_values(ac_api_cookie):
        api = RosterTracker(ac_api_cookie)
        res = api.get_trackers_by_id(TRACKER_ID)

        productivity_metrics = res.json_response[0]
        metric_id = res.json_response[0]['productivityMetrics'][0]['metricId']
        print("Metric ID", metric_id)
        project_markets = get_project_market(ac_api_cookie)
        params = {
            "trackerId": TRACKER_ID,
            "market": project_markets[1],
            "startDate": "2021-02-12T00:00:00",
            "endDate": "2022-02-19T00:00:00",
            "goalFilter": "{\"metricId\": 188, \"metricDataType\": \"PRODUCTIVITY\", \"minGoalValue\": 1, \"maxGoalValue\": 30}"
        }
        res1 = api.get_workers_of_market(TRACKER_ID, project_markets[1], payload=params)
        res1.assert_response_status(200)
        assert len(res1.json_response['workers'])>0


def test_get_goal_filter_values_no_workers(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    project_markets = get_project_market(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "market": project_markets[1],
        "startDate": "2021-02-12T00:00:00",
        "endDate": "2022-02-19T00:00:00",
        "goalFilter": "{\"metricId\": 188, \"metricDataType\": \"PRODUCTIVITY\", \"minGoalValue\": 1, \"maxGoalValue\": 8}"
    }
    res1 = api.get_workers_of_market(TRACKER_ID, project_markets[1], payload=params)
    res1.assert_response_status(200)
    assert len(res1.json_response['workers']) == 0

def test_get_goal_filter_values_invlaid_metric(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    project_markets = get_project_market(ac_api_cookie)
    params = {
        "trackerId": TRACKER_ID,
        "market": project_markets[1],
        "startDate": "2021-02-12T00:00:00",
        "endDate": "2022-02-19T00:00:00",
        "goalFilter": "{\"metricId\": metric_id, \"metricDataType\": \"PRODUCTIVITY\", \"minGoalValue\": 1, \"maxGoalValue\": 70}"
    }
    res1 = api.get_workers_of_market(TRACKER_ID, "ENG-DEU", payload=params)
    res1.assert_response_status(500)




