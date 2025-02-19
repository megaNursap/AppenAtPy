from appen_connect.api_automation.services_config.ac_api import *
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_tenants, pytest.mark.ac_api]


@pytest.fixture(scope="module")
def new_project_tenant(ac_api_cookie):
    new_project_api = AC_API(ac_api_cookie)
    result = create_new_random_project(new_project_api)
    return result


@pytest.mark.ac_api_uat
def test_get_local_tenants(ac_api_cookie, new_project_tenant):
    api = AC_API(ac_api_cookie)
    res = api.get_locale_tenants(new_project_tenant['output']['id'])
    res.assert_response_status(200)
    assert res.json_response == []


def test_get_local_tenants_empty_cookie(ac_api_cookie, new_project_tenant):
    api = AC_API()
    res = api.get_locale_tenants(new_project_tenant['output']['id'])
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.ac_api_uat
def test_create_locale_tenant(ac_api_cookie, new_project_tenant):
    api = AC_API(ac_api_cookie)
    project_id = new_project_tenant['output']['id']

    payload = {
        "country": "USA",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)
    assert res.json_response.get('id', False)
    assert res.json_response['country'] == payload['country']
    assert res.json_response['tenantId'] == payload['tenantId']

    new_res = api.get_locale_tenants(project_id)
    new_res.assert_response_status(200)
    assert new_res.json_response[0]['id'] == res.json_response['id']
    assert new_res.json_response[0]['country'] == payload['country']
    assert new_res.json_response[0]['tenantId'] == payload['tenantId']


def test_create_locale_tenant_empty_cookie(new_project_tenant):
    api = AC_API()
    project_id = new_project_tenant['output']['id']
    payload = {
        "country": "USA",
        "projectId": project_id,
        "tenantId": 1
    }
    res = api.create_locale_tenant(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_locale_tenants_duplicates(ac_api_cookie, new_project_tenant):
    api = AC_API(ac_api_cookie)
    project_id = new_project_tenant['output']['id']

    payload = {
        "country": "ALB",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)
    assert res.json_response.get('id', False)
    assert res.json_response['country'] == payload['country']
    assert res.json_response['tenantId'] == payload['tenantId']

    res = api.create_locale_tenant(payload)
    res.assert_response_status(400)
    assert res.json_response['code'] == "LocaleTenantAlreadyExistsForCountry"
    assert res.json_response['message'] == "A Tenant already exists for this country"


# TODO invalid payload - country id, tenant id, empty value....
# @pytest.mark.skip(reason='Bug')
def test_update_locale_tenants(ac_api_cookie, new_project_tenant):
    api = AC_API(ac_api_cookie)

    project_id = new_project_tenant['output']['id']

    _tenants = api.get_locale_tenants(project_id)
    num_tenants = len(_tenants.json_response)

    payload = {
        "country": "FRA",
        "projectId": project_id,
        "tenantId": 1
    }

    res = api.create_locale_tenant(payload)
    res.assert_response_status(201)

    _tenants = api.get_locale_tenants(project_id)
    num__new_tenants = len(_tenants.json_response)
    assert num_tenants == num__new_tenants - 1

    tenant_id = res.json_response['id']

    new_payload = {
        "country": "MNE",
        "id": tenant_id,
        "projectId": project_id,
        "tenantId": 1
    }

    update_tenant = api.update_locale_tenants(tenant_id, new_payload)
    update_tenant.assert_response_status(200)
    assert update_tenant.json_response['id'] == tenant_id
    assert update_tenant.json_response['country'] == "MNE"
    assert update_tenant.json_response['tenantId'] == 1

    _tenants = api.get_locale_tenants(project_id)
    num_new_tenants = len(_tenants.json_response)
    assert num_tenants == num_new_tenants - 1


# TODO invalid payload for updates- country id, tenant id, empty value....


def test_delete_tenant(ac_api_cookie, new_project_tenant):
    project_id = new_project_tenant['output']['id']
    api = AC_API(ac_api_cookie)
    _tenants = api.get_locale_tenants(project_id)
    num_tenants = len(_tenants.json_response)

    if num_tenants == 0:
        payload = {
            "country": "FRA",
            "projectId": project_id,
            "tenantId": 1
        }
        res = api.create_locale_tenant(payload)
        res.assert_response_status(201)
        tenant_id = res.json_response['id']
        num_tenants = 1
    else:
        tenant_id = _tenants.json_response[0]['id']

    res = api.delete_locale_tenant(tenant_id)
    res.assert_response_status(204)

    _tenants = api.get_locale_tenants(project_id)
    num_new_tenants = len(_tenants.json_response)
    assert num_new_tenants == num_tenants - 1


@pytest.mark.ac_api_uat
def test_get_project_pages(ac_api_cookie, new_project_tenant):
    project_id = new_project_tenant['output']['id']
    api = AC_API(ac_api_cookie)

    res = api.get_project_pages(project_id)
    res.assert_response_status(200)
    assert len(res.json_response) > 0
#     TODO expand tests for project pages


def test_get_get_project_pages_no_cookies(new_project_tenant):
    project_id = new_project_tenant['output']['id']
    ac_api = AC_API()
    res = ac_api.get_project_pages(project_id)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


