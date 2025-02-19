#!/usr/bin/env python3

from datetime import datetime
from adap.settings import Config
from . import sql_queries as sql
from .db import DBUtils, conn_pool, check_pool_exists, init_pool
import inspect
import random
import json
import time
import os


def pool(func):
    """
    Decorator to create a global connection pool for ResultsDB if not exists
    """
    def wrapper(*args, **kwargs):
        if not check_pool_exists(Config.RESULTS_DB_CONN['dbname']):
            init_pool(
                Config.RESULTS_DB_CONN,
                Config.MIN_POOL,
                Config.MAX_POOL
                )
        return func(*args, **kwargs)
    return wrapper


def init_session(env=None):
    """
    Insert a row into "sessions" table in the ResultsDB with state 'active'
    Used by master0
    """
    st = parse_stack_trace(inspect.stack())
    scenario = st[-1][0]
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        res = db.execute(
            sql.add_session,
            args={
                'state': 'active',
                'scenario': scenario,
                'env': env
                },
            fetch=1)
        session_id = str(res.pop()[0])

    print(f"CURRENT SESSION_ID: {session_id}")
    return session_id


def finilize_session(session_id, state):
    """
    Set "state" = 'complete' for a record in "sessions" table
    Used by master0
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        db.execute(
            sql.update_session_complete,
            args={
                'session_id': session_id,
                'finished_at': datetime.now(),
                'state': state
                })


def add_task_info(info: dict, session_id=None, task_id=None):
    """
    add json info for current session_id and task_id to
    "tasks" table in Results DB
    """
    session_id = session_id or Config.SESSION_ID
    task_id = task_id or Config.TASK_ID
    info_existing = get_task_info(session_id, task_id, accept_null=True)
    args = {
        'session_id': session_id,
        'task_id': task_id,
        'info': json.dumps(info)
    }

    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        if not info_existing:
            db.execute(
                sql.add_task_info, args=args
            )
        else:
            db.execute(
                sql.update_task_info, args=args
            )


def get_task_info(session_id=Config.SESSION_ID, task_id=Config.TASK_ID, accept_null=False) -> dict:
    """
    get json info from "tasks" table in Results DB
    by current session_id and task_id
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        if accept_null:
            task_info = db.fetch_all(
                sql.select_task_info,
                args={
                    'session_id': session_id,
                    'task_id': task_id
                })
            if task_info:
                return task_info[0]
        else:
            task_info = db.fetch_one(
                sql.select_task_info,
                args={
                    'session_id': session_id,
                    'task_id': task_id
                })
            return task_info


def update_task_info(info: dict, session_id=None, task_id=None):
    session_id = session_id or Config.SESSION_ID
    task_id = task_id or Config.TASK_ID
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        db.execute(
            sql.update_task_info,
            args={
                'session_id': session_id,
                'task_id': task_id,
                'info': json.dumps(info)
            })


@pool
def save_to_db(rtype: str, duration: float, info: dict, ep_name='unk'):
    """ Insert a row into requests table in platform_performance DB """
    args={
        'host': Config.HOSTNAME,
        'type': rtype,
        'ep_name': ep_name,
        'duration': duration,
        'session_id': int(Config.SESSION_ID),
        'task_id': int(Config.TASK_ID),
        'info': json.dumps(info)
    }
    if batch_size := Config.BATCHED_SAVE_RESULTS_SIZE:
        if globals().get('results_batch') is None:
            globals()['results_batch'] = []
        global results_batch
        results_batch.append((
            args['type'],
            args['host'],
            args['ep_name'],
            args['duration'],
            args['session_id'],
            args['task_id'],
            args['info']
        ))
        if len(results_batch) >= batch_size or random.random() > 0.99:
            _batch = results_batch
            results_batch = []
            with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
                db.execute_batch(
                    sql.send_request_results,
                    _batch,
                    page_size=100
                    )
    else:
        with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
            db.execute(
                sql.send_request_result,
                args=args
                )


def parse_stack_trace(stack_trace) -> list:
    # exclude impl(allure) and wrapper_func(timeit)
    st = [i for i in stack_trace if i.function not in ('impl', 'wrapper_func')]
    # keep only file name and function name
    st = [(os.path.basename(s.filename), s.function) for s in st]
    return st


def timeit(func):
    """
    Decorator function to measure duration of each event (http request)
    """

    def wrapper_func(*args, **kwargs):
        t0 = time.time()
        resp = func(*args, **kwargs)
        duration_ms = (time.time() - t0) * 1000

        if kwargs.get('endpoint'):
            endpoint_full = kwargs.get('endpoint')
        else:
            endpoint_full = args[1]

        info = {
            # 'stack_trace': parse_stack_trace(inspect.stack()),
            'endpoint_full': endpoint_full,
            'request': {
                'payload': None
            },
            'response': {
                'status_code': resp.status_code,
                'url': getattr(resp, 'url', None),
            },
        }

        if Config.CAPTURE_PAYLOAD and kwargs.get('data'):
            try:
                payload = json.loads(kwargs.get('data'))
            except Exception:
                payload = kwargs.get('data')
            info['request'].update({
                'payload': payload,
                })
        if Config.CAPTURE_RESPONSE:
            info['response'].update({
                'json_response': resp.json_response,
                })

        save_to_db(
            rtype=func.__name__,
            ep_name=kwargs.get('ep_name') or 'unk',
            duration=duration_ms,
            info=info
            )
        return resp

    def _func(*args, **kwargs):
        resp = func(*args, **kwargs)
        return resp

    if Config.CAPTURE_RESULTS:
        return wrapper_func
    else:
        return _func


@pool
def log_to_db(level: str, msg: dict):
    # with DBUtils(**Config.RESULTS_DB_CONN) as db:
    try:
        _msg = json.dumps(msg)
    except TypeError:
        _msg = json.dumps(msg.__repr__())
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        session_id = Config.SESSION_ID or '0'
        task_id = Config.TASK_ID or '0'
        db.execute(
            sql.send_k8_log,
            args={
                'host': Config.HOSTNAME,
                'level': level,
                'session_id': session_id,
                'task_id': task_id,
                'msg': _msg,
                }
            )


@pool
def send_kafka_in(message_id, value=None, error=None):
    if error is not None:
        if not isinstance(error, str):
            error = error.__repr__()
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        session_id = Config.SESSION_ID or 0
        db.execute(
            sql.send_kafka_in,
            args={
                'session_id': session_id,
                'message_id': message_id,
                'value': value,
                'error': error
                }
            )


@pool
def send_kafka_in_batch(messages: list):
    """
    Messages are streamed into execute_batch
    Expected message format:
    ("time": timestamp, session_id: int, message_id: str, value: json)
    """
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        db.execute_batch(
            sql.send_kafka_in_batch,
            (m for m in messages),
            page_size=1000
            )


@pool
def send_kafka_out(message_id, value=None, error=None, details=None):
    if error is not None:
        if not isinstance(error, str):
            error = error.__repr__()
    session_id = Config.SESSION_ID or 0
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        db.execute(
            sql.send_kafka_out,
            args={
                'session_id': session_id,
                'message_id': message_id,
                'value': json.dumps(value),
                'error': error,
                'host': Config.HOSTNAME,
                'details': json.dumps(details)
                }
            )


@pool
def send_locust_user_counts(users_count):
    host = Config.HOSTNAME
    session_id = Config.SESSION_ID or '0'
    task_id = Config.TASK_ID or '0'
    with conn_pool(Config.RESULTS_DB_CONN['dbname']) as db:
        db.execute(
            sql.send_locust_user_count,
            args={
                'host': host,
                'session_id': session_id,
                'task_id': task_id,
                'users_count': users_count
                }
            )


def get_requests_stats_buckets(session_id):
    """
    returns list of dicts
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        return db.fetch_all(
            sql.get_requests_session_agg_stats,
            args={'session_id': session_id},
            include_column_names=True
            )

def save_requests_stats(rows: list):
    batch = []
    for row in rows:
        batch.append((
          row['time'],
          row['session_id'],
          row['metric'],
          row['rpm'],
          row['avg_latency'],
          row['max_latency'],
          row['95th_percentile'],
          row['99th_percentile']
        ))
    batch = sorted(batch, key=lambda x: x[0])
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        db.execute_batch(
            sql.send_requests_stats,
            batch,
            page_size=100
            )