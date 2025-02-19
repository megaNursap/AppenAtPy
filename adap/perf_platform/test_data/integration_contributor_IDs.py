"""
Generating list of contributor user IDs that were
created and validated in Integration env
"""
import os
import pandas as pd
import decouple


def get():
    contributor_ids = []
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'integration_contributor_IDs.csv'))
    for index, row in df.iterrows():
        contributor_ids.append({"worker_id": row['worker_id'], "qa_1_worker_id": row['qa_1_worker_id']})

    return contributor_ids[:decouple.config('NUM_CLIENTS', default=len(contributor_ids), cast=int)]
