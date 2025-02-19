import datetime

from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_process, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_qualification_process, pytest.mark.ac_api]


@pytest.mark.ac_api_uat
def test_qp_types(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_qualification_process_types()

    res.assert_response_status(200)
    assert res.json_response[0] == {"value": "ACTIVITY_CUSTOMER_QUALIFICATION_DEFAULT",
                                    "label": "ActivitiCustomerQualificationDefault"}


def test_qp_types_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_qualification_process_types()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
 # TODO content verification


@pytest.mark.ac_api_uat
def test_qualification_processes(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_qualification_processes()

    res.assert_response_status(200)
    assert len(res.json_response) > 0


def test_get_qualification_process_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_qualification_processes()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
# TODO content verification


@pytest.mark.ac_api_uat
def test_create_qp(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_qualification_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation test"+current_date,
        "type": "QUALIFICATION_PROJECT",
        "description": "<p>This is a test</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    res = api.create_qualification_processes(payload)
    res.assert_response_status(201)
    assert res.json_response['name'] == payload['name']
    assert res.json_response['type'] == payload['type']
    assert res.json_response['processSteps'][0]['stepDefinition'] == bpm_step

    process = api.get_qualification_process_by_id(res.json_response['id'])
    process.assert_response_status(200)

    assert process.json_response['id'] == res.json_response['id']
    assert process.json_response['name'] == res.json_response['name']
    assert process.json_response['type'] == res.json_response['type']


    # TODO content verification;

def test_create_qp_no_cookies(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_qualification_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation test"+current_date,
        "type": "QUALIFICATION_PROJECT",
        "description": "<p>This is a test</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    api = AC_API()
    res = api.create_qualification_processes(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_update_qp(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_qualification_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation process TB update" + current_date,
        "type": "QUALIFICATION_PROJECT",
        "description": "<p>This is a test</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    res = api.create_qualification_processes(payload)
    res.assert_response_status(201)
    process_id = res.json_response['id']

    new_name = "QA Automation process updated" + current_date
    payload["name"] = new_name
    payload["description"] = "<p>This is a test (updated)</p>"

    update_qp = api.update_qualification_process_by_id(process_id,payload)
    update_qp.assert_response_status(200)

    assert update_qp.json_response['id'] == process_id
    assert update_qp.json_response['name'] == new_name
    assert update_qp.json_response['processSteps'][0]['stepDefinition'] == bpm_step


def test_get_projects_by_qp_id(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    # create new qp
    qp_steps = api.get_bpm_qualification_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation test "+current_date,
        "type": "QUALIFICATION_PROJECT",
        "description": "<p>This is a test</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    res = api.create_qualification_processes(payload)
    res.assert_response_status(201)
    qp_id = res.json_response['id']

    # create new project
    project_name = generate_project_name()
    payload = {
        "alias": project_name[1],
        "name": project_name[0],
        "taskVolume": "VERY_LOW",
        "workType": "LINGUISTICS",
        "description": project_name[0],
        "projectType": "Regular",
        "qualificationProcessTemplateId": str(qp_id)

    }
    res = api.create_project(payload=payload)
    res.assert_response_status(201)
    project_id = res.json_response['id']

    res = api.get_projects_by_qualification_process_id(qp_id)
    res.assert_response_status(200)
    assert res.json_response[0]['name'] ==  project_name[0]
    assert res.json_response[0]['alias'] == project_name[1]
    assert res.json_response[0]['id'] == project_id