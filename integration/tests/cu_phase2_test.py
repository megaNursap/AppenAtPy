import time

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.service_util import delete_jobs
from integration.tests.cu_phase1_test import _create_adap_user, _prepare_adap_user


@pytest.fixture(scope="module", autouse=True)
def delete_adap_jobs():
    yield
    delete_jobs(pytest.data.job_collections, env='integration')


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_feca_contributor_request_withdraw_money(app):
    user_name, password = _create_adap_user(app)
    copy_job_id = _prepare_copy_job(app)

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.navigation.click_link('Register')
    app.adap.navigation.click_link('Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.navigation.click_btn('Skip', timeout=5)
    app.adap.user.contributor.close_guide()

    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')
    app.adap.navigation.click_link('Payment Method')
    app.adap.verification.text_present_on_page(
        "You need to link your PayPal account and withdraw your micro tasks "
        "payment from this page.")

    app.adap.navigation.click_link('Add')
    app.adap.verification.text_present_on_page('Connect to PayPal')

    paypal_account = 'qa+paypal3@figure-eight.com'
    app.adap.user.add_paypal_account(paypal_account, password)
    time.sleep(3)

    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')
    app.adap.navigation.click_link('Payment Method')

    app.adap.verification.text_present_on_page('paypal')
    app.adap.verification.text_present_on_page('qa+paypal3@figure-eight.com')
    time.sleep(10)

    app.adap.navigation.click_link('Jobs')
    time.sleep(5)
    assert app.adap.user.contributor.get_available_jobs_amount() >= 1
    app.adap.user.contributor.sort_jobs_by('Job')

    app.adap.user.contributor.open_job_contains_text(copy_job_id)
    current_window = app.adap.driver.window_handles[0]
    window_after = app.adap.driver.window_handles[1]
    app.adap.navigation.switch_to_window(window_after)

    # doesn't work submitting judgments using API calls:
    # j = Judgments(user_name, password, env=pytest.env, internal=True)
    # Config.JOB_TYPE = 'what_is_greater'
    # assignment_page = j.get_assignments(internal_job_url=job_link, job_id=job_id)
    # j.contribute(assignment_page)
    # time.sleep(60)

    app.adap.job.judgements.create_random_judgments_answer(var_numbers=2)
    assert app.adap.verification.wait_untill_text_present_on_the_page(
        text="Wait! Before you go!", max_time=10
    )
    app.adap.driver.close()
    app.adap.navigation.switch_to_window(current_window)

    app.adap.user.contributor.logout()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.user.contributor.open_payments_menu()
    app.adap.verification.text_present_on_page("Available for Withdraw")
    withdraw_balance = app.adap.user.contributor.get_withdraw_balance()
    app.adap.navigation.click_link('Withdraw Funds')
    app.adap.verification.text_present_on_page('Withdraw Request')

    app.adap.navigation.click_link('Request')
    app.adap.verification.text_present_on_page('Request Received!')

    app.adap.navigation.click_link('Check Status')

    app.adap.user.contributor.open_payments_menu()
    app.adap.verification.text_present_on_page("Available for Withdraw")
    pending_balance = app.adap.user.contributor.get_pending_payment_balance()

    assert withdraw_balance == pending_balance, 'pending payment is incorrect'
    assert app.adap.user.contributor.get_withdraw_balance() == '$0.00'


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_worker_without_paypal_account_cannot_see_withdraw_option(app):
    user_name, password = _create_adap_user(app)
    copy_job_id = _prepare_copy_job(app)

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.navigation.click_link('Register')
    app.adap.navigation.click_link('Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.navigation.click_btn('Skip', timeout=5)
    app.adap.user.contributor.close_guide()

    assert app.adap.user.contributor.get_available_jobs_amount() >= 1

    app.adap.user.contributor.sort_jobs_by('Job')
    app.adap.user.contributor.open_job_contains_text(copy_job_id)
    current_window = app.adap.driver.window_handles[0]
    window_after = app.adap.driver.window_handles[1]
    app.adap.navigation.switch_to_window(window_after)

    app.adap.job.judgements.create_random_judgments_answer(var_numbers=2)
    assert app.adap.verification.wait_untill_text_present_on_the_page(
        text="Wait! Before you go!", max_time=10
    )
    app.adap.driver.close()
    app.adap.navigation.switch_to_window(current_window)

    app.adap.user.contributor.logout()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.user.contributor.open_payments_menu()
    app.adap.verification.text_present_on_page("Available for Withdraw")
    app.adap.navigation.click_link('Withdraw Funds')
    app.adap.verification.text_present_on_page('Withdraw Request')

    app.adap.navigation.click_link('Request')
    time.sleep(2)
    app.adap.verification.text_present_on_page('Withdraw Request')


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_feca_contributor_with_paypal_account_migrated_to_ac(app, app_test):
    # the test logic:
    # create ADAP annotate account
    # add PayPal account to ADAP FECA account
    # update user migration status to 'pending'
    # pass manually a screening process in AC
    # navigate to the vendor profile page
    # check: migrated status; Paypal info, Direct pay

    _set_teardown_apps(app, app_test)

    email, password = _prepare_adap_user(app)
    additional_info = {
        'last_name': generate_random_string(10),
        'primary_language': 'English',
        'language_region': 'Australia',
        'country': 'United States of America',
        'state': 'Texas',
        'city': 'Houston',
        'full_address': generate_random_string(20),
        'postal_code': 77001,
        'phone': 2145096995
    }

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(email, password)

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('Appen Upgrade Notice')

    app.adap.navigation.click_btn('Continue', timeout=3)

    app.adap.user.contributor.fill_out_additional_information(additional_info)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Submit')

    assert app.adap.verification.text_present_on_page('Please give us a moment...')

    # manually complete user screening on the AC side
    username = get_user_name('ac_test_ui_account')
    password = get_user_password('ac_test_ui_account')
    app_test.ac.ac_user.login_as(user_name=username, password=password)
    app_test.ac.navigation.click_link('Recruiting')
    app_test.ac.user_screening.open()

    app_test.ac.user_screening.reset_filter_status()
    app_test.ac.user_screening.empty_search_users_field()
    app_test.ac.user_screening.search_users(email)

    user_row = app_test.ac.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    user_id = user_row.id
    user_row.click_on_action_button('Complete')
    user_row.select_complete_reason('Full name')
    user_row.proceed()

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Go to Dashboard')
    assert app.adap.verification.text_present_on_page('Welcome Back!')
    assert app.adap.verification.text_present_on_page('Upgrade Successful')
    assert app.adap.verification \
        .text_present_on_page('You have successfully completed the upgrade process! '
                              'You can now access your account and work on your tasks as usual.')
    app.adap.navigation.click_link('Close')

    # paypal logic
    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')
    app.adap.navigation.click_link('Payment Method')
    app.adap.verification.text_present_on_page(
        "You need to link your PayPal account and withdraw your micro tasks "
        "payment from this page.")

    app.adap.navigation.click_link('Add')
    app.adap.verification.text_present_on_page('Connect to PayPal')

    paypal_account = 'qa+paypal3@figure-eight.com'
    app.adap.user.add_paypal_account(paypal_account, password)
    time.sleep(3)

    app_test.ac.driver.switch_to.default_content()
    app_test.ac.navigation.click_link('Vendors')
    app_test.ac.vendor_pages.open_vendor_profile_by(email)
    assert app_test.ac.vendor_pages.get_profile_user_status() == 'SCREENED'
    assert app_test.ac.vendor_pages.get_profile_paypal_email() == paypal_account
    assert app_test.ac.vendor_pages.get_profile_direct_pay() == 'Yes PAYPAL'


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_payment_withdrawn_create_an_invoice_in_draft_mode_in_ac(app, app_test):
    # test logic:
    # Migrated contributor (has  correct PayPal account) with some money withdrawn
    # Navigate to AC as Internal User
    # Navigate to “Invoices” page
    # Verify for the contributor new invoice for the current period the invoice is created
    # Invoice amount = Withdrawn amount
    # Invoice status = Not Yet Submitted

    _set_teardown_apps(app, app_test)

    copy_job_id = _prepare_copy_job(app)
    email, password = _prepare_adap_user(app)
    additional_info = {
        'last_name': generate_random_string(10),
        'primary_language': 'English',
        'language_region': 'Australia',
        'country': 'United States of America',
        'state': 'Texas',
        'city': 'Houston',
        'full_address': generate_random_string(20),
        'postal_code': 77001,
        'phone': 2145096995
    }

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(email, password)

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('Appen Upgrade Notice')

    app.adap.navigation.click_btn('Continue', timeout=3)

    app.adap.user.contributor.fill_out_additional_information(additional_info)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Submit')

    assert app.adap.verification.text_present_on_page('Please give us a moment...')

    # manually complete user screening on the AC side
    username = get_user_name('ac_test_ui_account')
    password = get_user_password('ac_test_ui_account')
    app_test.ac.ac_user.login_as(user_name=username, password=password)
    app_test.ac.navigation.click_link('Recruiting')
    app_test.ac.user_screening.open()

    app_test.ac.user_screening.reset_filter_status()
    app_test.ac.user_screening.empty_search_users_field()
    app_test.ac.user_screening.search_users(email)

    time.sleep(2)
    user_row = app_test.ac.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    user_id = user_row.id
    user_row.click_on_action_button('Complete')
    user_row.select_complete_reason('Full name')
    user_row.proceed()

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Go to Dashboard')
    assert app.adap.verification.text_present_on_page('Welcome Back!')
    assert app.adap.verification.text_present_on_page('Upgrade Successful')
    assert app.adap.verification \
        .text_present_on_page('You have successfully completed the upgrade process! '
                              'You can now access your account and work on your tasks as usual.')
    app.adap.navigation.click_link('Close')

    # paypal logic
    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')
    app.adap.navigation.click_link('Payment Method')
    app.adap.verification.text_present_on_page(
        "You need to link your PayPal account and withdraw your micro tasks "
        "payment from this page.")

    app.adap.navigation.click_link('Add')
    app.adap.verification.text_present_on_page('Connect to PayPal')

    paypal_account = 'qa+paypal3@figure-eight.com'
    app.adap.user.add_paypal_account(paypal_account, password)
    time.sleep(7)

    app.adap.navigation.click_link('Jobs')
    time.sleep(5)
    assert app.adap.user.contributor.get_available_jobs_amount() >= 1

    app.adap.user.contributor.close_guide()
    app.adap.user.contributor.sort_jobs_by('Job')
    app.adap.user.contributor.open_job_contains_text(copy_job_id)
    current_window = app.adap.driver.window_handles[0]
    window_after = app.adap.driver.window_handles[1]
    app.adap.navigation.switch_to_window(window_after)

    app.adap.job.judgements.create_random_judgments_answer(var_numbers=2)
    assert app.adap.verification.wait_untill_text_present_on_the_page(
        text="Wait! Before you go!", max_time=10
    )
    app.adap.driver.close()
    app.adap.navigation.switch_to_window(current_window)

    app.adap.user.contributor.logout()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(email, password)

    app.adap.user.contributor.open_payments_menu()
    app.adap.verification.text_present_on_page("Available for Withdraw")
    withdraw_balance = app.adap.user.contributor.get_withdraw_balance()
    app.adap.navigation.click_link('Withdraw Funds')
    app.adap.verification.text_present_on_page('Withdraw Request')

    app.adap.navigation.click_link('Request')
    app.adap.verification.text_present_on_page('Request Received!')

    app_test.ac.driver.switch_to.default_content()
    app_test.ac.navigation.click_link('Invoices')
    app_test.ac.invoices.click_on_go_button()

    assert app_test.ac.invoices.get_current_status_by_text_in_row(email) == 'Not Yet Submitted'
    assert app_test.ac.invoices.get_amount(email) == withdraw_balance


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_upgraded_feca_contributor_with_paypal_account_withdrawn_their_money(app, app_test):
    # test logic:
    # Migrated contributor (has  correct PayPal account) with some money withdrawn
    # Withdrawn amount is in the 'Pending Payments'
    # Navigate to AC as Internal User
    # Navigate to “Vendor/contributor” profile page
    # Verify that the Invoice is created in “Not yet submitted” or “Draft” status
    _set_teardown_apps(app, app_test)

    user_name, password = _prepare_adap_user(app)
    copy_job_id = _prepare_copy_job(app)

    additional_info = {
        'last_name': generate_random_string(10),
        'primary_language': 'English',
        'language_region': 'Australia',
        'country': 'United States of America',
        'state': 'Texas',
        'city': 'Houston',
        'full_address': generate_random_string(20),
        'postal_code': 77001,
        'phone': 2145096995
    }

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.navigation.click_link('Register')
    app.adap.navigation.click_link('Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('Appen Upgrade Notice')

    app.adap.navigation.click_btn('Continue', timeout=3)

    app.adap.user.contributor.fill_out_additional_information(additional_info)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Submit')

    assert app.adap.verification.text_present_on_page('Please give us a moment...')

    # manually complete user screening on the AC side
    username = get_user_name('ac_test_ui_account')
    password = get_user_password('ac_test_ui_account')
    app_test.ac.ac_user.login_as(user_name=username, password=password)
    app_test.ac.navigation.click_link('Recruiting')
    app_test.ac.user_screening.open()

    app_test.ac.user_screening.reset_filter_status()
    app_test.ac.user_screening.empty_search_users_field()
    app_test.ac.user_screening.search_users(user_name)

    time.sleep(2)
    user_row = app_test.ac.user_screening.get_first_user_row()
    user_row.click_on_toggle_user_row()
    user_id = user_row.id
    user_row.click_on_action_button('Complete')
    user_row.select_complete_reason('Full name')
    user_row.proceed()

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Go to Dashboard')
    assert app.adap.verification.text_present_on_page('Welcome Back!')
    assert app.adap.verification.text_present_on_page('Upgrade Successful')
    assert app.adap.verification \
        .text_present_on_page('You have successfully completed the upgrade process! '
                              'You can now access your account and work on your tasks as usual.')
    app.adap.navigation.click_link('Close')

    # paypal logic
    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')
    app.adap.navigation.click_link('Payment Method')
    app.adap.verification.text_present_on_page(
        "You need to link your PayPal account and withdraw your micro tasks "
        "payment from this page.")

    app.adap.navigation.click_link('Add')
    app.adap.verification.text_present_on_page('Connect to PayPal')

    paypal_account = 'qa+paypal3@figure-eight.com'
    app.adap.user.add_paypal_account(paypal_account, password)
    time.sleep(7)

    app.adap.navigation.click_link('Jobs')
    time.sleep(5)
    assert app.adap.user.contributor.get_available_jobs_amount() >= 1

    app.adap.user.contributor.close_guide()
    app.adap.user.contributor.sort_jobs_by('Job')
    app.adap.user.contributor.open_job_contains_text(copy_job_id)
    current_window = app.adap.driver.window_handles[0]
    window_after = app.adap.driver.window_handles[1]
    app.adap.navigation.switch_to_window(window_after)

    app.adap.job.judgements.create_random_judgments_answer(var_numbers=2)
    assert app.adap.verification.wait_untill_text_present_on_the_page(
        text="Wait! Before you go!", max_time=10
    )
    app.adap.driver.close()
    app.adap.navigation.switch_to_window(current_window)

    app.adap.user.contributor.logout()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.user.contributor.open_payments_menu()
    app.adap.verification.text_present_on_page("Available for Withdraw")
    withdraw_balance = app.adap.user.contributor.get_withdraw_balance()

    app.adap.navigation.click_link('Withdraw Funds')
    app.adap.verification.text_present_on_page('Withdraw Request')
    app.adap.navigation.click_link('Request')
    app.adap.verification.text_present_on_page('Request Received!')
    assert float(withdraw_balance.replace('$', '')) > 0

    app_test.ac.driver.switch_to.default_content()
    app_test.ac.navigation.click_link('Vendors')
    app_test.ac.vendor_pages.open_vendor_profile_by(user_name)
    app_test.ac.vendor_pages.open_an_invoice()
    app_test.ac.verification.text_present_on_page('Current Invoice Status: Not Yet Submitted')


def _prepare_copy_job(app):
    job_id_to_copy = '2200847'
    api_key = get_user_api_key('adap_cf_internal_role')
    builder = Builder(api_key, env=app.adap.env)
    copy_job = builder.copy_job(job_id_to_copy, "all_units")
    copy_job.assert_response_status(200)
    builder.launch_job(external_crowd=True)
    copy_job_id = copy_job.json_response.get("id")

    # delete jobs after test session
    pytest.data.job_collections[copy_job_id] = api_key

    return copy_job_id


def _set_teardown_apps(first_app, second_app):
    # next 2 lines are for the case when the test is failed and one of the browser remains open
    first_app.destroy = lambda: second_app.driver.quit()
    second_app.destroy = lambda: first_app.driver.quit()
