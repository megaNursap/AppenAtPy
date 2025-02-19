from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('unsupported_cml_tag', '')
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')


@pytest.fixture(scope='module')
def login(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)


@pytest.mark.regression_ipa
def test_generate_aggregations_unsupported_cml(app, login):
    """
    Checks that the user can generate aggregations (Setup Audit) with unsupported CML
    """

    app.job.ipa.open_quality_audit_page(TEST_DATA)
    make = Make(API_KEY)
    resp = make.get_jobs_cml_tag(TEST_DATA)
    cml_tags = resp.json_response

    assert app.verification.wait_untill_text_present_on_the_page('Setup Audit', 60)
    app.navigation.click_link('Setup Audit')

    app.verification.text_present_on_page(
        'Select up to 3 different columns from your source data to display in the audit preview. '
        'Please note that at least 1 source data column is required for the preview.'
    )

    assert cml_tags[0]['name'] == 'hours'
