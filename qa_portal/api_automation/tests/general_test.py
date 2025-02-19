
import pytest

from qa_portal.api_automation.services_config.portal import Portal

pytestmark = pytest.mark.qa_portal


@pytest.mark.qa_portal
def test_healthcheck_portal():
    api = Portal()
    resp  = api.get_healthcheck()
    resp.assert_response_status(200)
    assert resp.json_response == {"status": "success"}


@pytest.mark.qa_portal
def test_env_details_portal():
    api = Portal()
    resp  = api.get_env_details()
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0


@pytest.mark.qa_portal
def test_env_details_integration_portal():
    api = Portal()
    resp = api.get_env_details(env='integration')
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0

    for service in resp.json_response:
        assert service["env"] == 'integration'
        assert service.get('branch_name', False)
        assert service.get('date', False)
        assert service.get('service', False)


@pytest.mark.qa_portal
def test_env_details_not_exist_portal():
    api = Portal()
    resp = api.get_env_details(env='test')
    resp.assert_response_status(200)
    assert resp.json_response == []

