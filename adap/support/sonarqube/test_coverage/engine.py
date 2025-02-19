from adap.api_automation.utils.data_util import convert_date_format, convert_date_format_iso8601
from adap.perf_platform.utils.logging import get_logger

LOGGER = get_logger(__name__)


class Engine:
    def __init__(self, client):
        LOGGER.info('Initialize Sonarqube engine')
        self.client = client

    def get_projects_metrics(self, projects):
        LOGGER.info('Collect projects metrics: status; coverage; new_coverage')
        result = {}

        for project in sorted(projects):
            if project.find('sandbox') != -1: continue  # exclude data from sandbox branch
            m_resp = self.client.get_project_metrics(project)
            metrics = m_resp['component']['measures']
            if not metrics:
                LOGGER.info('Skipped the project because it\'s not analyzed yet')
                continue

            d_resp = self.client.get_analysis_dates(project)
            updated_date = convert_date_format_iso8601(d_resp['analyses'][0]['date'], "%d %b %Y, %I:%M%p")

            nc = lambda: self.__get_metric('new_coverage', metrics)
            service_name = m_resp['component']['name'].replace(' ', '_').lower()
            result[service_name] = {
                'status': 'passed' if self.__get_metric('alert_status', metrics)['value'] == 'OK' else 'failed',
                'coverage': float(self.__get_metric('coverage', metrics)['value']),
                'new_coverage': float(nc()['period']['value'] if nc() else 0),
                'date': updated_date
            }

        return result

    def get_all_projects(self):
        LOGGER.info('Get all projects from all pages')
        p = 0
        projects = []
        while True:
            p += 1
            resp = self.client.get_projects(p)
            projects.extend(resp['components'])
            if int(resp['paging']['pageSize']) * p > resp['paging']['total']:
                break

        return list(map(lambda x: x['key'], projects))

    @staticmethod
    def __get_metric(name, metrics):
        return next(filter(lambda x: x['metric'] == name, metrics), None)
