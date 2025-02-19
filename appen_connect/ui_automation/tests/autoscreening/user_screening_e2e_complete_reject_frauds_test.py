import time

import pytest


from adap.api_automation.utils.data_util import get_test_data

pytestmark = pytest.mark.regression_ac_user_screening

_USERNAME = get_test_data('test_ui_account', 'email')
_PASSWORD = get_test_data('test_ui_account', 'password')


@pytest.fixture(scope="module", autouse=True)
def login(app):
    app.ac_user.login_as(_USERNAME, _PASSWORD)
    app.navigation.click_link('Recruiting')
    app.user_screening.open()

    #check data presents or generate if not
    # app.user_screening.filter_status_by('Application Received')
    # app.user_screening.search_users('firstname')
    # users = app.user_screening.get_all_user_rows()
    # if len(users) < 2:
    #     pass
    #     ## TODO generate users_under_test


@pytest.fixture(autouse=True)
def for_each_test(app):
    yield
    app.navigation.refresh_page()
    app.user_screening.open()


@pytest.mark.parametrize('num_of_users, num_of_signals', [
        [2, 1],
        [2, 3],
        [2, 100]])
def test_complete_bulk_users(app, num_of_users, num_of_signals):
    """
    Verify complete the bulk users with one (1), three(3) оr all(100) signals selected
    """
    existing_status = 'Application Received'
    target_status = 'Screened'
    operation = "Complete"

    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.verification.text_present_on_page('User screening')
    app.user_screening.reset_filter_status().\
        empty_search_users_field().\
        filter_status_by(existing_status)
    # app.user_screening.search_users('firstname')

    user_rows = app.user_screening.get_all_user_rows()[:num_of_users]

    userids = []

    for user_row in user_rows:
        user_row.select()
        userids.append(user_row.id)

    app.user_screening.click_on_bulk_update_button()
    app.user_screening.choose_bulk_update_option(select_option=operation)

    modal_win_title = f"Bulk {operation}"
    assert modal_win_title == omw.get_modal_win_title(), \
        f"Modal window title not as {modal_win_title}"

    expected_signal_nums, selected = omw.select_signals(num_of_signals)
    actual_signal_nums = len(selected)
    assert expected_signal_nums == actual_signal_nums, \
        f"Invalid number selected signals. Expected: {expected_signal_nums} Actual: {actual_signal_nums}"

    actual_total_signal_nums = omw.get_content_of_total_selected_signals_counter()
    assert expected_signal_nums == actual_total_signal_nums, \
        f"Invalid selected signals total counter Expected: {expected_signal_nums}, Actual: {actual_total_signal_nums}"

    assert omw.manage_button('Proceed'), f"Operation {operation} not proceed"

    app.user_screening.check_users_status(userids, expected_status=target_status)


@pytest.mark.parametrize('num_of_signals', [1, 3, 100])
def test_complete_single_user(app, num_of_signals):
    """
    Verify complete the user with one (1), three(3) оr all(100) signals selected
    """
    existing_status = 'Application Received'
    target_status = 'Screened'
    operation = "Complete"
    focus_user_name = 'firstname'

    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.verification.text_present_on_page('User Screening')
    app.user_screening \
        .reset_filter_status() \
        .empty_search_users_field()

    app.user_screening.filter_status_by(existing_status)
    if len(focus_user_name):
        app.user_screening.search_users(focus_user_name)

    user_row = app.user_screening.get_first_user_row()
    user_id = user_row.id
    #
    assert int(user_id) > 0, 'Userid cannot be 0'
    user_row.click_on_toggle_user_row()
    user_row.click_on_action_button(action_name=operation)

    assert omw.get_modal_win_title() == operation, f"Modal window title is not {operation}"
    expected_signal_nums, selected = omw.select_signals(num_of_signals)
    actual_signal_nums = len(selected)
    print(f"Selected signals: {selected}")
    assert expected_signal_nums == actual_signal_nums,\
        f"Invalid number selected signals. Expected: {expected_signal_nums} Actual: {actual_signal_nums}"

    actual_total_signal_nums = omw.get_content_of_total_selected_signals_counter()
    assert expected_signal_nums == actual_total_signal_nums,\
        f"Invalid selected signals total counter Expected: {expected_signal_nums}, Actual: {actual_total_signal_nums}"

    assert omw.manage_button('Proceed'), f"Operation {operation} not proceed"

    app.user_screening.reset_filter_status().empty_search_users_field()
    app.user_screening.search_users(user_id)

    expected_user_row = app.user_screening.get_first_user_row()
    assert expected_user_row.status == target_status


@pytest.mark.parametrize('operation', ['Complete', 'Stage', 'Reject'])
def test_operation_without_required_selection_bulk_users_(app, operation):
    """
    Verify operations for bulk users cannot proceed without required selection
    """
    existing_status = 'Application Received'
    num_of_users = 2

    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()
    time.sleep(1)

    app.verification.text_present_on_page('User screening')
    app.user_screening.reset_filter_status()
    app.user_screening.empty_search_users_field()

    app.user_screening.filter_status_by(existing_status)
    expected_operation_modal_win_title = 'Bulk ' + operation
    all_rows = app.user_screening.get_all_user_rows()
    assert len(all_rows) >= num_of_users, 'Not enough users in list'
    user_rows = app.user_screening.get_all_user_rows()[:num_of_users]
    users_id = []

    for user_row in user_rows:
        assert user_row.status == existing_status, f"Current user status is not {existing_status}"
        user_row.select()
        users_id.append(user_row.id)

    assert len(users_id) == num_of_users, "Incorrect number of users selected"
    app.user_screening.click_on_bulk_update_button()
    app.user_screening.choose_bulk_update_option(select_option=operation)

    assert omw.get_modal_win_title() == expected_operation_modal_win_title,\
        f"Modal window title is not {expected_operation_modal_win_title}"
    assert omw.is_proceed_button_disabled(), "Button Proceed shall not be enabled"

    assert omw.manage_button('Cancel'), f"Canceling {operation} not proceed"

@pytest.mark.parametrize('operation', ['Complete', 'Stage', 'Reject'])
def test_operation_without_required_selection_single_user(app, operation):
    """
    Verify operations (Complete, Stage, Reject) for single user cannot proceed without required selection
    """
    existing_status = 'Application Received'

    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.verification.text_present_on_page('User screening')
    app.user_screening.reset_filter_status()
    app.user_screening.empty_search_users_field()

    app.user_screening.filter_status_by(existing_status)

    expected_operation_modal_win_title = operation

    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    user_id = user_row.id

    assert int(user_id) > 0, 'Userid cannot be 0'
    user_row.click_on_action_button(operation)

    assert omw.get_modal_win_title() == expected_operation_modal_win_title,\
        f"Modal window title is not {expected_operation_modal_win_title}"
    assert omw.is_proceed_button_disabled(), "Button Proceed shall not be enabled"
    assert omw.manage_button('Cancel'), f"Canceling {operation} not proceed"

@pytest.mark.parametrize('num_of_frauds', [1, 3, 100])
def test_reject_via_frauds_bulk_users(app, num_of_frauds):
    """
    Verify bulk users can be rejected with single(1), three(3) or all(100) numbers of frauds
    """
    operation = "Reject"
    reason = "Duplicate or Fraud"
    total_users = 2
    existing_status = 'Application Received'
    target_status = 'Rejected'

    # clean up start
    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.verification.text_present_on_page('User screening')
    app.user_screening \
        .reset_filter_status() \
        .empty_search_users_field()
    # clean up end

    # app.user_screening.search_users("firstname") #narrow search to generated users
    app.user_screening.filter_status_by(existing_status)

    user_rows = app.user_screening.get_all_user_rows()[:total_users]

    user_ids = []

    for user_row in user_rows:
        assert user_row.status == existing_status, f"Current user status is not {existing_status}"
        user_row.select()
        user_ids.append(user_row.id)

    app.user_screening.click_on_bulk_update_button()
    app.user_screening.choose_bulk_update_option(select_option=operation)
    expected_modal_win_title = f'Bulk {operation}'

    assert omw.get_modal_win_title() == expected_modal_win_title, \
        f"Modal window title is not {expected_modal_win_title}"
    omw.select_reason(reason)

    expected_frauds, actual_list_selected_frauds = omw.select_frauds(num_of_frauds=num_of_frauds)
    actual_num_frauds = len(actual_list_selected_frauds)
    assert expected_frauds == actual_num_frauds, \
        f"Frauds. Expected: {num_of_frauds} Actual: {actual_num_frauds}"

    total_selected_frauds_shown = omw.get_content_of_total_frauds_counter()
    assert expected_frauds == total_selected_frauds_shown, \
        f"Total selected frauds counter Expected: {expected_frauds} Actual: {total_selected_frauds_shown}"

    assert omw.manage_button('Proceed'), f"Operation {operation} not proceed"

    for user_id in user_ids:
        app.user_screening.empty_search_users_field()
        app.user_screening.search_users(user_id)
        app.user_screening.reset_filter_status()

        user_current_status = app.user_screening.get_first_user_row().status
        assert user_current_status == target_status, \
            f'User {user_id} has status {user_current_status}, expected: {target_status}'


@pytest.mark.parametrize('num_of_frauds', [1, 3, 100])
def test_reject_via_frauds_single_user(app, num_of_frauds):
    """
    Verify single user can be rejected with single(1), three(3) or all(100) numbers of frauds
    """
    operation = "Reject"
    reason = "Duplicate or Fraud"
    existing_status = 'Application Received'
    target_status = 'Rejected'

    #clean up start
    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.verification.text_present_on_page('User screening')
    app.user_screening \
        .reset_filter_status() \
        .empty_search_users_field()
    #clean up end

    # app.user_screening.search_users("firstname") #narrow search to generated users
    app.user_screening.filter_status_by(existing_status)

    user_row = app.user_screening.get_first_user_row()
    user_row.select()
    user_id = user_row.id
    assert user_row.status == existing_status, f"Current user status is not {existing_status}"
    assert int(user_id) > 0, "User id from row cannot be negative"

    #invoke operation
    user_row.click_on_toggle_user_row()
    user_row.click_on_action_button(action_name=operation)

    assert omw.get_modal_win_title() == operation, f"Modal window title is not {operation}"
    omw.select_reason(reason)

    expected_frauds, actual_list_selected_frauds = omw.select_frauds(num_of_frauds=num_of_frauds)
    actual_num_frauds = len(actual_list_selected_frauds)
    assert expected_frauds == actual_num_frauds, f"Frauds. Expected: {num_of_frauds} Actual: {actual_num_frauds}"

    total_selected_frauds_shown = omw.get_content_of_total_frauds_counter()
    assert expected_frauds == total_selected_frauds_shown, \
        f"Total selected frauds counter Expected: {expected_frauds} Actual: {total_selected_frauds_shown}"

    assert omw.manage_button('Proceed'), f"Operation {operation} not proceed"

    app.user_screening.reset_filter_status()
    app.user_screening.empty_search_users_field()
    app.user_screening.search_users(user_id)

    user_current_status = app.user_screening.get_first_user_row().status
    assert user_current_status == target_status, \
        f'User {user_id} has status {user_current_status}, expected: {target_status}'


@pytest.mark.parametrize('user_status, reason,', [
    ('In Activation Queue', 'Did not meet project requirement'),
    ('In Activation Queue', 'DNH state for US and country'),
    ('In Activation Queue', 'Other'),
    ('Application Received', 'Did not meet project requirement'),
    ('Application Received', 'DNH state for US and country'),
    ('Application Received', 'Other'),
        ])
def test_reject_common_bulk_users(app, user_status, reason):
    """
    Verify bulk users can be rejected with 'Did not meet project requirement', 'DNH state for US and country' or 'Other' reason(s)
    """
    operation = "Reject"
    total_users = 2
    target_users_status = 'Rejected'
    focus_username = "firstname"

    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.user_screening \
        .reset_filter_status() \
        .empty_search_users_field()

    app.user_screening.filter_status_by(user_status)
    # app.user_screening.search_users(focus_username)

    user_rows = app.user_screening.get_all_user_rows()[:total_users]

    user_ids = []

    for user_row in user_rows:
        assert user_row.status == user_status, f"Current user status is not {user_status}"
        user_row.select()
        user_ids.append(user_row.id)

    assert len(user_ids) == total_users, "Not enough users for bulk update"

    app.user_screening.click_on_bulk_update_button()
    app.user_screening.choose_bulk_update_option(select_option=operation)
    modal_win_title = f"Bulk {operation}"
    assert modal_win_title == omw.get_modal_win_title(), \
        f"Modal window title not as {modal_win_title}"

    app.verification.text_present_on_page('Action will be applied to')
    app.verification.text_present_on_page(f'{total_users}')

    omw.select_reason(reason)
    assert omw.manage_button('Proceed'), f"Operation {operation} not proceed"

    app.user_screening.check_users_status(user_ids,expected_status=target_users_status)


@pytest.mark.parametrize('user_status, reason,', [
    ('In Activation Queue', 'Did not meet project requirement'),
    ('In Activation Queue', 'DNH state for US and country'),
    ('In Activation Queue', 'Other'),
    ('Application Received', 'Did not meet project requirement'),
    ('Application Received', 'DNH state for US and country'),
    ('Application Received', 'Other'),
        ])
def test_reject_common_single_user(app, user_status, reason):
    """
    Verify single user can be rejected with 'Did not meet project requirement', 'DNH state for US and country' or 'Other' reason(s)
    """
    operation = "Reject"
    target_status = 'Rejected'
    focus_username = "firstname"

    # clean up start
    omw = app.user_screening.define_operational_modal_window(action=operation)
    omw.close_dialog()

    app.verification.text_present_on_page('User screening')
    app.user_screening \
        .reset_filter_status() \
        .empty_search_users_field()
    # clean up end

    app.user_screening.filter_status_by(user_status)
    # app.user_screening.search_users(focus_username)
    user_row = app.user_screening.get_first_user_row()
    user_row.select()
    user_id = user_row.id
    assert user_row.status == user_status, f"Current user status is not {user_status}"
    assert int(user_id) > 0, "User id from row cannot be negative"

    # invoke operation
    user_row.click_on_toggle_user_row()
    user_row.click_on_action_button(action_name=operation)

    assert omw.get_modal_win_title() == operation, f"Modal window title is not {operation}"
    omw.select_reason(reason)

    assert omw.manage_button('Proceed'), f"Operation {operation} not proceed"

    app.user_screening.reset_filter_status()
    app.user_screening.empty_search_users_field()
    app.user_screening.search_users(user_id)

    user_current_status = app.user_screening.get_first_user_row().status
    assert user_current_status == target_status, \
        f'User {user_id} has status {user_current_status}, expected: {target_status}'