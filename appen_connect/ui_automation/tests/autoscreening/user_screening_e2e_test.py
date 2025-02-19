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


@pytest.fixture(autouse=True)
def for_each_test(app):
    yield
    app.navigation.refresh_page()
    app.user_screening.open()


def test_user_screening_find_by_id(app):
    user_id = '1298483'

    assert app.user_screening.search_users(user_id)\
               .reset_filter_status()\
               .get_first_user_row()\
               .id == user_id


def test_user_screening_find_by_user_name(app):
    user_name = 'Test User'

    assert app.user_screening.search_users(user_name)\
               .reset_filter_status()\
               .get_first_user_row()\
               .username == user_name


def test_user_screening_dashboard_loads_data(app):
    user_rows = app.user_screening.get_all_user_rows()

    assert app.verification.text_present_on_page('No results found', False)
    for user_row in user_rows:
        assert user_row.id
        assert user_row.username
        assert user_row.status == 'Application Received'
        assert user_row.last_update
        assert f'qrp/core/vendor/view/{user_row.id}' in user_row.vendor_url


def test_verify_ip_check_modal(app):
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()

    assert user_row.get_ip_check_status() in ['Passed', 'Failed']

    ip_check_modal = user_row.click_ip_check_review_button()
    assert ip_check_modal.get_detected_ip_address()
    assert ip_check_modal.get_detected_ip_location()


def test_verify_maliciousness_modal(app):
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()

    signals_count = user_row.get_maliciousness_signals_count()
    assert signals_count > 0
    assert user_row.get_maliciousness_check_status() in ['Low', 'Medium', 'High']

    maliciousness_check_modal = user_row.click_maliciousness_review_button()
    assert maliciousness_check_modal.get_signals_count() == signals_count

    signal_list = maliciousness_check_modal.get_signals_list()
    assert len(signal_list) == signals_count
    for signal in signal_list:
        assert signal['type']
        assert signal['text']


def test_verify_duplicates_modal(app):
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()

    assert 'duplicates found' in user_row.get_duplicates_check_text()
    amount_val = user_row.get_duplicates_check_amount()
    if isinstance(amount_val, int):
        assert amount_val > 0
    else:
        assert amount_val == 'No'

    duplicates_modal = user_row.click_duplicates_check_review_button()
    assert duplicates_modal.get_total_duplicates_text() in \
           duplicates_modal.get_total_duplicates_table_footer_text()


@pytest.mark.parametrize(
    'filter_name, current_filter_status',
    [
        ('Users Waiting To Be Screened', 'Application Received'),
        ('Users Requiring Activation',   'In Activation Queue'),
        ('Users Staged',                 'Staged'),
    ])
def test_view_numbers_apply_filters(app, filter_name, current_filter_status):
    view_numbers_modal = app.user_screening.view_numbers()
    users_amount = view_numbers_modal.get_filter_by_users_amount(filter_name)
    view_numbers_modal.filter_by(filter_name)
    total_users_on_the_page = app.user_screening.get_total_users_amount_footer()

    assert int(users_amount) == total_users_on_the_page
    assert app.user_screening.get_current_filter_status() == current_filter_status


def test_review_a_duplicate(app):
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    assert 'duplicates found' in user_row.get_duplicates_check_text()

    duplicates_modal = user_row.click_duplicates_check_review_button()
    duplicate_amount = duplicates_modal.get_total_duplicates_amount()
    duplicates_modal \
        .get_first_duplication_verification_row() \
        .click_on_toggle_user_row() \
        .click_on_this_user_is_not_duplicate() \
        .save_changes()

    assert app.verification.text_present_on_page('User updated successfully')
    assert duplicates_modal.get_total_duplicates_amount() == duplicate_amount - 1


@pytest.mark.parametrize(
    'filter_status, action_button, expected_statuses',
    [
        ('Active',                  'Suspend',                      ('Suspended', 'Expired Contract')),
        ('Rejected',                'Restart Qualification Process', 'Registered'),
        ('Abandoned',               'Restart Qualification Process', 'Registered'),
        ('Suspended',               'Reinstate',                     'Contract Pending'),
        ('Reactivation Requested',  'Reinstate',                     'Contract Pending'),
        ('Express Active',          'Suspend',                       'Suspended'),
        ('Application Received',      'Stage',                         'Staged'),
        # ('Application Received',      'Complete',                      'Screened'), #commented, tested per test_complete_single_user
    ])
def test_view_action_button_apply_filters(app, filter_status, action_button, expected_statuses):
    app.user_screening \
        .reset_filter_status() \
        .empty_search_users_field()

    app.user_screening.filter_status_by(filter_status)
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    user_id = user_row.id

    user_row.click_on_action_button(action_button)
    if action_button == 'Stage':
        user_row.select_reason('Pending verification (address, resume, etc)')
    user_row.proceed()

    assert app.user_screening \
              .reset_filter_status() \
              .search_users(user_id) \
              .get_first_user_row() \
              .status in expected_statuses


def test_bulk_update_button(app):
    user_rows = app.user_screening.get_all_user_rows()[:2]
    for user_row in user_rows:
        user_row.select()

    app.user_screening.click_on_bulk_update_button()
    assert app.verification.text_present_on_page('Complete')
    assert app.verification.text_present_on_page('Stage')
    assert app.verification.text_present_on_page('Reject')
    assert app.verification.text_present_on_page('Add User Note')
    assert app.verification.text_present_on_page('Download .CSV')


def test_view_resume(app):
    app.user_screening \
        .reset_filter_status() \
        .search_users(1297563)

    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()

    assert app.verification.text_present_on_page('View Resume')


# def test_reject_user(app):
#     """
#     Verify if the action button Reject User is displayed and it works correctly for the filter In Activation Queue
#     """
#
#     app.user_screening.filter_status_by('In Activation Queue')
#
#     user_row = app.user_screening.get_first_user_row()
#     assert user_row.status == 'In Activation Queue'
#
#     user_id = user_row.id
#     print(user_id)
#
#     user_row.click_on_toggle_user_row().click_on_action_button("Reject User")
#     user_row.select_reason('Did not meet project requirement')
#     user_row.proceed()
#
#     assert app.user_screening \
#               .reset_filter_status() \
#               .empty_search_users_field() \
#               .search_users(user_id) \
#
#     user_row = app.user_screening.get_first_user_row()
#
#     assert user_row.status == 'Rejected'


def test_sign_msa_action(app, login):
    """
    Verify if the SignMSA->Proceed action works correctly
    """
    app.verification.text_present_on_page('User screening')
    app.user_screening.reset_filter_status().empty_search_users_field()

    app.user_screening.filter_status_by('In Activation Queue')
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    app.verification.text_present_on_page('Profile info')
    app.navigation.click_btn('Sign MSA')
    app.verification.text_present_on_page('Are you sure you want to proceed?')
    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page('Profile info')
    app.navigation.click_btn('Sign MSA')
    app.verification.text_present_on_page('Are you sure you want to proceed?')
    app.navigation.click_btn('Proceed')


def test_view_master_services_agreement(app):
    app.user_screening \
        .filter_status_by('In Activation Queue')
    user_row = app.user_screening.get_first_user_row()
    assert user_row.status == 'In Activation Queue'

    current_window = app.driver.window_handles[0]
    user_row.click_on_toggle_user_row() \
        .view_master_service_agreement()

    agreement_window = app.driver.window_handles[1]
    app.navigation.switch_to_window(agreement_window)
    assert app.verification.text_present_on_page('MASTER SERVICES AGREEMENT')
    assert app.verification.text_present_on_page('THIS AGREEMENT (“AGREEMENT”) IS MADE AND ENTERED INTO')
    app.navigation.switch_to_window(current_window)


def test_email_contributor_action(app, login):
    """
    Verify if the Email Contirbutor action works correctly
    """
    app.verification.text_present_on_page('User screening')
    app.user_screening.reset_filter_status().empty_search_users_field()

    app.user_screening.filter_status_by('In Activation Queue')
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    app.verification.text_present_on_page('Profile info')
    app.navigation.click_btn('Email Contributor')
    app.verification.text_present_on_page('Do you want to email the MSA to the vendor?')
    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page('Profile info')
    app.navigation.click_btn('Email Contributor')
    app.verification.text_present_on_page('Do you want to email the MSA to the vendor?')
    user_row = app.user_screening.get_first_user_row()
    user_row.proceed(msg="Document successfully sent!")


def test_reject_msa_action(app, login):
    """
    Verify if the Reject MSA action works correctly
    """
    app.verification.text_present_on_page('User screening')
    app.user_screening.reset_filter_status().empty_search_users_field()

    app.user_screening.filter_status_by('In Activation Queue')
    user_row = app.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    app.verification.text_present_on_page('Profile info')
    app.navigation.click_btn('Reject MSA')
    app.verification.text_present_on_page('Are you sure you want to proceed?')
    app.navigation.click_btn('Cancel')
    app.verification.text_present_on_page('Profile info')
    app.navigation.click_btn('Reject MSA')
    app.verification.text_present_on_page('Are you sure you want to proceed?')
    user_row = app.user_screening.get_first_user_row()
    user_row.proceed(msg="MSA rejected successfully!")
