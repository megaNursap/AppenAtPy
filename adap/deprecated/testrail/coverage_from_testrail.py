from adap.perf_platform.utils.logging import get_logger
from adap.support.crp.core.portal_api import PortalApiClient
from adap.deprecated.testrail.core.testrail_api import TestRailClient

LOGGER = get_logger(__name__)

status = {"Done": 1,
          "In progress": 2,
          "None": 3,
          "TODO": 4,
          "Wont automate": 5}


def get_projects_from_testrail(api):
    LOGGER.info("Get projects from TestRail")
    res = api.get_projects()
    return [{'id': x['id'], 'name': x['name']} for x in res.json_response.get('projects', [])]


def get_suites_from_testrail(api, projects):
    LOGGER.info("Get suites from TestRail")
    suites = []
    for project in projects:
        project_id = project['id']

        res = api.get_suites(project_id=project_id)
        _data = {
            'id': project_id,
            'name': project['name'],
            'suites': [{'id': x['id'], 'name': x['name']} for x in res.json_response]
        }
        suites.append(_data)

    return suites


def get_cases_from_testrail(api, data):
    LOGGER.info("Get test ceses from TestRail")
    for project in data:
        project_id = project['id']
        for suit in project['suites']:
            res = api.get_cases(project_id=project_id, suite_id=suit['id'])
            cases = [x['custom_automation_status'] for x in res.json_response.get('cases', [])]
            auto_status = {
                'Total': len(cases),
                'None': cases.count(None) + cases.count(3),
                'Done': cases.count(1),
                'Wont automate': cases.count(5),
                'In progress': cases.count(2),
                'TODO': cases.count(4),
                'Other': len(cases)
                         - cases.count(None)
                         - cases.count(3)
                         - cases.count(1)
                         - cases.count(5)
                         - cases.count(2)
                         - cases.count(4)
            }
            suit['automation'] = auto_status

    return data


def get_data_from_testrail(api):
    projects = get_projects_from_testrail(api)
    suites = get_suites_from_testrail(api, projects)
    cases = get_cases_from_testrail(api, suites)

    return cases


def prepare_data_for_portal(data):
    LOGGER.info("Prepare data for Portal")
    result = {}
    for project in data:
        project_name = project['name'].lower()
        result[project_name] = {'features': {}}

        summary = {
            'Total': 0,
            'None': 0,
            'Done': 0,
            'Wont automate': 0,
            'In progress': 0,
            'TODO': 0,
            'Other': 0
        }

        features = project['suites']
        for feature in features:
            feature_name = feature['name']
            automation_data = feature['automation']
            total = automation_data['Total']
            if total > 0:
                result[project_name]['features'][feature_name] = automation_data
                summary['Total'] += automation_data['Total']
                summary['None'] += automation_data['None']
                summary['Done'] += automation_data['Done']
                summary['Wont automate'] += automation_data['Wont automate']
                summary['In progress'] += automation_data['In progress']
                summary['TODO'] += automation_data['TODO']
                summary['Other'] += automation_data['Other']

        result[project_name]['summary'] = summary

    return result


if __name__ == '__main__':
    api = TestRailClient()
    portal = PortalApiClient()
    data = get_data_from_testrail(api)
    result = prepare_data_for_portal(data)

    portal.send_test_coverage_data(result)
