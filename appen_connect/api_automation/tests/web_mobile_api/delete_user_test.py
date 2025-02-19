import time

import pytest

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user, get_test_data
from appen_connect.api_automation.services_config.contributor_experience import ContributorExperience
from appen_connect.api_automation.services_config.identity_service import IdentityService

pytestmark = [pytest.mark.regression_ac_web_mobile, pytest.mark.regression_ac_web_mobile_api]


@pytest.fixture(scope='module')
def create_user():
    user = ContributorExperience()
    user_data = generate_data_for_contributor_experience_user()
    res = user.post_create_user(email=user_data['email'], password=user_data['password'],
                                firstname=user_data['firstname'], lastname=user_data['lastname'])
    res.assert_response_status(201)
    return {
        'email': user_data['email'],
        'password': user_data['password'],
        'firstname': user_data['firstname'],
        'lastname': user_data['lastname']
    }


@pytest.fixture(scope='module')
def get_valid_token(create_user):
    identity_service = IdentityService(pytest.env)
    client_secret = get_test_data('keycloak_web_mobile', 'client_secret')
    resp = identity_service.get_token(
        username=create_user['email'],
        password=create_user['password'],
        token=client_secret
    )
    resp.assert_response_status(200)
    return resp.json_response['access_token']


@pytest.mark.dependency()
def test_delete_user_with_valid_data(get_valid_token):
    user = ContributorExperience()
    response = user.delete_user(get_valid_token)
    response.assert_response_status(200)
    assert response.json_response


@pytest.mark.dependency(depends=['test_delete_user_with_valid_data'])
def test_delete_user_in_second_time(get_valid_token):
    user = ContributorExperience()
    response = user.delete_user(get_valid_token)
    response.assert_response_status(500)
    assert response.json_response['error'] == 'Unknown error'
    assert response.json_response['code'] == 'E00'