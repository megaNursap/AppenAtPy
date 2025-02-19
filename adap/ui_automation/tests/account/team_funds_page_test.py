"""
https://appen.atlassian.net/browse/QED-1762 --React Migration
Test covers:
1. Delete save card if there is any
2. Enter new card information
3. Check page view information
4. View the purchase history
"""

import time

import allure

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
ADD_AMOUNT = random.randint(10, 503)
BUYER_NAME = generate_random_string()
CC_NUMBER = '4111 1111 1111 1111'

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.ui_uat,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat,
    pytest.mark.regression_team_funds
]


@pytest.mark.dependency()
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_add_funds_by_entering_card_info(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.account_menu('Account')
    app.navigation.click_link('Funds')
    time.sleep(10)
    app.verification.current_url_contains('/account/funds')
    # delete saved card if there is any
    app.team_funds.delete_saved_card()
    app.navigation.refresh_page()
    # enter card information and save card and enable automatic payment
    app.team_funds.make_purchase_by_entering_card_info(amount=ADD_AMOUNT, card_number=CC_NUMBER, name=BUYER_NAME, expiration_date='03/28',
                                   cvv='357', zipcode='94105', automatic_payment=True, remember_card=False)


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.dependency(depends=["test_add_funds_by_entering_card_info"])
@allure.issue("https://appen.atlassian.net/browse/JW-1353", "BUG JW-1353")
def test_view_page_info(app):
    app.verification.text_present_on_page('Add Funds')
    assert app.team_funds.is_cc_active(last4digits=CC_NUMBER[-4:])
    assert app.team_funds.get_edit_automatic_payments_ele().is_displayed()
    assert app.team_funds.get_automatic_payments_status() == '$100'
    app.verification.text_present_on_page('Choose another way to pay')
    # assert app.team_funds.button_is_disable('Make Purchase')
    app.verification.text_present_on_page('Current Funds')
    app.verification.text_present_on_page('Team Name')
    app.verification.text_present_on_page('Row Limit')
    app.verification.text_present_on_page('Available Rows')
    app.verification.text_present_on_page('Funds In Progress')
    app.verification.text_present_on_page('Available Funds')


# @pytest.mark.skipif(pytest.env not in ["sandbox", "qa", "integration", "staging"], reason="Sandbox and QA enabled feature")
# @pytest.mark.dependency(depends=["test_add_funds_by_entering_card_info"])
# def test_view_purchase_history(app):
#     app.navigation.click_link('View Purchase History')
#     purchase_history = app.team_funds.get_purchase_history()
#     assert purchase_history[0].get('buyer_name') == BUYER_NAME
#     assert purchase_history[0].get('last_4') == CC_NUMBER[-4:]
#     assert purchase_history[0].get('total')[1:] == "%.2f" % float(ADD_AMOUNT)
#     app.navigation.click_link('Funds')


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.dependency(depends=["test_view_page_info"])
def test_remove_autopay(app):
    """
    Removes 'Automatic Payments' on the 'Funds' page
    """

    app.verification.text_present_on_page('Disabled', False)
    app.team_funds.get_edit_automatic_payments_ele().click()
    app.navigation.click_btn(btn_name='Disable')
    app.verification.text_present_on_page('Disabled')


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
@pytest.mark.dependency(depends=["test_remove_autopay"])
def test_remove_autopay_from_account(app):
    """
    Removes 'Automatic Payments' on the Edit(User) page
    """

    time.sleep(10)
    app.team_funds.delete_saved_card()
    app.navigation.refresh_page()

    # enter card information and save card and enable automatic payment
    app.team_funds.make_purchase_by_entering_card_info(
        amount=ADD_AMOUNT,
        card_number=CC_NUMBER,
        name=BUYER_NAME,
        expiration_date='03/28',
        cvv='357',
        zipcode='94105',
        automatic_payment=True,
        remember_card=False
    )

    app.verification.text_present_on_page('Disabled', False)

    app.mainMenu.account_menu('Customers')
    app.navigation.click_link('Users')
    time.sleep(10)
    app.verification.current_url_contains('/users')

    app.user.search_user(USER_EMAIL)
    app.user.click_edit_user(USER_EMAIL)
    app.verification.current_url_contains('/edit')
    app.user.update_role_for_team('Automatic payments disabled', True)
    app.navigation.click_btn('Save Changes')

    app.mainMenu.account_menu('Account')
    app.navigation.click_link('Funds')
    time.sleep(10)
    app.verification.current_url_contains('/account/funds')

    app.verification.text_present_on_page('Disabled')
