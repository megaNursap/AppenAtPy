import time

import pytest

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user, get_test_data
from appen_connect.api_automation.services_config.ac_project_service import ProjectServiceAPI
from appen_connect.api_automation.services_config.contributor_experience import ContributorExperience
from appen_connect.api_automation.services_config.identity_service import IdentityService

pytestmark = [pytest.mark.regression_ac_web_mobile, pytest.mark.regression_ac_web_mobile_api]
client_secret = get_test_data('keycloak_web_mobile', 'client_secret')
user_data = generate_data_for_contributor_experience_user(pr_language='spa', country='AR', city='San Rafael')

@pytest.fixture(scope='module')
def create_and_sign_user():

    user = ContributorExperience()
    res_user = user.post_create_user(email=user_data['email'], password=user_data['password'],
                                firstname=user_data['firstname'], lastname=user_data['lastname'])
    res_user.assert_response_status(201)

    identity_service = IdentityService(pytest.env)

    res_token = identity_service.get_token(
        username=user_data['email'],
        password=user_data['password'],
        token=client_secret
    )
    res_token.assert_response_status(200)
    valid_token = res_token.json_response['access_token']

    res_document = user.get_onboarding_document(token=valid_token)
    res_sign_document = user.post_document_signature(res_document.json_response, valid_token)
    res_sign_document.assert_response_status(200)
    yield {
        'email': user_data['email'],
        'password': user_data['password'],
        'firstname': user_data['firstname'],
        'lastname': user_data['lastname'],
        'token': valid_token
    }
    response = user.delete_user(valid_token)
    response.assert_response_status(200)


def test_get_profile_with_valid_token(create_and_sign_user):
    user = ContributorExperience()
    res_profile = user.get_profile(create_and_sign_user['token'])
    res_profile.assert_response_status(200)
    assert res_profile.json_response['firstName'] == create_and_sign_user['firstname']
    assert res_profile.json_response['lastName'] == create_and_sign_user['lastname']
    assert res_profile.json_response['businessName'] == create_and_sign_user['firstname'] + ' ' + create_and_sign_user['lastname']
    assert res_profile.json_response['email'] == create_and_sign_user['email']
    assert res_profile.json_response['country'] == None


def test_get_pofile_with_defunct_user():
    user = ContributorExperience()
    identity_service = IdentityService(pytest.env)

    res_token = identity_service.get_token(
        username="integration+jimmya@figure-eight.com",
        password="_1a!d53b4V2",
        token=client_secret
    )
    res_token.assert_response_status(200)
    valid_token = res_token.json_response['access_token']
    res_profile = user.get_profile(valid_token)
    res_profile.assert_response_status(400)
    assert res_profile.json_response['error'] == 'Error updating user profile'
    assert res_profile.json_response['code'] == 'E12'


def test_update_profile_with_account_info(create_and_sign_user):
    user = ContributorExperience()
    api = ProjectServiceAPI()
    res_countries = api.get_countries_available_list(language_code=user_data['primary_language'], allow_redirects=True)
    res_countries.assert_response_status(200)
    countries = res_countries.json_response
    local_code = '_'.join([user_data['primary_language'], countries[0]['value']])
    payload = {"languages":
                   [
                    {"localeCode": local_code,
                     "language": user_data['primary_language'],
                     "region": countries[0]['value'],
                     "spokenFluency": "NATIVE_OR_BILINGUAL",
                     "writtenFluency": "NATIVE_OR_BILINGUAL",
                     "primary": True}
                    ],
               "socialMediaAccounts": {"instagram": "", "facebook": "", "twitter": "", "linkedin": "some:url"}, "businessName": ""}
    res_update_profile = user.update_profile(payload, create_and_sign_user['token'])
    res_update_profile.assert_response_status(200)
    assert res_update_profile.json_response['languages'][0]['localeCode'] == local_code
    assert res_update_profile.json_response['languages'][0]['region'] == countries[0]['value']
    assert res_update_profile.json_response['languages'][0]['primary']
    assert res_update_profile.json_response['socialMediaAccounts']['linkedin'] == "some:url"


def test_update_profile_languages(create_and_sign_user):
    user = ContributorExperience()
    api = ProjectServiceAPI()
    res_countries = api.get_countries_available_list(language_code=user_data['primary_language'], allow_redirects=True)
    res_countries.assert_response_status(200)
    countries = res_countries.json_response
    local_code = '_'.join([user_data['primary_language'], countries[0]['value']])
    local_code_second = '_'.join([user_data['primary_language'], countries[2]['value']])
    payload = {"languages":
                   [
                    {"localeCode": local_code,
                     "language": user_data['primary_language'],
                     "region": countries[0]['value'],
                     "spokenFluency": "NATIVE_OR_BILINGUAL",
                     "writtenFluency": "NATIVE_OR_BILINGUAL",
                     "primary": True},
                    {"localeCode": local_code_second,
                     "language": user_data['primary_language'],
                     "region": countries[2]['value'],
                     "spokenFluency": "NATIVE_OR_BILINGUAL",
                     "writtenFluency": "NATIVE_OR_BILINGUAL",
                     "primary": False}
                    ]
               }
    res_update_profile = user.update_profile(payload, create_and_sign_user['token'])
    res_update_profile.assert_response_status(200)
    assert res_update_profile.json_response['languages'][1]['localeCode'] == local_code
    assert res_update_profile.json_response['languages'][1]['region'] == countries[0]['value']
    assert res_update_profile.json_response['languages'][1]['primary']
    assert res_update_profile.json_response['languages'][0]['localeCode'] == local_code_second
    assert res_update_profile.json_response['languages'][0]['region'] == countries[2]['value']
    assert not res_update_profile.json_response['languages'][0]['primary']


def test_two_primary_languages_not_allowed(create_and_sign_user):
    user = ContributorExperience()
    api = ProjectServiceAPI()
    res_countries = api.get_countries_available_list(language_code=user_data['primary_language'], allow_redirects=True)
    res_countries.assert_response_status(200)
    countries = res_countries.json_response
    local_code = '_'.join([user_data['primary_language'], countries[0]['value']])
    local_code_second = '_'.join([user_data['primary_language'], countries[3]['value']])
    payload = {"languages":
                   [
                    {"localeCode": local_code,
                     "language": user_data['primary_language'],
                     "region": countries[0]['value'],
                     "spokenFluency": "NATIVE_OR_BILINGUAL",
                     "writtenFluency": "NATIVE_OR_BILINGUAL",
                     "primary": True},
                    {"localeCode": local_code_second,
                     "language": user_data['primary_language'],
                     "region": countries[3]['value'],
                     "spokenFluency": "NATIVE_OR_BILINGUAL",
                     "writtenFluency": "NATIVE_OR_BILINGUAL",
                     "primary": True}
                    ]
               }
    res_update_profile = user.update_profile(payload, create_and_sign_user['token'])
    res_update_profile.assert_response_status(400)
    assert res_update_profile.json_response['errorMessage'] == "Could not update profile data. Error: More than one primary language is not allowed"


def test_update_profile_with_invalid_data(create_and_sign_user):
    user = ContributorExperience()
    api = ProjectServiceAPI()
    res_countries = api.get_countries_available_list(language_code='ukr', allow_redirects=True)
    res_countries.assert_response_status(200)
    region = res_countries.json_response[0]['value']
    local_code = '_'.join([user_data['primary_language'], region])
    payload = {"languages":
                   [
                    {"localeCode": local_code,
                     "language": user_data['primary_language'],
                     "region": region,
                     "spokenFluency": "NATIVE_OR_BILINGUAL",
                     "writtenFluency": "NATIVE_OR_BILINGUAL",
                     "primary": True}
                    ]
    }
    res_update_profile = user.update_profile(payload, create_and_sign_user['token'])
    res_update_profile.assert_response_status(422)
    assert res_update_profile.json_response['error'] == 'Locale not found'


def test_update_profile_with_contact_info(create_and_sign_user):
    user = ContributorExperience()
    payload = {"country": user_data['country'],
               "city": user_data['city'],
               "zip": user_data['zipcode'],
               "address": user_data['address'],
               "primaryPhone": user_data['phone_number']
               }
    res_update_profile = user.update_profile(payload, create_and_sign_user['token'])
    res_update_profile.assert_response_status(200)
    get_profile = user.get_profile(create_and_sign_user['token'])
    assert get_profile.json_response['country'] == 'AR'
    assert get_profile.json_response['city'] == 'San Rafael'
    assert not get_profile.json_response['address'] is None
    assert not get_profile.json_response['zip'] is None
    assert not get_profile.json_response['primaryPhone'] is None
    assert get_profile.json_response['viaEmail'] is None


# TODO  fix - it is not working in jenkins when we use parallel running
# @pytest.mark.parametrize("country, state, primary_phone, zip_code, error, field",
#                          [
#     ('USA', user_data['state'], user_data['phone_number'], user_data['zipcode'], 'size must be between 0 and 2', 'contacts.country'),
#     (user_data['country'], "California", user_data['phone_number'], user_data['zipcode'], 'size must be between 0 and 2', 'contacts.state'),
#     (user_data['country'], user_data['state'], "+3421111175893874923875920485", user_data['zipcode'], 'The primary phone is too long.', 'contacts.primaryPhone'),
#     (user_data['country'], user_data['state'], user_data['phone_number'], "888888888888888888888888888", 'The zip code is too long.', 'contacts.zip')
#                          ])
# def test_invalid_size_of_field_contacts(create_and_sign_user, country, state, primary_phone, zip_code, error, field):
#     user = ContributorExperience()
#     payload = {"country": country,
#                 "state": state,
#                 "zip": zip_code,
#                 "primaryPhone": primary_phone
#                }
#     res_update_profile = user.update_profile(payload, create_and_sign_user['token'])
#     res_update_profile.assert_response_status(422)
#     assert res_update_profile.json_response['fieldErrors'][0]['message'] == error
#     assert res_update_profile.json_response['fieldErrors'][0]['field'] == field

