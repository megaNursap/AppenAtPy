import datetime
import random

import pytest

from adap.api_automation.utils.data_util import get_test_data
from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from appen_connect.api_automation.services_config.ac_user_service import UserService


mark_only_envs = pytest.mark.skipif(
    pytest.env not in ["stage"],
    reason="Only AC Stage enabled feature")

pytestmark = [pytest.mark.pdup, pytest.mark.regression_ac_user_service, mark_only_envs]


API = UserService()

PDUP_VALID_ATTRIBUTES = ["full_name",
                         "first_name",
                         "last_name",
                         "primary_locale",
                         "registration_ip",
                         "self_reported_country",
                         "state",
                         "payoneer_status",
                         "platform_status",
                         "resume_hash",
                         "primary_phone",
                         "address",
                         "photo",
                         "facebook_account",
                         "twitter_account",
                         "instagram_id",
                         "instagram_account",
                         "dynamic_ips",
                         "dynamic_ips_creation_date",
                         "emails",'phones','resume_hash']


def create_new_vendor(app_vendor):
    _today = datetime.datetime.today()
    prefix = "FP" + _today.strftime("%Y%m%d") + "_" + str(random.randint(1000, 9999))
    vendor_name1 = "sandbox+" + prefix + "@figure-eight.com"
    password1 = get_test_data('test_ui_account', 'password')
    verification_code1 = "4266E5"

    first_name = "False"
    last_name = "Positive"

    app_vendor.ac_user.register_new_vendor(vendor_name=vendor_name1,
                                           vendor_password=password1,
                                           verification_code=verification_code1,
                                           vendor_first_name=first_name,
                                           user_last_name=last_name)

    app_vendor.navigation.click_btn('Go to Login page')

    AUTH_KEY = get_test_data('auth_key', 'auth_key')
    api = AC_API_V1(AUTH_KEY)

    payload = {
        "email": vendor_name1
    }
    resp = api.get_user_by_email(payload)
    resp.assert_response_status(200)

    vendor_id = resp.json_response['id']

    return {"vendor": vendor_name1,
            "password": password1,
            "id": vendor_id,
            "first_name": first_name,
            "last_name": last_name}


def test_get_all_false_positive_no_cookies():
    res = API.get_all_false_positive()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_get_all_false_positive(ac_api_cookie):
    res = API.get_all_false_positive(cookies=ac_api_cookie)

    all_units = res.json_response
    assert len(all_units) > 0

    response_fields = ["id",
                       "userId",
                       "duplicateUserId",
                       "attribute",
                       "isFalsePositive",
                       "createdByUserId",
                       "updatedByUserId",
                       "dateCreated",
                       "dateUpdated"
                    ]

    random_units = random.choices(all_units, k=min(5, len(all_units)))

    for unit in random_units:
        for _field in response_fields:
            assert _field in unit.keys()

        assert unit['attribute'] in PDUP_VALID_ATTRIBUTES, '{attribute} has not been found'.format(attribute=unit['attribute'])


def test_get_false_positive_by_user_no_cookies():
    res = API.get_false_positive_by_user()
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_get_false_positive_by_user(ac_api_cookie):
    res = API.get_all_false_positive(cookies=ac_api_cookie)
    res.assert_response_status(200)

    all_users = res.json_response
    assert len(all_users) > 0

    random_user = random.choice(all_users)

    res = API.get_false_positive_by_user(user_id=random_user['userId'], cookies=ac_api_cookie)
    res.assert_response_status(200)
    units = res.json_response
    assert len(units), "Units have not been found"

    for unit in units:
        assert unit['userId'] == random_user['userId'], "User_id not match"
        assert unit['attribute'] in PDUP_VALID_ATTRIBUTES, '{attribute} has not been found'.format(attribute=unit['attribute'])


def test_get_false_positive_for_new_user_no_data(app_test, ac_api_cookie):
    global vendor
    vendor = create_new_vendor(app_test)
    print(vendor)

    res = API.get_false_positive_by_user(user_id=vendor['id'], cookies=ac_api_cookie)
    res.assert_response_status(200)
    assert res.json_response == []


def test_post_false_positive_for_user_no_cookies():
    payload = {
        "userId": vendor['id'],
        "duplicateUserId": 1296577,
        "attribute": "full_name",
        "isFalsePositive": 'true'
    }

    res = API.post_false_positive_by_user(payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


def test_post_false_positive_for_user(ac_api_cookie):
    payload = {
        "userId": vendor['id'],
        "duplicateUserId": 1296577,
        "attribute": "full_name",
        "isFalsePositive": 'true'
    }

    res = API.post_false_positive_by_user(payload, cookies=ac_api_cookie)
    res.assert_response_status(200)
    assert res.json_response['userId'] == vendor['id']
    assert res.json_response['duplicateUserId'] == 1296577
    assert res.json_response['attribute'] == "full_name"
    assert res.json_response['isFalsePositive']
    assert str(res.json_response['createdByUserId']) == get_test_data('test_ui_account', 'id')

    res = API.get_false_positive_by_user(user_id=vendor['id'], cookies=ac_api_cookie)
    res.assert_response_status(200)
    assert len(res.json_response) == 1 # one record - full_name
    assert res.json_response[0]['userId'] == vendor['id']
    assert res.json_response[0]['duplicateUserId'] == 1296577
    assert res.json_response[0]['attribute'] == "full_name"
    assert res.json_response[0]['isFalsePositive']


def test_post_2nd_false_positive_attribute_for_user(ac_api_cookie):
    payload = {
        "userId": vendor['id'],
        "duplicateUserId": 1296577,
        "attribute": "last_name",
        "isFalsePositive": 'true'
    }

    res = API.post_false_positive_by_user(payload, cookies=ac_api_cookie)
    res.assert_response_status(200)
    assert res.json_response['userId'] == vendor['id']
    assert res.json_response['duplicateUserId'] == 1296577
    assert res.json_response['attribute'] == "last_name"
    assert res.json_response['isFalsePositive']
    assert str(res.json_response['createdByUserId']) == get_test_data('test_ui_account', 'id')

    res = API.get_false_positive_by_user(user_id=vendor['id'], cookies=ac_api_cookie)
    res.assert_response_status(200)
    assert len(res.json_response) == 2  # one record - full_name

    assert list(filter(lambda x: x['userId'] != vendor['id'], res.json_response)) == []
    assert sorted(list(map(lambda x: x['attribute'], res.json_response))) == ['full_name', 'last_name']
    assert list(filter(lambda x: not x['isFalsePositive'], res.json_response)) == []


def test_update_false_positive_attribute_false(ac_api_cookie):
    res = API.get_false_positive_by_user(user_id=vendor['id'], cookies=ac_api_cookie)
    res.assert_response_status(200)

    record = res.json_response[0]
    is_false_positive = record['isFalsePositive']
    duplicate_user_id = record['duplicateUserId']
    record_id = record['id']
    record_attribute = record['attribute']

    assert is_false_positive

    payload ={
        "id": record_id,
        "userId": vendor['id'],
        "duplicateUserId": duplicate_user_id,
        "attribute": record_attribute,
        "isFalsePositive": 'false'
    }

    res = API.put_false_positive_by_user(payload=payload, cookies=ac_api_cookie)
    res.assert_response_status(200)

    assert res.json_response['id'] == record_id
    assert res.json_response['userId'] == vendor['id']
    assert res.json_response['attribute'] == record_attribute
    assert not res.json_response['isFalsePositive']
