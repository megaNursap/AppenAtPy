import allure
import pytest
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_data_file, get_user_api_key, count_row_in_file, \
    get_hosted_channel_id
from adap.api_automation.services_config.hosted_channel import HC
from faker import Faker

faker = Faker()
users = pytest.data.users
API_KEY = get_user_api_key('test_hc_account')
# TODO: @OscarDena : Add assertions for Hosted Channel IDs once the endpoint is created


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


@pytest.fixture(scope="module")
def _channels():
    """
    pytest fixture - create multiple channel
    """
    hc1 = create_hc(API_KEY)
    hc2 = create_hc(API_KEY)
    return [hc1, hc2]


@allure.parent_suite('/jobs/upload:post')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.env != "fed", reason="FED specific")
def test_create_job_with_json_data_hosted_channel(_channel):

    api_key = get_user_api_key('test_hc_account')
    hosted_channel = _channel
    sample_file = get_data_file('/sample_data.json')
    rows_in_json = count_row_in_file(sample_file)

    job = Builder(api_key)
    payload = {
        "hosted_channel_ids": hosted_channel
    }
    resp = job.create_job_with_json(sample_file, payload)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert rows_in_json == job_status.json_response['all_units']


@allure.parent_suite('/jobs/upload:post')
@pytest.mark.uat_api
@pytest.mark.skipif(pytest.env != "fed", reason="FED specific")
@pytest.mark.fed_api
def test_create_job_with_json_data_multiple_hosted_channels(_channels):

    api_key = get_user_api_key('test_hc_account')
    hosted_channels = _channels
    sample_file = get_data_file('/sample_data.json')

    rows_in_json = count_row_in_file(sample_file)

    job = Builder(api_key)
    payload = {
        "hosted_channel_ids": hosted_channels
    }
    resp = job.create_job_with_json(sample_file, payload)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert rows_in_json == job_status.json_response['all_units']


@allure.parent_suite('/jobs/upload:post')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skipif(pytest.env != "fed", reason="FED specific")
def test_create_job_with_csv_data_hosted_channel(_channel):

    api_key = get_user_api_key('test_hc_account')
    hosted_channel = _channel
    sample_file = get_data_file('/dod_data.csv')

    rows_in_csv = count_row_in_file(sample_file)

    job = Builder(api_key)
    payload = {
        "hosted_channel_ids": hosted_channel
    }

    resp = job.create_job_with_csv(sample_file, payload)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert rows_in_csv == job_status.json_response['all_units']


@allure.parent_suite('/jobs/upload:post')
@pytest.mark.uat_api
@pytest.mark.skipif(pytest.env != "fed", reason="FED specific")
def test_create_job_with_csv_data_multiple_hosted_channel(_channels):

    api_key = get_user_api_key('test_hc_account')
    hosted_channels = _channels
    sample_file = get_data_file('/dod_data.csv')

    rows_in_csv = count_row_in_file(sample_file)

    job = Builder(api_key)
    payload = {
        "hosted_channel_ids[]": hosted_channels
    }

    resp = job.create_job_with_csv(sample_file, payload)
    resp.assert_response_status(200)

    job_status = job.get_job_status(job.job_id)
    assert rows_in_csv == job_status.json_response['all_units']

