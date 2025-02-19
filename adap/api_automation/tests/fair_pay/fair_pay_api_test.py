import pytest

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key


pytestmark = pytest.mark.regression_fair_pay_v2


URL = f"https://api.{pytest.env}.cf3.us"
MAX_JUDGMENTS = 50


@pytest.fixture(autouse=True)
def fair_pay_job():
    """
    Fixture copies job
    """

    api_key = get_user_api_key("fair_pay2_account")

    predefined_jobs = pytest.data.predefined_data.get("fair_pay_job_for_copying")
    job_id = predefined_jobs.get(pytest.env)
    resp = Builder(api_key).get_json_job_status(job_id)
    assert resp.status_code == 200, (
        f"Failed to get job status for job {job_id}"
        f"Status code: {resp.status_code}"
        f"Response: {resp.text}"
    )

    builder = Builder(api_key, custom_url=URL)
    copy_job = builder.copy_job(job_id, "all_units")
    copy_job.assert_response_status(200)
    copy_job_id = copy_job.json_response.get("id")

    return {"job_id": copy_job_id, "builder": builder}


@pytest.mark.regression_fair_pay_v2
def test_change_max_judgments_per_ip(fair_pay_job):
    """
    Checks that 'max_judgments_per_ip' changed
    """

    max_judgments_per_ip_1 = fair_pay_job['builder'].get_json_job_status().json_response.get("max_judgments_per_ip")
    assert not max_judgments_per_ip_1

    max_judgments_param = {'job[max_judgments_per_ip]': MAX_JUDGMENTS}
    fair_pay_job['builder'].update_job_settings(max_judgments_param)
    max_judgments_per_ip_2 = fair_pay_job['builder'].get_json_job_status().json_response.get("max_judgments_per_ip")
    assert max_judgments_per_ip_2 == MAX_JUDGMENTS
    assert not max_judgments_per_ip_1 == max_judgments_per_ip_2
