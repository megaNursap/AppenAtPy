import pytest
import allure

from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.api_automation.utils.data_util import get_user_api_key

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
@pytest.mark.parametrize('cml_type, question_name, job_id',
                         [('radio', 'what_on_picture', TEST_DATA_RADIO),
                          ('checkbox', 'is_number', TEST_DATA_CHECKBOX),
                          ('checkboxes', 'has_fruit', TEST_DATA_CHECKBOXES),
                          ('ratings', 'your_rating_for_this_food', TEST_DATA_RATINGS),
                          ('select', 'how_do_you_prefer_your_eggs', TEST_DATA_SELECT),
                          ('text', 'color', TEST_DATA_TEXT),
                          ('textarea', 'describe_the_picture', TEST_DATA_TEXTAREA),
                          ('taxonomy_tool', 'taxonomy_qa', TEST_DATA_TAXONOMY)])
@allure.parent_suite('jobs/{job_id}/contributors')
def test_get_contributors(cml_type, question_name, job_id):
    """Checks that contributors appear for Quality Audit"""

    api_key = get_user_api_key('test_account')
    quality_audit = IPA_API(api_key)

    res = quality_audit.get_contributors(job_id, question_name)
    res.assert_response_status(200)
    assert res.json_response['contributors']
