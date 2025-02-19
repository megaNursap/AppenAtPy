import time
import pytest
from integration.tests.cu_phase1_test import _create_adap_user


@pytest.mark.regression_contributor_unification
@pytest.mark.skipif(not pytest.running_in_preprod_adap_ac, reason="for Integration ADAP + AC env")
def test_link_paypal_account_to_profile(app_test):
    email, password = _create_adap_user(app_test)

    app_test.adap.user.contributor.open_home_page()
    time.sleep(1)
    app_test.adap.user.contributor.login_as(email,password)
    time.sleep(5)

    app_test.adap.user.contributor.open_user_menu()
    app_test.adap.navigation.click_link('Account Settings')

    app_test.adap.navigation.click_link('Payment Method')

    app_test.adap.verification.text_present_on_page("Micro tasks payment is separate from other Appen payment methods.")
    app_test.adap.verification.text_present_on_page("You need to link your PayPal account and withdraw your micro tasks "
                                               "payment from this page.")

    app_test.adap.navigation.click_link('Add')

    app_test.adap.verification.text_present_on_page('Connect to PayPal')
    app_test.adap.verification.text_present_on_page('Use PayPal to receive your full earnings.')

    paypal_account = 'qa+paypal3@figure-eight.com'
    app_test.adap.user.add_paypal_account(paypal_account, password)

    app_test.adap.user.contributor.open_user_menu()
    app_test.adap.navigation.click_link('Account Settings')
    app_test.adap.navigation.click_link('Payment Method')

    app_test.adap.verification.text_present_on_page('paypal')
    app_test.adap.verification.text_present_on_page('qa+paypal3@figure-eight.com')

