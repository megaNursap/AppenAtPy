""" Units data generator """

from adap.data.units.catdog_golden import catdog_golden_units
from adap.settings import Config
import pandas as pd
import random
import json
import uuid


def get_answers_list(col1: list, col2: list) -> list:
    answers = []
    assert len(col1) == len(col2)
    for i, e1 in enumerate(col1):
        e2 = col2[i]
        if e1 > e2:
            answers.append('col1')
        elif e1 < e2:
            answers.append('col2')
        else:
            answers.append('equals')
    return answers


def generate_csv_data_what_is_greater(num_units, filename='/tmp/job_data.csv', gold=False):
    """ Write a csv file with data """

    col1 = [random.randint(1, 1000) for i in range(num_units)]
    col2 = [random.randint(1, 1000) for i in range(num_units)]
    d = {
        'column_1': col1,
        'column_2': col2,
        'marker': [uuid.uuid4().__str__() for i in range(num_units)]
    }
    if gold:
        golds = {
            '_golden': ['true' for i in range(num_units)],
            'what_is_greater_gold': get_answers_list(col1, col2),
            'what_is_greater_gold_reason': ['reason' for i in range(num_units)]
        }
        d.update(golds)
    df = pd.DataFrame(data=d)
    df.to_csv(filename, index=False)
    return filename


def generate_csv_data_catdog(num_units, filename='/tmp/job_data.csv', gold=False):
    """ Write a csv file with data """

    if gold:
        units = []
        for i in range(num_units):
            unit = random.choice(catdog_golden_units).copy()
            unit['_golden'] = 'true'
            unit['nothing_to_box_gold'] = None
            unit['nothing_to_box_gold_reason'] = None
            unit['annotation_gold_reason'] = 'reason'
            annotations = json.loads(unit.get('annotation_gold'))
            annotations_new = []
            for annotation in annotations:
                annotation['id'] = uuid.uuid4().__str__()
                annotations_new.append(annotation)
            unit['annotation_gold'] = json.dumps(annotations_new)
            units.append(unit)
        df = pd.DataFrame(data=units)
        df.to_csv(filename, index=False)
    else:
        csv_fn = f'{Config.APP_DIR}/data/units/catdog.csv'
        df = pd.read_csv(csv_fn)
        _range = range(df.size)
        df_new = pd.DataFrame()
        for i in range(num_units):
            index = random.choice(_range)
            df_new = df_new.append(df.iloc[index])
        df_new['marker'] = [uuid.uuid4().__str__() for i in range(num_units)]
        df_new.to_csv(filename, index=False)

    return filename


def generate_csv_data_liquid(num_units, filename='/tmp/job_data.csv'):
    """ Write a csv file with data """
    csv_fn = f'{Config.APP_DIR}/data/units/liquid.csv'
    df = pd.read_csv(csv_fn)
    _range = range(df.size)
    df_new = pd.DataFrame()
    for i in range(num_units):
        index = random.randint(0, 5)
        df_new = df_new.append(df.iloc[index])
    df_new.to_csv(filename, index=False)
    return filename


def generate_csv_data_nab_meaning(num_units, filename='/tmp/job_data.csv', gold=False):
    """ Write a csv file with data """

    if gold:
        d = []
        for i in range(num_units):
            inclusion = random.randint(1, 499)
            unit = {
                'inclusion': inclusion,
                'message': "Alice's Tea Time",
                '_golden': 'true',
                'nab_meaning_gold': None,
                'nab_meaning_gold_reason': None,
                'consumption_related_gold': None,
                'consumption_related_gold_reason': None,
                'ingredient_gold': None,
                'ingredient_gold_reason': None,
                'category_related_gold': None,
                'category_related_gold_reason': None,
            }
            if inclusion < 100:
                unit.update({
                    'nab_meaning_gold': 'no',
                    'nab_meaning_gold_reason': 'reason',
                    'category_related_gold': 'no',
                    'category_related_gold_reason': 'reason'
                })
            elif inclusion < 200:
                unit.update({
                    'nab_meaning_gold': 'no',
                    'nab_meaning_gold_reason': 'reason',
                    'category_related_gold': 'yes',
                    'category_related_gold_reason': 'reason'
                })
            elif inclusion < 300:
                unit.update({
                    'nab_meaning_gold': 'yes',
                    'nab_meaning_gold_reason': 'reason',
                    'consumption_related_gold': 'no',
                    'consumption_related_gold_reason': 'reason'
                })
            elif inclusion < 400:
                unit.update({
                    'nab_meaning_gold': 'yes',
                    'nab_meaning_gold_reason': 'reason',
                    'consumption_related_gold': 'yes',
                    'consumption_related_gold_reason': 'reason',
                    'ingredient_gold': 'no',
                    'ingredient_gold_reason': 'reason'
                })
            else:
                unit.update({
                    'nab_meaning_gold': 'yes',
                    'nab_meaning_gold_reason': 'reason',
                    'consumption_related_gold': 'yes',
                    'consumption_related_gold_reason': 'reason',
                    'ingredient_gold': 'yes',
                    'ingredient_gold_reason': 'reason'
                })
            d.append(unit)
    else:
        inclusion = [random.randint(1, 1000) for i in range(num_units)]
        d = {
            'inclusion': inclusion,
            'message': "Alice's Tea Time"
        }

    df = pd.DataFrame(data=d)
    df.to_csv(filename, index=False)
    return filename


def generate_csv_data_hands(num_units, filename='/tmp/job_data.csv', gold=False):

    if gold:
        raise Exception("This generator does not support golden units")
    if Config.VIDEO_SIZE:
        video_link = 'https://annotation-sandbox.s3.amazonaws.com/puppies-segs/{_size}/seg_{_id}.mp4'
        annotation_link = 'https://annotation-sandbox.s3.amazonaws.com/puppies-segs/{_size}/annotations/seg_{_id}.json'
        if Config.VIDEO_SIZE == 1:
            available_units = range(246)
        elif Config.VIDEO_SIZE == 25:
            available_units = range(10)
        elif Config.VIDEO_SIZE == 125:
            available_units = range(2)
        elif Config.VIDEO_SIZE == 246:
            available_units = range(1)
        elif Config.VIDEO_SIZE == 984:
            available_units = range(1)
    else:
        video_link = 'https://annotation-sandbox.s3.amazonaws.com/puppies-segs/seg_{_id}.mp4'
        annotation_link = 'https://annotation-sandbox.s3.amazonaws.com/puppies-segs/annotations/seg_{_id}.json'
        available_units = range(10)

    videos = []
    annotations = []
    for i in range(num_units):
        _id = random.choice(available_units)
        videos.append(video_link.format(_id=_id, _size=Config.VIDEO_SIZE))
        annotations.append(annotation_link.format(_id=_id, _size=Config.VIDEO_SIZE))

    data = {
        'video_link': videos,
        'annotation': annotations
    }
    df = pd.DataFrame(data=data)
    df.to_csv(filename, index=False)
    return filename

# find JEOPARDY_CSV_cleaned.csv in sharepoint:
# https://appencorp.sharepoint.com/:x:/t/Technology/ESq_VchaRyhBqRH2hpe9t_QBCnBNw6mPXdprko1iYWKkog?e=8LlI4C
def generate_csv_data_text_annotation(num_units, filename='/tmp/job_data.csv', gold=False):

    if gold:
        raise Exception("This generator does not support golden units")
    else:
        csv_fn = f'{Config.APP_DIR}/data/units/JEOPARDY_CSV_cleaned.csv'
        df = pd.read_csv(csv_fn)
        _range = range(df.size)
        df_new = pd.DataFrame()
        for i in range(num_units):
            if i < df.size:
                index = i
            else:
                index = random.choice(_range)
            df_new = df_new.append(df.iloc[index])
        df_new['marker'] = [uuid.uuid4().__str__() for i in range(num_units)]
        df_new.to_csv(filename, index=False)

    return filename

