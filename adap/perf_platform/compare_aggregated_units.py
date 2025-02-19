
from adap.api_automation.utils.data_util import get_user, unzip_file
from adap.api_automation.services_config.builder import Builder
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
from adap.perf_platform.utils import helpers
from adap.settings import Config
from deepdiff import DeepDiff
import jsonlines
import time

log = get_logger(__name__)


def fetch_job_report_json(job_id):
    """
    1. Generate job report (API)
    2. Download full json report for the job_id (API)
    3. Write the report into zip file
    """
    user = get_user('perf_platform', env=Config.ENV)
    api_key = user.get('api_key')
    b = Builder(
        env=Config.ENV,
        job_id=job_id,
        api_key=api_key)
    payload = {
        'type': 'json',
        'key': api_key
    }
    resp0 = b.regenerate_report(payload=payload)
    resp0.assert_response_status(200)
    time.sleep(2*60)
    c_wait = 0
    while c_wait < Config.MAX_WAIT_TIME:
        resp = b.generate_report(payload=payload)
        if resp.status_code == 200:
            with open(f"/tmp/job_{job_id}.zip", 'wb') as f:
                f.write(resp.content)
            break
        else:
            log.debug(f"generate_report status_code: {resp.status_code} "
                      "retry in 30s")
            time.sleep(30)
            c_wait += 30
    else:
        raise Exception({
            'message': 'Failed to generate job report',
            'info': 'Max wait time exceeded'
            })


def read_report(job_id) -> list:
    """
    1. Unzip the report
    2. Read json lines
    3. Return list of lines
    """
    unzip_file(f"/tmp/job_{job_id}.zip")
    report_json = f"/tmp/job_{job_id}.json"
    with jsonlines.open(report_json, mode='r') as reader:
        report_rows = list(reader)
    log.info(f"Num rows for job_id {job_id} in report: "
             f"{len(report_rows)}")
    return report_rows


def fetch_agg_units_from_resultsdb(job_id) -> list:
    """
    Fetch message value for messages consumed by Kafka
    for this session_id and job_id
    """
    sql_fetch_rows = """
    SELECT "value"
    FROM kafka_out
    WHERE session_id = %(session_id)s
    AND "value" ->> 'job_id' = %(job_id)s
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        results_rows = db.fetch_all(
            sql_fetch_rows,
            args={
                'session_id': Config.SESSION_ID,
                'job_id': str(job_id)
                }
            )
        results_rows = [i[0] for i in results_rows]
    log.info(f"Num rows for job_id {job_id} in resultsdb: "
             f"{len(results_rows)}")
    return results_rows


def fetch_latest_agg_units_from_resultsdb(job_id) -> list:
    """
    Fetch latest message value for messages consumed by Kafka
    for this session_id and job_id
    """
    sql_fetch_rows = """
    SELECT ko."value"
    FROM kafka_out ko
    JOIN (
        SELECT
        value ->> 'id' as unit_id,
        max("time") as latest_dts
        FROM kafka_out
        WHERE "time" > (
            select started_at
            from sessions
            where session_id = %(session_id)s )
        AND "value" ->> 'job_id' = %(job_id)s
        GROUP BY 1
    ) sub
    ON ko.value ->> 'id' = sub.unit_id
    AND ko."time" = sub.latest_dts
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        results_rows = db.fetch_all(
            sql_fetch_rows,
            args={
                'session_id': Config.SESSION_ID,
                'job_id': str(job_id)
                }
            )
        results_rows = [i[0] for i in results_rows]
    log.info(f"Num rows for job_id {job_id} in resultsdb: "
             f"{len(results_rows)}")
    return results_rows


def diff_rows(report_rows, results_rows):
    report_dict = {i['id']: i for i in report_rows}
    results_dict = {i['id']: i for i in results_rows}
    for _id, row_expected in report_dict.items():
        if row_expected['state'] == 'finalized':
            row_actual = results_dict.get(_id)
            if not row_actual:
                log.error({
                    'message': 'Missing row in resultsDB',
                    'unit_id': _id
                    })
            else:
                ddiff = DeepDiff(
                            row_expected,
                            row_actual,
                            ignore_order=True,
                            # exclude_paths=[
                            #     "root['updated_at']",
                            #     "root['results']"
                            #     ]
                            )
                if ddiff:
                    log.error({
                        'message': 'Mismatch',
                        'unit_id': _id,
                        'diff': ddiff.__repr__()
                        })


def main():
    job_id = helpers.get_job_id_from_tasks_info()
    fetch_job_report_json(job_id)
    report_rows = read_report(job_id)
    results_rows = fetch_latest_agg_units_from_resultsdb(job_id)
    diff_rows(report_rows, results_rows)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
