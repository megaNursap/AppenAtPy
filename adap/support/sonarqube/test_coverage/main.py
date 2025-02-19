from adap.perf_platform.utils.logging import get_logger
from adap.support.sonarqube.core.sonarqube_api import SonarqubeApiClient
from adap.support.sonarqube.test_coverage.engine import Engine

from adap.support.sonarqube.core.portal_api import PortalApiClient

LOGGER = get_logger(__name__)

if __name__ == '__main__':
    portal_client = PortalApiClient()
    sonarqube_client = SonarqubeApiClient()

    engine = Engine(sonarqube_client)
    projects = engine.get_all_projects()
    data = engine.get_projects_metrics(projects)
    portal_client.send_sonarqube_data(data)
