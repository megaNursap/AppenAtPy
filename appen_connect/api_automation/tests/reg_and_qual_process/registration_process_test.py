import datetime

from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_process, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_registration_process, pytest.mark.ac_api]


def test_rp_types(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_registration_process_types()

    res.assert_response_status(200)
    assert res.json_response[0] == {"value": "ACTIVITY_CUSTOMER_REGISTRATION_DEFAULT",
                                    "label": "ActivitiCustomerRegistrationDefault"}


def test_rp_types_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_registration_process_types()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
 # TODO content verification


@pytest.mark.ac_api_uat
def test_get_registration_processes(ac_api_cookie):
    api = AC_API(ac_api_cookie)
    res = api.get_registration_processes()

    res.assert_response_status(200)
    assert len(res.json_response) > 0


def test_get_registration_process_no_cookies():
    ac_api = AC_API()
    res = ac_api.get_registration_processes()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}
# TODO content verification


# Creates a Registration Process with a randon Step
@pytest.mark.ac_api_uat
def test_create_rp(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_registration_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation REG PROCESS "+current_date,
        "type": "REGISTRATION_PROJECT",
        "description": "<p>Empty registration process.</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    res = api.create_registration_processes(payload)
    res.assert_response_status(201)
    assert res.json_response['name'] == payload['name']
    assert res.json_response['type'] == payload['type']
    assert res.json_response['processSteps'][0]['stepDefinition'] == bpm_step

    process = api.get_registration_process_by_id(res.json_response['id'])
    process.assert_response_status(200)

    assert process.json_response['id'] == res.json_response['id']
    assert process.json_response['name'] == res.json_response['name']
    assert process.json_response['type'] == res.json_response['type']


    # TODO content verification;

def test_create_rp_no_cookies(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_registration_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation REG PROCESS" + current_date,
        "type": "REGISTRATION_PROJECT",
        "description": "<p>Empty registration process.</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    api = AC_API()
    res = api.create_registration_processes(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_update_rp(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_registration_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation REG PROCESS TB update" + current_date,
        "type": "REGISTRATION_PROJECT",
        "description": "<p>Empty registration process.</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    res = api.create_registration_processes(payload)
    res.assert_response_status(201)
    process_id = res.json_response['id']

    new_name = "QA Automation REG PROCESS updated" + current_date
    payload["name"] = new_name
    payload["description"] = "<p>This is a test (updated)</p>"

    update_qp = api.update_registration_process_by_id(process_id,payload)
    update_qp.assert_response_status(200)

    assert update_qp.json_response['id'] == process_id
    assert update_qp.json_response['name'] == new_name
    assert update_qp.json_response['processSteps'][0]['stepDefinition'] == bpm_step


def test_get_projects_by_rp_id(ac_api_cookie):
    # create new rp
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_registration_steps('project')

    num_steps = len(qp_steps.json_response)
    bpm_step = qp_steps.json_response[random.randint(0, num_steps - 1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "QA Automation REG PROCESS3" + current_date,
        "type": "REGISTRATION_PROJECT",
        "description": "<p>Empty registration process.</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_step
            }
        ]
    }
    res = api.create_registration_processes(payload)
    res.assert_response_status(201)
    rp_id = res.json_response['id']

    # create new project
    project_name = generate_project_name()
    payload = {
        "alias": project_name[1],
        "name": project_name[0],
        "taskVolume": "VERY_LOW",
        "workType": "LINGUISTICS",
        "description": project_name[0],
        "projectType": "Regular",
        "registrationProcessTemplateId": str(rp_id)

    }
    res = api.create_project(payload=payload)
    res.assert_response_status(201)
    project_id = res.json_response['id']

    res = api.get_projects_by_registration_process_id(rp_id)
    res.assert_response_status(200)
    assert res.json_response[0]['name'] ==  project_name[0]
    assert res.json_response[0]['alias'] == project_name[1]
    assert res.json_response[0]['id'] == project_id


# Creates a Registration Process for: Data Collection PII Consent Form
def test_create_rp_pii(ac_api_cookie):
    api = AC_API(ac_api_cookie)

    qp_steps = api.get_bpm_registration_steps('project')
    bpm_pii = qp_steps.json_response[(1)]

    current_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    payload = {
        "name": "Data Collection PII Consent Form Automation"+current_date,
        "type": "REGISTRATION_PROJECT",
        "description": "<p>Data Collection PII Consent Form Automation Registration process.</p>",
        "processSteps": [
            {
                "order": 1,
                "stepDefinition": bpm_pii
            }
        ]
    }
    res = api.create_registration_processes(payload)
    res.assert_response_status(201)
    assert res.json_response['name'] == payload['name']
    assert res.json_response['type'] == payload['type']

    process = api.get_registration_process_by_id(res.json_response['id'])
    process.assert_response_status(200)

    assert process.json_response['id'] == res.json_response['id']
    assert process.json_response['name'] == res.json_response['name']
    assert process.json_response['type'] == res.json_response['type']
    assert process.json_response['description'] == res.json_response['description']

