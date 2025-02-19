"""
E2E workflow tests with judgment submissions via APIs
"""
import pandas as pd
import pytest
import requests
import operator
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.judgments import Judgments
from adap.e2e_automation.services_config.job_api_support import (
    create_job_from_config_api, generate_job_link
)
from adap.perf_platform.test_data.jobs_data import jobs_data
from adap.api_automation.utils.data_util import get_user
from adap.api_automation.utils.helpers import retry
import time

pytestmark = [pytest.mark.uat_api,  pytest.mark.adap_wf_api]

env = pytest.env
user = get_user('test_account', env=env)
api_key = user['api_key']
job_data = jobs_data.get('what_is_greater')
data_generator = job_data['data_generator']

def create_job():
    """
    Create a job for WF (no units, no launch)
    """
    config = {
        "job": {
            "title": "QA Test - WF",
            "instructions": "<h1>Overview</h1>",
            "cml": job_data['cml'],
            "units_per_assignment": 5,
            "gold_per_assignment": 0,
            "judgments_per_unit": 1,
            "project_number": "PN000112"
        },
        "launch": False,
        "external_crowd": False,
        "user_email": user['email'],
        "user_password": user['password']
    }
    job_id = create_job_from_config_api(config, env, api_key)
    return job_id

def create_jobs(num_jobs):
    jobs = []
    for i in range(num_jobs):
        job_id = create_job()
        jobs.append(job_id)
    return jobs

def create_workflow():
    wf = Workflow(api_key)
    payload = {'name': 'WF E2E Test', 'description': 'WF E2E Test Automation'}
    wf.create_wf(payload=payload)
    return wf.wf_id

def verify_data_upload_complete(wf_id):
    resp = requests.get(f'https://workflows-service.internal.{env}.cf3.us/v1/workflows/{wf_id}/data_uploads')
    info = resp.json()[0]
    assert info.get('state') == 'completed', info

def verify_job_has_units(job_id, num_units, op=operator.eq):
    resp = Builder(api_key, env=env).get_json_job_status(job_id)
    actual_num_units = resp.json_response['units_count']
    assert op(actual_num_units, num_units), ''\
        f"Job {job_id}, expected {num_units} units, got {actual_num_units}"\
        f"\nComparison operator: {op}"

def verify_job_has_ordered_units(job_id, num_units, op=operator.eq):
    resp = Builder(api_key, env=env).get_job_status(job_id)
    actual_num_ordered_units = resp.json_response['ordered_units']
    assert op(actual_num_ordered_units, num_units), ''\
        f"Job {job_id}, expected {num_units} units ordered, got {actual_num_ordered_units}"\
        f"\nComparison operator: {op}"

def verify_job_has_needed_judgments(job_id, num_units, op=operator.eq):
    resp = Builder(api_key, env=env).get_job_status(job_id)
    actual_num_needed_judgments = resp.json_response['needed_judgments']
    assert op(actual_num_needed_judgments, num_units), ''\
        f"Job {job_id}, expected {num_units} judgments to be ordered, got {actual_num_needed_judgments}"\
        f"\nComparison operator: {op}"

def submit_judgments(job_id):
    j = Judgments(
        worker_email=user['email'],
        worker_password=user['password'],
        env=env,
        internal=True
    )
    resp = j.get_assignments(
        job_id=job_id,
        internal_job_url=generate_job_link(job_id, api_key, env)
    )
    j.contribute(resp)

@pytest.mark.workflow_e2e
def test_e2e_wf_with_all_filter_rule():
    """
    Create a WF with 2 jobs and route ALL units rule.
    Launch WF, work on the jobs to verify finalized units are routed as expected.
    Note: this test takes ~3 minutes
    """
    job1 = create_job()
    job2 = create_job()
    wf_id = create_workflow()
    wf_service = Workflow(api_key)
    step1, step2 = wf_service.create_job_step([job1, job2], wf_id)
    route_resp = wf_service.create_route(step1['step_id'], step2['step_id'], wf_id)
    assert route_resp.status_code == 201, 'failed to create a route'
    route_id = route_resp.json_response['id']
    payload = {
        "filter_rule": {
            "rule_connector": "all"
        }
    }
    resp = wf_service.create_filter_rule(step1['step_id'], route_id, payload, wf_id)
    assert resp.status_code == 201, 'failed to create a filter rule'
    # upload data
    units_filepath = data_generator(25, filename='/tmp/units.csv')
    wf_service.upload_data(units_filepath, wf_id=wf_id)
    retry(verify_data_upload_complete, wf_id=wf_id)
    # launch workflow
    resp = wf_service.launch(num_rows=25, wf_id=wf_id)
    assert resp.status_code == 202, 'failed to launch a workflow'
    retry(verify_job_has_units, job_id=job1, num_units=25)
    retry(verify_job_has_ordered_units, job_id=job1, num_units=25)
    retry(verify_job_has_needed_judgments, job_id=job1, num_units=25)
    Builder(api_key, env=env, job_id=job1).wait_until_status2('running')
    # work on job1
    submit_judgments(job1)
    # verify job2 has at least 20 units (this is a flaky one)
    retry(
        verify_job_has_units,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=20,
        op=operator.ge
    )
    retry(
        verify_job_has_ordered_units,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=20,
        op=operator.ge
    )
    retry(
        verify_job_has_needed_judgments,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=20,
        op=operator.ge
    )
    Builder(api_key, env=env, job_id=job2).wait_until_status2('running')
    # work on job2 (mainly to ensure that units get launched)
    submit_judgments(job2)


@pytest.mark.workflow_e2e
def test_e2e_wf_with_rnd_els_filter_rules():
    """
    Create a WF with 3 steps:
    Step1 -> Step2 (20% random sampling) & Step3 (Else route)
    Step2 -> Step3 (Merge)
    Launch WF, work on the jobs to verify finalized units are routed as expected.
    Note: this test takes ~12 minutes
    """
    # create jobs
    jobs = create_jobs(num_jobs=3)
    job1, job2, job3 = jobs
    # create workflow
    wf_id = create_workflow()
    wf_service = Workflow(api_key)
    # create wf steps
    steps = wf_service.create_job_step(jobs, wf_id)
    step1, step2, step3 = [i['step_id'] for i in steps]
    # create wf routes
    route_1_2_resp = wf_service.create_route(step1, step2, wf_id)
    route_1_3_resp = wf_service.create_route(step1, step3, wf_id)
    route_2_3_resp = wf_service.create_route(step2, step3, wf_id)
    for resp in [route_1_2_resp, route_1_3_resp, route_2_3_resp]:
        assert resp.status_code == 201, ''\
            f'failed to create a route: {resp.text}'
    route_1_2 = route_1_2_resp.json_response['id']
    route_1_3 = route_1_3_resp.json_response['id']
    route_2_3 = route_2_3_resp.json_response['id']
    # craete wf filter rules
    # create rnd rule
    rnd_payload = {
        "filter_rule": {
            "comparison_value": 20,
            "rule_connector": "rnd"
        }
    }
    res_rnd = wf_service.create_filter_rule(step1, route_1_2, rnd_payload, wf_id)
    assert res_rnd.status_code == 201, ''\
        f'failed to create rnd filter rule: {res_rnd.text}'
    # create els rule
    els_payload = {
        "filter_rule": {
            "rule_connector": "els"
        }
    }
    res_els = wf_service.create_filter_rule(step1, route_1_3, els_payload, wf_id)
    assert res_els.status_code == 201, ''\
        f'failed to create els filter rule: {res_els.text}'
    # create all rule (merge step2 -> step3)
    all_payload = {
        "filter_rule": {
            "rule_connector": "all"
        }
    }
    res_all = wf_service.create_filter_rule(step2, route_2_3, all_payload, wf_id)
    assert res_all.status_code == 201, ''\
        f'failed to create all filter rule: {res_all.text}'
    # upload data
    units_filepath = data_generator(50, filename='/tmp/units.csv')
    wf_service.upload_data(units_filepath, wf_id=wf_id)
    retry(verify_data_upload_complete, wf_id=wf_id)
    # launch workflow
    resp = wf_service.launch(num_rows=50, wf_id=wf_id)
    assert resp.status_code == 202, 'failed to launch a workflow'
    retry(verify_job_has_units, job_id=job1, num_units=50)
    retry(verify_job_has_ordered_units, job_id=job1, num_units=50)
    retry(verify_job_has_needed_judgments, job_id=job1, num_units=50)
    Builder(api_key, env=env, job_id=job1).wait_until_status2('running')
    # work on job1
    submit_judgments(job1)
    time.sleep(60)
    # verify job2 has at least 5 units and no more than 10 (this is a flaky one)
    retry(
        verify_job_has_units,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=5,
        op=operator.ge
    )
    retry(
        verify_job_has_units,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=10,
        op=operator.le
    )
    # verify job3 has at least 30 units and no more than 40 (this is a flaky one)
    retry(
        verify_job_has_units,
        max_wait=180,
        interval=15,
        job_id=job3,
        num_units=30,
        op=operator.ge
    )
    retry(
        verify_job_has_units,
        max_wait=180,
        interval=15,
        job_id=job3,
        num_units=40,
        op=operator.le
    )
    # work on job2
    Builder(api_key, env=env, job_id=job2).wait_until_status2('running')
    retry(
        verify_job_has_needed_judgments,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=5,
        op=operator.ge
    )
    submit_judgments(job2)
    time.sleep(60)
    # verify job3 has at least 45 units
    retry(
        verify_job_has_units,
        max_wait=180,
        interval=15,
        job_id=job3,
        num_units=45,
        op=operator.ge
    )
    Builder(api_key, env=env, job_id=job3).wait_until_status2('running')
    # give it a minute to autolaunch units from previous step
    time.sleep(60)
    # check job3 needs judgments
    retry(
        verify_job_has_needed_judgments,
        max_wait=180,
        interval=15,
        job_id=job3,
        num_units=45,
        op=operator.ge
    )
    # work on job3
    submit_judgments(job3)
    time.sleep(60)
    units_resp = Builder(api_key, env=env).get_rows_and_judgements(job3)
    units = units_resp.json_response
    assert len(units) >= 45, ''\
        f'Job {job3}, expected 45 or more judged units, got {len(units)}'
    assert len(units) <= 50, ''\
        f'Job {job3}, expected 50 or less judged units, got {len(units)}'


@pytest.mark.workflow_e2e
@pytest.mark.workflow_deploy_engine
@pytest.mark.prod_bug
def test_e2e_wf_engine():
    """
    Create a WF with 2 steps:
    Step1 -> Step2 route all units when what_is_greate=Column1
    Step1 -> Step3 route all units when what_is_greate=Column2
    Launch WF, work on the jobs to verify finalized units are routed as expected.
    Note: this test takes ~12 minutes

    additional verification:
    prod bug  https://appen.atlassian.net/browse/ADAP-844
    Builder Jobs: Ignore the comments in Job CML
    """
    # create jobs
    jobs = create_jobs(num_jobs=3)
    job1, job2, job3 = jobs

    # create workflow
    wf_id = create_workflow()
    wf_service = Workflow(api_key)

    # create wf steps
    steps = wf_service.create_job_step(jobs, wf_id)
    step1, step2, step3 = [i['step_id'] for i in steps]

    # create wf routes
    route_1_2_resp = wf_service.create_route(step1, step2, wf_id)
    route_1_3_resp = wf_service.create_route(step1, step3, wf_id)
    for resp in [route_1_2_resp, route_1_3_resp]:
        assert resp.status_code == 201, ''\
            f'failed to create a route: {resp.text}'
    route_1_2 = route_1_2_resp.json_response['id']
    route_1_3 = route_1_3_resp.json_response['id']

    # craete wf filter rules
    # create rnd rule
    equal_col1_payload = {
        "filter_rule": {
             "comparison_field": "what_is_greater",
              "comparison_operation": "\u003d\u003d",
              "comparison_value": "col1",
              "rule_connector": "and"
        }
    }
    res_rnd = wf_service.create_filter_rule(step1, route_1_2, equal_col1_payload, wf_id)
    assert res_rnd.status_code == 201, ''\
        f'failed to create rnd filter rule: {res_rnd.text}'

    # create els rule
    equal_col2_payload = {
        "filter_rule": {
            "comparison_field": "what_is_greater",
            "comparison_operation": "\u003d\u003d",
            "comparison_value": "col2",
            "rule_connector": "and"
        }
    }
    res_els = wf_service.create_filter_rule(step1, route_1_3, equal_col2_payload, wf_id)
    assert res_els.status_code == 201, ''\
        f'failed to create els filter rule: {res_els.text}'

    # upload data
    data_units_to_order = 10
    units_filepath = data_generator(data_units_to_order, filename='/tmp/units.csv', gold=True)
    data = pd.read_csv(units_filepath)
    units_job2 = data[data.what_is_greater_gold == 'col1'].shape[0]
    units_job3 = data[data.what_is_greater_gold == 'col2'].shape[0]

    wf_service.upload_data(units_filepath, wf_id=wf_id)
    retry(verify_data_upload_complete, wf_id=wf_id)

    # # launch workflow
    resp = wf_service.launch(num_rows=data_units_to_order, wf_id=wf_id)
    assert resp.status_code == 202, 'failed to launch a workflow'

    retry(verify_job_has_units, job_id=job1, num_units=data_units_to_order)
    retry(verify_job_has_ordered_units, job_id=job1, num_units=data_units_to_order)
    retry(verify_job_has_needed_judgments, job_id=job1, num_units=data_units_to_order)

    # work on job1
    Builder(api_key, env=env, job_id=job1).wait_until_status2('running')
    submit_judgments(job1)
    # time.sleep(60)

    # verify job2 has at least 1 unit
    retry(
        verify_job_has_units,
        max_wait=240,
        interval=15,
        job_id=job2,
        num_units=1,
        op=operator.ge
    )

    # verify job2 has all units
    retry(
        verify_job_has_units,
        max_wait=240,
        interval=15,
        job_id=job2,
        num_units=units_job2,
        op=operator.le
    )


    # work on job2
    Builder(api_key, env=env, job_id=job2).wait_until_status2('running')
    retry(
        verify_job_has_needed_judgments,
        max_wait=180,
        interval=15,
        job_id=job2,
        num_units=units_job2,
        op=operator.ge
    )

    submit_judgments(job2)
    # time.sleep(60)

    # verify job3 has all units (units_job3)
    retry(
        verify_job_has_units,
        max_wait=240,
        interval=15,
        job_id=job3,
        num_units=units_job3,
        op=operator.ge
    )

    Builder(api_key, env=env, job_id=job3).wait_until_status2('running')
    # give it a minute to autolaunch units from previous step
    # time.sleep(60)

    # check job3 needs judgments
    retry(
        verify_job_has_needed_judgments,
        max_wait=180,
        interval=15,
        job_id=job3,
        num_units=units_job3,
        op=operator.ge
    )

    # work on job3
    submit_judgments(job3)
    time.sleep(60)

    #check jobs status
    job1_status = Builder(api_key, env=env).get_job_status(job1)
    assert job1_status.json_response['all_units'] == data_units_to_order
    assert job1_status.json_response['needed_judgments'] == 0
    assert job1_status.json_response['completed_units_estimate'] == data_units_to_order

    job2_status = Builder(api_key, env=env).get_job_status(job2)
    assert job2_status.json_response['all_units'] == units_job2
    assert job2_status.json_response['needed_judgments'] == 0
    assert job2_status.json_response['completed_units_estimate'] == units_job2

    job3_status = Builder(api_key, env=env).get_job_status(job3)
    assert job3_status.json_response['all_units'] == units_job3
    assert job3_status.json_response['needed_judgments'] == 0
    assert job3_status.json_response['completed_units_estimate'] == units_job3
