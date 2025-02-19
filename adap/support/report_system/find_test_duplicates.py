import os

import pytest

from adap.support.report_system.automation_coverage import TestCoverageReport


def generate_report():
    PROJECT_DIR = os.path.abspath(os.path.dirname(__file__) + "/../../..")
    my_plugin = TestCoverageReport()
    pytest.main(['--collect-only', '-qq', PROJECT_DIR], plugins=[my_plugin])
    return my_plugin


def find_duplicates_by_name(data):
    all_tests = {}

    for test in data:
        test_data = test.split("::")
        test_name = test_data[1]
        test_path = test_data[0]

        if all_tests.get(test_name, None):
            _ = all_tests[test_name]
            _.append(test_path)
            all_tests[test_name] = _
        else:
            all_tests[test_name] = [test_path]

    duplicates = {}
    for key, value in all_tests.items():
        if len(value) > 1:
            duplicates[key] = value

    return duplicates


if __name__ == "__main__":
    _data = generate_report()
    duplicates = find_duplicates_by_name(_data.collected)
    if duplicates:
        print("Duplicates: ", duplicates)
    else:
        print("No duplicates found")
