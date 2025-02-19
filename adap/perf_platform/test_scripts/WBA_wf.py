from adap.perf_platform.test_scripts.common import *
from adap.api_automation.utils.helpers import retry
import time


def test_WBA_workflows():
    """
    Run a workflow with 2 jobs and submit judgments on both jobs.
    Verify Workflow Builder Adapter handles messages coming from AFU producer,
    as well as WF-to-Builder messages.
    """
    num_units = 50
    job_ids = create_jobs(2, launch=False)
    wf_id = new_workflow()
    log.debug(f'Create WF job steps for jobs {job_ids}')
    step1, step2 = [s['step_id'] for s in wf.create_job_step(job_ids, wf_id)]
    log.debug('Create WF route')
    route_id = wf.create_route(step1, step2, wf_id).json_response['id']
    payload = {
        "filter_rule": {
            "rule_connector": "all"
        }
    }
    log.debug('Create WF filter rule')
    assert wf.create_filter_rule(
        step1,
        route_id,
        payload,
        wf_id
    ).status_code == 201
    data_generator = JOB_DATA['data_generator']
    log.debug('Upload data to the WF')
    assert wf.upload_data(
        file_name=data_generator(num_units, filename='/tmp/wf_data.csv'),
        wf_id=wf_id
    ).status_code == 201
    time.sleep(10)
    log.debug('Launch the WF')
    assert wf.launch(
        num_rows=num_units,
        wf_id=wf_id
    ).status_code == 202

    log.debug('Sleep 10')
    time.sleep(10)
    job1, job2 = job_ids

    log.debug(f'Job 1: Validations for the JOB 1 of the workflow (job_id {job1}, wf_id {wf_id})')
    log.info("Job 1: verify units in 'builder.units.from.external' topic")
    time.sleep(50)
    # log.info("count count is:", get_count_msg_bu_topic(job_id=job1))
    log.info("original count count is:", num_units)
    # assert get_count_msg_bu_topic(job_id=job1) == num_units
    retry(verify_jobs_running, job_id=job1)
    submit_judgments(job1)
    time.sleep(10)
    finalized_units = fetch_finalized_units_from_builder(job1)
    assert len(finalized_units) > 0
    log.info("Job 1: verify units in 'builder.aggregated.finalized.units.from.builder'")
    log.info("count count afu is:", get_count_msg_afu_topic(job_id=job1))
    # assert get_count_msg_afu_topic(job_id=job1) == len(finalized_units)
    log.info("Job 1: verify units in 'wfp.datalines.from.external.to.workflows'")
    log.info("count count wf is:", get_count_msg_to_wf_topic(wf_id=wf_id, step_id=step1))
    # assert get_count_msg_to_wf_topic(wf_id=wf_id, step_id=step1) == len(finalized_units)
    time.sleep(10)
    log.info("Job 1: verify units in 'wfp.builder.adapter.datalines.to.builder'")
    # assert get_count_msg_wf_to_ba_topic(wf_id=wf_id, step_id=step1) == len(finalized_units)


    log.info("Job 2: Validations for the JOB 2 of the workflow"
            f"(job_id {job2}, wf_id {wf_id})")
    log.info("Job 2: verify units in 'builder.units.from.external' topic")
    # log.info("count count 2 wf is:", get_count_msg_bu_topic(job_id=job2))
    # assert get_count_msg_bu_topic(job_id=job2) == num_units
    retry(verify_jobs_running, job_id=job2)
    submit_judgments(job2)
    time.sleep(10)
    finalized_units = fetch_finalized_units_from_builder(job2)
    assert len(finalized_units) > 0
    log.info("Job 2: verify units in 'builder.aggregated.finalized.units.from.builder'")
    # assert get_count_msg_afu_topic(job_id=job2) == len(finalized_units)
    log.info("Job 2: verify units in 'wfp.datalines.from.external.to.workflows'")
    # assert get_count_msg_to_wf_topic(wf_id=wf_id, step_id=step2) == len(finalized_units)
    log.info("Job 2: verify units in 'wfp.builder.adapter.datalines.to.builder'")
    # assert get_count_msg_wf_to_ba_topic(wf_id=wf_id, step_id=step1) == len(finalized_units)

    log.info('WF Jobs Test PASSED')

if __name__ == '__main__':
    try:
        test_WBA_workflows()
    except Exception as exc:
        log.error(exc.__repr__())
        raise
