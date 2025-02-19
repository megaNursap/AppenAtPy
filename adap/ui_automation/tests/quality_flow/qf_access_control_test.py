import pytest

from adap.api_automation.utils.data_util import get_test_data

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              pytest.mark.qf_ui_smoke,
              mark_env]


def test_qf_is_disable(app_test):
    """
    'Quality Flow Enabled' flag must be disabled for test_account
    and feature is not available
    """
    username = get_test_data('test_predefined_jobs', 'email')
    password = get_test_data('test_predefined_jobs', 'password')

    app_test.user.login_as_customer(username, password)
    app_test.mainMenu.menu_item_is_disabled('quality')


def test_qf_is_enabled(app_test):
    """
    'Quality Flow Enabled' flag is enabled for qf_user_ui
    and feature is available
    """
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')

    app_test.user.login_as_customer(username, password)
    app_test.mainMenu.menu_item_is_disabled('quality', is_not=True)

    app_test.mainMenu.quality_flow_page()

    app_test.verification.text_present_on_page('Projects')
    app_test.verification.text_present_on_page('PROJECT ID')
    app_test.verification.text_present_on_page('PROJECT NAME')
    app_test.verification.text_present_on_page('CREATION DATE')
    app_test.verification.text_present_on_page('TOTAL UNITS')
    app_test.verification.text_present_on_page('ENRICHMENT')
    app_test.verification.text_present_on_page('Create Project')

