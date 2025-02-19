import json
import time

import pytest
import requests
import logging

LOGGER = logging.getLogger(__name__)

URL = "https://qa-portal.internal.cf3.us/"
ENDPOINT = "api/v1/test_run"
HEADERS = {
    "Content-type": "application/json"
}


def define_test_set_details(jenkins_test_url):
    _test_set_name = ""
    _test_set_type = ""

    if jenkins_test_url:
        _test_set_name = jenkins_test_url.split("/")[-3]
        for _type in ["regression", "smoke", "deployment", "uat"]:
            if _type in _test_set_name:
                _test_set_type = _type
                if _test_set_type == "deployment": _test_set_type = "CI/CD deployment"

    return {"test_set_name": _test_set_name,
            "test_set_type": _test_set_type}


def post_test_result_to_crp(time_started):
    test_set_details = define_test_set_details(pytest.jenkins_test_url)

    payload = {
        "env": f"ac_{pytest.env}" if pytest.appen == 'true' else pytest.env,
        "service_tag": pytest.set,
        "jenkins_test_url": pytest.jenkins_test_url,
        "deployment_link": pytest.deployment_url,
        "jira": pytest.jira,
        "created": time_started,
        "test_set_name": test_set_details["test_set_name"],
        "test_set_type": test_set_details["test_set_type"]
    }

    LOGGER.info(f" Portal message: {payload}")

    res = requests.post(URL + ENDPOINT,
                        headers=HEADERS,
                        data=json.dumps(payload))

    LOGGER.info(f"========== Send message to CRP POST: tests started ==========")
    LOGGER.info(res.status_code)
    LOGGER.info(res.json())


def push_test_result_to_crp(report):
    LOGGER.info(f"========== Test Report ==========")
    LOGGER.info(report)

    res = requests.put(URL + ENDPOINT,
                       headers=HEADERS,
                       data=report,
                       timeout=5)

    LOGGER.info(f"========== Send results to CRP PUT: test results ==========")
    LOGGER.info(res.status_code)
    LOGGER.info(res.json())


def modify_report_crp(json_report):
    del json_report["environment"]

    if json_report.get("duration"):
        json_report["duration"] = json_report["duration"] * 1000  # milliseconds

    if json_report.get("created"):
        json_report["created"] = json_report["created"] * 1000  # milliseconds

    _del_params = ["setup",
                   "call",
                   "teardown",
                   "lineno"
                   ]

    for _t in json_report["tests"]:
        for _param in ["setup", "call", "teardown", "lineno"]:
            if _t.get(_param): del _t[_param]

        _node = _t["nodeid"].split("/")
        _test_name = _t["nodeid"].split("::")[-1]
        _test_module = _t["nodeid"].split("::")[0].split("/")[-1]
        _t["module"] = _test_module.replace(".py", "")
        _t["name"] = f"{_test_module}::{_test_name}"  # temporary until portal does not have module column
        _t["package"] = _node[_node.index("tests") + 1]
        _t["type"] = "api" if "api_automation" in _node else "ui"
        _t["platform"] = _node[0]
        _t["outcome"] = "passed" if _t["outcome"] == "rerun" else _t["outcome"]
        try:
            _t["execution_count"] = _t["metadata"]["execution_count"]
            del _t["metadata"]
        except:
            _t["execution_count"] = 1

    test_set_details = define_test_set_details(pytest.jenkins_test_url)

    json_report["env"] = f"ac_{pytest.env}" if pytest.appen == 'true' else pytest.env
    json_report["service_tag"] = pytest.set
    json_report["jenkins_test_url"] = pytest.jenkins_test_url
    json_report["deployment_link"] = pytest.deployment_url
    json_report["jira"] = pytest.jira
    json_report["test_set_name"] = test_set_details["test_set_name"]
    json_report["test_set_type"] = test_set_details["test_set_type"]

    return json_report
