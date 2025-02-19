import time

import pytest

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user
from appen_connect.api_automation.services_config.contributor_experience import ContributorExperience

pytestmark = [pytest.mark.regression_ac_web_mobile, pytest.mark.regression_ac_web_mobile_api]


def test_create_user_with_valid_data():
    user = ContributorExperience()
    user_data = generate_data_for_contributor_experience_user()
    res = user.post_create_user(email=user_data['email'], password=user_data['password'],
                                firstname=user_data['firstname'], lastname=user_data['lastname'])

    res.assert_response_status(201)
    assert res.json_response['email'] == user_data['email']
    assert res.json_response['firstName'] == user_data['firstname']
    assert res.json_response['lastName'] == user_data['lastname']
    assert res.json_response['businessName'] == " ".join([user_data['firstname'], user_data['lastname']])


@pytest.mark.parametrize("email, password, firstname, lastname, field_error",[
                         ("", "_ab542V13d!", "Dan", "TestUser", "email"),
                         ("integration+dan_test@figure-eight.com", " ", "Dan", "TestUser", 'password'),
                         ("integration+dan_test@figure-eight.com", "_ab542V13d", " ", "TestUser", 'firstName'),
                          ("integration+dan_test@figure-eight.com", "_ab542V13d", "Dan", " ", 'lastName')
                          ])
def test_create_user_with_blank_data(email, password, firstname, lastname, field_error):
    user = ContributorExperience()
    res = user.post_create_user(email=email, password=password,
                                firstname=firstname, lastname=lastname)

    res.assert_response_status(422)
    assert res.json_response['error'] == "Validation error"
    assert res.json_response['fieldErrors'][0]['field'] == field_error
    assert res.json_response['fieldErrors'][0]["message"] == 'must not be blank'


@pytest.mark.parametrize("email, password, verification_code, error_message",[
                         ("integration+dan_test@figure-eight.com","_ab543d!", 999999, 'Password does not meet minimum security requirements'),
                         ("integration+dan_test@figure-eight.com", "_ab542V13d!", 1234, 'Invalid code. Try again or resend email.'),
                         ("integration+dan_test@figure-eight.com", "_ab542V13d!", 999999, 'The email address is already registered.'),
                          ])
def test_create_user_with_invalid_data(email, password, verification_code, error_message):
    user = ContributorExperience()
    res = user.post_create_user(email="integration+dan_test@figure-eight.com", password=password,
                                firstname='Dan', lastname="TestUser", verificationCode=verification_code)

    res.assert_response_status(400)
    assert res.json_response['error'] == error_message
