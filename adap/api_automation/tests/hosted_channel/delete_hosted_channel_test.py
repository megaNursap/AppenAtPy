"""
delete hosted channel tests
"""
import allure
import pytest
from faker import Faker

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, get_data_file
from adap.api_automation.services_config.hosted_channel import HC

faker = Faker()
API_KEY = get_user_api_key('test_hc_account')
TEAM_ID = get_user_team_id('test_hc_account')


def create_hc(api_key):
    """
    new channel
    """
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(api_key).create_channel(payload)
    hc_res.assert_response_status(201)
    return hc_res.json_response['id']


@pytest.fixture(scope="module")
def _channel():
    """
    pytest fixture - create new channel
    """
    return create_hc(API_KEY)


@allure.parent_suite('/hosted_channels:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('api_key_type, api_key, expected_status, expected_msg',
                         [("empty_key", "", 403, 'Unauthorized token'),
                          ("invalid_key", "12345678qwerty", 403, 'Unauthorized token'),
                          ("valid_key", get_user_api_key('test_hc_account'), 202, '')])
def test_delete_hc_with_api_key(api_key_type, api_key, expected_status, expected_msg, _channel):
    """
    delete HC with api key
    """
    hc_res = HC(api_key).delete_channel(_channel)
    hc_res.assert_response_status(expected_status)
    if expected_msg: assert hc_res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.parametrize('test_name, hc_id, expected_status, expected_msg',
                         [("empty_id", "", 405, ''),
                          ("not_exist", 99999, 404, 'Invalid Hosted Channel ID.'),
                          ("invalid_type", 'abc', 404, 'Invalid Hosted Channel ID.'),
                          ("unsupported_format", 10.23, 404, 'Invalid Hosted Channel ID.')
                          ])
def test_delete_hc_invalid_id(test_name, hc_id, expected_status, expected_msg):
    """
    delete HC with invalid id
    """
    res = HC(API_KEY).delete_channel(hc_id)
    res.assert_response_status(expected_status)
    print("error message is:", res.json_response)
    if expected_msg: assert res.json_response['message'] == expected_msg


@allure.parent_suite('/hosted_channels:delete')
@pytest.mark.skip(reason='Not implemented yet')
@pytest.mark.hosted_channel
def test_delete_hc_another_team():
    """
    delete HC for other team
    """
    team_api_key = get_user_api_key('test_predefined_jobs')
    hc_id = create_hc(team_api_key)
    res = HC(API_KEY).delete_channel(hc_id)

    res.assert_response_status(400)  # not working right now
    # if expected_msg: assert res.json_response['error'] == expected_msg


@allure.parent_suite('/hosted_channels:delete')
@pytest.mark.hosted_channel
@pytest.mark.fed_api
def test_delete_hc_on_running_job():
    """
    delete HC for running job
    """

    hc_id = create_hc(API_KEY)

    # create and launch job
    sample_file = get_data_file("/simple_job/simple_data__tq_ex.json")
    cml_sample = '''
                   <div class="html-element-wrapper">
                     <span>{{text}}</span>
                   </div>
                   <cml:radios label="Is this funny or not?" validates="required" gold="true">
                     <cml:radio label="funny" value="funny" />
                     <cml:radio label="not funny" value="not_funny" />
                   </cml:radios>
                '''

    job = Builder(API_KEY)
    job.create_job_with_json(sample_file, {"hosted_channel_ids": hc_id})
    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "Updated",
            'instructions': "Updated",
            'cml': cml_sample
        }
    }
    job.update_job(payload=updated_payload)

    resp = job.launch_job()
    resp.assert_response_status(200)

    res = HC(API_KEY).delete_channel(hc_id)
    res.assert_response_status(422)
    assert res.json_response['error'] == "[\"Cannot delete channel enabled on running jobs\"]"
