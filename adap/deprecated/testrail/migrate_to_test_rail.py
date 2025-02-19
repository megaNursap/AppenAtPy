import argparse
import re


from adap.perf_platform.utils.logging import get_logger

from adap.support.spira import SpiraApiClient
from adap.deprecated.testrail.core.testrail_api import TestRailClient

LOGGER = get_logger(__name__)

TAG_RE = re.compile(r'<.*?>')

def remove_tags(text):
    if text is not None:
        return TAG_RE.sub('', text)
    return ''

def verify_title(title_name):
    if not title_name:
        title_name = "Empty Title"
    return title_name


def create_test_cases_for_testrail(testrail_project_id, testrail_suite_id, spira_suite_id):
    payload = ''
    spira_api_client = SpiraApiClient()
    test_rail_api = TestRailClient()
    section_id = test_rail_api.sections_name(testrail_project_id, testrail_suite_id)
    spira_test_case_ids = [index['TestCaseId'] for index in spira_api_client.get_test_cases_by_suite_id(spira_suite_id)]
    for spira_test_case_id in spira_test_case_ids:
        test_cases_for_testrail = []
        migrated_cases = spira_api_client.get_test_case(spira_test_case_id)
        custom_steps_separated = [migrated_case for migrated_case in migrated_cases['TestSteps']]
        for custom_step_separated in custom_steps_separated:
            my_custom_step = {
                "content": remove_tags(custom_step_separated['Description']),
                "expected": remove_tags(custom_step_separated['ExpectedResult'])
            }
            test_cases_for_testrail.append(my_custom_step)
        payload = {
                "title": verify_title(migrated_cases['Name']),
                "type_id": 1,
                "priority_id": 1,
                "estimate": "3m",
                "template_id": 2,
                "custom_preconds": remove_tags(migrated_cases['Description']),
                "custom_steps_separated": test_cases_for_testrail
            }
        test_rail_api.add_test_cases(section_id[1], payload)
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Just an example",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--testrail_project_id", help="archive mode", type=int)
    parser.add_argument("--testrail_suite_id", help="archive mode", type=int)
    parser.add_argument("--spira_section_ids", nargs='+', help="archive mode", type=int)
    arg = parser.parse_args()

    for spira_section_id in arg.spira_section_ids:
        print("THE SPIRA SUITE_ID - ", spira_section_id)
        ss = spira_section_id
        create_test_cases_for_testrail(arg.testrail_project_id, arg.testrail_suite_id, spira_section_id)