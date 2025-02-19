#!/usr/bin/env python3

from psycopg2.extensions import cursor
from psycopg2 import pool as psycopg2_pool
from contextlib import contextmanager
from adap.settings import Config
from .logging import get_logger
import psycopg2
import psycopg2.extras


log = get_logger(__name__, db=False)
globals()['pools'] = {}


class DBUtils:

    def __init__(self, **kwargs):
        params = {
            'host': Config.DB_HOST,
            'port': int(Config.DB_PORT),
            'user': Config.DB_USER,
            'dbname': Config.DB_NAME,
            'password': Config.DB_PASSWORD,
            'application_name': 'QA_psycopg2'
            }
        for k, v in kwargs.items():
            if v:
                params.update({k: v})
        self.conn_params = params
        self.uri = "postgresql://" \
                   f"{params['user']}:{params['password']}" \
                   f"@{params['host']}:{params['port']}/" \
                   f"{params['dbname']}"

        if 'pool_conn' in kwargs:
            self.pool_conn = True
            self.conn = kwargs.get('pool_conn')
        else:
            self.pool_conn = None
            self.conn = None
        self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
        return not(any([args, kwargs]))

    def connect(self, autocommit=True, **params):
        if not self.conn:
            if params:
                conn_params = params
            else:
                conn_params = self.conn_params
            _params = {k: v for k, v in conn_params.items() if k != 'password'}
            try:
                log.debugv(f"DB connect: {_params}")
                self.conn = psycopg2.connect(**conn_params)
                if autocommit:
                    self.conn.set_session(autocommit=True)
            except Exception:
                log.error(f"Unable to connect to the database: {_params}")
                raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.pool_conn:
            self.conn = None
        else:
            self.conn.close()

    def get_cursor(self) -> cursor:
        if not(self.cursor and not self.cursor.closed):
            self.cursor = self.conn.cursor()
        return self.cursor

    def fetch_all(self, sql: str, args=None, include_column_names=False):
        try:
            log.debugv(f"Executing: {sql}")
            cur = self.conn.cursor()
            cur.execute(sql, args)
            if include_column_names:
                colnames = [desc[0] for desc in cur.description]
                data = []
                for row in cur.fetchall():
                    data.append({colname: row[i] for i, colname in enumerate(colnames)})
                result = data
            else:
                result = cur.fetchall()
            cur.close()
            return result
        except psycopg2.Error:
            log.error(f"Unable to execute: {sql}")
            raise

    def fetch_one(self, sql: str, args=None, include_column_names=False, keep_cursor=False):
        try:
            log.debugv(f"Executing: {sql}")
            cur = self.get_cursor()
            cur.execute(sql, args)
            data = cur.fetchone()
            assert data, f"Query {sql} returned 0 rows, at least 1 is expected"
            if include_column_names:
                colnames = [desc[0] for desc in cur.description]
                result = {colname: data[i] for i, colname in enumerate(colnames)}
            else:
                result = data
            if not keep_cursor:
                cur.close()
            return result
        except psycopg2.Error:
            log.error(f"Unable to execute: {sql}")
            raise

    def execute(self, sql: str, args=None, fetch=False, keep_cursor=False, commit=False):
        try:
            log.debugv(f"Executing: {sql}")
            result = None
            cur = self.get_cursor()
            cur.execute(sql, args)
            if fetch:
                result = cur.fetchall()
            if not keep_cursor:
                cur.close()
            if commit:
                self.conn.commit()
            return result
        except psycopg2.Error:
            log.error(f"Unable to execute: {sql}")
            raise

    def execute_values(self, sql: str, data: list):
        psycopg2.extras.execute_values(self.get_cursor(), sql, data)

    def execute_batch(self, sql: str, data: list, page_size=1):
        psycopg2.extras.execute_batch(
            self.get_cursor(),
            sql,
            data,
            page_size=page_size)


class Psycopg2Pool:

    def __init__(self, minconn: int, maxconn: int, *args, **kwargs):
        self.pool = psycopg2_pool.SimpleConnectionPool(
            minconn,
            maxconn,
            **kwargs)

    @contextmanager
    def get_conn(self):
        try:
            log.debugv(f"Get connection from the pool")
            conn = self.pool.getconn()
            conn.set_session(autocommit=True)
            yield conn
            log.debugv(f"Put connection back into the pool")
            self.pool.putconn(conn)
        except Exception as e:
            raise e


def init_pool(conn_params: dict, minconn: int, maxconn: int):
    log.debugv("Starting new connection pool"
               f"dbname = {conn_params['dbname']}"
               )
    global pools
    dbname = conn_params['dbname']
    pools[dbname] = Psycopg2Pool(
        int(minconn),
        int(maxconn),
        **conn_params)


def check_pool_exists(pool_name):
    global pools
    try:
        return pools[pool_name]
    except Exception:
        return


@contextmanager
def conn_pool(dbname):
    try:
        global pools
        pool = pools[dbname]
        with pool.get_conn() as conn:
            with DBUtils(pool_conn=conn) as db:
                yield db
    except Exception as e:
        raise e
