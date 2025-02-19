"""
EPIC:https://appen.atlassian.net/browse/QED-1353
JIRA:https://appen.atlassian.net/browse/QED-1354
POSTMAN COLLECTION:https://figure-eight-eng.postman.co/collections/5577736-f0ba2f20-ef5d-4749-bff0-7807d0d62e13?version=latest&workspace=4faa266b-bc41-4b48-8f9a-f1dac4b33281#cfde793c-8e84-4e13-9bc1-cce83246afeb
"""

import pytest
from adap.api_automation.services_config.pointcloud import *

pytestmark = pytest.mark.regression_lidar

@pytest.mark.lidar_pointcloud_api
@pytest.mark.uat_api
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")# Spira Testcase: https://appen.spiraservice.net/5/TestCase/1035.aspx
def test_get_healthcheck():
    res = PointCloud().get_healthcheck()
    res.assert_response_status(200)
    assert res.json_response.get('status') == 'pass'