"""
Judgments module provides functionality to access job using internal link or
as an external contributor (using vcare channel by default)
"""
from adap.api_automation.utils.data_util import get_user
from adap.api_automation.utils.http_util import HttpMethod, ApiResponse
from adap.api_automation.utils.helpers import (
    find_authenticity_token,
    get_unit_markers_from_tasks)
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils import error_handler as eh
from adap.data.units.catdog_golden import catdog_golden_units
from adap.data.units import hands_vid_annotation as hva
from adap.settings import Config
from adap.api_automation.services_config.requestor_proxy import RP
from bs4 import BeautifulSoup
import gevent
import json
import uuid
import re
import requests
import random

log = get_logger(__name__)


def find_job_secret(tasks: str, job_id: str):
    """
    Find a secret for a job_id on tasks listing page (external access)
    """

    search_str = f"{job_id}.+?\]"
    task = re.findall(search_str, tasks)
    if task:
        job_secret = task[0].split(';')[-2].replace('&quot', '')
        return job_secret


def find_dynamic_values(page_text):
    """
    :param page_text: ApiResponse.text

    Returns:
    :tuple (assignment_id, form_data, tasks)
    :type assignment_id: str
    :type form_data: dict
    :type tasks: bs4.element.ResultSet
    """
    try:
        soup = BeautifulSoup(page_text, 'html.parser')
        form_data = {}
        form_data['authenticity_token'] = soup.find('input', {'name': 'authenticity_token'}).get('value')
        form_data['started_at_next'] = soup.find('input', {'name': 'started_at_next'}).get('value')
        form_data['started_at'] = soup.find('input', {'name': 'started_at'}).get('value')
        # ref: https://github.com/CrowdFlower/CrowdFlower/blob/master/projects/worker_ui/app/controllers/assignments_controller.rb#L309
        form_data['started_at_next'] = int(form_data['started_at_next']) ^ 1364934572
        assignment_id = soup.find('div', {'class': 'js-assignment-id hidden'}).get('data-assignment-id')
        tasks = soup.find_all('div', {'class': 'cml jsawesome'})
        return assignment_id, form_data, tasks
    except Exception as e:
        raise Exception({
            'message': 'Error getting dynamic values',
            'page_text': page_text,
            'exception': e.__repr__()
            })


def find_worker_id(page_text) -> int:
    try:
        soup = BeautifulSoup(page_text, 'html.parser')
        worker_id = int(soup.find('span', {'id': 'assignment-worker-id'}).text)
        return worker_id
    except Exception as e:
        log.error({
            'message': 'Error getting worker_id',
            'page_text': page_text,
            'exception': e.__repr__()
            })


def handler_what_is_greater(tasks):
    """
    :type task: bs4.element.Tag
    """
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name') for i in task.find_all('input')]))[0]
        q_values = task.find_all('p')
        v1 = float(q_values[0].text.split()[-1])
        v2 = float(q_values[1].text.split()[-1])
        if Config.RANDOM_JUDGMENT:
            ans = random.choice(['col1', 'col2'])
        else:  # correct answer
            if v1 > v2:
                ans = 'col1'
            elif v1 < v2:
                ans = 'col2'
            else:
                ans = 'equals'
        if Config.JUDGMENT_ACCURACY:
            if random.random() > Config.JUDGMENT_ACCURACY:
                ans = 'col1' if ans == 'col2' else 'col2'
        answers[_id] = ans

    return answers


def handler_tqg_what_is_greater(tasks):
    """
    :type task: bs4.element.Tag
    """
    # TODO
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        q_values = task.find_all('p')
        v1 = float(q_values[0].text.split()[-1])
        v2 = float(q_values[1].text.split()[-1])
        if v1 > v2:
            ans = 'col1'
        elif v1 < v2:
            ans = 'col2'
        else:
            ans = 'equals'
        answer = {
            f'{_id}[skip_question_reason]': '',
            f'{_id}[what_is_greater]': ans,
            f'{_id}[what_is_greater_reason]': 'some reason',
            f'{_id}[confirm_completion]': 'tq_confirm_completion',
        }

        _logic_fields = [
            "skip_this_question",
            "skip_question_reason",
            "what_is_greater",
            "what_is_greater_reason",
            "confirm_completion"
            ]
        _logic = {}
        for field in _logic_fields:
            _logic[field] = str(f'{_id}[{field}]' in answer).lower()

        answer[f'{_id}[_logic]'] = json.dumps(_logic)
        answers.update(answer)

    return answers


def handler_cat_or_dog(tasks):
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        image_url = re.findall(r'(?<={\"image_url\":\").+?(?=\")', task.text)[0]
        golden_unit = [u for u in catdog_golden_units if u.get('image_url') == image_url]
        if golden_unit:
            golden_unit = golden_unit[0]
            annotation = json.loads(golden_unit.get('annotation_gold'))
            list(map(lambda u: u.update({'id': uuid.uuid4().__str__()}), annotation))
            ans = {
                f"{_id}[annotation]": json.dumps(annotation),
                f"{_id}[_logic]": json.dumps({
                    "nothing_to_box": "true",
                    "annotation": "true"
                    })
                }
        else:
            annotation_template = {
                "id": uuid.uuid4().__str__(),
                "class": random.choice(["Cat", "Dog"]),
                "type": "box",
                "coordinates": {
                    "x": random.choice(range(100, 200)),
                    "y": random.choice(range(400, 500)),
                    "w": random.choice(range(150, 250)),
                    "h": random.choice(range(150, 250))
                    }
                }
            annotation = [annotation_template for i in range(Config.NUM_ANNOTATIONS_PER_UNIT)]
            ans = {
                f"{_id}[annotation]": json.dumps(annotation),
                f"{_id}[_logic]": json.dumps({
                    "nothing_to_box": "true",
                    "annotation": "true"
                    })
                }
        answers.update(ans)
    return answers


def handler_nab_meaning(tasks) -> dict:
    answers = {}
    for task in tasks:
        q_value = int(task.find(id='q_value').text)
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        _logic_fields = [
            "nab_meaning",
            "consumption_related",
            "ingredient",
            "category_related",
            ]
        if q_value < 500:
            # give correct answer
            if q_value < 100:
                ans = {
                    f'{_id}[nab_meaning]': 'no',
                    f'{_id}[category_related]': 'no'
                }
            elif q_value < 200:
                ans = {
                    f'{_id}[nab_meaning]': 'no',
                    f'{_id}[category_related]': 'yes'
                }
            elif q_value < 300:
                ans = {
                    f'{_id}[nab_meaning]': 'yes',
                    f'{_id}[consumption_related]': 'no'
                }
            elif q_value < 400:
                ans = {
                    f'{_id}[nab_meaning]': 'yes',
                    f'{_id}[consumption_related]': 'yes',
                    f'{_id}[ingredient]': 'no'
                }
            else:
                ans = {
                    f'{_id}[nab_meaning]': 'yes',
                    f'{_id}[consumption_related]': 'yes',
                    f'{_id}[ingredient]': 'yes'
                }
            _logic = {}
            for field in _logic_fields:
                _logic[field] = str(f'{_id}[{field}]' in ans).lower()
            ans[f'{_id}[_logic]'] = json.dumps(_logic)
        else:
            # TODO: give bad answer
            ans = {
                f'{_id}[nab_meaning]': 'no',
                f'{_id}[category_related]': 'yes'
            }
            _logic = {}
            for field in _logic_fields:
                _logic[field] = str(f'{_id}[{field}]' in ans).lower()
            ans[f'{_id}[_logic]'] = json.dumps(_logic)
        answers.update(ans)
    return answers


def handler_server_side_validation(tasks) -> dict:
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        _logic_fields = [
            "parent_question",
            "child_question_1",
            "child_question_2",
            "subchild_question_1",
            "subchild_question_2"
        ]
        ans = {
            f'{_id}[parent_question]': 'Second option',
            f'{_id}[child_question_1]': 'Second option',
            f'{_id}[child_question_2]': 'Second option',
            f'{_id}[subchild_question_1]': 'Second option',
            f'{_id}[subchild_question_2]': 'First option'
        }
        _logic = {}
        for field in _logic_fields:
            _logic[field] = str(f'{_id}[{field}]' in ans).lower()
        ans[f'{_id}[_logic]'] = json.dumps(_logic)
        answers.update(ans)
    return answers


def handler_server_side_validation_simple_case(tasks) -> dict:
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        # q_values = task.find_all('p')
        v1 = random.randint(1, 100)
        v2 = random.randint(1, 100)
        _logic_fields = [
            "field1",
            "field2",
            "field3"
        ]
        # all valid answers
        if Config.ANSWER_TYPE == 0:
            ans = {
                f'{_id}[field1]': 'Second option',
                f'{_id}[field2]': 'test all valid answers',
                f'{_id}[field3]': True
            }
        #  mix valid and invalid answers
        elif Config.ANSWER_TYPE == 1:
            if v1 > v2:
                ans = {
                    f'{_id}[field1]': 'Second option',
                    f'{_id}[field2]': 'test mix valid answers and invalid answers',
                    f'{_id}[field3]': True
                }
            else:
                ans = {
                    f'{_id}[field1]': 'Second option',
                    f'{_id}[field2]': '',
                    f'{_id}[field3]': False
                }
        # all invalid answers
        else:
            if v1 > v2:
                ans = {
                    f'{_id}[field1]': 'First option',
                    f'{_id}[field2]': '',
                    f'{_id}[field3]': False
                }
            elif v1 < v2:
                ans = {
                    f'{_id}[field1]': '',
                    f'{_id}[field2]': 'test invalid answers',
                    f'{_id}[field3]': False
                }
            else:
                ans = {
                    f'{_id}[field1]': '',
                    f'{_id}[field2]': '',
                    f'{_id}[field3]': False
                }
        _logic = {}
        for field in _logic_fields:
            _logic[field] = str(f'{_id}[{field}]' in ans).lower()
        ans[f'{_id}[_logic]'] = json.dumps(_logic)
        answers.update(ans)
    return answers


def handler_server_side_validation_liquid_case(tasks) -> dict:
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        q_values = task.find_all('p')
        v1 = str(q_values[0].text.split()[-1])
        v2 = str(q_values[1].text.split()[-1])
        log.info({
            'message': 'Start getting p value',
            'v1_value': v1,
            'v2_value': v2
        })
        _logic_fields = [
            "root",
            "foo",
            "field1",
            "field2",
            "optional_tag",
            "bar",
            "lorem_ipsum"
        ]

        test1_another_valid_answers = [{
            f'{_id}[root]': 'test',
            f'{_id}[foo]': 'baz',
            f'{_id}[field2]': 'test'
        },
            {
                f'{_id}[root]': 'test2',
                f'{_id}[foo]': 'baz2',
                f'{_id}[field2]': 'test2',
                f'{_id}[optional_tag]': 'test2'
            }
        ]
        test1_another_invalid_answers = [{
            f'{_id}[lorem_ipsum]': 'bar',
            f'{_id}[field2]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[bar]': 'bar2',
                f'{_id}[optional_tag]': 'test'
            }
        ]

        test2_another_valid_answers = [{
            f'{_id}[root]': 'test',
            f'{_id}[bar]': 'yes',
            f'{_id}[field2]': 'test'
        },
            {
                f'{_id}[root]': 'test2',
                f'{_id}[bar]': 'no',
                f'{_id}[field2]': 'test2',
                f'{_id}[optional_tag]': 'test2'
            }
        ]
        test2_another_invalid_answers = [{
            f'{_id}[lorem_ipsum]': 'bar',
            f'{_id}[field2]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[foo]': 'bar2',
                f'{_id}[optional_tag]': 'test'
            }
        ]

        another_test1_valid_answers = [{
            f'{_id}[root]': 'test',
            f'{_id}[lorem_ipsum]': 'test',
            f'{_id}[field1]': 'test'
        },
            {
                f'{_id}[root]': 'test2',
                f'{_id}[lorem_ipsum]': 'test2',
                f'{_id}[field1]': 'test2',
                f'{_id}[optional_tag]': 'test2'
            }
        ]
        another_test1_invalid_answers = [{
            f'{_id}[bar]': 'bar',
            f'{_id}[field2]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[foo]': 'bar2',
                f'{_id}[optional_tag]': 'test'
            }
        ]

        another_test2_valid_answers = [{
            f'{_id}[root]': 'test',
            f'{_id}[lorem_ipsum]': 'test',
            f'{_id}[field2]': 'test'
        },
            {
                f'{_id}[root]': 'test2',
                f'{_id}[lorem_ipsum]': 'test2',
                f'{_id}[field2]': 'test2',
                f'{_id}[optional_tag]': 'test2'
            }
        ]
        another_test2_invalid_answers = [{
            f'{_id}[bar]': 'bar',
            f'{_id}[field1]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[foo]': 'bar2',
                f'{_id}[optional_tag]': 'test'
            }
        ]

        test1_test1_valid_answers = [{
            f'{_id}[root]': 'foo',
            f'{_id}[foo]': 'bar',
            f'{_id}[field1]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[foo]': 'bar2',
                f'{_id}[field1]': 'baz2',
                f'{_id}[optional_tag]': 'test'
            }
        ]
        test1_test1_invalid_answers = [{
            f'{_id}[lorem_ipsum]': 'bar',
            f'{_id}[field2]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[bar]': 'bar2',
                f'{_id}[optional_tag]': 'test'
            }
        ]

        test2_test2_valid_answers = [{
            f'{_id}[root]': 'foo',
            f'{_id}[bar]': 'yes',
            f'{_id}[field2]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[bar]': 'no',
                f'{_id}[field2]': 'baz2',
                f'{_id}[optional_tag]': 'test'
            }
        ]
        test2_test2_invalid_answers = [{
            f'{_id}[lorem_ipsum]': 'bar',
            f'{_id}[field1]': 'baz'
        },
            {
                f'{_id}[root]': 'test',
                f'{_id}[bar]': 'bar2',
                f'{_id}[optional_tag]': 'test'
            }
        ]

        # all valid answers
        if Config.ANSWER_TYPE == 0:
            if v1 == 'test1' and v2 == 'another':
                ans = test1_another_valid_answers[random.randint(0, len(test1_another_valid_answers) - 1)]
            elif v1 == 'test2' and v2 == 'another':
                ans = test2_another_valid_answers[random.randint(0, len(test2_another_valid_answers) - 1)]
            elif v1 == 'another' and v2 == 'test1':
                ans = another_test1_valid_answers[random.randint(0, len(another_test1_valid_answers) - 1)]
            elif v1 == 'another' and v2 == 'test2':
                ans = another_test2_valid_answers[random.randint(0, len(another_test2_valid_answers) - 1)]
            elif v1 == 'test1' and v2 == 'test1':
                ans = test1_test1_valid_answers[random.randint(0, len(test1_test1_valid_answers) - 1)]
            else:
                ans = test2_test2_valid_answers[random.randint(0, len(test2_test2_valid_answers) - 1)]
                #  mix valid and invalid answers
        elif Config.ANSWER_TYPE == 1:
            # valid answers
            if v1 == 'test1' and v2 == 'another':
                log.info({
                    'inside_v1_value': v1,
                    'inside_v2_value': v2
                })
                ans = test1_another_valid_answers[random.randint(0, len(test1_another_valid_answers) - 1)]
            elif v1 == 'test2' and v2 == 'another':
                ans = test2_another_valid_answers[random.randint(0, len(test2_another_valid_answers) - 1)]
            elif v1 == 'another' and v2 == 'test1':
                ans = another_test1_valid_answers[random.randint(0, len(another_test1_valid_answers) - 1)]
            elif v1 == 'another' and v2 == 'test2':
                ans = another_test2_invalid_answers[random.randint(0, len(another_test2_invalid_answers) - 1)]
            elif v1 == 'test1' and v2 == 'test1':
                ans = test1_test1_invalid_answers[random.randint(0, len(test1_test1_invalid_answers) - 1)]
            else:
                ans = test2_test2_invalid_answers[random.randint(0, len(test2_test2_invalid_answers) - 1)]
        # all invalid answers
        else:
            if v1 == 'test1' and v2 == 'another':
                log.info({
                    'inside_v1_value': v1,
                    'inside_v2_value': v2
                })
                ans = test1_another_invalid_answers[random.randint(0, len(test1_another_invalid_answers) - 1)]
            elif v1 == 'test2' and v2 == 'another':
                ans = test2_another_invalid_answers[random.randint(0, len(test2_another_invalid_answers) - 1)]
            elif v1 == 'another' and v2 == 'test1':
                ans = another_test1_invalid_answers[random.randint(0, len(another_test1_invalid_answers) - 1)]
            elif v1 == 'another' and v2 == 'test2':
                ans = another_test2_invalid_answers[random.randint(0, len(another_test2_invalid_answers) - 1)]
            elif v1 == 'test1' and v2 == 'test1':
                ans = test1_test1_invalid_answers[random.randint(0, len(test1_test1_invalid_answers) - 1)]
            else:
                ans = test2_test2_invalid_answers[random.randint(0, len(test2_test2_invalid_answers) - 1)]

        _logic = {}
        for field in _logic_fields:
            _logic[field] = str(f'{_id}[{field}]' in ans).lower()
        ans[f'{_id}[_logic]'] = json.dumps(_logic)
        answers.update(ans)
    return answers


def handler_server_side_validation_complicated_case(tasks) -> dict:
    answers = {}
    for task in tasks:
        _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
        v1 = random.randint(1, 100)
        v2 = random.randint(1, 100)
        _logic_fields = [
            "root",
            "depth2",
            "depth3",
            "depth4",
            "root_and",
            "and_clause_mon_openallday",
            "and_clause_tue_openallday",
            "and_clause_wed_openallday",
            'and_clause_wed_open_1',
            'and_clause_wed_close_1',
            'and_clause_wed_open_2',
            'and_clause_wed_close_2',
            "and_clause_thu_openallday",
            "and_clause_fri_openallday",
            "and_clause_sat_closedallday",
            "and_clause_sun_closedallday",
            "group_field",
            "or_clause"
        ]
        valid_answers = [{
            f'{_id}[root]': 'yes',
            f'{_id}[depth2]': ['human'],
            f'{_id}[depth3]': 'depth3',
            f'{_id}[depth4]': 'depth4',
            f'{_id}[root_and]': 'baz',
        },
            {
                f'{_id}[root]': 'no',
                f'{_id}[root_and]': 'baz',
                f'{_id}[group_field]': 'bar',
                f'{_id}[or_clause]': 'or_clause',
            },
            {
                f'{_id}[root]': 'yes',
                f'{_id}[depth2]': ['dog'],
                f'{_id}[root_and]': 'baz',
                f'{_id}[and_clause_mon_openallday]': 'TRUE',
                f'{_id}[and_clause_tue_openallday]': 'TRUE',
                f'{_id}[and_clause_wed_open_1]': '09:00',
                f'{_id}[and_clause_wed_close_1]': '12:00',
                f'{_id}[and_clause_wed_open_2]': '13:00',
                f'{_id}[and_clause_wed_close_2]': '18:00',
                f'{_id}[and_clause_thu_openallday]': 'TRUE',
                f'{_id}[and_clause_fri_openallday]': 'TRUE',
                f'{_id}[and_clause_sat_closedallday]': 'TRUE',
                f'{_id}[and_clause_sun_closedallday]': 'TRUE',
            }
        ]
        invalid_answers = [{
            f'{_id}[root]': 'yes',
            f"{_id}[depth2]": ['human', 'dog'],
            f'{_id}[depth3]': 'foo',
            f'{_id}[root_and]': 'baz',
        },
            {
                f'{_id}[root]': 'yes',
                f'{_id}[depth3]': 'depth3',
                f'{_id}[and_clause_mon_openallday]': 'TRUE',
                f'{_id}[group_field]': 'group_field',
                f'{_id}[or_clause]': 'or_clause',
            },
            {
                f'{_id}[root]': 'no',
                f'{_id}[depth4]': 'foo',
                f'{_id}[root_and]': 'test',
            }
        ]
        # all valid answers
        if Config.ANSWER_TYPE == 0:
            ans = valid_answers[random.randint(0, len(valid_answers) - 1)]
        #  mix valid and invalid answers
        elif Config.ANSWER_TYPE == 1:
            # valid answers
            if v1 > v2:
                ans = valid_answers[random.randint(0, len(valid_answers) - 1)]
            # invalid answer
            else:
                ans = invalid_answers[random.randint(0, len(invalid_answers) - 1)]
        # all invalid answers
        else:
            ans = invalid_answers[random.randint(0, len(invalid_answers) - 1)]
        _logic = {}
        for field in _logic_fields:
            _logic[field] = str(f'{_id}[{field}]' in ans).lower()
        ans[f'{_id}[_logic]'] = json.dumps(_logic)
        answers.update(ans)
    return answers


def handler_video_found_yn(tasks):
    return 'Yes'


def text_annotation(text):
    words = text.split()
    tokens = [text_token(text, word) for word in words]
    spans = [text_span(token) for token in tokens]
    res = {
      "text": text,
      "tokens": tokens,
      "spans": spans,
      "allow_nesting": False
    }
    return res


def text_span(token):
    ontology_classes = ['verb', 'noun', 'other', 'punctuation', 'none']
    token_span = {
        "id": uuid.uuid4().__str__(),
        "tokens": [token],
        "annotated_by": 'human',
        "parent": None,
        "children": [],
        "class_names": [random.choice(ontology_classes)]
    }
    return token_span


def text_token(text, str):
    idx = text.index(str)
    return { "token": str, "startIdx": idx, "endIdx": idx+len(str) }


def is_work_available(assignment):
    """
    Ensure that current assignment page allows to do work

    :param assignment: ApiResponse
    """
    page_text = assignment.text

    available_msg = "Working on Task"
    unavailable_msgs = [
        "You've completed all your work!",
        "There is no work currently available in this task",
        "You have done the maximum amount of work on this job"
    ]
    bummer_msgs = ['An error occurred', 'Bummer']
    if available_msg in page_text:
        return True
    elif any([t in page_text for t in unavailable_msgs]):
        return False
    elif all([t in page_text for t in bummer_msgs]):
        eh.handle("Bummer")
    else:
        raise Exception({
            'message': 'Invalid assignment page',
            'page_text': page_text,
            'url': assignment.url,
            'status_code': assignment.status_code
            })


def is_temp_unavailable(page_text: str):
    temprorary_unavailable_messages = [
        "Task not yet available",
        # "There is no work currently available in this task"
    ]
    return any(map(lambda msg: msg in page_text, temprorary_unavailable_messages))


def is_work_complete(page_text: str):
    return "You've completed all your work!" in page_text or \
           "There is no work currently available in this task" in page_text


class Judgments:
    def __init__(self, worker_email, worker_password, **kwargs):
        """
        E2E working session of one contributor on one job

        Args:
        worker_email (str): Contributor's email
        worker_password (str): Contributor's password

        Kwargs:
        env (str): Environment (qa,stage etc.)
        internal (bool): If job is accessed via internal link; default: False
        external_channel (str): External channel name (if external)
        service (HttpMethod obj): if not supplied, new instance is created
        session (bool): When new HttpMethod is created,
                        whether to use requests.Session()
        wait_interval (int): Seconds to wait before retry; default 30

        """
        self.env = kwargs.get('env')
        self.internal = kwargs.get('internal')
        self.external_channel = kwargs.get('external_channel') or 'vcare'
        if session := kwargs.get('session') is None:
            session = True
        self.service = kwargs.get('service') or HttpMethod(session=session)
        # self.service.request.max_redirects = 60
        self.wait_interval = kwargs.get('wait_interval') or 30
        self.worker_email = worker_email
        self.worker_password = worker_password

        self.signin_form_data = {
                                    "session[email]": worker_email,
                                    "session[password]": worker_password,
                                    "commit": "Sign In",
                                    "authenticity_token": 'changeme'
                                }
        self.header = {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Pragma": "no-cache"
                    }

        self.ch_cookie_name = f'_ch_v3_{self.external_channel}'
        self.job_id = None
        self.worker_id = None
        self.base_url = None

        if self.env == 'integration':
            self.requestor_proxy_url = f"https://requestor-proxy.{self.env}.cf3.work"
        else:
            self.requestor_proxy_url = f"https://requestor-proxy.{self.env}.cf3.us"

    def get_assignments(self, *args, **kwargs):
        if self.internal:
            return self.sign_in_internal(*args, **kwargs)
        else:
            return self.sign_in_external(*args, **kwargs)

    def sign_in_internal(self, job_id: int, internal_job_url: str) -> ApiResponse:
        """
        Access job's page using internal link
        Returns assignments page (ApiResponse)
        """
        self.job_id = job_id
        self.base_url = internal_job_url.split('/channels')[0]    
        c_wait = 0
        while c_wait < Config.MAX_WAIT_TIME:
            job_resp = self.service.get(
                        internal_job_url,
                        headers=self.header,
                        allow_redirects=True,
                        ep_name='internal_job_url')
            # sign in to ADAP
            if '/sessions/new' in job_resp.url:
                self.signin_form_data['authenticity_token'] = find_authenticity_token(job_resp.content)
                signed_internal = self.service.post(
                    f'{self.base_url}/sessions',
                    allow_redirects=True,
                    headers=self.header,
                    data=self.signin_form_data,
                    cookies=job_resp.cookies,
                    ep_name='/sessions'
                    )
            # sign in to ADAP with SSO (Keycloak)
            elif 'identity' in job_resp.url:
                soup = BeautifulSoup(job_resp.text, 'html.parser')
                kc_login_url = soup.find('form', {'id': 'kc-form-login'}).get('action')
                signin_form_data = {
                    'username': self.worker_email,
                    'password': self.worker_password,
                    'credentialId': None
                }
                signed_internal = self.service.post(
                    kc_login_url,
                    allow_redirects=True,
                    data=signin_form_data,
                    headers=self.header,
                    cookies=job_resp.cookies
                )
            else:
                raise Exception({
                    'message': 'Something is wrong',
                    'worker_email': self.worker_email,
                    'link': internal_job_url,
                    'status_code': job_resp.status_code,
                    'resp content': job_resp.text
                })
            # Check if work is available
            if is_work_available(signed_internal):
                self.worker_id = find_worker_id(signed_internal.content)
                return signed_internal
            elif is_temp_unavailable(job_resp.text):
                log.info({
                    'message': 'No work currently available',
                    'worker_email': self.worker_email,
                    'info': f'sleeping {self.wait_interval} seconds and retry',
                    'text': job_resp.text
                    })
                gevent.sleep(self.wait_interval)
                c_wait += self.wait_interval
                continue
        raise Exception({
            'message': 'Failed to get first assignment',
            'worker_email': self.worker_email,
            'info': 'Max wait time exceeded '
            })

    def sign_in_external(self, job_id: int) -> ApiResponse:
        """
        Access external_channel tasks page
        Returns assignments page (ApiResponse)
        """
        if not self.base_url:
            self.base_url = f'https://account.{self.env}.cf3.us'
        self.job_id = job_id
        c_wait = 0
        while c_wait < Config.MAX_WAIT_TIME:
            tasks_page_url = f'{self.base_url}/channels/{self.external_channel}/tasks?uid={self.worker_email}'
            tasks_headers = self.header.copy()
            tasks_headers['Cookie'] = 'cookies_enabled=true;'
            tasks_resp = self.service.get(
                tasks_page_url,
                headers=tasks_headers,
                ep_name='tasks_page_url')

            # Access job's page using link from the tasks page
            job_secret = find_job_secret(tasks_resp.text, job_id)
            if job_secret:
                job_url = f'{self.base_url}/channels/{self.external_channel}/tasks/{job_id}?secret={job_secret}'
                job_headers = self.header.copy()
                job_headers['Cookie'] = "cookies_enabled=true; " \
                    f"{self.ch_cookie_name}={tasks_resp.cookies.get(self.ch_cookie_name)};"
                job_resp = self.service.get(
                    job_url,
                    allow_redirects=True,
                    headers=job_headers,
                    ep_name='external_job_url')
            else:
                log.info({
                    'message': 'Job not found on tasks page',
                    'job_id': job_id,
                    'tasks_page_url': tasks_page_url,
                    'info': f'sleeping {self.wait_interval} seconds and retry'
                    })
                gevent.sleep(self.wait_interval)
                c_wait += self.wait_interval
                continue
            # sign in to ADAP
            if 'sessions/new' in job_resp.url:
                self.signin_form_data['authenticity_token'] = find_authenticity_token(job_resp.content)
                sign_in_cookies = {
                    '_worker_ui_session': job_resp.cookies.get('_worker_ui_session'),
                    self.ch_cookie_name: tasks_resp.cookies.get(self.ch_cookie_name)
                }
                signed_external = self.service.post(
                    f'{self.base_url}/sessions',
                    allow_redirects=True,
                    headers=self.header,
                    data=self.signin_form_data,
                    cookies=sign_in_cookies,
                    ep_name='/sessions'
                    )
            # sign in to ADAP with SSO (Keycloak)
            elif 'identity-service' in job_resp.url:
                soup = BeautifulSoup(job_resp.text, 'html.parser')
                kc_login_url = soup.find('form', {'id': 'kc-form-login'}).get('action')
                signin_form_data = {
                    'username': self.worker_email,
                    'password': self.worker_password,
                    'credentialId': None
                }
                sign_in_cookies = {
                    '_worker_ui_session': job_resp.cookies.get('_worker_ui_session'),
                    self.ch_cookie_name: tasks_resp.cookies.get(self.ch_cookie_name)
                }
                signed_external = self.service.post(
                    kc_login_url,
                    allow_redirects=True,
                    data=signin_form_data,
                    headers=self.header,
                    cookies=sign_in_cookies
                )
            else:
                raise Exception({
                    'message': 'Something is wrong',
                    'worker_email': self.worker_email,
                    'status_code': job_resp.status_code,
                    'resp content': job_resp.text
                })
            if is_work_available(signed_external):
                self.worker_id = find_worker_id(signed_external.content)
                return signed_external
            elif is_temp_unavailable(job_resp.text):
                log.info({
                    'message': 'No work currently available',
                    'worker_email': self.worker_email,
                    'info': f'sleeping {self.wait_interval} seconds and retry'
                    })
                gevent.sleep(self.wait_interval)
                c_wait += self.wait_interval
                continue
        raise Exception({
            'message': 'Failed to get first assignment',
            'worker_email': self.worker_email,
            'info': 'Max wait time exceeded'
            })

    def handler_hands_video(self, tasks):
        answers = {}
        units_annotations = {}
        for task in tasks:
            _id = list(set([i.get('name') for i in task.find_all('input')]))
            assert len(_id) == 1
            _id = _id[0]
            unitId = re.findall(r"[0-9]+", _id)[0]

            video_info_url = f"{self.requestor_proxy_url}/contributor_proxy/v1/video_info?unitId={unitId}"
            video_info = self.service.get(
                video_info_url,
                headers=self.header,
                ep_name='get_video_info')
            assert video_info.status_code == 200, video_info.content
            frameCount = video_info.json_response['frameCount']
            videoId = video_info.json_response['videoId']
            gevent.sleep(1)

            # GET ml-assisted prediction, for random units
            prediction_url = f'{self.requestor_proxy_url}/contributor_proxy/v1/video/{videoId}/predict_box'
            if random.random() < float(Config.PREDICT_BOX_RATE):
                predicted = 1
                params = hva.prediction_params
                while True:
                    if frameCount - predicted < 10:
                        params['trackedFrameCount'] = frameCount - predicted
                    prediction = self.service.get(
                        prediction_url,
                        headers=self.header,
                        params=params,
                        ep_name='predict_box')
                    assert prediction.status_code == 200, prediction.content
                    predicted += params['trackedFrameCount']
                    if predicted == frameCount:
                        break
                    last_frame = prediction.json_response[-1]
                    params = hva.next_prediction_params(last_frame)

            # annotations are hard-coded
            annotations = [hva.frame_annotation for f in range(frameCount)]
            annotationData = {
                'annotation': annotations,
                'jobId': self.job_id,
                'unitId': unitId,
                'workerId': self.worker_id
            }
            units_annotations[_id] = annotationData

        save_annotation_url = f'{self.requestor_proxy_url}/contributor_proxy/v1/video/save_annotation'
        save_annotation_header = self.header.copy()
        save_annotation_header['Content-Type'] = 'application/json'
        for _id, annotationData in units_annotations.items():
            save_annotation = self.service.post(
                save_annotation_url,
                headers=save_annotation_header,
                data=json.dumps(annotationData),
                ep_name='save_annotation'
                )
            assert save_annotation.status_code == 200, save_annotation.content
            annotation_url = save_annotation.json_response['url']
            answers[_id] = annotation_url

        return answers

    def handler_text_annotation(self, tasks):
        answers = {}
        _jwt_token = get_user('perf_platform')['jwt_token']
        rp = RP(_jwt_token, env=Config.ENV)
        for task in tasks:
            _id = list(set([i.get('name').split('[')[0] for i in task.find_all('input')]))[0]
            _script = task.find_all('script')[-1].text
            _job_id = re.search('"job_id":"([^,]*)",', _script).group(1)
            _unit_id = re.search('"unit_id":"([^,]*)",', _script).group(1)
            text = task.find_all('span', {'class': 'input_text'})[0].text
            stored_annotation = { 
                "format": "json",
                "jobId": int(_job_id),
                "unitId": _unit_id,
                "workerId": self.worker_id,
                "annotation": text_annotation(text) 
            }
            super_saver_res = rp.post_contributor_proxy_save_annotation_text_annotation(stored_annotation)
            annotation = super_saver_res.json_response
            ans = { f"{_id}[annotation]": json.dumps(annotation) }
            answers.update(ans)
        return answers

    def make_judgments(self, tasks: list) -> dict:
        """
        Apply handler function to each task in tasks list to get correct answers
        :param tasks: set of tasks (units) from assignent page, identified by class='cml jsawesome'
        :type tasks: bs4.element.ResultSet
        """

        job_types_map = {
            'what_is_greater': handler_what_is_greater,
            'TQG_what_is_greater': handler_tqg_what_is_greater,
            'nab_meaning': handler_nab_meaning,
            'image_annotation': handler_cat_or_dog,
            'server_side_validation': handler_server_side_validation,
            'server_side_validation_simple_case': handler_server_side_validation_simple_case,
            'server_side_validation_complicated_case': handler_server_side_validation_complicated_case,
            'server_side_validation_liquid_case': handler_server_side_validation_liquid_case,
            'text_annotation': self.handler_text_annotation,
            'video_annotation': self.handler_hands_video
        }
        handler = job_types_map.get(Config.JOB_TYPE)
        assert handler is not None, 'Handler not found for ' \
                                    f'job type {Config.JOB_TYPE} ' \
                                    f'Available types are {job_types_map}'
        return handler(tasks)

    def contribute(self, assignment: ApiResponse, num_assignments=None):
        """
        Submit judgments as long as there's work available
        """

        log.info({
            'message': 'starting work on assignments',
            'worker_email': self.worker_email,
            'job_id': self.job_id
            })
        cur_num_assignments = 0
        while status := is_work_available(assignment):
            assignment_id, form_data, tasks = find_dynamic_values(assignment.content)
            if Config.WAIT_IDLE_TIME > 0:
                log.info({
                    'message': f'wait  {Config.WAIT_IDLE_TIME} secs before make judgment',
                    'worker_email': self.worker_email,
                    'assignment_id': assignment_id
                })
                gevent.sleep(Config.WAIT_IDLE_TIME)
            answers = self.make_judgments(tasks)
            # unit_markers = get_unit_markers_from_tasks(tasks)
            form_data.update(answers)
            form_data['_method'] = 'put'
            if self.internal:
                form_data['cf_internal'] = 'true'
            assignment_url = f'{self.base_url}/assignments/' + assignment_id
            try:
                gevent.sleep(Config.WAIT_ON_ASSIGNMENT)
                log.info({
                    'message': 'submitting judgment',
                    'worker_email': self.worker_email,
                    'assignment_id': assignment_id
                    # 'unit_markers': unit_markers
                    })
                submit_resp = self.service.post(
                    assignment_url,
                    headers=self.header,
                    data=form_data,
                    allow_redirects=True,
                    ep_name='assignment_url')
            except requests.exceptions.TooManyRedirects:
                log.error({
                    'message': 'Caught requests.exceptions.TooManyRedirects\n',
                    'info': assignment_url
                    })
                gevent.sleep(10)
                break
            err_msg = "Something went wrong," \
                f"Response text: {submit_resp.text}\n\n"
            # assert submit_resp.status_code == 200, err_msg
            assert submit_resp.url != assignment.url, err_msg
            assignment = submit_resp
            cur_num_assignments += 1
            if is_work_complete(assignment.text):
                log.info({
                    'message': 'All work is done',
                    'worker_email': self.worker_email
                    })
                break
            elif Config.WORKER_RANDOM_EXIT is not None:
                if random.random() < float(Config.WORKER_RANDOM_EXIT):
                    log.info({
                        'message': 'Worker exited randomly',
                        'worker_email': self.worker_email
                        })
                    break
            elif num_assignments and cur_num_assignments >= num_assignments:
                    log.info({
                        'message': 'Required number of assignments has been submitted\n',
                        'worker_email': self.worker_email
                        })
                    break

        else:
            if status is None:
                m = 'Worker exited due to Bummer\n\n'
            else:
                m = 'Worker exited because there is no work available\n'
            log.error({
                'message': m,
                'worker_email': self.worker_email
                })
