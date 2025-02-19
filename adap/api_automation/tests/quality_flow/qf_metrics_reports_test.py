"""
swagger - https://api-kepler.integration.cf3.us/project/swagger-ui/index.html#/Project%20File%20Controller
swagger - https://api-kepler.integration.cf3.us/metrics/swagger-ui/index.html#/
"""
import random
from adap.api_automation.services_config.quality_flow import QualityFlowApiProject, QualityFlowApiMetrics
import io
import pytest
import time
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
import logging
import pandas as pd
logger = logging.getLogger('faker')
logger.setLevel(logging.INFO)  # Quiet faker locale messages down in testself.

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiProject()
    cookies = api.get_valid_sid(username, password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project
    }


@pytest.mark.parametrize("report_type", [
    "JOB_DAILY",
    "CONTRIBUTOR_DAILY"
])
def test_metrics_daily_report_download_process(setup, report_type):
    api = setup['api']
    project_id = setup['default_project']['dashboard']['projectId']
    team_id = setup['team_id']

    body_data = {
        "projectId": project_id,
        "type": report_type
    }
    res = api.post_download_file(team_id, body_data)
    assert res.json_response['data']['status'] == 'DOWNLOAD_PREPARE'

    start_time = datetime.datetime.now()
    download_URL = None
    MAX_LOOP = 300
    count = 0
    while count < MAX_LOOP:
        count += 1
        res = api.get_list_of_downloaded_files(project_id, team_id, report_type)
        if res.json_response['data']['status'] == 'DOWNLOAD_READY':
            download_URL = res.json_response['data']['filePath']
            break
        time.sleep(1)
    end_time = datetime.datetime.now()
    print(f'Download cost %.3f seconds' % (end_time - start_time).seconds)
    base_url_bak, api.service.base_url = api.service.base_url, ''
    res = api.service.get(download_URL)
    api.service.base_url = base_url_bak
    assert res.status_code == 200
