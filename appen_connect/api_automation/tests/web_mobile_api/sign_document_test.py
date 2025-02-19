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
def valid_token(create_user):
    identity_service = IdentityService(pytest.env)
    client_secret = get_test_data('keycloak_web_mobile', 'client_secret')
    resp = identity_service.get_token(
        username=create_user['email'],
        password=create_user['password'],
        token=client_secret
    )
    resp.assert_response_status(200)
    return resp.json_response['access_token']


@pytest.fixture(autouse=True, scope='module')
def delete_user(valid_token):
    yield
    user = ContributorExperience()
    response = user.delete_user(valid_token)
    response.assert_response_status(200)


def test_get_sign_onboarding_document(valid_token):
    user = ContributorExperience()

    res = user.get_onboarding_document(token=valid_token)

    res.assert_response_status(200)
    get_sign_documents = res.json_response

    assert 'By clicking "I Agree" below, you consent and agree to the above confidentiality statement' in get_sign_documents[0]['content']
    assert get_sign_documents[0]['title'] == 'Confidentiality Agreement'
    assert get_sign_documents[1]['title'] == 'Bona Fide Occupational Qualification Disclosure'
    assert get_sign_documents[2]['title'] == 'Electronic Consent'


def test_sign_onboarding_document(valid_token, create_user):
    user = ContributorExperience()
    res = user.get_onboarding_document(token=valid_token)
    res_sign_document = user.post_document_signature(res.json_response, valid_token)
    res_sign_document.assert_response_status(200)
    data_in_response = res_sign_document.json_response
    for _data in data_in_response:
        assert _data['firstName'] == create_user['firstname']
        assert _data['lastName'] == create_user['lastname']
        assert 'signature' in _data


def test_get_sign_onboarding_document_without_token():
    user = ContributorExperience()
    res = user.get_onboarding_document()
    res.assert_response_status(401)