import random
import time

import pytest
import allure
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, get_test_data, get_user_team_id, get_data_file
from adap.settings import Config
from adap.api_automation.services_config.judgments import Judgments
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth]

users = pytest.data.users
predifined_jobs = pytest.data.predefined_data


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/judgments:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.devspace
def test_get_row_and_judgements():
    api_key = get_user_api_key('test_account')
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    job = Builder(api_key)
    job.job_id = job_id

    res = job.get_rows_and_judgements()
    res.assert_response_status(200)
    assert len(res.json_response) > 0

    for row in res.json_response.values():
        assert len(row['_ids']) > 0


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units/{unit_id}:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.devspace
def test_get_aggregated_result_for_row():
    api_key = get_user_api_key('test_account')
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    job = Builder(api_key)
    job.job_id = job_id

    res = job.get_rows_and_judgements()
    res.assert_response_status(200)

    for unit_id in res.json_response.keys():
        agg_result = job.get_agg_result_per_row(unit_id)
        agg_result.assert_response_status(200)

        num_judgements = agg_result.json_response['judgments_count']
        assert num_judgements > 0
        assert len(agg_result.json_response['results']['judgments']) == num_judgements


@allure.severity(allure.severity_level.CRITICAL)
@allure.parent_suite('/jobs/{job_id}/units/{unit_id}/judgments:get')
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.devspace
def test_get_all_judgments_per_row():
    api_key = get_user_api_key('test_account')
    job_id = predifined_jobs['job_with_judgments'][pytest.env]

    job = Builder(api_key)
    job.job_id = job_id

    res = job.get_rows_and_judgements()
    res.assert_response_status(200)

    for unit_id in res.json_response.keys():
        judgments_row = job.get_agg_result_per_row(unit_id)
        judgments_row.assert_response_status(200)

        num_judgements = judgments_row.json_response['judgments_count']

        assert num_judgements > 0
        assert len(judgments_row.json_response['results']['judgments']) == num_judgements

        for j in judgments_row.json_response['results']['judgments']:
            assert str(j['unit_id']) == unit_id


@allure.severity(allure.severity_level.CRITICAL)
def test_get_judgments_report():
    # set up - copy job, launch job and get judgments
    api_key = get_test_data('test_account', 'api_key')
    email = get_test_data('test_account', 'email')
    password = get_test_data('test_account', 'password')
    test_data = pytest.data.predefined_data['job_2K'].get(pytest.env)

    copied_job = Builder(api_key)

    copied_job_resp = copied_job.copy_job(test_data, "all_units")
    copied_job_resp.assert_response_status(200)

    job_id = copied_job_resp.json_response['id']
    copied_job.job_id = job_id
    copied_job.launch_job()
    copied_job.wait_until_status("running", max_time=60)
    time.sleep(90)

    j = Judgments(email, password, env=pytest.env, internal=True)
    job_link = generate_job_link(job_id, api_key, pytest.env)

    Config.JOB_TYPE = 'what_is_greater'
    assignment_page = j.get_assignments(internal_job_url=job_link, job_id=job_id)

    random_judge = random.randint(40, 70)
    j.contribute(assignment_page, num_assignments=random_judge)
    time.sleep(60)

    # set up - done

    json_status = copied_job.get_json_job_status()
    json_status.assert_response_status(200)

    num_judgments = json_status.json_response.get('judgments_count', 0)
    assert num_judgments > 0, "No judgments have been found for job %s" % job_id

    pages = num_judgments // 100 + 1 if num_judgments % 100 > 0 else 0

    api = Builder(api_key=api_key)
    report_judgments = []
    for page in range(1, pages+1):
        res = api.get_judgements_json_report(job=job_id, page=page)
        res.assert_response_status(200)

        _response = res.json_response
        for value in _response.values():
            assert len(value['_ids']) > 0
            report_judgments = report_judgments + value['_ids']

    assert len(report_judgments) == num_judgments


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.prod_bug
def test_get_judgments_cml_with_comments():
    """
    prod bug  https://appen.atlassian.net/browse/ADAP-844
    Builder Jobs: Ignore the comments in Job CML
    """
    # set up - copy job, launch job and get judgments
    api_key = get_test_data('test_account', 'api_key')
    email = get_test_data('test_account', 'email')
    password = get_test_data('test_account', 'password')
    data_file = get_data_file("/quiz_work_mode_switch/whatisgreater.csv")

    new_cml = """
       <div class="html-element-wrapper">
         <p>Column1: {{column_1}}</p>
         <p>Column2: {{column_2}}</p>
         <p>marker: {{marker}}</p>
       </div>
       <cml:radios label="What is greater?" validates="required" name="what_is_greater" gold="true">
         <cml:radio label="Column1" value="col1" />
         <cml:radio label="Column2" value="col2" />
         <!--<cml:radio label="Equals" value="equals" />-->
       </cml:radios>
       <!--test-->
    """

    job = Builder(api_key)

    job.create_job_with_csv(data_file)
    job.get_json_job_status()
    updated_payload = {
        'key': api_key,
        'job': {
            'title': "Testing: Ignore the comments in Job CML ",
            'instructions': "Updated",
            'cml': new_cml,
            'project_number': 'PN000112',
            'units_per_assignment': 3
        }
    }
    job.update_job(payload=updated_payload)
    job.launch_job()
    job.wait_until_status("running", max_time=60)
    time.sleep(90)

    job_id = job.job_id

    j = Judgments(email, password, env=pytest.env, internal=True)
    job_link = generate_job_link(job_id, api_key, pytest.env)

    Config.JOB_TYPE = 'what_is_greater'
    assignment_page = j.get_assignments(internal_job_url=job_link, job_id=job_id)

    j.contribute(assignment_page, num_assignments=5)
    time.sleep(60)

    # set up - done

    json_status = job.get_json_job_status()
    json_status.assert_response_status(200)

    num_judgments = json_status.json_response.get('judgments_count', 0)
    assert num_judgments > 0, "No judgments have been found for job %s" % job_id

    pages = num_judgments // 100 + 1 if num_judgments % 100 > 0 else 0

    api = Builder(api_key=api_key)
    report_judgments = []
    for page in range(1, pages+1):
        res = api.get_judgements_json_report(job=job_id, page=page)
        res.assert_response_status(200)

        _response = res.json_response
        for value in _response.values():
            assert len(value['_ids']) > 0
            report_judgments = report_judgments + value['_ids']

    assert len(report_judgments) == num_judgments

