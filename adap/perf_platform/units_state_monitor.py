"""
Selects count of units by state from Builder for a given job_id
Save the counts into ResultsDB
"""

from adap.settings import Config
from adap.perf_platform.utils.db import (
    conn_pool,
    init_pool,
    check_pool_exists)
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.results_handler import get_task_info
import time
import json

log = get_logger(__name__)

sql_select_units_state_counts = """
SELECT state, count(*) as c
FROM units
WHERE job_id = %(job_id)s
GROUP BY 1
ORDER BY 1
"""

sql_insert_units_state_counts = """
INSERT INTO units_state_monitor
(job_id, counts)
VALUES
(%(job_id)s, %(counts)s)
"""

sql_select_job_id_from_logs = """
SELECT msg ->> 'job_id'
FROM k8_logs
WHERE msg ->> 'message' = 'New job created'
AND session_id = %(session_id)s
AND task_id = %(task_id)s
"""

sql_select_units_states = """
SELECT id, state
FROM units
WHERE job_id = %(job_id)s
"""

sql_insert_units_states = """
INSERT INTO units_state_monitor2 (job_id, unit_id, state) VALUES (%s, %s, %s)
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
        res = db.fetch_all(
            sql_select_units_state_counts,
            args={'job_id': job_id},
            include_column_names=True)
    log.debug(f"Current units state on the job {job_id}: {res}")
    return res


def get_all_units_from_builder(job_id: int) -> dict:
    with conn_pool('builder') as db:
        res = db.fetch_all(
            sql_select_units_states,
            args={'job_id': job_id},
            include_column_names=True)
    log.debug(f"Fetched all units for the job {job_id}")
    return res


def save_counts_to_resultsdb(job_id: int, counts: dict):
    log.debug("Saving to ResultsDB")
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        db.execute(
            sql_insert_units_state_counts,
            args={
                'job_id': job_id,
                'counts': json.dumps(counts)
                })


def save_unit_states_to_resultsdb(rows: list):
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        db.execute_batch(
            sql_insert_units_states,
            (m for m in rows),
            page_size=1000
            )


def get_job_id_from_logs(interval=5):
    log.debug('Fetching job_id from k8_logs table ResultsDB')
    job_id = None
    _wait = 0
    while not job_id and _wait < Config.MAX_WAIT_TIME:
        with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
            job_id = db.fetch_all(
                sql_select_job_id_from_logs,
                args={
                    'session_id': Config.SESSION_ID,
                    'task_id': Config.TASK_ID
                    })
        if job_id:
            job_id = job_id[0][0]
            log.debug(f'Retrieved job_id {job_id}')
            return job_id
        else:
            log.debug(f'job_id not found, retry in {interval} seconds')
            time.sleep(interval)
            _wait += interval
    else:
        raise Exception({
            'message': 'job_id not found in k8_logs before timeout',
            'info': f"waited {_wait} seconds"
        })


def get_job_id_from_task_info(interval=5):
    try:
        job_id = None
        _wait = 0
        while not job_id and _wait < Config.MAX_WAIT_TIME:
            if Config.TASK_ID_DATA:
                task_id = Config.TASK_ID_DATA
            else:
                task_id = Config.TASK_ID
            info = get_task_info(task_id=task_id, accept_null=True)
            log.debug(f"Current task info: {info}")
            if info:
                if step := Config.WORKFLOW_STEP:
                    workflow_job_ids = info[0].get('workflow_job_ids')
                    job_id = workflow_job_ids[step-1]
                elif Config.JOB_TYPE.startswith('TQG'):
                    job_id = info[0].get('tqg_job_id')
                else:
                    job_id = info[0].get('job_id')
                log.debug({
                    'job_id': job_id
                    })
                return job_id
            else:
                log.debug(f'task info not found, retry in {interval} seconds')
                time.sleep(interval)
                _wait += interval
    except Exception as e:
        log.error(e.__repr__())
        raise


def start_monitoring_counts(job_id, duration, interval):
    """
    job_id (int): job_id of the job for which units will be monitored
    duration (int): number of seconds to keep the monitor running for
    interval (int): number of seconds to wait between each probe
    """
    log.info({
        'message': f"Starting units state monitoring for {duration} seconds"
        })
    started_at = time.time()
    while time.time() < started_at + duration:
        _counts = get_counts_from_builder(job_id)
        if _counts:
            _counts = {i['state']: i['c'] for i in _counts}
            save_counts_to_resultsdb(job_id, _counts)
        time.sleep(interval)
    log.info({
        'message': f'Units state monitor finished after {duration} seconds'
        })


def start_monitoring_states(job_id, duration, interval):
    """
    job_id (int): job_id of the job for which units will be monitored
    duration (int): number of seconds to keep the monitor running for
    interval (int): number of seconds to wait between each probe
    """
    log.info({
        'message': f"Starting units state monitoring for {duration} seconds"
        })
    started_at = time.time()
    units = get_all_units_from_builder(job_id)
    assert units, f'There are no units for the job {job_id}'
    data = [(job_id, row['id'], row['state']) for row in units]
    save_unit_states_to_resultsdb(data)
    units = {row['id']: row['state'] for row in units}
    time.sleep(interval)
    while time.time() < started_at + duration:
        # if _counts:
        #     _counts = {i['state']: i['c'] for i in _counts}
        #     save_counts_to_resultsdb(job_id, _counts)
        _units = get_all_units_from_builder(job_id)
        updates = []
        for row in _units:
            unit_id = row['id']
            state = row['state']
            if state != units[unit_id]:
                units[unit_id] = state
                updates.append((job_id, unit_id, state))
        if updates:
            save_unit_states_to_resultsdb(updates)
        time.sleep(interval)
    log.info({
        'message': f'Units state monitor finished after {duration} seconds'
        })


if __name__ == '__main__':
    init_connection_pools()
    if Config.MONITOR_JOB_ID:
        job_id = int(Config.MONITOR_JOB_ID)
    elif Config.UNITS_MONITOR_SOURCE == 'task_info':
        job_id = get_job_id_from_task_info()
    else:
        job_id = get_job_id_from_logs()
    duration = int(Config.RUN_TIME)
    interval = Config.INTERVAL
    if not interval:
        interval = 1
    if Config.UNITS_MONITOR_TYPE == 'counts':
        start_monitoring_counts(job_id, duration, interval)
    elif Config.UNITS_MONITOR_TYPE == 'state_changes':
        start_monitoring_states(job_id, duration, interval)
