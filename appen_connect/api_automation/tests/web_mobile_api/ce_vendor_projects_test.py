import pytest

from adap.api_automation.utils.data_util import  get_test_data
from appen_connect.api_automation.services_config.ce_mobile import CE_MOBILE_API
from appen_connect.api_automation.services_config.identity_service import IdentityService

pytestmark = [pytest.mark.regression_ac_web_mobile, pytest.mark.regression_ac_web_mobile_api]


def get_valid_token(username, password):
    identity_service = IdentityService(pytest.env)
    client_secret = get_test_data('keycloak', 'client_secret')
    res_token = identity_service.get_token(
        username=username,
        password=password,
        token=client_secret
    )

    return res_token.json_response['access_token']


def test_ce_mobile_vendor_list_no_token():
    api = CE_MOBILE_API()

    vendor_id = get_test_data('ce_vendor_mobile', 'id')
    res = api.get_all_vendor_projects(vendor_id=vendor_id)

    assert res.status_code == 401
    # assert res.json_response['error'] == 'Unauthorized'


def test_ce_mobile_vendor_list_expired_token():
    expired_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJBbWtOeF9YbWFMeTJqZHAzVVVUbjY1SVN2UGhNd2kxM2' \
                    'dnVVgxN29DTmlrIn0.eyJleHAiOjE2ODczNzI1ODYsImlhdCI6MTY4NzM3MTk4NiwianRpIjoiMjJiNjU5ZWYtMGZiYy00' \
                    'OWZhLWIwZWEtZjQ5OWY3ZTg5YjU5IiwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS1zdGFnZS5pbnRlZ3JhdGlvbi5jZjMud' \
                    'XMvYXV0aC9yZWFsbXMvUVJQIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjBkZTcwNjYwLTI1NmUtNGZkNS1iYTQxLTg4OWE' \
                    '5ZmU5Mzg2YiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImFwcGVuLWNvbm5lY3QiLCJzZXNzaW9uX3N0YXRlIjoiYjBjNWJhM' \
                    'DgtMWNhYi00OGY1LTk1ODktYzNmZWMxZmU5NDRhIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJST' \
                    '0xFX0VYUFJFU1NfUEVORElORyIsIlJPTEVfVVNFUiIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX' \
                    '0sInJlc291cmNlX2FjY2VzcyI6eyJhcHBlbi1jb25uZWN0Ijp7InJvbGVzIjpbIkFQUF9VU0VSIl19LCJhY2NvdW50Ij' \
                    'p7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJ' \
                    'zY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiYjBjNWJhMDgtMWNhYi00OGY1LTk1ODktYzNmZWMxZmU5ND' \
                    'RhIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJleiBleiIsInByZWZlcnJlZF91c2VybmFtZSI6ImludGVnc' \
                    'mF0aW9uK2V6QGZpZ3VyZS1laWdodC5jb20iLCJnaXZlbl9uYW1lIjoiZXoiLCJhY19pZCI6MTI5NzQ5MywiZmFtaWx5X' \
                    '25hbWUiOiJleiIsImVtYWlsIjoiaW50ZWdyYXRpb24rZXpAZmlndXJlLWVpZ2h0LmNvbSJ9.dAglg88S4tn4tO-RrI51' \
                    'LTcwzp9yBPTxsxv6AnuzGDjPyultCE8KqFlFy4GOTm3J9mtMWTaLGFSd7ChEY9xUyVyF7mLouozUZBwAz4SKQ7wFhO44' \
                    '18mQh8Run54pYCGyMKTyoe2L2-y7EWsc1XRZk8dQpDeNzZQ8gCGXyVj_q3fGXW_Zlf-Fd2SEqDmR4N408nTXE-1keIb' \
                    'W9M3822jVD5uf6ad2dsvlKFOeSQ-AfbRivssUHic_zXOx659GZb5kMMD4SKKi99vuCtGDO3I4H4AlxsX2dTFNUzgEdJ38' \
                    'pO7XQO8Oj76UUivbpIakelyizKnIo7-dnh3l3NH9w2CIOw'

    api = CE_MOBILE_API(token=expired_token)

    vendor_id = get_test_data('ce_vendor_mobile', 'id')
    res = api.get_all_vendor_projects(vendor_id=vendor_id)

    assert res.status_code == 401
    # assert res.json_response['error'] == 'Unauthorized'


def test_ce_mobile_vendor_list_invalid_id():
    username = get_test_data('ce_vendor_mobile', 'email')
    password = get_test_data('ce_vendor_mobile', 'password')
    vendor_id = get_test_data('ce_vendor_mobile', 'id')

    valid_token = get_valid_token(username, password)
    api = CE_MOBILE_API(token=valid_token)

    res = api.get_all_vendor_projects(vendor_id=vendor_id)

    assert res.status_code == 200
    assert len(res.json_response['projects']) > 1

    expected_project_data = [
        "projectId",
        "projectName",
        "projectAlias",
        "projectDescription",
        "workType",
        "rate",
        "rates",
        "rateType",
        "taskWorkload",
        "category",
        "rankScore",
        "externalSystemId",
        "applicationStatus",
        "myProjectStatuses",
        "external",
        "expressProject",
        "myProjectActive",
        "myProjectAssigned",
        "myProjectFinished"
    ]
    actual_project_data = res.json_response['projects'][0].keys()
    for key in expected_project_data:
        assert key in actual_project_data



