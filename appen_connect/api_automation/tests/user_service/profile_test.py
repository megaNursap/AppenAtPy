import pytest

from adap.api_automation.utils.data_util import get_test_data, sorted_list_of_dict_by_value
from appen_connect.api_automation.services_config.ac_user_service import UserService
from faker import Faker

pytestmark = [pytest.mark.regression_ac_user_service, pytest.mark.regression_ac, pytest.mark.ac_api_user_service, pytest.mark.ac_api_user_service_profile, pytest.mark.ac_api]

faker = Faker()
API = UserService()


@pytest.mark.ac_api_uat
@pytest.mark.ac_api_smoke
def test_vendor_profile(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')

    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    res.assert_response_status(200)
    assert res.json_response['email'] == get_test_data('test_active_vendor_account', 'email')
    assert res.json_response['firstName'] == get_test_data('test_active_vendor_account', 'firstName')
    assert res.json_response['lastName'] == get_test_data('test_active_vendor_account', 'lastName')
    assert res.json_response['country'] == get_test_data('test_active_vendor_account', 'country')
    assert res.json_response['state'] == get_test_data('test_active_vendor_account', 'state')
    # TODO there is a mismatch between the expected languages json to actual json response returned from the API.
    # assert res.json_response['languages'] == get_test_data('test_active_vendor_account', 'languages')

    assert sorted_list_of_dict_by_value(res.json_response['translationExperiences'], 'fromLanguage') == get_test_data('test_active_vendor_account',
                                                                        'translationExperiences')


def test_vendor_profile_unauthorized():
    _vendor = get_test_data('test_active_vendor_account', 'id')

    res = API.get_vendor_profile(_vendor, cookies='')
    res.assert_response_status(401)
    assert res.json_response['error'] == 'Unauthorized'


@pytest.mark.parametrize('id', ['10000000000000000001', ' ', 'one', '123!'])
def test_profile_vendor_invalid_id(ac_api_cookie_no_customer, id):
    res = API.get_vendor_profile(id, cookies=ac_api_cookie_no_customer)
    res.assert_response_status(403)
    # !!! not user friendly error msg and status


# TODO response json structure
@pytest.mark.ac_api_uat
def test_update_profile(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')
    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    current_payload = res.json_response

    new_zip = faker.zipcode()
    new_phone = faker.phone_number()

    current_payload['zip'] = new_zip
    current_payload['primaryPhone'] = new_phone

    res_update = API.update_vendor_profile(_vendor, current_payload, cookies=ac_api_cookie_vendor)
    res_update.assert_response_status(200)
    assert res_update.json_response['zip'] == new_zip
    assert res_update.json_response['primaryPhone'] == new_phone

    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    res.assert_response_status(200)
    assert res.json_response['zip'] == new_zip
    assert res.json_response['primaryPhone'] == new_phone


def test_update_profile_unauthorized(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')
    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    current_payload = res.json_response

    res = API.update_vendor_profile(_vendor, current_payload,  cookies='')
    res.assert_response_status(401)
    assert res.json_response['error'] == 'Unauthorized'


def test_update_profile_empty_payload(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')

    res = API.update_vendor_profile(_vendor, {}, cookies=ac_api_cookie_vendor)
    res.assert_response_status(500)
    assert res.json_response['error'] == "Unknown error"


@pytest.mark.skip(reason='need investigation QED-2563')
def test_update_profile_primary_lan(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')
    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    current_payload = res.json_response

    current_payload['languages'][3]['primary'] = 'false'

    res_update = API.update_vendor_profile(_vendor, current_payload, cookies=ac_api_cookie_vendor)
    res_update.assert_response_status(400)
    assert res_update.json_response['errorMessage'] == "Could not update profile data. Error: Primary language is required"

    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    assert res.json_response['languages'][3]['primary']


def test_update_profile_one_primary_lan(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')
    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    original_lan_len = len(res.json_response['languages'])
    current_payload = res.json_response

    new_lan = {
             "localeCode":"ekk_EST",
             "language":"ekk",
             "region":"EST",
             "spokenFluency":"NATIVE_OR_BILINGUAL",
             "writtenFluency":"NATIVE_OR_BILINGUAL",
             "primary":True
      }
    lan_list = current_payload['languages']
    lan_list.append(new_lan)
    current_payload['languages'] = lan_list

    res_update = API.update_vendor_profile(_vendor, current_payload, cookies=ac_api_cookie_vendor)
    res_update.assert_response_status(400)
    assert res_update.json_response['errorMessage'] == "Could not update profile data. Error: More than one primary language is not allowed"

    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    assert len(res.json_response['languages']) == original_lan_len


@pytest.mark.ac_api_uat
def test_update_profile_additional_lan(ac_api_cookie_vendor):
    _vendor = get_test_data('test_active_vendor_account', 'id')
    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    current_payload = res.json_response

    translation_experiences = current_payload['translationExperiences']
    translation_experiences.append({"fromLanguage":"jpn_JPN","toLanguage":"eng_USA"})

    res_update = API.update_vendor_profile(_vendor, current_payload, cookies=ac_api_cookie_vendor)
    res_update.assert_response_status(400)
    assert res_update.json_response['errorMessage'] == "Could not update profile data. Error: Additional language is " \
                                                       "required to include a translation experience"

    res = API.get_vendor_profile(_vendor, cookies=ac_api_cookie_vendor)
    assert len(res.json_response['translationExperiences']) == 2
