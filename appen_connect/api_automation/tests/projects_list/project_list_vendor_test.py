from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.ac_project_service import ProjectServiceAPI
from appen_connect.api_automation.services_config.ac_sme import SME
from appen_connect.api_automation.services_config.identity_service import IdentityService
import requests
from bs4 import BeautifulSoup

pytestmark = [pytest.mark.regression_ac_project_list, pytest.mark.regression_ac, pytest.mark.ac_api_project_service_list, pytest.mark.ac_api]


USER = get_test_data("test_active_vendor_account", "email")
PASSWORD = get_test_data("test_active_vendor_account", "password")
ID = get_test_data("test_active_vendor_account", "id")

expected_resp_fields = [
    'projectId',
    'projectName',
    'projectAlias',
    'projectDescription',
    'workType',
    'rate',
    'taskWorkload',
    'category',
    'rankScore',
    'suggested',
    'applied',
    'myProject'
]


def get_token(user_name, user_password):
    identity_service = IdentityService(pytest.env)
    CLIENT_SECRET = get_test_data('keycloak', 'client_secret')
    resp = identity_service.get_token(
        username=user_name,
        password=user_password,
        token=CLIENT_SECRET
    )
    resp.assert_response_status(200)
    return resp.json_response['access_token']


def get_projects_from_ui(app, user=None, password=None):
    app.ac_user.login_as(user_name=user, password=password)
    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}

    form_headers = {
        'Accept': '*/*',
        'Content-Type': 'text/html;charset=UTF-8',
        "Cache-Control": "no-cache"
    }
    url = "https://connect-stage.integration.cf3.us/qrp/core/vendors/projects"

    qualified_projects_ui = requests.get(url, headers=form_headers, cookies=flat_cookie_dict)
    soup2 = BeautifulSoup(qualified_projects_ui.text, 'html.parser')
    qualified_projects = [_.attrs['data-content-name'] for _ in soup2.find_all("td", {"data-content-name": True})]

    projects_ui = requests.post(url, headers=form_headers, params={"projectQualificationFilter": 'ALL',
                                                                   "posted": 'true'}, allow_redirects=True,
                                cookies=flat_cookie_dict)
    soup = BeautifulSoup(projects_ui.text, 'html.parser')
    all_projects = []
    my_projects = []
    for _ in soup.find_all("td", {"data-content-name": True}):
        project_id = _.attrs['data-content-name']
        all_projects.append(project_id)
        if _.find_all("a", {"class": "single-click"}): my_projects.append(project_id)

    not_qualified_projects_ui = requests.post(url, headers=form_headers,
                                              params={"projectQualificationFilter": 'NOT_QUALIFIED',
                                                      "posted": 'true'}, allow_redirects=True, cookies=flat_cookie_dict)
    soup = BeautifulSoup(not_qualified_projects_ui.text, 'html.parser')
    not_qualified_projects = [_.attrs['data-content-name'] for _ in soup.find_all("td", {"data-content-name": True})]

    # sme_api = SME()
    # payload = {
    #     "workerId": ID,
    #     "useCase": "allWorkers",
    #     "maxReturnCount": 2000,
    #     "hireGapThreshold": 0.01
    # }
    # res = sme_api.find_projects(payload)
    # suggested_projects = [_['projectId'] for _ in res.json_response['projects']]

    return {"all_projects": all_projects,
            "qualified_projects": qualified_projects,
            "not_qualified_projects": not_qualified_projects,
            "my_projects": my_projects
            # "suggested_projects":suggested_projects
            }


@pytest.fixture(scope="module")
def valid_token():
    return get_token(USER, PASSWORD)


def test_get_vendor_project_invalid_token():
    #  https://appen.atlassian.net/browse/ACE-6825
    _token = 'JhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGVU56a0FVYXk0MVd1VUtpQmtUUkZ1NjhaN1J2aFNOX3EtMG1wVGF2cnY4In0.eyJleHAiOjE2MDc3MDc5NjMsImlhdCI6MTYwNzcwNzY2MywianRpIjoiZGQyOWE5Y2EtM2EyNi00MGFhLWJiYmEtNjYzMmE2MDE4NDI5IiwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS1zdGFnZS5hcHBlbi5jb20vYXV0aC9yZWFsbXMvUVJQIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImY6MTNkMWVhM2EtY2MxZi00ZDQ1LWEzNTEtNDFhNjcxYjhlYWNhOjEyOTQ4NzciLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhcHBlbi1jb25uZWN0Iiwic2Vzc2lvbl9zdGF0ZSI6IjU0NTIzZjQ4LTdkYjctNDUzMS04NDU4LTU2YjJhY2M0NDJiNCIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFwcGVuLWNvbm5lY3QiOnsicm9sZXMiOlsiQVBQX1VTRVIiXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJNYXJpbmEgU2VueXV0aW5hIiwicHJlZmVycmVkX3VzZXJuYW1lIjoibXNlbnl1dGluYUBhcHBlbi5jb20iLCJnaXZlbl9uYW1lIjoiTWFyaW5hIiwiZmFtaWx5X25hbWUiOiJTZW55dXRpbmEiLCJlbWFpbCI6Im1zZW55dXRpbmFAYXBwZW4uY29tIn0.V41Qve3KyJnRT-_qPuvET_0c-s0P0arjvJXmHYhsQc8Odr_bJ1kHADNR4al7RZhYC9yq6rNCZRXKC_N0_64nW1Lven7IOVCbYqNtWfChxorfBT6TPmA0ZcM4zjLFlECHwQjEyWLscsL5gfXKMyrW2MbTYIcFXAhhZSkY5n4-NExZXlg02Bhde9RVBsCLu_tJPafPv51Gkwx2jYKpRU0romd3a3Wkz_KeGBYrA1JLKC3HuhwU-1fEtQvgnxsS324Tl8QodpYFbTonSOQN_6VqoQKnb_Em1cbBV1YCiDCXNI08kNxZ9EVRTUNr__kKl7vFCk1DHuW7ZHpxzhamUwzRog '
    api = ProjectServiceAPI(token=_token)

    res = api.get_vendor_project_all(ID)
    res.assert_response_status(401)


def test_get_vendor_project_empty_token():
    #  https://appen.atlassian.net/browse/ACE-6825
    api = ProjectServiceAPI(token="")

    res = api.get_vendor_project_all(ID, allow_redirects=False)
    res.assert_response_status(302)


@pytest.mark.parametrize('vendor_id, expected_status, error_msg',
                         [('9999999999', 500, "403 FORBIDDEN"),
                          ('one', 500, 'Failed to convert value of type \'java.lang.String\' to required type \'java.lang.Long\'; nested exception is java.lang.NumberFormatException: For input string: \"one\"'),
                          ('', 404, 'Not Found'),
                          ('!!!!', 500, 'Failed to convert value of type \'java.lang.String\' to required type \'java.lang.Long\'; nested exception is java.lang.NumberFormatException: For input string: \"!!!!\"'),
                          (' ', 500, "Required URI template variable 'userId' for method parameter type Long is present but converted to null")])
def test_project_list_invalid_vendor(valid_token, vendor_id, expected_status, error_msg):
    api = ProjectServiceAPI(valid_token)

    res = api.get_vendor_project_all(vendor_id)
    res.assert_response_status(expected_status)

    if res.json_response.get('message'):
        assert res.json_response['message'] == error_msg
    else:
       assert res.json_response['error'] == error_msg


@pytest.mark.ac_api_uat
def test_vendor_project_valid(valid_token, app):
    api = ProjectServiceAPI(valid_token)

    res = api.get_vendor_project_all(ID)
    res.assert_response_status(200)

    assert len(res.json_response['projects']) > 0

    for _field_name in expected_resp_fields:
        assert _field_name in res.json_response['projects'][0], res.json_response


# @pytest.mark.skip
# # TODO update this test
# def test_vendor_project_type(valid_token, app):
#     api = ProjectServiceAPI(valid_token)
#
#     res = api.get_vendor_project_all(ID)
#     res.assert_response_status(200)
#
#     projects_list = get_projects_from_ui(app, user=USER, password=PASSWORD)
#
#     for _project in res.json_response['projects']:
#         _project_id = str(_project['projectId'])
#
#         if _project['applied']:
#             assert _project_id in projects_list['my_projects']
#
#         if _project['myProject']:
#             assert _project_id in projects_list['qualified_projects']
#
#         # if _project['suggested']:
#         #     assert _project_id in projects_list['suggested_projects']
#
#         assert _project_id in projects_list['all_projects']


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_projects_detail(ac_api_cookie_no_customer, valid_token):
    api = ProjectServiceAPI(valid_token)

    res = api.get_vendor_project_all(ID)
    res.assert_response_status(200)
    assert len(res.json_response['projects']) > 0

    project_api = AC_API(ac_api_cookie_no_customer)
    for _project in res.json_response['projects']:
        resp_project = project_api.get_project_by_id(_project['projectId'])
        resp_project.assert_response_status(200)
        project_info = resp_project.json_response
        assert _project['projectId'] == project_info['id']
        assert _project['projectName'] == project_info['name']
        assert _project['projectAlias'] == project_info['alias']
        assert _project['projectDescription'] == project_info['description']
        assert _project['workType'] == project_info['workType']
        assert _project['taskWorkload'] == project_info['taskVolume']
