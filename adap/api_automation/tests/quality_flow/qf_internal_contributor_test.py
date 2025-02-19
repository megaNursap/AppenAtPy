import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor
import pytest
import random
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
import logging

from adap.support.generate_test_data.utils_fed_users.generate_random_names import generate_fake_email, \
    generate_fake_name

logger = logging.getLogger('faker')
logger.setLevel(logging.INFO)  # Quiet faker locale messages down in tests.

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)
    email = generate_fake_email("qf_user")
    name = generate_fake_name("test user").replace("_","")
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "email": email,
        "name": name
    }


def test_add_internal_contributor(setup):

    api = setup["api"]
    res = api.post_internal_contributor_create(setup["email"], setup["name"],setup["team_id"])
    assert res.json_response.get("message") == "success"
    assert res.status_code == 200
    # Comment here


def test_delete_internal_contributor(setup):
    # delete contributor expects a contributor id , which we cant get right now .
    # if there was a delete by email we could have used. While creating if the response has returned contributor-id
    # we could have used that
    pass
