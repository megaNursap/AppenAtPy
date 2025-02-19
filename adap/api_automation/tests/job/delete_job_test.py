import pytest
import allure
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key

users = pytest.data.users
pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/QED-4381")
@allure.parent_suite('/jobs/{job_id}:delete')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
@pytest.mark.flaky(reruns=3)
def test_delete_job():
    api_key = get_user_api_key('test_account')
    # create job
    new_job = Builder(api_key)
    new_job.create_job()

    # delete job
    resp = Builder(api_key, api_version='v2').delete_job(new_job.job_id)
    resp.assert_response_status(200)
    assert resp.json_response == {"action":"requested"}

