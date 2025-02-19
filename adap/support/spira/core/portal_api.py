import requests
import json

from adap.perf_platform.utils.logging import get_logger
from adap.support.spira.core.config import get_config

LOGGER = get_logger(__name__)


class PortalApiClient:
    def __init__(self):
        LOGGER.info('Initialize Portal API client')
        self.cfg = get_config(section='portal')
        self.base_url = self.cfg['url']
        self.endpoints = Endpoints(self.base_url)

    def send_test_coverage_data(self, data):
        LOGGER.info('Send test coverage data')
        resp = requests.post(
            self.endpoints.spira_test_coverage,
            json=data
        )

        if not resp.ok:
            LOGGER.error('Request Failed: {0}'.format(resp.text))
        else:
            LOGGER.info(f'Data has been sent successfully: {data}')

        json_resp = json.loads(resp.content)

        return json_resp


class Endpoints:
    def __init__(self, base_url):
        self.base_url = base_url
        cfg = get_config(section='portal_endpoints')

        self.spira_test_coverage = self.base_url + cfg['test_coverage']
