import time
import sys
import subprocess

import psycopg2

from core.config import get_config
from core.helpers import time_execution


DB_SETTINGS = get_config()


def get_db_size(pretty=True):
    conn = psycopg2.connect(**DB_SETTINGS)
    cur = conn.cursor()
    cur.execute(
        f"SELECT pg_size_pretty(pg_database_size('{DB_SETTINGS['database']}'))" if pretty else
        f"SELECT pg_database_size('{DB_SETTINGS['database']}')"
    )

    all_results = cur.fetchone()
    result = all_results[-1]

    conn.commit()
    cur.close()

    return result


def get_sessions_count():
    conn = psycopg2.connect(**DB_SETTINGS)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM public.sessions")

    all_results = cur.fetchone()
    result = all_results[-1]
    conn.commit()

    cur.close()
    if conn is not None:
        conn.close()

    return result


def do_port_forwarding():
    print(f'Starting port-forward to results-db-timescaledb-0 '
          'listening on {local_port}...')
    port_forward = f"kubectl port-forward results-db-timescaledb-0 {DB_SETTINGS['port']}:5432"
    port_forward = subprocess.Popen(port_forward, shell=1)
    time.sleep(5)
    return port_forward


@time_execution
def clean_up(count_or_ids):
    print("Start cleaning up DB...")
    conn = psycopg2.connect(**DB_SETTINGS)
    cur = conn.cursor()

    if not isinstance(count_or_ids, list):
        print(f"Sessions count: {count_or_ids}")
        cur.execute(f"SELECT session_id FROM sessions ORDER by session_id ASC limit {count_or_ids}")
        results = cur.fetchall()
        ids_to_delete = list(map(lambda x: x[0], results))
        conn.commit()
    else:
        ids_to_delete = count_or_ids

    print(f"Session ids which will be erased: {ids_to_delete}\n")
    for s_id in ids_to_delete:
        s_start = time.time()
        for table in [
            "requests",
            "requests_stats",
            "k8_logs",
            "tasks",
            "locust_user_counts",
            "kafka_in",
            "kafka_out",
            "sessions"
        ]:
            t_start = time.time()
            cur.execute(f"DELETE FROM {table} WHERE session_id={s_id}")
            conn.commit()
            t_end = time.time()
            print(f"[{s_id}]: {table.upper()} has cleaned up, - {round(t_end - t_start, 2)}s")
        s_end = time.time()
        print(f"Total time consumed, - {round(s_end - s_start, 2)} seconds\n")

    cur.close()
    print(f"Clean up operation finished, {len(ids_to_delete)} session(s) have been deleted")
    if conn is not None:
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide an argument, closing...")
        sys.exit()

    arg = sys.argv[1]
    # identify what was provided either a number or a session id range
    count_or_ids = list(range(int(arg.split('-')[0]), int(arg.split('-')[1]) + 1)) if '-' in arg else arg

    port_forward = do_port_forwarding()

    initial_size_r = get_db_size(False)
    print(f"[start]: Sessions count: {get_sessions_count()}")
    print(f"[start]: DB size: {get_db_size()}")

    clean_up(count_or_ids)

    cleaned_size_r = get_db_size(False)
    print(f"[end]: Sessions count now: {get_sessions_count()}")
    print(f"[end]: DB size: {get_db_size()}")
    print(f"Cleaned size: {(int(initial_size_r) - int(cleaned_size_r)) / 1024 / 1024} MB")
    if port_forward:
        print('Killing port-forward to results-db-timescaledb-0...')
        port_forward.kill()
