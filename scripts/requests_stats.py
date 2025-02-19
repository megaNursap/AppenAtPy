"""
Script to aggregate http requests results by 1 minute buckets.
Need this when there is a large number of records to analyze, otherwise grafana will overload results db.
Example usage:
> python scripts/requests_stats.py 77
Note: DB connection params need to be in the environment
"""
import argparse
from adap.settings import Config
from adap.perf_platform.utils.db import DBUtils
from adap.perf_platform.utils import results_handler as rh
from adap.perf_platform.utils.logging import get_logger

log = get_logger(__name__)

def fetch_latest_session_id():
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        log.info("Fetching latest session_id")
        session_id = db.fetch_one("select session_id from sessions order by 1 desc limit 1")[0]
        log.info(f"session_id {session_id}")
    return session_id


def main(session_id):
    log.info(f"Fetching aggregated requests stats for sessions {session_id}")
    rows = rh.get_requests_stats_buckets(session_id)
    log.info("Saving data to ResultsDB")
    rh.save_requests_stats(rows)
    log.info("Complete")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "session_id",
        nargs='?',
        type=int,
        default='0',
        help="session_id")
    args = parser.parse_args()
    session_id = args.session_id
    if not session_id:
        session_id = fetch_latest_session_id()
    main(session_id)
