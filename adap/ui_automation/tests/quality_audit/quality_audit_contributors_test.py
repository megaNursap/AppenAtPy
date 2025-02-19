import pytest

from adap.api_automation.utils.data_util import get_user_email, get_user_password

pytestmark = pytest.mark.regression_ipa


TEST_DATA_RADIO = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('radio', '')
TEST_DATA_CHECKBOX = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkbox', '')
TEST_DATA_CHECKBOXES = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('checkboxes', '')
TEST_DATA_RATINGS = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('ratings', '')
TEST_DATA_SELECT = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('select', '')
TEST_DATA_TEXT = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('text', '')
TEST_DATA_TEXTAREA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('textarea', '')
TEST_DATA_TAXONOMY = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('taxonomy', '')


@pytest.mark.regression_ipa
@pytest.mark.parametrize('job_id',
                         [
                             TEST_DATA_RADIO,
                             TEST_DATA_CHECKBOX,
                             TEST_DATA_CHECKBOXES,
                             TEST_DATA_RATINGS,
                             TEST_DATA_SELECT,
                             TEST_DATA_TEXT,
                             TEST_DATA_TEXTAREA,
                             TEST_DATA_TAXONOMY
                         ])
def test_check_contributors_page(app_test, job_id):
    """Checks that contributors page appears for Quality Audit"""

    user_email = get_user_email('test_account')
    password = get_user_password('test_account')

    app_test.user.login_as_customer(user_name=user_email, password=password)
    app_test.job.ipa.open_quality_audit_with_endpoint(
        quality_audit_job_id=job_id,
        endpoint='contributors'
    )

    assert app_test.verification.wait_untill_text_present_on_the_page('Contributor ID', 10)
    app_test.verification.text_present_on_page('Overall Accuracy')
    app_test.verification.text_present_on_page('Judgments')

    app_test.navigation.click_on_element_by_attribute_value(attribute='data-test-id', value='item-header')

    app_test.verification.text_present_on_page('Unit ID')
    app_test.verification.text_present_on_page('name')
    app_test.verification.text_present_on_page('Judgment ID')
    app_test.verification.text_present_on_page('See Full List')
