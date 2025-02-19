from adap.perf_platform.test_scripts.common import *
from adap.api_automation.utils.helpers import retry
import time


def test_WBA_non_wf_job():
    """
    Run a regular, non-workflow job, and submit jugdgments.
    Verify Workflow Builder Adapter does not publish finalized units
    coming from a non-wf job anywhere.
    """
    num_units = 1000
    num_assignments = 30
    job_id = create_job(launch=True, num_units=num_units)
    retry(verify_jobs_running, job_id=job_id)
    log.debug('Submitting judgments on PART2 job')
    submit_judgments(job_id, num_assignments=num_assignments)

    time.sleep(10)
    
    log.info("PART 2: Verify all finalized units in Builder"
             "are present in AFU topic for the non-WF job")
    # querying Builder DB directly, because API returns inaccurate data
    finalized_units = fetch_finalized_units_from_builder(job_id)
    finalized_units_ids = [i.get('id') for i in finalized_units]
    afu_messages = get_msg_builder_topic(job_id, 'builder.aggregated.finalized.units.from.builder')
    assert len(finalized_units) == len(afu_messages), ''\
        f"Expected: {len(finalized_units)}\n"\
        f"Actual: {len(afu_messages)}"
    afu_msg_ids = [int(m['message_id']) for m in afu_messages]
    assert all(map(lambda _id: _id in afu_msg_ids, finalized_units_ids))

    # Verify messages were NOT published anywhere by WFBA
    sql = """
    SELECT * FROM kafka_out 
    WHERE session_id = %(session_id)s
    AND details ->> 'topics' ~ %(topic)s
    AND value::TEXT ~ %(unit_ids)s
    """
    log.info("PART 2: verify units NOT in 'wfp.datalines.from.external.to.workflows'")
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        wfp_messages = db.fetch_all(
            sql,
            args={
                'session_id': Config.SESSION_ID,
                'topic': 'wfp.datalines.from.external.to.workflows',
                'unit_ids': '|'.join(finalized_units)
            },
            include_column_names=True
        )
    assert len(wfp_messages) == 0
    
    log.info("PART 2: verify units NOT in 'builder.units.creation.dead.letters'")
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        dl_messages = db.fetch_all(
            sql,
            args={
                'session_id': Config.SESSION_ID,
                'topic': 'builder.units.creation.dead.letters',
                'unit_ids': '|'.join(finalized_units)
            },
            include_column_names=True
        )
    assert len(dl_messages) == 0
    log.info('Non-WF Job Test PASSED')

if __name__ == '__main__':
    try:
        test_WBA_non_wf_job()
    except Exception as exc:
        log.error(exc.__repr__())
        raise
