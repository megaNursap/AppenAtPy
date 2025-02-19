import time

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.in_platform_audit import IPA_API

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkbox', "")
UNIT_ID = '2295310297'


@pytest.fixture(scope="module")
def ipa_job(app):
    """
    Fixture logs in, opens job and returns IPA job
    """

    user_name = get_user_email('test_account')
    password = get_user_password('test_account')
    api_key = get_user_api_key('test_account')
    app.user.login_as_customer(user_name=user_name, password=password)
    app.job.ipa.open_quality_audit_page(TEST_DATA)
    ipa = IPA_API(api_key)

    return ipa


@pytest.mark.regression_ipa
def test_download_audit_aggregated_report(app, ipa_job):
    """
    Checks that the 'Audit Aggregated Report' is downloaded after rejecting and approving unit
    """

    app.job.ipa.view_details_by_unit_id(UNIT_ID)
    app.job.ipa.reject_question()
    app.job.ipa.select_correct_answer("seven")
    app.job.ipa.close_view_details()

    app.job.ipa.view_details_by_unit_id(UNIT_ID)
    app.job.ipa.approve_question()
    app.job.ipa.close_view_details()

    rp_res = ipa_job.generate_ipa_report(TEST_DATA)
    rp_res.assert_response_status(200)
    report_status = rp_res.json_response

    assert report_status['version'] is not None
    assert report_status['status'] == 'generating'
    assert report_status['file_url'] is None

    report_version = report_status['version']
    time.sleep(10)

    assert report_version is not None

    wait = 10
    running_time = 0
    current_status = ""
    while (current_status != 'finished') and (running_time < 30):
        rp_res = ipa_job.get_ipa_report(TEST_DATA, report_version)
        rp_res.assert_response_status(200)
        report_status = rp_res.json_response
        current_status = report_status['status']
        running_time += wait
        time.sleep(wait)

    assert report_status['version'] == report_version
    assert report_status['status'] == 'finished'
    assert report_status['file_url'] is not None
