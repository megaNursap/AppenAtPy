import pytest
import allure
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from deepdiff import DeepDiff
import time

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat, pytest.mark.rerun_test]

default_user = 'test_account'


@pytest.fixture(scope="module")
def sample_job():
    predefined_jobs = pytest.data.predefined_data.get('job_for_copying')
    job_id = predefined_jobs.get(pytest.env)
    resp = Builder(get_user_api_key(default_user)).get_json_job_status(job_id)
    assert resp.status_code == 200, f"Failed to get job status for job {job_id}" \
                                    f"Status code: {resp.status_code}" \
                                    f"Response: {resp.text}"
    job_info = resp.json_response
    # update "fair_pay_enabled"  param for 'old' jobs
    if job_info['fair_pay_enabled'] is None:
        job_info['fair_pay_enabled'] = False

    # print("---", job_info)
    return {
        "id": job_id,
        "info": job_info,
    }


exclude_diff_paths = [
    "root['message']",
    "root['options']['front_load']",
    "root['options']['include_unfinished']",
    "root['order_approved']",
    "root['copied_from']",
    "root['created_at']",
    "root['golds_count']",
    "root['id']",
    "root['judgments_count']",
    "root['options']['mail_to']",
    "root['project_number']",
    "root['secret']",
    "root['state']",
    "root['support_email']",
    "root['team_id']",
    "root['units_count']",
    "root['updated_at']",
    "root['options']['server_side_validation_enabled']",
    "root['options']['kafka_judgments_loading']",
    "root['design_verified']",
    "root['completed']",
    "root['recommended_price_per_judgment']",
    "root['estimated_time_per_judgment']"
]


@allure.parent_suite('/jobs/{job_id}/copy:get')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.uat_api
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@allure.issue("https://appen.atlassian.net/browse/ADAP-2855", "BUG on Integration ADAP-2855")
@pytest.mark.flaky(reruns=3)
def test_copy_job_no_rows(sample_job):
    user = get_user(default_user, env=pytest.env)
    copy_resp = Builder(user['api_key']).copy_job(sample_job['id'])
    copy_resp.assert_response_status(200)
    copy_info = copy_resp.json_response
    diff = DeepDiff(
        sample_job['info'],
        copy_info,
        exclude_paths=exclude_diff_paths
    )
    assert not diff, f"Unexpected diff in copied job: {diff}"
    assert copy_info.get('state') == 'unordered'
    assert copy_info.get('copied_from') == sample_job['id']
    assert copy_info.get('options').get('mail_to') == user['email']
    assert copy_info.get('team_id') == user['teams'][0]['id']
    assert copy_info.get('support_email') == user['email']
    assert copy_info.get('message') == {'success': 'Job successfully copied.'}
    assert copy_info['judgments_count'] == 0
    assert copy_info.get('golds_count') == 0
    assert copy_info.get('units_count') == 0


@allure.parent_suite('/jobs/{job_id}/copy:get')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.workflow_temp
@pytest.mark.uat_api
@pytest.mark.builder
@allure.issue("https://appen.atlassian.net/browse/ADAP-2855", "BUG on Integration ADAP-2855")
@pytest.mark.flaky(reruns=3)
def test_copy_job_all_rows(sample_job):
    user = get_user(default_user, env=pytest.env)
    builder = Builder(user['api_key'])
    copy_resp = builder.copy_job(sample_job['id'], "all_units")
    copy_resp.assert_response_status(200)
    copy_info = copy_resp.json_response
    diff = DeepDiff(
        sample_job['info'],
        copy_info,
        exclude_paths=exclude_diff_paths
    )
    print(diff)
    assert not diff, f"Unexpected diff in copied job: {diff}"
    assert copy_info.get('state') == 'unordered'
    assert copy_info.get('copied_from') == sample_job['id']
    assert copy_info.get('options').get('mail_to') == user['email']
    assert copy_info.get('team_id') == user['teams'][0]['id']
    assert copy_info.get('support_email') == user['email']
    assert copy_info.get('message') == {'notice': 'Job copied. Units will be copied over shortly.'}
    time.sleep(10)
    copy_info = builder.get_json_job_status(copy_info['id']).json_response
    assert copy_info['judgments_count'] == 0
    assert copy_info.get('golds_count') == sample_job['info']['golds_count']
    assert copy_info.get('units_count') == sample_job['info']['units_count']


@allure.parent_suite('/jobs/{job_id}/copy:get')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.uat_api
@pytest.mark.flaky(reruns=3)
# @allure.issue("https://appen.atlassian.net/browse/ADAP-3237", "Bug Integration ADAP-3237")
def test_copy_job_unfinalized_units(sample_job):
    user = get_user(default_user, env=pytest.env)
    builder = Builder(user['api_key'])
    copy_resp = builder.copy_job(sample_job['id'], "only_new_and_judgable")
    copy_resp.assert_response_status(200)
    copy_info = copy_resp.json_response
    diff = DeepDiff(
        sample_job['info'],
        copy_info,
        exclude_paths=exclude_diff_paths
    )
    assert not diff, f"Unexpected diff in copied job: {diff}"
    assert copy_info.get('state') == 'unordered'
    assert copy_info.get('copied_from') == sample_job['id']
    assert copy_info.get('options').get('mail_to') == user['email']
    assert copy_info.get('team_id') == user['teams'][0]['id']
    assert copy_info.get('support_email') == user['email']
    assert copy_info.get('message') == {'notice': 'Job copied. New and judgable units will be copied over shortly.'}
    time.sleep(5)
    copy_info = builder.get_json_job_status(copy_info['id']).json_response
    assert copy_info['judgments_count'] == 0
    assert copy_info.get('golds_count') == 0


@allure.parent_suite('/jobs/{job_id}/copy:get')
@allure.severity(allure.severity_level.NORMAL)
# @allure.issue("https://appen.atlassian.net/browse/ADAP-3237", "Bug Integration ADAP-3237")
@pytest.mark.uat_api
@pytest.mark.flaky(reruns=3)
def test_copy_job_unfinalized_and_gold_units(sample_job):
    user = get_user(default_user, env=pytest.env)
    builder = Builder(user['api_key'])
    copy_resp = builder.copy_job(sample_job['id'], "only_new_and_judgable=true&gold")
    copy_resp.assert_response_status(200)
    copy_info = copy_resp.json_response
    diff = DeepDiff(
        sample_job['info'],
        copy_info,
        exclude_paths=exclude_diff_paths
    )

    print("sample", sample_job['info'])
    print("copy", copy_info)
    assert not diff, f"Unexpected diff in copied job: {diff}"
    assert copy_info.get('state') == 'unordered'
    assert copy_info.get('copied_from') == sample_job['id']
    assert copy_info.get('options').get('mail_to') == user['email']
    assert copy_info.get('team_id') == user['teams'][0]['id']
    assert copy_info.get('support_email') == user['email']
    # TODO: this messages doesn't match the operation
    assert copy_info.get('message') == {'notice': 'Job copied. Test questions will be copied over shortly.'}
    time.sleep(7)
    copy_info = builder.get_json_job_status(copy_info['id']).json_response
    assert copy_info['judgments_count'] == 0
    assert copy_info.get('golds_count') == sample_job['info']['golds_count']


@allure.parent_suite('/jobs/{job_id}/copy:get')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.uat_api
@pytest.mark.flaky(reruns=3)
def test_copy_job_test_questions_only(sample_job):
    user = get_user(default_user, env=pytest.env)
    builder = Builder(user['api_key'])
    copy_resp = builder.copy_job(sample_job['id'], "gold")
    copy_resp.assert_response_status(200)
    copy_info = copy_resp.json_response
    diff = DeepDiff(
        sample_job['info'],
        copy_info,
        exclude_paths=exclude_diff_paths
    )
    assert not diff, f"Unexpected diff in copied job: {diff}"
    assert copy_info.get('state') == 'unordered'
    assert copy_info.get('copied_from') == sample_job['id']
    assert copy_info.get('options').get('mail_to') == user['email']
    assert copy_info.get('team_id') == user['teams'][0]['id']
    assert copy_info.get('support_email') == user['email']
    assert copy_info.get('message') == {'notice': 'Job copied. Test questions will be copied over shortly.'}
    time.sleep(5)
    copy_info = builder.get_json_job_status(copy_info['id']).json_response
    assert copy_info['judgments_count'] == 0
    assert copy_info.get('golds_count') == sample_job['info']['golds_count']
    assert copy_info.get('units_count') == copy_info.get('golds_count')


@allure.parent_suite('/jobs/{job_id}/copy.json:get')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.cross_team
@pytest.mark.skip_hipaa
@pytest.mark.flaky(reruns=3)
def test_copy_job_template_team_id():
    api_key = get_user_api_key('multi_team_user')

    i = random.randint(1, 2)
    team = get_user_team_id('multi_team_user', i)
    builder = Builder(api_key)

    # Creating a new job from a template -- the job id is hardcoded because it has to match the id of the template
    res = builder.copy_template_job(get_template_job_id(), get_template_id(), team)
    res.assert_response_status(200)
    assert res.json_response.get('team_id') == team
    assert res.json_response.get('copied_from') == get_template_job_id()


@allure.parent_suite('/jobs/{job_id}/copy.json:get')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.cross_team
@pytest.mark.skip_hipaa
@pytest.mark.flaky(reruns=3)
def test_copy_job_template_invalid_team_id():
    """
    :param: team_id of team that the user does not belong to
    """
    api_key = get_user_api_key('multi_team_user')

    team = get_user_team_id('multi_team_user', 0)
    builder = Builder(api_key)

    # Creating a new job from a template -- the job id is hardcoded because it has to match the job id of the template
    res = builder.copy_template_job(get_template_job_id(), get_template_id(),  team)
    res.assert_response_status(404)


@allure.parent_suite('/jobs/{job_id}/copy.json:get')
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.cross_team
@pytest.mark.skip_hipaa
@pytest.mark.flaky(reruns=3)
def test_copy_job_template_org_admin_outside_org():
    """
    :param: team_id of team that is not in the org
    """
    api_key = get_user_api_key('org_admin')

    team = 'invalid'
    builder = Builder(api_key)

    # Creating a new job from a template -- the job id is hardcoded because it has to match the job id of the template
    res = builder.copy_template_job(get_template_job_id(), get_template_id(), team)
    res.assert_response_status(404)


