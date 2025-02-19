"""`scenario01.py` - Load test adapted from Postman test: Customer01-01

This file is a Work in Progress.
All of the postman tests have been stubbed out, but some are not fully implemented:
Some functions are marked with Pytest skip.

These tests are not currently to be run as part of the regular QA_Automation cycle.

To run: create a virtual environment for the QA_Automation projects, enter it

  cd adap/api_automation/tests/workflow/load
  SERVICE_DOMAIN=sandbox pytest -x --verbose scenario01.py

  for Sandbox; for QA:
  SERVICE_DOMAIN=qa pytest -x --verbose scenario01.py

"""
import json
import logging
import os
import re
from datetime import datetime
import time

import pytest
from adap.api_automation.utils.http_util import HttpMethod, ApiResponse

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())

logging.basicConfig(level=logging.INFO)

DATE_FORMAT = "%Y.%m.%d_%H:%M:%S"

TOKEN_FINDER = re.compile(r'name="authenticity_token" value="([^"]+)')

INSECURE_AUTH_HEADERS = {
    "Upgrade-Insecure-Requests": "1",
    "Origin": "null",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}

AKON_HEADER = {
    "Authorization": "Token make-authentication-token",
    "Accept": "application/json",
    "Cache-Control": "no-cache",
    "content_type": "application/json",
}

SIMPLE_HEADERS = {"Content-Type": "application/json"}

CURR_VALS = {}  #: temp state container

# Temp dev defaults:
if "akon_id" not in os.environ:
    os.environ["akon_id"] = "f9f96007-29d3-4826-8bc4-081ff3ef4e70"
if "api_key" not in os.environ:
    os.environ["api_key"] = "X6a5shL-BjxoGfb3xLf8"
if "proj_num" not in os.environ:
    os.environ["proj_num"] = "PN1101"
if "team_id" not in os.environ:
    os.environ["team_id"] = "1cfb5bf0-31a7-4631-bb40-ec30e72e572f"

if os.environ.get("SERVICE_DOMAIN", "") == "sandbox":
    os.environ["akon_id"] = "15991d3d-4fa4-4584-8d56-a1199ab59e88"
    os.environ["api_key"] = "zjnbTdwk1pBrTzS733Uh"
    os.environ["proj_num"] = "PN1101"
    os.environ["team_id"] = "6c6d9d8e-6a0d-4e00-87e6-eed334ed1020"

# allow Postman cmd execution params to override defaults
if "akon_id" in os.environ:
    CURR_VALS["MY_AKON_UUID"] = os.environ.get("akon_id")
if "api_key" in os.environ:
    CURR_VALS["MY_API_KEY"] = os.environ.get("api_key")
if "team_id" in os.environ:
    CURR_VALS["MY_TEAM_ID"] = os.environ.get("team_id")
if "proj_num" in os.environ:
    CURR_VALS["MY_PROJ_NUM"] = os.environ.get("proj_num")

global current_cookies
global contributor_cookies


def test_Customer_01_01_Create_Cust01_Job1(
    SERVICE_SHORTNAME, PROTOCOL, SERVICE_DOMAIN, JOB_JSON
):

    endpoint = "{{PROTOCOL}}://api.{{SERVICE_DOMAIN}}/v1/jobs.json?key={{MY_API_KEY}}"
    # TODO probably change the API
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{SERVICE_DOMAIN}}", SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{MY_API_KEY}}", CURR_VALS["MY_API_KEY"])
    params = {"key": CURR_VALS["MY_API_KEY"]}
    payload = json.dumps(JOB_JSON)
    payload = payload.replace("{{SERVICE_SHORTNAME}}", SERVICE_SHORTNAME)
    method = HttpMethod()
    response = method.post(endpoint, data=json.loads(payload), params=params)
    assert response.status_code == 200
    if response.json_response:
        CURR_VALS["CUST01_WF01_JOB1"] = str(response.json_response["id"])
        CURR_VALS["CUST01_WF01_JOB1_SECRET"] = response.json_response["secret"]
    else:
        pytest.fail("response expected")
    if response.cookies:
        global current_cookies
        current_cookies = response.cookies.get_dict()


def test_Customer_01_02_Create_Cust01_Job2(
    SERVICE_SHORTNAME, PROTOCOL, SERVICE_DOMAIN, JOB2_JSON
):

    endpoint = "{{PROTOCOL}}://api.{{SERVICE_DOMAIN}}/v1/jobs.json?key={{MY_API_KEY}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{SERVICE_DOMAIN}}", SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{MY_API_KEY}}", CURR_VALS["MY_API_KEY"])
    params = {"key": CURR_VALS["MY_API_KEY"]}
    payload = json.dumps(JOB2_JSON)
    payload = payload.replace("{{SERVICE_SHORTNAME}}", SERVICE_SHORTNAME)
    method = HttpMethod()
    global current_cookies
    response = method.post(
        endpoint, data=json.loads(payload), params=params, cookies=current_cookies
    )
    assert response.status_code == 200
    if response.json_response:
        CURR_VALS["CUST01_WF01_JOB2"] = str(response.json_response["id"])
        CURR_VALS["CUST01_WF01_JOB2_SECRET"] = response.json_response["secret"]
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()


def test_Customer_01_06_Create_Workflow(
    INTERNAL_SERVICE_DOMAIN,
    WORKFLOWS_KAFKA_FLAG,
    SERVICE_SHORTNAME,
    PROTOCOL,
    WORKFLOW_JSON,
):
    endpoint = (
        "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows"
    )
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    payload = json.dumps(WORKFLOW_JSON)
    payload = payload.replace("{{SERVICE_SHORTNAME}}", SERVICE_SHORTNAME)
    payload = payload.replace("{{MY_AKON_UUID}}", CURR_VALS["MY_AKON_UUID"])
    payload = payload.replace("{{MY_TEAM_ID}}", CURR_VALS["MY_TEAM_ID"])
    payload = payload.replace("{{WORKFLOWS_KAFKA_FLAG}}", str(WORKFLOWS_KAFKA_FLAG))
    payload = payload.replace(
        "{{$timestamp}}", datetime.now().strftime(DATE_FORMAT)
    )  # TODO fix non-standard variable name
    method = HttpMethod(endpoint)
    payload = json.loads(payload)
    payload["kafka"] = WORKFLOWS_KAFKA_FLAG
    global current_cookies
    response = method.post(
        "", data=json.dumps(payload), headers=SIMPLE_HEADERS, cookies=current_cookies
    )
    assert response.status_code == 201
    if response.json_response:
        CURR_VALS["CUST01_WF01"] = str(response.json_response["id"])
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(current_cookies)


def test_Customer_01_07_Create_Step_1__Determine(
    PROTOCOL, INTERNAL_SERVICE_DOMAIN, STEP_01_JSON
):

    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows/{{CUST01_WF01}}/steps"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01}}", CURR_VALS["CUST01_WF01"])
    payload = json.dumps(STEP_01_JSON)
    payload = payload.replace("{{CUST01_WF01_JOB1}}", CURR_VALS["CUST01_WF01_JOB1"])
    method = HttpMethod()
    global current_cookies
    response = method.post(
        endpoint,
        data=json.loads(payload),
        headers=INSECURE_AUTH_HEADERS,
        cookies=current_cookies,
    )
    assert response.status_code == 201
    if response.json_response:
        CURR_VALS["CUST01_WF01_STEP_1"] = str(response.json_response["id"])
        CURR_VALS["CUST01_WF01_STEP_1_JOB"] = str(
            response.json_response["data_processor_id"]
        )
        assert (
            CURR_VALS["CUST01_WF01_STEP_1_JOB"] == CURR_VALS["CUST01_WF01_JOB1"]
        ), "Job id mismatch"
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(response.cookies)


def test_Customer_01_08_Create_Step_2__Match(
    PROTOCOL, INTERNAL_SERVICE_DOMAIN, STEP_02_JSON
):

    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows/{{CUST01_WF01}}/steps"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01}}", CURR_VALS["CUST01_WF01"])
    payload = json.dumps(STEP_02_JSON)
    payload = payload.replace("{{CUST01_WF01_JOB2}}", CURR_VALS["CUST01_WF01_JOB2"])
    method = HttpMethod()
    global current_cookies
    response = method.post(
        endpoint,
        data=json.loads(payload),
        headers=INSECURE_AUTH_HEADERS,
        cookies=current_cookies,
    )
    assert response.status_code == 201
    if response.json_response:
        CURR_VALS["CUST01_WF01_STEP_2"] = str(response.json_response["id"])
        CURR_VALS["CUST01_WF01_STEP_2_JOB"] = str(
            response.json_response["data_processor_id"]
        )
        assert (
            CURR_VALS["CUST01_WF01_STEP_2_JOB"] == CURR_VALS["CUST01_WF01_JOB2"]
        ), "Job id mismatch"
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(response.cookies)


def test_Customer_01_09_Create_Route_from_Step_1_to_Step_2(
    INTERNAL_SERVICE_DOMAIN, PROTOCOL, ROUTE_STEP_01_TO_02_JSON
):

    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows/{{CUST01_WF01}}/steps/{{CUST01_WF01_STEP_1}}/routes"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01}}", CURR_VALS["CUST01_WF01"])
    endpoint = endpoint.replace(
        "{{CUST01_WF01_STEP_1}}", CURR_VALS["CUST01_WF01_STEP_1"]
    )
    payload = json.dumps(ROUTE_STEP_01_TO_02_JSON)
    payload = payload.replace("{{CUST01_WF01_STEP_2}}", CURR_VALS["CUST01_WF01_STEP_2"])
    method = HttpMethod()
    auth_header = {
        "Content-Type": "application/json",
        "X-Request-TeamID": CURR_VALS["MY_TEAM_ID"],
    }
    json_payload = json.loads(payload)
    global current_cookies
    response = method.post(
        endpoint,
        data=json.dumps(json_payload),
        headers=auth_header,
        cookies=current_cookies,
    )
    assert response.status_code == 201, response.json_response
    if response.json_response:
        CURR_VALS["STEP_ROUTE_ID"] = str(response.json_response["id"])
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(response.cookies)


def test_Customer_01_10_Create_FilterRule__video_found_yn__Yes(
    PROTOCOL, INTERNAL_SERVICE_DOMAIN, FILTER_RULE_JSON
):

    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/step_routes/{{STEP_ROUTE_ID}}/filter_rules"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{STEP_ROUTE_ID}}", CURR_VALS["STEP_ROUTE_ID"])
    payload = json.dumps(FILTER_RULE_JSON)
    auth_header = {
        "Content-Type": "application/json",
        "X-Request-TeamID": CURR_VALS[
            "MY_TEAM_ID"
        ],  # TODO check for this header value globally
    }
    global current_cookies
    response = HttpMethod(payload=json.loads(payload)).post(
        endpoint, headers=auth_header, cookies=current_cookies
    )
    assert response.status_code == 201, response.content
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(response.cookies)


def test_Customer_01_11_Create_DataUpload_22rows(
    INTERNAL_SERVICE_DOMAIN, PROTOCOL, CUST01_WF01_DATA_STORAGE_KEY, DATA_UPLOAD_JSON
):

    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows/{{CUST01_WF01}}/data_uploads"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01}}", CURR_VALS["CUST01_WF01"])
    payload = json.dumps(DATA_UPLOAD_JSON)
    payload = payload.replace(
        "{{CUST01_WF01_DATA_STORAGE_KEY}}", CUST01_WF01_DATA_STORAGE_KEY
    )
    # TODO the file may need to be added
    payload = payload.replace("{{MY_TEAM_ID}}", CURR_VALS["MY_TEAM_ID"])
    payload = payload.replace("{{MY_AKON_UUID}}", CURR_VALS["MY_AKON_UUID"])
    method = HttpMethod()
    global current_cookies
    response = method.post(endpoint, data=payload, cookies=current_cookies)
    assert response.status_code == 201, response.content
    if response.json_response:
        CURR_VALS["CUST01_WF01_DATA"] = str(response.json_response["id"])
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(response.cookies)


def test_Customer_01_12_C01W01_Get_DataUpload__completed(
    INTERNAL_SERVICE_DOMAIN, PROTOCOL, CUST01_WF01_DATA
):
    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows/{{CUST01_WF01}}/data_uploads/{{CUST01_WF01_DATA}}?team_id={{MY_TEAM_ID}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01}}", CURR_VALS["CUST01_WF01"])
    endpoint = endpoint.replace("{{CUST01_WF01_DATA}}", CURR_VALS["CUST01_WF01_DATA"])
    endpoint = endpoint.replace("{{MY_TEAM_ID}}", CURR_VALS["MY_TEAM_ID"])
    auth_header = {
        "Content-Type": "application/json",
        "X-Request-TeamID": CURR_VALS[
            "MY_TEAM_ID"
        ],  # TODO check for this header value globally
    }
    method = HttpMethod()
    global current_cookies
    response = method.get(endpoint, headers=auth_header, cookies=current_cookies)
    assert response.status_code == 200
    for interval in range(10):
        if (
            response.json_response.get("validation_outcome", "") == "valid"
            and response.json_response.get("state", "") == "completed"
        ):
            if response.json_response["total_rows"] != 22:
                LOG.warning("Upload doesn't match expected rows!")
            break
        time.sleep(25)
        response = method.get(endpoint, headers=auth_header)
        assert response.status_code == 200
        if response.json_response.get("state") == "Incomplete upload":
            assert False, "Incomplete upload"
        if response.json_response.get("validation_outcome") == "Invalid upload":
            assert False, "Invalid upload"
        if response.cookies:
            current_cookies = response.cookies.get_dict()
            LOG.info(response.cookies)


def test_Customer_01_13_C01W01_Launch_Workflow(
    INTERNAL_SERVICE_DOMAIN, LAUNCH_ROWS, PROTOCOL
):

    endpoint = "{{PROTOCOL}}://workflows-service.{{INTERNAL_SERVICE_DOMAIN}}/v1/workflows/{{CUST01_WF01}}/launch?rows={{LAUNCH_ROWS}}&user_id={{MY_AKON_UUID}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_SERVICE_DOMAIN}}", INTERNAL_SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01}}", CURR_VALS["CUST01_WF01"])
    endpoint = endpoint.replace("{{LAUNCH_ROWS}}", str(10))  # CURR_VALS["LAUNCH_ROWS"])
    endpoint = endpoint.replace("{{MY_AKON_UUID}}", CURR_VALS["MY_AKON_UUID"])
    endpoint = endpoint.replace(
        "{{UPLOAD_ROW_COUNT}}", str(22)
    )  # TODO probably store from earlier call
    method = HttpMethod()
    global current_cookies
    payload = '{ "rows": LAUNCH_ROWS}'.replace("LAUNCH_ROWS", str(LAUNCH_ROWS))
    response = method.post(
        endpoint, data=payload, headers=AKON_HEADER, cookies=current_cookies
    )
    if response.status_code == 400:
        assert False, response.content
    if response.json_response:
        assert (
            response.json_response.get("status") == "running"
        ), "Hmm, launch was expected"
    else:
        pytest.fail("response expected")
    if response.cookies:
        current_cookies = response.cookies.get_dict()
        LOG.info(response.cookies)


# TODO Continue implementing this section
@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_A_Launch_Sign_Up_Page(PROTOCOL, INTERNAL_TASKS_DOMAIN):
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/users/new"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    method = HttpMethod()
    global contributor_cookies
    auth_header = {
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    }
    response = method.get(
        endpoint, headers=INSECURE_AUTH_HEADERS, cookies=current_cookies
    )
    assert response.status_code == 200
    if response.content:
        auth_token = TOKEN_FINDER.findall(response.content.decode("utf-8"))[0]
        CURR_VALS["CONTRIB_AUTH_TOKEN"] = auth_token
    else:
        pytest.fail("response expected")

    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_B_Signup_a_USER(
    USER_SIGNUP_PASSWORD,
    PROTOCOL,
    INTERNAL_TASKS_DOMAIN,
    USER_SIGNUP_EMAIL,
    CONTRIB_SIGNUP_JSON,
):
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/users"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    endpoint = endpoint.replace("{{MY_API_KEY}}", CURR_VALS["MY_API_KEY"])
    params = {"key": CURR_VALS["MY_API_KEY"]}
    auth_header = {
        "Upgrade-Insecure-Requests": "1",
        "Origin": "null",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }
    payload = json.dumps(CONTRIB_SIGNUP_JSON)
    payload = payload.replace("{{USER_SIGNUP_PASSWORD}}", USER_SIGNUP_PASSWORD)
    payload = payload.replace("{{USER_SIGNUP_EMAIL}}", USER_SIGNUP_EMAIL)
    payload = payload.replace("{{USER_SIGNUP_PASSWORD}}", USER_SIGNUP_PASSWORD)
    payload = payload.replace("{{CONTRIB_AUTH_TOKEN}}", CURR_VALS["CONTRIB_AUTH_TOKEN"])
    global contributor_cookies
    response = HttpMethod().post(
        endpoint,
        data=payload,
        params=params,
        headers=INSECURE_AUTH_HEADERS,
        cookies=current_cookies,
    )
    assert response.status_code == 200
    if response:
        print(response.content)
        # TODO fix
        print("Success!")
    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_C_New_session(PROTOCOL, INTERNAL_TASKS_DOMAIN):
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/sessions/new"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    endpoint = endpoint.replace("{{MY_API_KEY}}", CURR_VALS["MY_API_KEY"])
    params = {"key": CURR_VALS["MY_API_KEY"]}
    auth_header = {
        "Upgrade-Insecure-Requests": "1",
        "Origin": "null",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }
    global contributor_cookies
    method = HttpMethod()
    # TODO mod
    response = method.get(
        endpoint, headers=INSECURE_AUTH_HEADERS, cookies=contributor_cookies
    )
    assert response.status_code == 200
    if response.content:
        print("Success!")
    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_Login(
    PROTOCOL,
    CONTRIB_LOGIN_JSON,
    USER_SIGNUP_PASSWORD,
    USER_SIGNUP_EMAIL,
    INTERNAL_TASKS_DOMAIN,
):

    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/sessions"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    payload = json.dumps(CONTRIB_LOGIN_JSON)
    payload = payload.replace("{{USER_SIGNUP_EMAIL}}", USER_SIGNUP_EMAIL)
    payload = payload.replace("{{USER_SIGNUP_PASSWORD}}", USER_SIGNUP_PASSWORD)
    payload = payload.replace("{{SERVICE_SHORTNAME}}", CURR_VALS["SERVICE_SHORTNAME"])
    method = HttpMethod()
    global contributor_cookies
    response = method.post(
        endpoint,
        data=payload,
        headers=INSECURE_AUTH_HEADERS,
        cookies=contributor_cookies,
    )
    assert response.status_code == 200
    if response:
        print(response.content)
        print("Success!")
    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_D_Capture_Akon_ID(SERVICE_DOMAIN, PROTOCOL, USER_SIGNUP_EMAIL):

    endpoint = "{{PROTOCOL}}://api.{{SERVICE_DOMAIN}}/v1/jobs.json?key={{MY_API_KEY}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{SERVICE_DOMAIN}}", SERVICE_DOMAIN)
    endpoint = endpoint.replace("{{MY_API_KEY}}", CURR_VALS["MY_API_KEY"])

    method = HttpMethod()
    global contributor_cookies

    response = method.get(endpoint, headers=AKON_HEADER, cookies=contributor_cookies)
    assert response.status_code == 200
    if response.content:
        print("Success!")
        obj = json.loads(response.content)
        CURR_VALS["CONTRIB_AKON_ID"] = obj[0]["id"]
    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


# TODO find out if this is necessary
@pytest.mark.skip
def test_Customer_01_E_Authenticate_Akon_ID_API(PROTOCOL, SERVICE_DOMAIN):
    """
## event
[
  {
    "listen": "test",
    "script": {
      "id": "d46d8585-cd4f-444d-a533-b6edbfb797cb",
      "exec": [
        "// pm.test(\"Akon ID is authenticated\", function () { pm.response.to.have.status(204); });",
        "pm.test(\"response is ok\", function () {",
        "    console.log(pm.response);",
        "});"
      ],
      "type": "text/javascript"
    }
  },
  {
    "listen": "prerequest",
    "script": {
      "id": "d27ff740-5295-4bcf-89e1-98c3a461855e",
      "exec": [
        ""
      ],
      "type": "text/javascript"
    }
  }
]


	"""
    """
## request
{
  "method": "GET",
  "header": [
    {
      "key": "Authorization",
      "type": "text",
      "value": "Token make-authentication-token"
    },
    {
      "key": "Accept",
      "type": "text",
      "value": "application/json"
    },
    {
      "key": "Cache-Control",
      "type": "text",
      "value": "no-cache"
    },
    {
      "key": "content_type",
      "type": "text",
      "value": "application/json"
    }
  ],
  "body": {
    "mode": "raw",
    "raw": "{\n\t\"user\": {\n\t\t\"email_verified_at\": \"2018-07-02 15:43:24 -0700\"\n\t}\n\t\n}"
  },
  "url": {
    "raw": "https://id.{{SERVICE_DOMAIN}}/users/{{CONTRIB_AKON_ID}}",
    "protocol": "https",
    "host": [
      "id",
      "{{SERVICE_DOMAIN}}"
    ],
    "path": [
      "users",
      "{{CONTRIB_AKON_ID}}"
    ]
  },
  "description": "Launch My Workflow"
}

this failed:
'https://id.sandbox.cf3.us/users/1440103'
	"""
    endpoint = "{{PROTOCOL}}://id.{{SERVICE_DOMAIN}}/users/{{CONTRIB_AKON_ID}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{SERVICE_DOMAIN}}", SERVICE_DOMAIN)
    endpoint = endpoint.replace(
        "{{CONTRIB_AKON_ID}}", str(CURR_VALS["CONTRIB_AKON_ID"])
    )
    method = HttpMethod()
    global contributor_cookies

    response = method.get(endpoint, headers=AKON_HEADER, cookies=contributor_cookies)
    assert response.status_code == 204, response.content
    if response:
        # TODO, maybe
        # CURR_VALS("CUST01_WF01_JOB2", response.json_response["id"])
        # CURR_VALS("CUST01_WF01_JOB2_SECRET", response.json_response["secret"])
        print("Success!")
    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_F_Contributor_Login(
    CONTRIB_LOGIN_JSON,
    USER_SIGNUP_PASSWORD,
    PROTOCOL,
    INTERNAL_TASKS_DOMAIN,
    USER_SIGNUP_EMAIL,
):
    """
## event
[
  {
    "listen": "test",
    "script": {
      "id": "d46d8585-cd4f-444d-a533-b6edbfb797cb",
      "exec": [
        ""
      ],
      "type": "text/javascript"
    }
  },
  {
    "listen": "prerequest",
    "script": {
      "id": "d27ff740-5295-4bcf-89e1-98c3a461855e",
      "exec": [
        "pm.test('CUST01_WF01_DATA_STORAGE_KEY should exist in environment json file', function () {",
        "    pm.expect(pm.environment.has('CUST01_WF01_DATA_STORAGE_KEY')).to.equal(true);",
        "    pm.expect(pm.environment.get('CUST01_WF01_DATA_STORAGE_KEY')).to.not.equal(\"\");",
        "});",
        ""
      ],
      "type": "text/javascript"
    }
  }
]


	"""
    """
## request
{
  "method": "POST",
  "header": [
    {
          "key": "Upgrade-Insecure-Requests",
      "type": "text",
      "value": "1"
    },
    {
      "key": "Origin",
      "type": "text",
      "value": "null"
    },
    {
      "key": "Content-Type",
      "type": "text",
      "value": "application/x-www-form-urlencoded"
    },
    {
      "key": "Accept",
      "type": "text",
      "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
  ],
  "body": {
    "mode": "formdata",
    "formdata": [
      {
        "key": "session[email]",
        "value": "{{USER_SIGNUP_EMAIL}}",
        "type": "text"
      },
      {
        "key": "session[password]",
        "value": "{{USER_SIGNUP_PASSWORD}}",
        "type": "text"
      },
      {
        "key": "utf8",
        "value": "true",
        "type": "text"
      },
      {
        "key": "authenticity_token",
        "value": "{{CONTRIB_AUTH_TOKEN}}",
        "type": "text"
      }
    ]
  },
  "url": {
    "raw": "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/sessions",
    "protocol": "{{PROTOCOL}}",
    "host": [
      "tasks",
      "{{INTERNAL_TASKS_DOMAIN}}"
    ],
    "path": [
      "sessions"
    ]
  },
  "description": "Launch My Workflow"
}
	"""
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/sessions"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    params = {"key": CURR_VALS["MY_API_KEY"]}
    payload = json.dumps(CONTRIB_LOGIN_JSON)
    payload = payload.replace("{{USER_SIGNUP_EMAIL}}", USER_SIGNUP_EMAIL)
    payload = payload.replace("{{USER_SIGNUP_PASSWORD}}", USER_SIGNUP_PASSWORD)
    payload = payload.replace("{{CONTRIB_AUTH_TOKEN}}", CURR_VALS["CONTRIB_AUTH_TOKEN"])
    method = HttpMethod()
    global contributor_cookies

    response = method.post(endpoint, data=payload, cookies=contributor_cookies)
    if response.json_response:
        CURR_VALS["CUST01_WF01_JOB2"] = str(response.json_response["id"])
        CURR_VALS["CUST01_WF01_JOB2_SECRET"] = response.json_response["secret"]
        print("Success!")
    if response.cookies:
        contributor_cookies = response.cookies.get_dict()


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_G_Session_assignment_extraction(PROTOCOL, INTERNAL_TASKS_DOMAIN):
    """
## event
[
  {
    "listen": "test",
    "script": {
      "id": "d46d8585-cd4f-444d-a533-b6edbfb797cb",
      "exec": [
        "console.log(pm.response.text());",
        "",
        "",
        "// var aid_regex = new RegExp(\"href=\\\"/assignments/(.+?)/give_up\");",
        "// var resultArray = aid_regex.exec(pm.response.text());",
        "// pm.environment.set(\"CONTRIB_ASSIGNMENT_ID\", resultArray[1]);",
        "// console.log(pm.environment.get(\"CONTRIB_ASSIGNMENT_ID\"))",
        "",
        "// var start_at_next_regex = new RegExp(\"<input type=\\\"hidden\\\" name=\\\"started_at_next\\\" id=\\\"started_at_next\\\" value=\\\"(.+?)\\\"\");",
        "// var resultArray = start_at_next_regex.exec(pm.response.text());",
        "// pm.environment.set(\"STARTED_AT_NEXT\", resultArray[1]);",
        "// console.log(pm.environment.get(\"STARTED_AT_NEXT\"))",
        "",
        "// var start_at_regex = new RegExp(\"<input type=\\\"hidden\\\" name=\\\"started_at\\\" id=\\\"started_at\\\" value=\\\"(.+?)\\\"\");",
        "// var resultArray = start_at_regex.exec(pm.response.text());",
        "// pm.environment.set(\"STARTED_AT\", resultArray[1]);",
        "// console.log(pm.environment.get(\"STARTED_AT\"))",
        "",
        "// var autheny_regex = new RegExp(\"authenticity_token\\\" value=\\\"(.+?)\\\" />\");",
        "// var resultArray = autheny_regex.exec(pm.response.text());",
        "// pm.environment.set(\"CONTRIB_AUTH_TOKEN\", resultArray[1]);",
        "// console.log(pm.environment.get(\"CONTRIB_AUTH_TOKEN\"))",
        "",
        "// var awesome_regex = new RegExp(\"<div class=\\\"cml jsawesome\\\" id=\\\"(.+?)\\\">\");",
        "// var resultArray = awesome_regex.exec(pm.response.text());",
        "// pm.environment.set(\"JSAWESOME_ID_1\", resultArray[1]);",
        "// pm.environment.set(\"JSAWESOME_ID_2\", resultArray[2]);",
        "// pm.environment.set(\"JSAWESOME_ID_3\", resultArray[3]);",
        "// pm.environment.set(\"JSAWESOME_ID_4\", resultArray[4]);",
        "// pm.environment.set(\"JSAWESOME_ID_5\", resultArray[5]);",
        "// console.log(pm.environment.get(\"JSAWESOME_ID_1\"))",
        "// console.log(pm.environment.get(\"JSAWESOME_ID_2\"))",
        "// console.log(pm.environment.get(\"JSAWESOME_ID_3\"))",
        "// console.log(pm.environment.get(\"JSAWESOME_ID_4\"))",
        "// console.log(pm.environment.get(\"JSAWESOME_ID_5\"))",
        ""
      ],
      "type": "text/javascript"
    }
  },
  {
    "listen": "prerequest",
    "script": {
      "id": "d27ff740-5295-4bcf-89e1-98c3a461855e",
      "exec": [
        "pm.test('CUST01_WF01_DATA_STORAGE_KEY should exist in environment json file', function () {",
        "    pm.expect(pm.environment.has('CUST01_WF01_DATA_STORAGE_KEY')).to.equal(true);",
        "    pm.expect(pm.environment.get('CUST01_WF01_DATA_STORAGE_KEY')).to.not.equal(\"\");",
        "});",
        ""
      ],
      "type": "text/javascript"
    }
  }
]


	"""
    """
## request
{
  "method": "GET",
  "header": [
    {
      "key": "Upgrade-Insecure-Requests",
      "type": "text",
      "value": "1"
    },
    {
      "key": "Origin",
      "type": "text",
      "value": "null"
    },
    {
      "key": "Content-Type",
      "type": "text",
      "value": "application/x-www-form-urlencoded"
    },
    {
      "key": "Accept",
      "type": "text",
      "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
  ],
  "body": {
    "mode": "raw",
    "raw": ""
  },
  "url": {
    "raw": "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/channels/cf_internal/jobs/{{CUST01_WF01_JOB1}}/work?secret={{CUST01_WF01_JOB1_SECRET}}",
    "protocol": "{{PROTOCOL}}",
    "host": [
      "tasks",
      "{{INTERNAL_TASKS_DOMAIN}}"
    ],
    "path": [
      "channels",
      "cf_internal",
      "jobs",
      "{{CUST01_WF01_JOB1}}",
      "work"
    ],
    "query": [
      {
        "key": "secret",
        "value": "{{CUST01_WF01_JOB1_SECRET}}"
      }
    ]
  },
  "description": "Launch My Workflow"
}


	"""
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/channels/cf_internal/jobs/{{CUST01_WF01_JOB1}}/work?secret={{CUST01_WF01_JOB1_SECRET}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    endpoint = endpoint.replace("{{CUST01_WF01_JOB1}}", CURR_VALS["CUST01_WF01_JOB1"])
    endpoint = endpoint.replace(
        "{{CUST01_WF01_JOB1_SECRET}}", CURR_VALS["CUST01_WF01_JOB1_SECRET"]
    )
    method = HttpMethod(endpoint)
    global current_cookies

    response = method.get(
        endpoint, headers=INSECURE_AUTH_HEADERS, cookies=current_cookies
    )
    assert response.status_code == 200
    if response:
        # TODO
        # CURR_VALS("CUST01_WF01_JOB2", response.json_response["id"])
        # CURR_VALS("CUST01_WF01_JOB2_SECRET", response.json_response["secret"])
        print(response.content)
        print("Success!")


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_H_Create_Assignments(
    STARTED_AT_NEXT, CONTRIB_ASSIGNMENT_ID, STARTED_AT, PROTOCOL, INTERNAL_TASKS_DOMAIN
):
    """
## event
[
  {
    "listen": "test",
    "script": {
      "id": "d46d8585-cd4f-444d-a533-b6edbfb797cb",
      "exec": [
        "var token_regex = new RegExp(\"amp;token=(.+?)\\\">\");",
        "var resultArray = token_regex.exec(pm.response.text());",
        "pm.environment.set(\"TOKEN\", resultArray[1]);",
        "console.log(pm.environment.get(\"TOKEN\"))",
        ""
      ],
      "type": "text/javascript"
    }
  },
  {
    "listen": "prerequest",
    "script": {
      "id": "d27ff740-5295-4bcf-89e1-98c3a461855e",
      "exec": [
        ""
      ],
      "type": "text/javascript"
    }
  }
]


	"""
    """
## request
{
  "method": "POST",
  "header": [
    {
      "key": "Upgrade-Insecure-Requests",
      "type": "text",
      "value": "1"
    },
    {
      "key": "Origin",
      "type": "text",
      "value": "https://view.qa.cf3.io"
    },
    {
      "key": "Content-Type",
      "type": "text",
      "value": "application/x-www-form-urlencoded"
    },
    {
      "key": "Accept",
      "type": "text",
      "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
  ],
  "body": {
    "mode": "raw",
    "raw": ""
  },
  "url": {
    "raw": "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/assignments/{{CONTRIB_ASSIGNMENT_ID}}?_method=put&authenticity_token={{CONTRIB_AUTH_TOKEN}}&started_at={{STARTED_AT}}&started_at_next={{STARTED_AT_NEXT}}&cf_internal=true",
    "protocol": "{{PROTOCOL}}",
    "host": [
      "tasks",
      "{{INTERNAL_TASKS_DOMAIN}}"
    ],
    "path": [
      "assignments",
      "{{CONTRIB_ASSIGNMENT_ID}}"
    ],
    "query": [
      {
        "key": "_method",
        "value": "put"
      },
      {
        "key": "authenticity_token",
        "value": "{{CONTRIB_AUTH_TOKEN}}"
      },
      {
        "key": "started_at",
        "value": "{{STARTED_AT}}"
      },
      {
        "key": "started_at_next",
        "value": "{{STARTED_AT_NEXT}}"
      },
      {
        "key": "cf_internal",
        "value": "true"
      }
    ]
  },
  "description": "Launch My Workflow"
}


	"""
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/assignments/{{CONTRIB_ASSIGNMENT_ID}}?_method=put&authenticity_token={{CONTRIB_AUTH_TOKEN}}&started_at={{STARTED_AT}}&started_at_next={{STARTED_AT_NEXT}}&cf_internal=true"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    endpoint = endpoint.replace("{{MY_API_KEY}}", CURR_VALS["MY_API_KEY"])
    endpoint = endpoint.replace("{{CONTRIB_ASSIGNMENT_ID}}", str(CONTRIB_ASSIGNMENT_ID))
    endpoint = endpoint.replace(
        "{{CONTRIB_AUTH_TOKEN}}", CURR_VALS["CONTRIB_AUTH_TOKEN"]
    )
    endpoint = endpoint.replace("{{STARTED_AT}}", str(STARTED_AT))
    endpoint = endpoint.replace("{{STARTED_AT_NEXT}}", str(STARTED_AT_NEXT))
    method = HttpMethod()
    global current_cookies
    response = method.post(
        endpoint, headers=INSECURE_AUTH_HEADERS, cookies=current_cookies
    )
    assert response.status_code == 200
    if response:
        print(response.content)
        # CURR_VALS("CUST01_WF01_JOB2", response.json_response["id"])
        # CURR_VALS("CUST01_WF01_JOB2_SECRET", response.json_response["secret"])
        print("Success!")


@pytest.mark.skip("Not going to create a new user for load testing")
def test_Customer_01_I_Get_next_assignment(
    PROTOCOL, TOKEN, ASSIGNMENT_ID, INTERNAL_TASKS_DOMAIN
):
    """
## event
[
  {
    "listen": "test",
    "script": {
      "id": "d46d8585-cd4f-444d-a533-b6edbfb797cb",
      "exec": [
        "var data_job_id_regex = new RegExp(\"data-job-id=\\\"(.+?)\\\"\");",
        "var resultArray = data_job_id_regex.exec(pm.response.text());",
        "pm.environment.set(\"DATA_JOB_ID\", resultArray[1]);",
        "console.log(pm.environment.get(\"DATA_JOB_ID\"))",
        "",
        "var data_worker_id_regex = new RegExp(\"data-worker-id=\\\"(.+?)\\\"\");",
        "var resultArray = data_job_id_regex.exec(pm.response.text());",
        "pm.environment.set(\"DATA_WORKER_ID\", resultArray[1]);",
        "console.log(pm.environment.get(\"DATA_WORKER_ID\"))",
        "",
        "var assignment_id_regex = new RegExp(\"href=\\\"/assignments/(.+?)/give_up\");",
        "var resultArray = assignment_id_regex.exec(pm.response.text());",
        "pm.environment.set(\"CONTRIB_ASSIGNMENT_ID\", resultArray[1]);",
        "console.log(pm.environment.get(\"CONTRIB_ASSIGNMENT_ID\"))",
        "",
        "var start_at_next_regex = new RegExp(\"<input type=\\\"hidden\\\" name=\\\"started_at_next\\\" id=\\\"started_at_next\\\" value=\\\"(.+?)\\\"\");",
        "var resultArray = start_at_next_regex.exec(pm.response.text());",
        "pm.environment.set(\"STARTED_AT_NEXT\", resultArray[1]);",
        "console.log(pm.environment.get(\"STARTED_AT_NEXT\"))",
        "",
        "var start_at_regex = new RegExp(\"<input type=\\\"hidden\\\" name=\\\"started_at\\\" id=\\\"started_at\\\" value=\\\"(.+?)\\\"\");",
        "var resultArray = start_at_regex.exec(pm.response.text());",
        "pm.environment.set(\"STARTED_AT\", resultArray[1]);",
        "console.log(pm.environment.get(\"STARTED_AT\"))",
        "",
        "var autheny_regex = new RegExp(\"authenticity_token\\\" value=\\\"(.+?)\\\" />\");",
        "var resultArray = autheny_regex.exec(pm.response.text());",
        "pm.environment.set(\"CONTRIB_AUTH_TOKEN\", resultArray[1]);",
        "console.log(pm.environment.get(\"CONTRIB_AUTH_TOKEN\"))",
        "",
        "var awesome_regex = new RegExp(\"<div class=\\\"cml jsawesome\\\" id=\\\"(.+?)\\\">\");",
        "var resultArray = awesome_regex.exec(pm.response.text());",
        "pm.environment.set(\"JSAWESOME_ID_1\", resultArray[1]);",
        "pm.environment.set(\"JSAWESOME_ID_2\", resultArray[2]);",
        "pm.environment.set(\"JSAWESOME_ID_3\", resultArray[3]);",
        "pm.environment.set(\"JSAWESOME_ID_4\", resultArray[4]);",
        "pm.environment.set(\"JSAWESOME_ID_5\", resultArray[5]);",
        "console.log(pm.environment.get(\"JSAWESOME_ID_1\"))",
        "console.log(pm.environment.get(\"JSAWESOME_ID_2\"))",
        "console.log(pm.environment.get(\"JSAWESOME_ID_3\"))",
        "console.log(pm.environment.get(\"JSAWESOME_ID_4\"))",
        "console.log(pm.environment.get(\"JSAWESOME_ID_5\"))",
        "",
        "var no_more_work = pm.response.text().contains(\"There is no work currently available\")",
        "pm.environment.set(\"WORK_AVAILABLE\", no_more_work);",
        "console.log(pm.environment.get(\"WORK_AVAILABLE\"))",
        "",
        ""
      ],
      "type": "text/javascript"
    }
  },
  {
    "listen": "prerequest",
    "script": {
      "id": "d27ff740-5295-4bcf-89e1-98c3a461855e",
      "exec": [
        "pm.test('CUST01_WF01_DATA_STORAGE_KEY should exist in environment json file', function () {",
        "    pm.expect(pm.environment.has('CUST01_WF01_DATA_STORAGE_KEY')).to.equal(true);",
        "    pm.expect(pm.environment.get('CUST01_WF01_DATA_STORAGE_KEY')).to.not.equal(\"\");",
        "});",
        ""
      ],
      "type": "text/javascript"
    }
  }
]


	"""
    """
## request
{
  "method": "GET",
  "header": [
    {
      "key": "Upgrade-Insecure-Requests",
      "type": "text",
      "value": "1"
    },
    {
      "key": "Origin",
      "type": "text",
      "value": "https://view.qa.cf3.io"
    },
    {
      "key": "Content-Type",
      "type": "text",
      "value": "application/x-www-form-urlencoded"
    },
    {
      "key": "Accept",
      "type": "text",
      "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
  ],
  "body": {
    "mode": "raw",
    "raw": ""
  },
  "url": {
    "raw": "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/assignments/{{ASSIGNMENT_ID}}?cf_internal=true&token={{TOKEN}}",
    "protocol": "{{PROTOCOL}}",
    "host": [
      "tasks",
      "{{INTERNAL_TASKS_DOMAIN}}"
    ],
    "path": [
      "assignments",
      "{{ASSIGNMENT_ID}}"
    ],
    "query": [
      {
        "key": "cf_internal",
        "value": "true"
      },
      {
        "key": "token",
        "value": "{{TOKEN}}"
      }
    ]
  },
  "description": "Launch My Workflow"
}


	"""
    endpoint = "{{PROTOCOL}}://tasks.{{INTERNAL_TASKS_DOMAIN}}/assignments/{{ASSIGNMENT_ID}}?cf_internal=true&token={{TOKEN}}"
    endpoint = endpoint.replace("{{PROTOCOL}}", PROTOCOL)
    endpoint = endpoint.replace("{{INTERNAL_TASKS_DOMAIN}}", INTERNAL_TASKS_DOMAIN)
    endpoint = endpoint.replace("{{ASSIGNMENT_ID}}", ASSIGNMENT_ID)
    endpoint = endpoint.replace("{{TOKEN}}", TOKEN)
    method = HttpMethod()
    global current_cookies
    response = method.get(endpoint, headers=INSECURE_AUTH_HEADERS)
    assert response.status_code == 200
    if response:
        # CURR_VALS("CUST01_WF01_JOB2", response.json_response["id"])
        # CURR_VALS("CUST01_WF01_JOB2_SECRET", response.json_response["secret"])
        print("Success!")
