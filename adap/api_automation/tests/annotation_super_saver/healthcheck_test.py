"""
Health check for super saver
"""

import pytest
from adap.api_automation.services_config.supersaver import *

pytestmark = [pytest.mark.super_saver_api,pytest.mark.regression_core]


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.annotation_frontend
@pytest.mark.adap_api_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_health_check():
    res = SuperSaver().health_check()
    res.assert_response_status(200)