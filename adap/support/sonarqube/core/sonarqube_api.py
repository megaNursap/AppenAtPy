import requests
import json
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from adap.perf_platform.utils.logging import get_logger
from adap.support.sonarqube.core.config import get_config

LOGGER = get_logger(__name__)


class SonarqubeApiClient:
    def __init__(self):
        LOGGER.info('Initialize Sonarqube API client')
        self.cfg = get_config()
        self.base_url = self.cfg["url"]
        self.endpoints = Endpoints(self.base_url)

        retry_strategy = Retry(
            total=10,
            status_forcelist=[504],
            method_whitelist=["GET"]
        )
        self.client = requests.Session()
        self.client.mount('https://', HTTPAdapter(max_retries=retry_strategy))

    def get_projects(self, page=1):
        LOGGER.info("Get all available projects")
        resp = requests.get(self.endpoints.projects.format(page=page))

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    def get_project_metrics(self, project, metrics=('coverage', 'new_coverage', 'alert_status')):
        LOGGER.info("Get metrics for: " + project)
        resp = self.client.get(
            self.endpoints.metrics
            .format(project=project, metrics=','.join(metrics))
        )

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp

    def get_analysis_dates(self, project, page_size=1):
        LOGGER.info("Get analysis dates for: " + project)
        resp = self.client.get(
            self.endpoints.date
            .format(project=project, page_size=page_size)
        )

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))

        json_resp = json.loads(resp.content)

        return json_resp


class Endpoints:
    def __init__(self, base_url):
        self.base_url = base_url
        cfg = get_config(section='sonarqube_endpoints')

        self.projects = self.base_url + cfg["projects"]
        self.metrics = self.base_url + cfg["metrics"]
        self.date = self.base_url + cfg["last_analysis_date"]
