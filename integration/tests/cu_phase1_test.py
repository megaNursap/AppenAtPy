import time

from adap.api_automation.utils.data_util import *
from adap.support.generate_test_data.adap.user_migration_status import update_migration_status, get_migration_user_id
from adap.support.generate_test_data.create_adap_contributor import create_adap_contributor
from appen_connect.api_automation.services_config.ac_user_service import UserService


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_populate_data_on_user_settings_profile_page(app):
    cu_acc_name = 'adap_contributor_unification_account1'
    user_name = get_user_email(cu_acc_name)
    password = get_user_password(cu_acc_name)
    profile_data = {
        'fullname': generate_random_string(10),
        'address': generate_random_string(10),
        'city': generate_random_string(5),
        'zipcode': random.randint(10000, 100000),
        'country': 'Canada',
        'gender': 'Male',
        'month_of_birth': 'May',
        'day_of_birth': 2,
        'year_of_birth': 2021
    }

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.navigation.click_link('Register')
    app.adap.navigation.click_link('Sign In')
    app.adap.user.contributor.login(user_name, password)
    assert app.adap.verification.text_present_on_page('Connect')
    assert app.adap.verification.text_present_on_page('Skip')

    app.adap.navigation.click_btn('Skip', timeout=5)
    app.adap.navigation.click_link('Close')
    app.adap.user.contributor.close_guide()
    assert app.adap.user.contributor.get_available_jobs_amount() >= 1

    app.adap.navigation.deactivate_iframe()
    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')
    assert app.adap.verification.texts_present_on_page([
        'Profile',
        'Change password',
        'Payment Method'
    ])

    app.adap.user.contributor.fill_out_profile_settings(profile_data)
    app.adap.navigation.click_btn('Save', timeout=3)
    assert app.adap.verification.text_present_on_page('Profile update successful')

    app.adap.user.contributor.logout()

    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.user.contributor.open_user_menu()
    app.adap.navigation.click_link('Account Settings')

    acc_settings = app.adap.user.contributor.get_profile_settings()
    assert acc_settings['fullname'] == profile_data['fullname']
    assert acc_settings['month_of_birth'] == profile_data['month_of_birth']
    assert acc_settings['day_of_birth'] == profile_data['day_of_birth']
    assert acc_settings['year_of_birth'] == profile_data['year_of_birth']
    assert acc_settings['gender'] == profile_data['gender']
    assert acc_settings['address'] == profile_data['address']
    assert acc_settings['city'] == profile_data['city']
    assert acc_settings['zipcode'] == profile_data['zipcode']
    assert acc_settings['country'] == profile_data['country']


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_submit_profile_details(app):
    # https://www.figma.com/proto/fNPmZqqaGom420u9pTJ1x7/ADAP-Profile-Redirect-to-AC---Web-Design?node-id=
    # 1801%3A5475&scaling=min-zoom&page-id=1%3A2&starting-point-node-id=1801%3A5475&show-proto-sidebar=1
    # no incentive happy path
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
    assert app.adap.verification.texts_present_on_page([
        'Appen Upgrade Notice',
        'In a few months, we will have a new platform to provide you with more earning opportunities and better '
        'match your Projects and Tasks!',
        'To ensure we deliver a seamless experience, we need a few minutes of your time to provide information '
        'enabling us to recommend Projects that match your language and location preferences. '
        'We’ve included a preview above of what’s coming.'
    ])
    app.adap.navigation.click_btn('Continue', timeout=3)

    app.adap.user.contributor.fill_out_additional_information(additional_info)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Submit')

    assert app.adap.verification.text_present_on_page('Please give us a moment...')
    assert app.adap.verification.text_present_on_page('We are currently processing the upgrade. '
                                                      'This may take a few minutes. Please avoid navigating away '
                                                      'from this page.')
    assert app.adap.verification.text_present_on_page('We will let you know once the review is done.')
    assert app.adap.verification.text_present_on_page('Thank you for your patience.')

    time.sleep(15)
    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('It’s taking longer than expected...')
    assert app.adap.verification.text_present_on_page('The upgrade process is taking longer than we expected. '
                                                      'We will get back to you in about 24-48 hours and notify '
                                                      'you either through email or the next time you log into '
                                                      'the platform.')
    assert app.adap.verification.text_present_on_page('Thank you for your patience!')
    app.adap.navigation.click_btn('Go to Dashboard')

    assert app.adap.verification.text_present_on_page('Welcome Back!')
    assert app.adap.verification.text_present_on_page('Upgrade in-progress')
    assert app.adap.verification.text_present_on_page('The upgrade process is taking longer than we expected. '
                                                      'We will get back to you in about 24-48 hours and notify '
                                                      'you either through email or the next time you log into '
                                                      'the platform.')
    assert app.adap.verification.text_present_on_page('Thank you for your time.')
    app.adap.navigation.click_link('Close')

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('Upgrade in-progress')
    assert app.adap.verification.text_present_on_page('The upgrade process is taking longer than we expected. '
                                                      'We will get back to you in about 24-48 hours and notify '
                                                      'you either through email or the next time you log into '
                                                      'the platform.')
    assert app.adap.verification.text_present_on_page('Sign in or create an Appen Platform account by clicking '
                                                      'any job below. You will see all of the jobs currently '
                                                      'available to you once you have signed in.')


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_skip_for_now_page_and_complete_my_profile(app):
    # login
    # skip filling up account information
    # skip pop up
    # clicking on the Complete My Profile redirects to account info
    user_name, password = _prepare_adap_user(app)

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Continue', timeout=3)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Skip For Now')
    assert app.adap.verification.text_present_on_page('Skip For Now?')
    assert app.adap.verification.text_present_on_page('Are you sure you want to skip the form now? '
                                                      'Until you complete it you won\'t be able to continue working '
                                                      'on your tasks.')
    app.adap.navigation.click_btn('Complete My Profile')
    assert app.adap.verification.texts_present_on_page([
        'Profile Details',
        'Please update your information, keep in mind all fields are required. '
        'You can review Appen’s Community Guidelines',
        'here'
    ])


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_no_incentive_skipped_path(app):
    # login
    # skip filling up account information
    # skip pop up
    # clicking on the 'Go To Dashboard'
    user_name, password = _prepare_adap_user(app)

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(user_name, password)

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.texts_present_on_page([
        'Appen Upgrade Notice',
        'In a few months, we will have a new platform to provide you with more earning opportunities and better '
        'match your Projects and Tasks!',
        'To ensure we deliver a seamless experience, we need a few minutes of your time to provide information '
        'enabling us to recommend Projects that match your language and location preferences. '
        'We’ve included a preview above of what’s coming.'
    ])
    app.adap.navigation.click_btn('Continue', timeout=3)

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Skip For Now')
    assert app.adap.verification.text_present_on_page('Skip For Now?')
    assert app.adap.verification.text_present_on_page('Are you sure you want to skip the form now? Until you '
                                                      'complete it you won\'t be able to continue working on '
                                                      'your tasks.')
    app.adap.navigation.deactivate_iframe()
    app.adap.user.contributor.skip_for_now_popup()

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.texts_present_on_page([
        'Your Account Needs Attention!',
        'Please complete your profile to continue working on your tasks without interruption.',
        'It should only take a moment to provide information to enable us to recommend Projects that match your '
        'language and location preferences. Until then you will no longer be able to work on your tasks.',
        'Please click “Complete My Profile” button below. There are a number of tasks waiting for you!',
        'Thank you for choosing Appen!'
    ])

    app.adap.navigation.click_btn('Go to Dashboard')
    assert app.adap.verification.texts_present_on_page([
        'Welcome Back!',
        'Your Account Needs Attention!',
        'Please complete your profile to continue working on your tasks without interruption.',
        'It should only take a moment to provide information to enable us to recommend Projects that match your '
        'language and location preferences. Until then you will no longer be able to work on your tasks.',
        'Please click “Complete My Profile” button below.',
        'There are a number of tasks waiting for you!',
        'Thank you for choosing Appen!'
    ])
    app.adap.navigation.click_link('Close')

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.texts_present_on_page([
        'Your Account Needs Attention!',
        'Please ',
        'complete your profile',
        ' to continue working on your tasks without interruption. '
        'We have a number of tasks waiting for you. '
        'To access them immediately, please complete your profile.',
        'Sign in or create an Appen Platform account by clicking any job below. '
        'You will see all of the jobs currently available to you once you have signed in.'
    ])


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_fresh_migration_status_user_skipped_path(app):
    # related to the bug - https://appen.atlassian.net/browse/ACE-17996
    # log in by the new adap user
    # without updating migration status
    # complete my profile
    # twice skip for now are clicked
    # go to dashboard
    # complete my profile

    cu_acc_name = 'adap_contributor_unification_account2'
    username = get_user_email(cu_acc_name)
    password = get_user_password(cu_acc_name)

    app.adap.user.contributor.open_home_page()
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(username, password)

    app.adap.navigation.click_link('Complete my Profile')

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Skip For Now')
    app.adap.navigation.deactivate_iframe()
    app.adap.user.contributor.skip_for_now_popup()

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Go to Dashboard')

    app.adap.navigation.click_link('Complete my Profile')
    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.texts_present_on_page([
        'Profile Details',
        'Please update your information, keep in mind all fields are required. '
        'You can review Appen’s Community Guidelines',
        'here'
    ])


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_submit_profile_details_happy_path_whitelist_ip(app):
    # https://www.figma.com/proto/fNPmZqqaGom420u9pTJ1x7/ADAP-Profile-Redirect-to-AC---Web-Design?node-id=
    # 1801%3A5475&scaling=min-zoom&page-id=1%3A2&starting-point-node-id=1801%3A5475&show-proto-sidebar=1
    # no incentive happy path, whitelist ip address
    email, password = _prepare_adap_user(app)
    ip = _whitelist_vendor_ip_address(app, email)

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

    time.sleep(15)
    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('It’s taking longer than expected...')
    assert app.adap.verification.text_present_on_page('The upgrade process is taking longer than we expected. '
                                                      'We will get back to you in about 24-48 hours and notify '
                                                      'you either through email or the next time you log into '
                                                      'the platform.')
    assert app.adap.verification.text_present_on_page('Thank you for your patience!')
    app.adap.navigation.click_btn('Go to Dashboard')

    assert app.adap.verification.text_present_on_page('Welcome Back!')
    assert app.adap.verification.text_present_on_page('Upgrade in-progress')
    assert app.adap.verification.text_present_on_page('The upgrade process is taking longer than we expected. '
                                                      'We will get back to you in about 24-48 hours and notify '
                                                      'you either through email or the next time you log into '
                                                      'the platform.')
    assert app.adap.verification.text_present_on_page('Thank you for your time.')
    app.adap.navigation.click_link('Close')

    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('Upgrade in-progress')
    assert app.adap.verification.text_present_on_page('The upgrade process is taking longer than we expected. '
                                                      'We will get back to you in about 24-48 hours and notify '
                                                      'you either through email or the next time you log into '
                                                      'the platform.')
    assert app.adap.verification.text_present_on_page('Sign in or create an Appen Platform account by clicking '
                                                      'any job below. You will see all of the jobs currently '
                                                      'available to you once you have signed in.')


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_submit_profile_details_successful_upgrade_manual_path(app, app_test):
    # next 2 lines are for the case when the test is failed and one of the browser remains open
    app.destroy = lambda: app_test.driver.quit()
    app_test.destroy = lambda: app.driver.quit()

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


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_submit_profile_details_unsuccessful_upgrade_manual_path(app, app_test):
    # next 2 lines are for the case when the test is failed and one of the browser remains open
    app.destroy = lambda: app_test.driver.quit()
    app_test.destroy = lambda: app.driver.quit()

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
    user_row.click_on_action_button('Reject')
    user_row.select_reason('Did not meet project requirement')
    user_row.proceed()

    app.adap.navigation.switch_to_frame(0)
    app.adap.navigation.click_btn('Go to Dashboard', timeout=5)
    app.adap.navigation.switch_to_frame(0)
    assert app.adap.verification.text_present_on_page('Upgrade was Unsuccessful')
    assert app.adap.verification \
        .text_present_on_page('We’ve reviewed your information and unfortunately your '
                              'account did not meet the Appen Community Guidelines.')
    assert app.adap.verification \
        .text_present_on_page('You can withdraw your earnings but you will not be able to work on your tasks.')
    assert app.adap.verification.text_present_on_page('If you think this is a mistake please reach out to ')
    assert app.adap.verification.text_present_on_page('crowd support')
    assert app.adap.verification.text_present_on_page('Thank you for working with Appen.')


def _create_adap_user(app):
    username = generate_random_string(7)
    email = f'integration+{username}@figure-eight.com'
    password = get_user_password('adap_contributor_unification_account2')
    api_key = get_test_data('adap_cf_internal_role', 'api_key')

    create_adap_contributor(
        user_email=email,
        user_name=username,
        user_password=password,
        url=f'{app.adap.user.task.URL}users',
        env='integration',
        admin_api_key=api_key
    )

    return email, password


def _prepare_adap_user(app):
    email, password = _create_adap_user(app)

    app.adap.user.contributor.open_home_page()
    time.sleep(1)
    app.adap.navigation.click_link('Continue to Sign In')
    app.adap.user.contributor.login(email, password)
    app.adap.user.contributor.logout()

    user_id = get_migration_user_id(email)
    update_migration_status(user_id, 'pending')

    return email, password


def _whitelist_vendor_ip_address(email, app):
    username = get_user_name('ac_test_ui_account')
    password = get_user_password('ac_test_ui_account')

    app.ac.ac_user.login_as(user_name=username, password=password)
    app.ac.navigation.click_link('Partner Home')
    # app.ac.navigation.click_link('View previous list page')
    # app.ac.ac_user.select_customer('Appen Internal')
    cookies = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.ac.driver.get_cookies()}

    user_service_api = UserService(cookies=cookies)
    faker = Faker()
    vendor_ip = faker.ipv4()
    user_service_api.whitelist_ip(email, vendor_ip)

    app.ac.ac_user.sign_out()
    app.ac.driver.delete_all_cookies()

    return vendor_ip
