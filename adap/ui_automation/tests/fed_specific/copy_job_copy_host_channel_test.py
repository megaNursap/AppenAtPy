"""
https://appen.atlassian.net/browse/QED-2079
Copy job will also copy over hosted channel
"""

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.services_config.hosted_channel import HC

faker = Faker()
_hc_name = [faker.company() + faker.zipcode(), faker.company() + faker.zipcode(), faker.company() + faker.zipcode()]
USER_EMAIL = get_user_email('cf_internal_role')
PASSWORD = get_user_password('cf_internal_role')
API_KEY = get_user_api_key('cf_internal_role')

pytestmark = pytest.mark.fed_ui


@pytest.fixture(scope="module")
def create_job_and_hosted_channel(app):
    job = JobAPI(API_KEY)
    job.create_simple_job()

    # create 3 hosted channel as available channels
    for i in range(3):
        payload = {
            "name": _hc_name[i]
        }
        hc_res = HC(API_KEY).create_channel(payload)
        hc_res.assert_response_status(201)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job.job_id)

    app.job.open_action("Settings")
    app.navigation.click_link("Select Contributor Channels")
    available_hosted_channel = app.job.get_available_hosted_channels()
    for channel in _hc_name:
        assert channel in available_hosted_channel
    app.job.select_hosted_channel_by_name(_hc_name[0])
    app.job.select_hosted_channel_by_name(_hc_name[1], save=True)
    return job.job_id


def test_copy_job_copy_hosted_channel(app, create_job_and_hosted_channel):
    # copy job with all units and no units
    for unit in ["all_units", ""]:
        copied_job = JobAPI(API_KEY)
        copied_job_resp = copied_job.copy_job(create_job_and_hosted_channel, unit)
        copied_job_resp.assert_response_status(200)

        app.mainMenu.jobs_page()
        app.job.open_job_with_id(copied_job.job_id)
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        available_hosted_channel = app.job.get_available_hosted_channels()
        for channel in _hc_name:
            assert channel in available_hosted_channel

        app.job.hosted_channel_is_selected(_hc_name[0])
        app.job.hosted_channel_is_selected(_hc_name[1])
        assert not app.job.hosted_channel_is_selected(_hc_name[2])
        # select channel 2 and deselect channel 0
        app.job.select_hosted_channel_by_name(_hc_name[2])
        app.job.select_hosted_channel_by_name(_hc_name[0], save=True)

        app.navigation.click_link("Select Contributor Channels")
        assert not app.job.hosted_channel_is_selected(_hc_name[0])
        app.job.hosted_channel_is_selected(_hc_name[1])
        app.job.hosted_channel_is_selected(_hc_name[2])
        app.navigation.click_link('Ok')
