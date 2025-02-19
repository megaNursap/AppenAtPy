"""
This script should be executed locally.
1. Login to aws
2. Do: export LOG_LEVEL=DEBUGV
3. Execute script via pycharm or from cli
    for executing script outside of pycharm(via cli) do the following:
    export PYTHONPATH=$PYTHONPATH:/Users/[your_username]/workspace_old/QA_Automation/adap


Create qa_performance_db and grafana users in results-db cluster
Create platform_performance database in results-db cluster
Create tables and views in platform_performance database (public schema)
Grant required permissions to Grafana user

Requires kubectl installed with permissions to get secrets in main namespace
and configmaps in monitoring namespace, and to port-farward to result-db pod

In order to view logs from DBUtils, set log level to DEBUGV:
export LOG_LEVEL=DEBUGV
"""

from adap.perf_platform.utils.db import DBUtils
from adap.perf_platform.utils import sql_queries as sql
from perf_platform_dbase_pwds import get_pg_pwd, get_qa_perf_db_pwd, get_grafana_pwd
import subprocess
import time


def main():

    # used for port-forwarding to results-db-timescaledb-0:5432
    local_port = 5433

    pgpassword = get_pg_pwd()
    qa_perf_db_password = get_qa_perf_db_pwd()
    grafana_password = get_grafana_pwd()

    print(f'Starting port-forward to results-db-timescaledb-0 '
          'listening on {local_port}...')
    port_forward = f'kubectl port-forward results-db-timescaledb-0 {local_port}:5432'
    port_forward = subprocess.Popen(port_forward, shell=1)
    time.sleep(5)

    pg_conn_params = {
        'host': 'localhost',
        'port': str(local_port),
        'dbname': 'postgres',
        'user': 'postgres',
        'password': pgpassword
    }
    platform_perf_conn_params = {
        'host': 'localhost',
        'port': str(local_port),
        'dbname': 'platform_performance',
        'user': 'qa_performance_db',
        'password': qa_perf_db_password
    }
    try:
        # executing as postgres user
        with DBUtils(**pg_conn_params) as db:
            db.execute(
                sql.create_user_qa_performance_db,
                args={'password': qa_perf_db_password}
                )
            db.execute(sql.create_platform_performance_database)
            db.execute(
                sql.create_user_grafana,
                args={'password': grafana_password}
                )

        # executing as qa_performance_db user
        with DBUtils(**platform_perf_conn_params) as db:
            db.execute(sql.create_table_sessions)
            db.execute(sql.create_table_tasks)
            db.execute(sql.create_table_requests)
            db.execute(sql.create_table_k8_logs)
            db.execute(sql.create_table_kafka_out)
            db.execute(sql.create_table_kafka_in)
            db.execute(sql.create_table_locust_user_counts)
            db.execute(sql.create_units_state_monitor)
            db.execute(sql.create_view_host_job_id)
            db.execute(sql.create_view_job_id_units_per_assignment)
            db.execute(sql.grant_grafana_permissions)

    except Exception:
        raise
    finally:
        if db.conn:
            db.close()

        if port_forward:
            print('Killing port-forward to results-db-timescaledb-0...')
            port_forward.kill()


if __name__ == '__main__':
    main()
