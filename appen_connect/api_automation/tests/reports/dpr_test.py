from appen_connect.api_automation.services_config.ac_api_v3 import *

from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_reports, pytest.mark.regression_ac, pytest.mark.ac_api_v3, pytest.mark.ac_api_v3_dpr, pytest.mark.ac_api]


# list all reports
@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_get_all_reports(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = None
    res = api.get_all_reports(payload)
    res.assert_response_status(200)
    assert len(res.json_response) > 0


# list only first page of DPRs
@pytest.mark.ac_api_uat
def test_get_reports_by_pages(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = {"page": 0,
               "size": 10}
    res = api.get_all_reports(payload)
    res.assert_response_status(200)
    assert len(res.json_response) == 10


# Request a invalid DPR
def test_post_reports_request_invalid_dpr(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = {"reportTypeId":"1","startDate": "2020-07-14T16:20:24.030Z", "endDate": "2020-07-14T16:20:24.030Z",
               "programId": "0",
               "programName":"string",
               "projects": ["string"], "projectIds": [0],
               "user": {"id": 0, "firstName": "string", "lastName": "string", "email": "string"}}
    res = api.post_reports_request_dpr_falcon_jobs(payload=payload)
    res.assert_response_status(200)
    assert len(res.json_response) > 0


# Request a valid DPR
@pytest.mark.ac_api_uat
def test_post_reports_request_dpr_falcon_jobs(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = {"reportTypeId":"1","startDate": "2020-08-30T03:00:00.000Z", "endDate":  "2020-09-05T03:00:00.000Z",
               "programName": "Jobs",
               "programId":"1",
               "projects": ["Jobs Post Classification", "Taxonomy Title Precision"],
               "projectIds": ["444", "547"],
               "user": {"id": 1295094, "firstName": "Fatima", "lastName": "Michalah", "fullName": "Fatima Michalah", "email": "fmichalach@appen.com"}}

    res = api.post_reports_request_dpr_falcon_jobs(payload=payload)
    res.assert_response_status(200)
    dpr_id = res.json_response["id"]
    assert len(res.json_response) > 1

    # make new request to find Report generated
    payload = {"page": 0,
               "size": 10}
    res = api.get_all_reports(payload)
    res.assert_response_status(200)
    assert res.json_response[0]['id'] == dpr_id



#updated the verification message to verify the number of results are greater than 47,
# as user can edit and create new templates now.
@pytest.mark.ac_api_uat
def test_get_programs(ac_api_cookie):
    api = AC_API_V3(ac_api_cookie)
    payload = {'clientId': '1'}
    res = api.get_all_programs(payload)
    res.assert_response_status(200)
    assert len(res.json_response) >= 47
    for i in range (1,len(res.json_response)):
        assert (res.json_response[i]['clientId']) == 1


def test_get_programs_no_cookies():
    api = AC_API_V3()
    payload = None
    res = api.get_all_programs(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}

