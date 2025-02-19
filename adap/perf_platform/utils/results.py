from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
from adap.settings import Config
from statistics import mean
import pandas as pd

log = get_logger(__name__)

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)
pd.set_option('precision', 2)
pd.set_option('display.width', 1000)


def fetch_session_summary(session_id) -> list:
    log.debug(f"fetch_session_summary for session_id {session_id}")
    sql = """
    SELECT
      session_id,
      s.scenario,
      s.started_at,
      s.finished_at,
      state::text,
      COUNT(*) as total_requests,
      MIN(c.duration) as min_latency,
      AVG(c.duration) as avg_latency,
      MAX(c.duration) as max_latency,
      percentile_cont(0.95) within group (order by c.duration) as "95th_percentile",
      stddev_pop(c.duration) as stddev
    FROM sessions s
    LEFT JOIN requests c USING (session_id)
    WHERE
      s.session_id = %(session_id)s
    GROUP BY 1
    ORDER BY 1
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        results_rows = db.fetch_all(
            sql,
            args={
                'session_id': session_id
                },
            include_column_names=True
            )
    assert len(results_rows) == 1
    return results_rows[0]


def fetch_session_api_summary(session_id) -> list:
    log.debug(f"fetch_session_api_summary for session_id {session_id}")
    sql = """
    SELECT
      "type" as method,
      ep_name,
      count(*) as total_count,
      avg(t1._count)::NUMERIC(10, 2) as avg_rpm,
      avg(duration) as avg_latency,
      --sum(duration) as sum_latency,
      percentile_cont(0.95) within group (order by duration) as "95th_percentile",
      stddev_pop(duration) as stddev
    FROM requests
    JOIN (
      SELECT
      time_bucket('1 minutes', time) AS one_min,
      "type",
      ep_name,
      count(*) as _count
      FROM requests
      WHERE session_id = %(session_id)s
      GROUP BY 1,2,3
      ) t1 USING ("type", ep_name)
    WHERE
      session_id = %(session_id)s
      -- AND task_id in ($tasks)
      -- AND host in ($hostname)
    GROUP BY 1,2
    ORDER BY 1,2
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        results_rows = db.fetch_all(
            sql,
            args={
                'session_id': session_id
                },
            include_column_names=True
            )
    assert results_rows
    return results_rows


def fetch_session_api_summary_df(session_id):
    data = fetch_session_api_summary(session_id)
    return pd.DataFrame(data)


def fetch_judgments_submitted_per_minute(session_id) -> list:
    log.debug(f"fetch_judgments_submitted_per_minute for session_id {session_id}")
    sql = """
    SELECT
    time_bucket('1 minutes', time) AS one_min,
    j.job_id,
    (count(*) * j.units_per_assignment) as jpu,
    avg(r.duration) as avg_latency
    FROM sessions s
    JOIN requests r
        ON r.session_id = s.session_id
    JOIN job_id_units_per_assignment j
        ON j.session_id = r.session_id
        AND j.task_id = r.task_id
    WHERE
      r.ep_name = 'assignment_url'
      AND r."type" = 'post'
      AND r.session_id = %(session_id)s
    GROUP BY one_min, j.job_id, j.units_per_assignment
    ORDER BY one_min DESC;
    """  # TODO
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        results_rows = db.fetch_all(
            sql,
            args={
                'session_id': session_id
                },
            include_column_names=True
            )
        # results_rows = [i[0] for i in results_rows]
    log.info(f"Num rows for session_id {session_id} in resultsdb: "
             f"{len(results_rows)}")
    return results_rows


def get_avg_judgments_per_minute(session_id) -> float:
    jpm = fetch_judgments_submitted_per_minute(session_id)
    jpm = [row['jpu'] for row in jpm]
    avg_jpm = float(round(mean(jpm), 2))
    return avg_jpm


def get_scenario_name(session_id):
    sql = """
    SELECT scenario
    FROM sessions
    WHERE session_id = %(session_id)s
    """  # TODO
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        resp = db.fetch_one(
            sql,
            args={
                'session_id': session_id
                },
            include_column_names=True
            )
    scenario_name = resp.get('scenario')
    return scenario_name


def get_agg_failed_api_requests(session_id):
    sql = """
    SELECT type as "Method",
    ep_name as "Endpoint",
    info -> 'response' ->> 'status_code' as "Status Code",
    count(*)
    FROM requests
    WHERE session_id = %(session_id)s
    AND info -> 'response' ->> 'status_code' NOT LIKE '2__'
    GROUP BY 1,2,3
    """
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        results_rows = db.fetch_all(
            sql,
            args={
                'session_id': session_id
                },
            include_column_names=True
            )
    return results_rows


def get_agg_failed_api_requests_df(session_id):
    data = get_agg_failed_api_requests(session_id)
    return pd.DataFrame(data)


def compare(cur_results: dict, gold_results: dict, metrics: list) -> list:
    """
    `metrics` is a list of tuples: (metric name, direction of comparison)
    metric name has to be present in the both results dicts
    """
    results = []
    for each in metrics:
        metric = each[0]
        measure = each[1]
        try:
            if measure == 'down':
                diff = float(gold_results[metric] / cur_results[metric])
                m = f"{gold_results[metric]} (gold) / {cur_results[metric]} "
            elif measure == 'up':
                diff = float(cur_results[metric] / gold_results[metric])
                m = f"{cur_results[metric]} / {gold_results[metric]} (gold)"
        except ZeroDivisionError:
            diff = 0.0
            m = f"{gold_results[metric]} (gold) / {cur_results[metric]} "
        log.debug(f"{metric}: {m} = {diff}")
        results.append(diff)
    return results


def compare_session_summary(current_session_id, golden_session_id):
    curr_summary = fetch_session_summary(current_session_id)
    curr_summary['avg_jpm'] = get_avg_judgments_per_minute(current_session_id)
    gold_summary = fetch_session_summary(golden_session_id)
    gold_summary['avg_jpm'] = get_avg_judgments_per_minute(golden_session_id)
    metrics = [
        ('avg_latency', 'down'),
        ('95th_percentile', 'down'),
        ('stddev', 'down'),
        ('avg_jpm', 'up')
    ]
    results = compare(curr_summary, gold_summary, metrics)
    final_grade = round(mean(results), 2)
    log.info(f"Final grade: {final_grade}")
    return final_grade


def compare_session_apis(current_session_id, golden_session_id):
    curr_results = fetch_session_api_summary(current_session_id)
    gold_results = fetch_session_api_summary(golden_session_id)
    metrics = [
        ('avg_latency', 'down'),
        ('95th_percentile', 'down'),
        ('stddev', 'down'),
        ('avg_rpm', 'up')
    ]
    curr_dict = {f"{d['method']}:{d['ep_name']}": d for d in curr_results}
    gold_dict = {f"{d['method']}:{d['ep_name']}": d for d in gold_results}
    # assert len(curr_dict.keys()) == len(gold_dict.keys())
    grades = {}  # grade per key
    for key, curr_summary in curr_dict.items():
        log.info(f"Comparing {key}")
        gold_summary = gold_dict.get(key)
        if not gold_summary:
            log.error(f"No entry found for {key} in golden data")
            continue
        results = compare(curr_summary, gold_summary, metrics)
        grade = round(mean(results), 2)
        grades[key] = grade
    session_total_count = sum([curr_dict[k]['total_count'] for k in grades])
    grades_weighted = {}
    for key, grade in grades.items():
        weight = curr_dict[key]['total_count'] / session_total_count
        grades_weighted[key] = grade * weight
        log.info(f"{key}: {round(grade,5)} * {round(weight,5)}")
    final_grade = round(sum(grades_weighted.values()), 5)
    log.info(f"Final grade: {final_grade}")
    return final_grade
