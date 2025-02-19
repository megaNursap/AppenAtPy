# ref: https://github.com/CrowdFlower/qa_performance_db/blob/master/qa_performance_db/sql_modules/init_results_db.py

create_user_qa_performance_db = """
CREATE USER qa_performance_db WITH PASSWORD %(password)s
"""

create_user_grafana = """
CREATE USER grafana WITH PASSWORD %(password)s
"""

create_platform_performance_database = """
CREATE DATABASE platform_performance;

GRANT ALL ON DATABASE platform_performance TO qa_performance_db;
"""

grant_grafana_permissions = """
GRANT USAGE ON SCHEMA public TO grafana;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public to grafana;
"""

create_table_sessions = """
CREATE TABLE sessions (
session_id  INT             GENERATED ALWAYS AS IDENTITY,
scenario    TEXT,
started_at  TIMESTAMPTZ     NOT NULL DEFAULT current_timestamp,
finished_at TIMESTAMPTZ,
state       TEXT,
env         TEXT,
PRIMARY KEY (session_id)
);
"""

create_table_tasks = """
CREATE TABLE tasks (
session_id  BIGINT NOT NULL,
task_id     BIGINT NOT NULL,
info        JSON,
PRIMARY KEY (session_id, task_id)
);
"""

create_table_requests = """
CREATE TABLE requests (
time        TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
host        TEXT                NOT NULL,
type        TEXT                NOT NULL,
ep_name     TEXT                NOT NULL,
duration    DOUBLE PRECISION    NOT NULL,
session_id  INT                 NOT NULL,
task_id     INT                 NOT NULL,
info        JSONB,
FOREIGN KEY (session_id) REFERENCES sessions
);
SELECT public.create_hypertable('requests'::regclass, 'time'::name);
CREATE INDEX requests_type_idx ON requests (type);
CREATE INDEX requests_ep_name_idx ON requests (ep_name);
CREATE INDEX ON requests (session_id, task_id);
"""

create_table_k8_logs = """
CREATE TABLE k8_logs (
time        TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
host        TEXT                NOT NULL,
level       TEXT                NOT NULL,
session_id  INT                 ,
task_id     INT                 ,
msg         JSONB
);
CREATE INDEX k8_logs_time_idx ON k8_logs (time DESC);
"""

create_table_locust_user_counts = """
CREATE TABLE locust_user_counts (
time        TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
host        TEXT                NOT NULL,
session_id  INT                 ,
task_id     INT                 ,
users_count BIGINT
);
CREATE INDEX locust_user_counts_time_idx ON locust_user_counts (time DESC);
"""

create_view_host_job_id = """
CREATE OR REPLACE VIEW host_job_id as (
SELECT host, session_id, task_id,
msg ->> 'job_id' as job_id
FROM k8_logs
WHERE msg ->> 'message' = 'Assigned job_id'
)
"""

create_view_job_id_units_per_assignment = """
CREATE OR REPLACE VIEW job_id_units_per_assignment as (
SELECT
DISTINCT
v.job_id,
l.session_id,
l.task_id,
(l.msg -> 'config' -> 'job' ->> 'units_per_assignment')::NUMERIC as units_per_assignment
FROM k8_logs as l
JOIN host_job_id as v
    ON (v.session_id = l.session_id
    AND l.task_id = v.task_id)
WHERE (l.msg -> 'config' -> 'job' ->> 'units_per_assignment') IS NOT NULL
)
"""

add_session = """
INSERT INTO sessions (scenario, state, env)
VALUES (%(scenario)s, %(state)s, %(env)s)
RETURNING session_id
"""

update_session_complete = """
UPDATE sessions
SET finished_at = %(finished_at)s, state = %(state)s
WHERE session_id = %(session_id)s
"""

add_task_info = """
INSERT INTO tasks (session_id, task_id, info)
VALUES (%(session_id)s, %(task_id)s, %(info)s)
"""

select_task_info = """
SELECT info
FROM tasks
WHERE session_id = %(session_id)s
AND task_id = %(task_id)s
"""

update_task_info = """
UPDATE tasks
SET info = %(info)s
WHERE session_id = %(session_id)s
AND task_id = %(task_id)s
"""

send_selenium_results = """
INSERT INTO selenium_results (duration, message)
VALUES (%(duration)s, %(message)s)
"""

send_request_result = """
INSERT INTO requests (type, host, ep_name, duration, session_id, task_id, info)
VALUES (%(type)s, %(host)s, %(ep_name)s, %(duration)s, %(session_id)s, %(task_id)s, %(info)s)
"""

send_request_results = """
INSERT INTO requests (type, host, ep_name, duration, session_id, task_id, info)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

send_k8_log = """
INSERT INTO k8_logs (host, level, session_id, task_id, msg)
VALUES (%(host)s, %(level)s, %(session_id)s, %(task_id)s, %(msg)s)
"""

send_k8_log = """
INSERT INTO k8_logs (host, level, session_id, task_id, msg)
VALUES (%(host)s, %(level)s, %(session_id)s, %(task_id)s, %(msg)s)
"""

send_locust_user_count = """
INSERT INTO locust_user_counts (host, session_id, task_id, users_count)
VALUES (%(host)s, %(session_id)s, %(task_id)s, %(users_count)s)
"""

# KAFKA

create_table_kafka_in = """
CREATE TABLE kafka_in (
time            TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
session_id      INT,
message_id      TEXT,
value           JSONB,
error           TEXT
);
CREATE INDEX kafka_in_time_idx ON kafka_in (time DESC);
CREATE INDEX kafka_in_message_id_idx ON kafka_in (message_id);
"""

create_table_kafka_out = """
CREATE TABLE kafka_out (
time            TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
session_id      INT,
message_id      TEXT,
value           JSONB,
error           TEXT,
host            TEXT,
details         JSONB
);
CREATE INDEX kafka_out_time_idx ON kafka_out (time DESC);
CREATE INDEX kafka_out_message_id_idx ON kafka_out (message_id);
CREATE INDEX kafka_out_session_id_idx ON kafka_out (session_id);
"""

create_view_kafka_view = """
CREATE OR REPLACE VIEW kafka_view as (
SELECT
COALESCE(i.message_id, o.message_id) as message_id,
i.time as t0,
o.time as t1,
(extract('epoch' from o.time) - extract('epoch' from i.time))*1000  as duration_ms,
i.session_id,
i.error as i_error,
o.error as o_error
FROM kafka_in i
LEFT JOIN kafka_out o USING(message_id)
)
"""

send_kafka_in = """
INSERT INTO kafka_in (session_id, message_id, value, error)
VALUES (%(session_id)s, %(message_id)s, %(value)s, %(error)s)
"""

send_kafka_in_batch = """
INSERT INTO kafka_in ("time", session_id, message_id, value)
VALUES (%s, %s, %s, %s)
"""

send_kafka_out = """
INSERT INTO kafka_out (session_id, message_id, value, error, host, details)
VALUES (%(session_id)s, %(message_id)s, %(value)s, %(error)s, %(host)s, %(details)s)
"""

create_units_state_monitor = """
CREATE TABLE units_state_monitor (
time            TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
job_id          BIGINT,
counts          JSONB
);
CREATE INDEX units_state_monitor_time_idx ON units_state_monitor (time DESC);
"""

create_judgments_monitor = """
CREATE TABLE judgments_monitor (
time            TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
job_id          BIGINT,
counts          BIGINT
);
CREATE INDEX judgments_monitor_time_idx ON judgments_monitor (time DESC);
"""

create_units_state_monitor2 = """
CREATE TABLE units_state_monitor2 (
time            TIMESTAMPTZ         NOT NULL DEFAULT current_timestamp,
job_id          BIGINT,
unit_id         BIGINT,
state           TEXT
);
CREATE INDEX units_state_monitor2_time_idx ON units_state_monitor2 (time DESC);
CREATE INDEX units_state_monitor2_job_id_idx ON units_state_monitor2 (job_id);
CREATE INDEX units_state_monitor2_unit_id_idx ON units_state_monitor2 (unit_id);
"""

create_table_requests_stats = """
CREATE TABLE requests_stats (
time            TIMESTAMPTZ         NOT NULL,
session_id      BIGINT,
metric          TEXT,
rpm             BIGINT,
avg_latency     DOUBLE PRECISION,
"95th_percentile" DOUBLE PRECISION,
"99th_percentile" DOUBLE PRECISION,
max_latency     DOUBLE PRECISION
);
CREATE INDEX requests_stats_time_idx ON requests_stats (time);
CREATE INDEX requests_stats_session_id_idx ON requests_stats (session_id);
"""

# requests stats grouped by 1 minute buckets
get_requests_session_agg_stats = """
SELECT
time_bucket('1 minutes', time) AS "time",
session_id,
info-> 'response'->>'status_code' || ' ' || "type" || ': ' || ep_name AS metric,
COUNT(*) as rpm,
AVG(duration) as avg_latency,
MAX(duration) as max_latency,
percentile_cont(0.95) within group (order by duration) as "95th_percentile",
percentile_cont(0.99) within group (order by duration) as "99th_percentile"
FROM requests
WHERE session_id = %(session_id)s
GROUP BY 1,2,3
"""

send_requests_stats = """
INSERT INTO requests_stats (time, session_id, metric, rpm, avg_latency, max_latency, "95th_percentile", "99th_percentile")
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
