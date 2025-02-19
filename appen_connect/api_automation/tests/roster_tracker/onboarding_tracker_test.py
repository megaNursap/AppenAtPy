import datetime

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.roster_tracker import  RosterTracker

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
def test_get_tracker_by_id_onboarding(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(TRACKER_ID)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response[0]['projectId'] == TRACKER_ID


def test_get_tracker_with_not_existing_id_onboarding(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_trackers_by_id(111111)
    res.assert_response_status(204)
    assert len(res.json_response) == 0

@pytest.mark.ac_api_uat
def test_get_onboarding_tracker_by_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_onboarding_trackers_by_id(TRACKER_ID)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
    assert res.json_response['totalWorkers'] >= 0
    print("MARKET", res.json_response['markets'][0]['market'])

@pytest.mark.ac_api_uat
def test_get_onboarding_tracker_no_id(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_onboarding_trackers_by_id()
    res.assert_response_status(500)
    assert res.json_response['message'] == 'Failed to convert value of type \'java.lang.String\' to required type \'java.lang.Long\'; nested exception is java.lang.NumberFormatException: For input string: "None"'


@pytest.mark.ac_api_uat
def test_post_onboarding_tracker_per_market(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_onboarding_trackers_by_id(TRACKER_ID)
    res.assert_response_status(200)
    startDate = "1900-01-01T00:00:00.000Z"
    markets = res.json_response['markets']
    for i in markets:
        for keys in i:
            if i['currentValue']:
                market = i['market']

    params = {
        "startDate": startDate,
        "endDate": TODAY,
        "workersType": "ONBOARDING"

    }
    res_workers = api.get_workers_of_market(TRACKER_ID, market=market, payload=params)
    workers = res_workers.json_response['workers']
    payload = {
            "workersIds": [
                workers[0]['workerAcId']
            ],
            "startDate": "1900-01-01T00:00:00.000Z",
            "endDate": TODAY
    }

    res_post = api.post_project_onboarding_metrics(payload=payload, project_id=TRACKER_ID, market_id=market)
    res_post.assert_response_status(200)
    assert len(res_post.json_response) == 0


@pytest.mark.ac_api_uat
def test_post_onboarding_tracker_per_market_invalid(ac_api_cookie):
    api = RosterTracker(ac_api_cookie)
    res = api.get_onboarding_trackers_by_id(TRACKER_ID)
    res.assert_response_status(200)
    startDate = "1900-01-01T00:00:00.000Z"
    markets = res.json_response['markets']
    for i in markets:
        for keys in i:
            if i['currentValue']:
                market = i['market']

    params = {
        "startDate": startDate,
        "endDate": TODAY,
        "workersType": "ONBOARDING"

    }
    res_workers = api.get_workers_of_market(TRACKER_ID, market='ENG-USA', payload=params)
    workers = res_workers.json_response['workers']
    payload = {
            "workersIds": [ 23332112111232 ],
            "startDate": "1900-01-01T00:00:00.000Z",
            "endDate": TODAY
    }

    res_post = api.post_project_onboarding_metrics(payload=payload, project_id=TRACKER_ID, market_id='ENG-SSS')
    #TODO work with developers to return 4XX error to let the users know invlaid market
    res_post.assert_response_status(200)
    assert len(res_post.json_response) == 0