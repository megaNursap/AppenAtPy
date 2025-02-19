import pytest

from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.ac_sme import SME

# not working, only for local run
# pytestmark = [pytest.mark.regression_ac, pytest.mark.ac_api_sme, pytest.mark.ac_api_sme_find_project]
#
SME_API = SME()

def test_find_projects_happy_path():
    payload = {
      "workerId": "499274",
      "useCase": "churnedWorkers",
      "maxReturnCount": 20,
      "hireGapThreshold": 0.1,
      "project_types": [
        "TRANSCRIPTION"
      ],
      "languages": [
        {
          "language_from": "eng",
          "country_from": "USA"
        }
      ]
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)
    assert res.json_response['success']
    print(len(res.json_response['projects']))


def test_verify_project_info(ac_api_cookie_no_customer):
    payload = {
        "workerId": "499274",
        "maxReturnCount": 2,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)

    matched_project = res.json_response['projects']
    assert len(matched_project) > 0

    api = AC_API(ac_api_cookie_no_customer)
    for project in matched_project:
        _id = project['projectId']
        _name = project['projectName']
        _alias = project['projectAlias']

        _res = api.get_project_by_id(_id)
        _res.assert_response_status(200)

        assert _res.json_response["id"] == _id
        assert _res.json_response['name'] == _name
        assert _res.json_response['alias'] == _alias


@pytest.mark.parametrize('worker_id, expected_status',
                         [('abcd', 200),
                          ('__', 200),
                          (' 499274', 200),
                          ('10000000000000000000', 200),
                          ('0000', 200),
                          ('123', 200),
                          ('1000000000000000000', 200)
                          ])
def test_worker_id_not_valid(worker_id, expected_status):
    payload = {
        "workerId": worker_id,
        "maxReturnCount": 2,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(expected_status)
    assert res.json_response['status'] == 'WORKER_DOES_NOT_EXIST_IN_ES'
    assert not res.json_response['success']
    assert res.json_response['reasons'][0] == "Worker {} not found!".format(worker_id)



# @pytest.mark.skip(reason='Bug! ')
def test_max_return_count():
    # TODO find worker with a lot of projects or create projects
    for count in [0, 5, 10, 20, 25, 100]:
        payload = {
            "workerId": "499274",
            "useCase": "churnedWorkers",
            "maxReturnCount": count,
            "hireGapThreshold": 0.1
        }
        res = SME_API.find_projects(payload)
        assert len(res.json_response['projects']) <= count


def test_no_project_found():

    _worker_id = 590672
    payload = {
        "workerId": _worker_id,
        "maxReturnCount": 1,
        "hireGapThreshold": 0.1
    }
    res = SME_API.find_projects(payload)
    res.assert_response_status(200)
    assert res.json_response['success']
    assert res.json_response['reasons'][0] == "Worker %s has no matched projects" % _worker_id
    assert res.json_response['projects'] == []
    assert res.json_response['status'] == "NO_PROJECT_MATCH"


# @pytest.mark.parametrize('payload, expected_status',
#                          [({}, 422),
#                           ({"maxReturnCount": "10", "hireGapThreshold": 0.2}, 422),
#                           ({"workerid": "499274", "maxReturnCount": "10", "hireGapThreshold": 0.2}, 422),
#                           ({" workerId": "499274", "maxReturnCount": "10", "hireGapThreshold": 0.2}, 422)])
# def test_empty_payload(payload, expected_status):
#     res = SME_API.find_projects(payload)
#     res.assert_response_status(expected_status)
#     assert res.json_response['detail'] == [{"loc": ["body", "workerId"],
#                                             "msg": "field required",
#                                             "type": "value_error.missing"
#                                             }]
#
#     assert res.json_response['body'] == payload


def test_invalid_payload():
    payload = """{
        "workerId": "499274",
        "maxReturnCount": 2
        "hireGapThreshold": 0.1
    }"""

    res = SME_API.find_projects(payload)
    res.assert_response_status(422)
    assert res.json_response['body'] == '{\n        "workerId": "499274",\n        "maxReturnCount": 2\n        ' \
                                        '"hireGapThreshold": 0.1\n    }'
    assert res.json_response['detail'][0]['msg'] == "value is not a valid dict"
    assert res.json_response['detail'][0]['type'] == "type_error.dict"


def test_invalid_max_return_count():
    payload = {
        "workerId": "499274",
        "maxReturnCount": "one",
        "hireGapThreshold": 0.1
    }
    res = SME_API.find_projects(payload)
    res.assert_response_status(422)
    assert res.json_response['detail'][0]['msg'] == "value is not a valid integer"
    assert res.json_response['detail'][0]['type'] == "type_error.integer"


@pytest.mark.parametrize('_hire_gap_threshold, expected_status, success',
                         [('0', 200, True),
                          ('0.1', 200, True),
                          ('1', 200, True),
                          ('1.1', 200, True)])
def test_hire_gap_threshold(_hire_gap_threshold, expected_status, success):
    payload = {
        "workerId": "499274",
        "maxReturnCount": 10,
        "hireGapThreshold": _hire_gap_threshold
    }
    res = SME_API.find_projects(payload)
    res.assert_response_status(expected_status)
    assert res.json_response['success'] == success

