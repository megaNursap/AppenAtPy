import time

import pytest
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.api_automation.utils.data_util import get_test_data
from adap.perf_platform.utils.logging import get_logger
from adap.settings import Config

API_KEY = get_test_data('test_account', 'api_key')

TEST_DATA = pytest.data.predefined_data['ipa_job_performance']
_ipa = IPA_API(API_KEY)

log = get_logger(__name__)


@pytest.mark.skipif(pytest.env != "integration", reason="Only set up with integration")
@pytest.mark.parametrize('number_unit, cml_type',
                         [
                          ("1000_unit", "checkbox"),
                          ("1000_unit", "radios"),
                          ("1000_unit", "image_annotation")
                          ])
def test_measure_generate_aggregation_checkbox(number_unit, cml_type):
    job_id = TEST_DATA[cml_type].get(number_unit)
    _ipa.generate_aggregation(job_id)
    start = time.perf_counter()
    _ipa.wait_until_regenerate_aggregation("in_progress_version", job_id)
    request_time = time.perf_counter() - start
    msg = f'The time for generate aggregation for cml type {cml_type} with {number_unit}: {request_time}'
    log.info(msg)
    write_result_to_file(msg)


def write_result_to_file(message):
    with open(f"{Config.APP_DIR}/data/generate_aggregation_time.txt", 'w') as f:
        f.write(message)
        f.write('\n')

