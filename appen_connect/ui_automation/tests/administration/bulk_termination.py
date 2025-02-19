import datetime

import pytest

from adap.api_automation.utils.data_util import get_test_data, generate_random_string, convert_date_format_iso8601

pytestmark = pytest.mark.regression_ac_user_screening

_USERNAME = get_test_data('test_ui_account', 'email')
_PASSWORD = get_test_data('test_ui_account', 'password')
_USER_ID_TO_TERMINATE = get_test_data('test_qa_user', 'id')
_USER_ID2_TO_TERMINATE = get_test_data('ac_internal_user', 'id')
_USER_ID3_TO_TERMINATE = get_test_data('test_consent_form_vendor', 'id')


@pytest.fixture(scope="module", autouse=True)
def login(app):
    app.ac_user.login_as(_USERNAME, _PASSWORD)
    app.navigation.click_link('Administration')


@pytest.mark.parametrize(
    'user_ids', [[_USER_ID_TO_TERMINATE], [_USER_ID2_TO_TERMINATE, _USER_ID3_TO_TERMINATE]])
def test_terminate_users(app, user_ids):
    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()
    termination_date = convert_date_format_iso8601(tomorrow, '%m/%d/%Y')
    note = generate_random_string(10)
    reason = 'URL Quality'

    app.navigation.click_link('Administration')
    app.administration \
        .open_batch_user_termination() \
        .set_termination_date(termination_date)\
        .set_user_ids(user_ids)\
        .set_termination_note(note)\
        .select_reason(reason)\
        .terminate()

    for user_id in user_ids:
        app.navigation.click_link('Vendors')
        status = app.vendor_pages.find_and_get_vendor_status_by_id(user_id)
        assert status == 'Terminated'

        app.vendor_pages.open_vendor_profile_by(user_id, search_type='id')
        assert 'TERMINATED' in app.vendor_pages.get_profile_user_status()
        profile_date = app.vendor_pages.get_profile_user_termination_date()
        assert profile_date == convert_date_format_iso8601(tomorrow, '%b %-d, %Y')
        profile_reason = app.vendor_pages.get_profile_user_termination_reason()
        assert profile_reason == reason
        profile_note = app.vendor_pages.get_profile_user_termination_note()
        assert profile_note == note

        app.vendor_pages.unterminate_user()
        assert 'TERMINATED' not in app.vendor_pages.get_profile_user_status()
