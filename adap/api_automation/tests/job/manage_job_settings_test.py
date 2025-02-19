import pytest
import allure
import random
import time
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, generate_random_string

pytestmark = [pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.adap_api_uat]


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('jobs/{job_id}/tags:get,jobs/{job_id}/tags:post')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.builder
def test_add_tag_to_job():
    api_key = get_user_api_key('test_account')
    tag_name = "tag generated through api %s" % generate_random_string()

    job = Builder(api_key)
    resp = job.create_job()
    resp.assert_response_status(200)

    resp = job.add_job_tag(tag_name)
    resp.assert_response_status(200)
    resp.assert_success_message_no_data("1 tags added")

    res = job.get_job_tags()
    res.assert_response_status(200)


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/tags:put')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
def test_replace_tags_on_job():
    api_key = get_user_api_key('test_account')
    tag_to_be_replaced = generate_random_string()
    tags = []

    num_tags = random.randint(2, 5)
    print(num_tags)
    for i in range(num_tags):
        tags.append("API Tag - %s" % generate_random_string())

    job = Builder(api_key)
    resp = job.create_job()
    resp.assert_response_status(200)

    resp = job.add_job_tag(tag_to_be_replaced)
    resp.assert_response_status(200)

    resp = job.replace_job_tags(tags)
    resp.assert_response_status(200)
    resp.assert_success_message("%s tags set", str(num_tags))

    resp = job.get_job_tags()
    resp.assert_response_status(200)


@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/channels:post')
@pytest.mark.uat_api
@pytest.mark.fed_api
@pytest.mark.fed_api_smoke
@pytest.mark.skip_hipaa
def test_add_channel_to_job():
    api_key = get_user_api_key('test_account')

    job = Builder(api_key)
    resp = job.create_simple_job()
    assert resp is True, "Job was not created"

    resp = job.get_channels_for_job()
    list_of_available_channels = resp.json_response['available_channels']

    # Choose a random channel from the available list of channels
    i = random.randint(0, len(list_of_available_channels)-1)

    # Add the random channel to the job
    resp = job.add_channel_to_job(list_of_available_channels[i])
    resp.assert_response_status(200)

    # Get list of enabled channels to verify that the channel is in the list
    resp = job.get_channels_for_job()
    updated_list_of_enabled_channels = resp.json_response['enabled_channels']

    assert list_of_available_channels[i] in updated_list_of_enabled_channels


# check after https://appen.atlassian.net/browse/DED-1522 is fixed, fed has bug right now, enable tag once this bug fixed
@allure.severity(allure.severity_level.NORMAL)
@allure.parent_suite('/jobs/{job_id}/disable_channel:post,/jobs/{job_id}/channels:get')
@pytest.mark.uat_api
# @pytest.mark.fed_api
# @pytest.mark.fed_api_smoke
@pytest.mark.skip_hipaa
def test_disable_channel_on_job():
    api_key = get_user_api_key('test_account')

    job = Builder(api_key)
    resp = job.create_simple_job()
    assert resp is True, "Job was not created"

    # launching the job to external crowd
    res = job.launch_job(external_crowd=1)
    res.assert_response_status(200)

    # Get the list of channels the job can be accessed from
    resp = job.get_channels_for_job()
    list_of_available_channels = resp.json_response['available_channels']
    list_of_enabled_channels = resp.json_response['enabled_channels']

    # Choose a random channel from the enabled list of channels to disable
    i = random.randint(0, len(list_of_enabled_channels) - 1)

    # Disable the random channel
    resp = job.disable_channel_on_job(list_of_enabled_channels[i])
    resp.assert_response_status(200)
    time.sleep(5)

    # Get updated list of channels the job can be accessed from
    resp = job.get_channels_for_job()
    updated_list_of_available_channels = resp.json_response['available_channels']
    updated_list_of_enabled_channels = resp.json_response['enabled_channels']

    # Verify that the disabled channel is not in the list of enabled channels
    assert list_of_enabled_channels[i] not in updated_list_of_enabled_channels
    assert list_of_enabled_channels[i] in updated_list_of_available_channels
