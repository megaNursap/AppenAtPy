from adap.perf_platform.utils.logging import get_logger

from adap.support.spira.core.portal_api import PortalApiClient
from adap.support.spira.core.spira_api import SpiraApiClient
from adap.support.spira.test_coverage.engine import prepare_test_data, \
    prepare_test_case_properties

LOGGER = get_logger(__name__)

if __name__ == '__main__':
    api_client = SpiraApiClient()
    portal_client = PortalApiClient()

    test_cases = api_client.get_all_test_cases()
    tc_props = api_client.get_case_properties()
    prepared_props = prepare_test_case_properties(tc_props)
    data = prepare_test_data(test_cases, prepared_props)

    portal_client.send_test_coverage_data(data)


