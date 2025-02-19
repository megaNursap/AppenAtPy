import os
import pytest
import allure
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import unzip_file, get_user_api_key, file_exists
from adap.api_automation.utils.helpers import retry

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]

users = pytest.data.users
predifined_jobs = pytest.data.predefined_data


# TODO: QED-1569 should be done for FED support
@allure.parent_suite('/jobs/{job_id}/regenerate:post,/jobs/{job_id}.csv')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.bug_smoke
@pytest.mark.uat_api
@pytest.mark.prod_smoke_api
@pytest.mark.flaky(reruns=3)
@pytest.mark.parametrize('report_type, value, file_format',
                         [("source", "source", "/source%s.csv"),
                          ("gold report", "gold_report", "/job_%s_gold_report.csv"),
                          ("full report", "full", "/f%s.csv"),
                          ("contributor report", "workset", "/workset%s.csv"),
                          ("aggregated report", "aggregated", "/a%s.csv"),
                          ("json report", "json", "/job_%s.json")])
def test_generate_report(tmpdir, report_type, value, file_format):
    api_key = get_user_api_key('test_account')
    payload = {
        'type': '%s' % value,
    }

    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    job = Builder(api_key)
    job.job_id = job_id

    # regenerate report
    resp0 = job.regenerate_report(payload=payload)
    resp0.assert_response_status(200)

    def get_report_zip():
        resp = job.generate_report(payload=payload)
        assert resp.status_code == 200
        with open(tmpdir + '/%s.zip' % value, 'wb') as f:
            f.write(resp.content)

    retry(get_report_zip, max_wait=300)

    # handle the zip file
    unzip_file(tmpdir + '/%s.zip' % value)

    csv_name = tmpdir + file_format % str(job.job_id)
    print(csv_name)

    # clean up the files
    if file_exists(csv_name):
        os.remove(csv_name)
        os.remove(tmpdir + '/%s.zip' % value)
        print('Files have been deleted')
    else:
        print("Files don't exist!!")
        assert False, "Files don't exist!!"
