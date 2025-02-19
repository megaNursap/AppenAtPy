import datetime
import os
import pytest
import json
import requests

class TestCoverageReport:
    def __init__(self):
        self.collected = []

    def pytest_collection_modifyitems(self, items):
        for item in items:
            self.collected.append(item.nodeid)


report = {
    "adap": {
        "api": {
            "path": "adap/api_automation",
            "total": 0
        },
        "ui": {
            "path": "adap/ui_automation",
            "total": 0
        }
    },
    "appen_connect": {
        "api": {
            "path": "appen_connect/api_automation",
            "total": 0
        },
        "ui": {
            "path": "appen_connect/ui_automation",
            "total": 0
        }
    },
    "integration": {
        "integration": {
            "path": "integration",
            "total": 0
        }
    }
}

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__) + "/../../..")


def generate_report():
    for app_type, info in report.items():
        for test_type, test_info in info.items():
            my_plugin = TestCoverageReport()
            full_path = PROJECT_DIR + "/" + test_info['path']
            pytest.main(['--collect-only', '-qq', full_path], plugins=[my_plugin])
            report[app_type][test_type]["total"] = len(my_plugin.collected)

    timestamp = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M")
    file_name = f"{PROJECT_DIR}/report_result/{timestamp}_automation_coverage.json"
    print("result:", report)
    print("report file:", file_name)
    with open(file_name, 'w') as fp:
        json.dump(report, fp)

    return  report


if __name__ == "__main__":
    _data = generate_report()

 
