"""
Selects count of judgments from Builder for a given job_id
Save the counts into ResultsDB
"""

from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils import helpers
from adap.settings import Config
from adap.perf_platform.utils.db import (
    conn_pool,
    init_pool,
    check_pool_exists)
import time

log = get_logger(__name__)

sql_select_judgments_counts = """
SELECT count(*) as c
FROM judgments
WHERE job_id = %(job_id)s
"""

sql_insert_judgments_counts = """
INSERT INTO judgments_monitor
(job_id, counts)
VALUES
(%(job_id)s, %(counts)s)
"""


def init_connection_pools():
    if not check_pool_exists(Config.RESULTS_DB_CONN['dbname']):
        init_pool(
            Config.RESULTS_DB_CONN,
            Config.MIN_POOL,
            Config.MAX_POOL
            )
    if not check_pool_exists(Config.BUILDER_DB_CONN['dbname']):
        init_pool(
            Config.BUILDER_DB_CONN,
            Config.MIN_POOL,
            Config.MAX_POOL
            )


def get_counts_from_builder(job_id: int) -> dict:
    with conn_pool('builder') as db:
        res = db.fetch_one(
            sql_select_judgments_counts,
            args={'job_id': job_id})
    log.debug(f"Current judgments count the job {job_id}: {res}")
    return res


def save_counts_to_resultsdb(job_id: int, counts: int):
    log.debug("Saving to ResultsDB")
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        db.execute(
            sql_insert_judgments_counts,
            args={
                'job_id': job_id,
                'counts': counts
                })


def start_monitoring(job_id, duration, interval):
    """
    job_id (int): job_id of the job for which units will be monitored
    duration (int): number of seconds to keep the monitor running for
    interval (int): number of seconds to wait between each probe
    """
    log.info({
        'message': f"Starting judgments monitoring for {duration} seconds"
        })
    started_at = time.time()
    while time.time() < started_at + duration:
        _counts = get_counts_from_builder(job_id)
        if _counts:
            _counts = _counts[0]
            save_counts_to_resultsdb(job_id, _counts)
        time.sleep(interval)
    log.info({
        'message': f'Units state monitor finished after {duration} seconds'
        })


if __name__ == '__main__':
    init_connection_pools()
    job_id = helpers.get_job_id_from_tasks_info()
    duration = int(Config.RUN_TIME)
    interval = Config.INTERVAL
    if not interval:
        interval = 1
    start_monitoring(job_id, duration, interval)
