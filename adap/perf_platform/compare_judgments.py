"""
Select all judgments for a job_id from Builder
Verify counts match with ResultsDB
Verify judgment data is the same
"""

from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils.db import DBUtils
from adap.perf_platform.utils import helpers
from adap.settings import Config
from sqlalchemy import create_engine
import pandas as pd
import json

log = get_logger(__name__)

# resultsdb table where diffs will be written
RESULTS_TABLE_NAME = 'judgment_diffs'
# num rows selected for diff at a time
BATCH_SIZE = 100

index_field = 'external_id'
fields = [
    'external_id', 'unit_id', 'worker_id', 'ip',
    'city', 'region', 'country', 'data', 'logic'
    # 'workset_id' is skipped because theyre different in WUI and Builder
    ]

sql_count_judgments_from_builder = """
SELECT COUNT(*)
FROM public.judgments
WHERE job_id = %(job_id)s
"""

sql_count_judgments_from_resultsdb = """
SELECT COUNT(*)
FROM kafka_out
WHERE session_id = %(session_id)s
AND value -> 'metadata' ->> 'jobId' = %(job_id)s
"""

sql_select_external_ids_from_builder = """
SELECT external_id
FROM public.judgments
WHERE job_id = %(job_id)s
"""

sql_select_judgments_from_builder = """
SELECT j.*, jd.data, jd.logic
FROM public.judgments j
JOIN public.judgment_data jd
ON j.id = jd.judgment_id
WHERE j.job_id = %(job_id)s
"""

sql_select_judgments_batch_from_builder = ' AND '.join([
    sql_select_judgments_from_builder,
    "j.external_id IN %(ids)s"
    ])

sql_select_judgments_from_resultsdb = """
SELECT
value -> 'metadata' ->> 'judgmentId' as external_id,
value -> 'metadata' ->> 'unitId' as unit_id,
value -> 'workerData' ->> 'workerId' as worker_id,
value -> 'workerData' ->> 'worksetId' as workset_id,
value -> 'workerData' ->> 'workerRemoteIp' as ip,
value -> 'workerData' ->> 'city' as city,
value -> 'workerData' ->> 'region' as region,
value -> 'workerData' ->> 'country' as country,
value -> 'data'->> 'judgmentData' as data,
value -> 'data'-> 'judgmentData' ->> '_logic' as logic
FROM kafka_out
WHERE session_id = %(session_id)s
AND value -> 'metadata' ->> 'jobId' = %(job_id)s
"""

sql_select_judgments_batch_from_resultsdb = ' AND '.join([
    sql_select_judgments_from_resultsdb,
    "value -> 'metadata' ->> 'judgmentId' IN %(ids)s"
    ])

sql_add_cond_column = f"""
ALTER TABLE {RESULTS_TABLE_NAME}
ADD COLUMN "_cond" TEXT,
ADD COLUMN session_id BIGINT,
ADD COLUMN task_id BIGINT
"""

sql_single_rows = f"""(
SELECT {index_field}
FROM {RESULTS_TABLE_NAME}
WHERE session_id = {Config.SESSION_ID}
AND task_id = {Config.TASK_ID}
GROUP BY 1 HAVING COUNT(*) = 1
)"""

sql_update_cond_missing = f"""
UPDATE {RESULTS_TABLE_NAME} SET "_cond" = 'MISSING'
WHERE {index_field} in ({sql_single_rows})
AND "_merge" = 'left_only'
"""

sql_update_cond_new = f"""
WITH cte as {sql_single_rows}
UPDATE {RESULTS_TABLE_NAME} SET "_cond" = 'NEW'
WHERE {index_field} in ({sql_single_rows})
AND "_merge" = 'right_only'
"""


def chunk(data: list, chunk_size: int):
    """ Split data into batches of chunk_size """
    chunks = []
    start = 0
    end = chunk_size
    while start <= len(data) - 1:
        chunk = data[start:end]
        chunks.append(chunk)
        start += chunk_size
        end += chunk_size
    return chunks


def get_judgments_count_from_builder(job_id):
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        judgments_count = db.fetch_one(
            sql_count_judgments_from_builder,
            args={'job_id': job_id})
    log.info({
        'builder_judgments_count': judgments_count
    })
    return judgments_count[0]


def get_judgments_count_from_resultsdb(job_id):
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        judgments_count = db.fetch_one(
            sql_count_judgments_from_resultsdb,
            args={
                'session_id': Config.SESSION_ID,
                'job_id': str(job_id)
                })
    log.info({
        'resultsdb_judgments_count': judgments_count
    })
    return judgments_count[0]


def get_judgments_externalid_from_builder(job_id):
    log.info(f'Fetching judgment external_ids from Builder from job_id {job_id}')
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        external_ids = db.fetch_all(
            sql_select_external_ids_from_builder,
            args={'job_id': job_id},
            include_column_names=True
            )
    return external_ids


def get_judgments_data_from_builder(job_id, external_ids=[]):
    log.debug('Fetching judgments data from Builder')
    with DBUtils(**Config.BUILDER_DB_CONN) as db:
        if external_ids:
            judgments = db.fetch_all(
                sql_select_judgments_batch_from_builder,
                args={
                    'job_id': job_id,
                    'ids': tuple(external_ids)
                    },
                include_column_names=True
                )
        else:
            judgments = db.fetch_all(
                sql_select_judgments_from_builder,
                args={'job_id': job_id},
                include_column_names=True
                )
    return judgments


def get_judgments_data_from_resultsdb(job_id, external_ids=[]):
    log.debug('Fetching judgments data from ResultsDB')
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        if external_ids:
            judgments = db.fetch_all(
                sql_select_judgments_batch_from_resultsdb,
                args={
                    'session_id': Config.SESSION_ID,
                    'job_id': str(job_id),
                    'ids': tuple(external_ids)
                    },
                include_column_names=True)
        else:
            judgments = db.fetch_all(
                sql_select_judgments_from_resultsdb,
                args={
                    'session_id': Config.SESSION_ID,
                    'job_id': str(job_id)
                    },
                include_column_names=True)
    return judgments


def save_diffs_to_resultsdb(df_diff, if_exists='append'):
    # save df_diff to ResultsDB
    engine = create_engine(DBUtils(**Config.RESULTS_DB_CONN).uri)
    df_diff['_cond'] = 'mismatch'
    df_diff['session_id'] = int(Config.SESSION_ID)
    df_diff['task_id'] = int(Config.TASK_ID)
    df_diff.to_sql(
        RESULTS_TABLE_NAME,
        engine,
        index=True,
        method='multi',
        if_exists=if_exists)
    with DBUtils(**Config.RESULTS_DB_CONN) as db:
        db.execute(sql_update_cond_missing)
        db.execute(sql_update_cond_new)


def pass_through_json(x):
    """ Decode & Encode to ensure same formatting """
    return json.dumps(json.loads(x))


def diff_rows(rows0: list, rows1: list):
    assert rows0, 'rows0 cannot be empty'
    assert rows1, 'rows1 cannot be empty'
    df0 = pd.DataFrame(rows0)
    df1 = pd.DataFrame(rows1)
    df0 = df0[fields].set_index(index_field)
    df0 = df0.astype('object')
    df0['data'] = df0.data.apply(pass_through_json)
    df0['logic'] = df0.logic.apply(pass_through_json)
    df1 = df1[fields].set_index(index_field)
    df1 = df1.astype('object')
    df1['data'] = df1.data.apply(pass_through_json)
    df1['logic'] = df1.logic.apply(pass_through_json)
    df_diff = df0.merge(
        df1,
        how='outer',
        on=fields,
        indicator=True,
        suffixes=('_left', '_right'))
    df_diff = df_diff[df_diff._merge != 'both']
    save_diffs_to_resultsdb(df_diff)
    return df_diff
    # df_missing = df_diff.loc[~df_diff.index.duplicated(keep=False)]
    # df_mismatches = df_diff.loc[df_diff.index.duplicated(keep=False)]


def test_judgments_counts(job_id):
    """ Diff judgment counts for the job between Builder and ResultsDB """

    j_count_builder = get_judgments_count_from_builder(job_id)
    j_count_resultsdb = get_judgments_count_from_resultsdb(job_id)
    if j_count_builder == j_count_resultsdb:
        log.info({
            'compare_judment_counts': 'Counts match!',
            'builder_judgments_count': j_count_builder,
            'resultsdb_judgments_count': j_count_resultsdb
        })
    else:
        log.error({
            'compare_judment_counts': 'Counts do not match!',
            'builder_judgments_count': j_count_builder,
            'resultsdb_judgments_count': j_count_resultsdb
        })


def test_judgments_data(job_id):
    """ Diff judgments data for the job between Builder and ResultsDB """

    def assertion(df):
        if df.empty:
            log.info({
                'compare_judments': 'Judgments match!'
                })
        else:
            log.error({
                'compare_judments': 'Judgments do not match!'
                })

    external_ids = get_judgments_externalid_from_builder(job_id)
    assert external_ids, "No external_id rows returned"
    external_ids = [i['external_id'] for i in external_ids]

    # select and compare rows in batches
    batches = chunk(external_ids, BATCH_SIZE)
    for batch in batches:
        log.debug(f'Current batch size: {batch}')
        judgments_builder = get_judgments_data_from_builder(job_id, batch)
        assert judgments_builder, "No judgments returned from builder"
        judgments_resultsdb = get_judgments_data_from_resultsdb(job_id, batch)
        assert judgments_resultsdb, "No judgments returned from builder"
        for row in judgments_resultsdb:
            # remove "_logic" from "data" json blob, it's compared separately
            if row.get('logic'):
                row_data = json.loads(row.get('data'))
                row_data = {k: v for k, v in row_data.items() if k != '_logic'}
                row['data'] = json.dumps(row_data)
            else:
                row['logic'] = '{}'  # it's set to '{}' by deafult in Builder
        df_diff = diff_rows(judgments_builder, judgments_resultsdb)
        assertion(df_diff)


def main():
    job_id = helpers.get_job_id_from_tasks_info()
    test_judgments_counts(job_id)
    test_judgments_data(job_id)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e.__repr__())
        raise
