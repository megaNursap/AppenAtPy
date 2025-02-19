from adap.api_automation.utils.data_util import *
from appen_connect.ui_automation.service_config.user import RL_URL

mark_only_stage = pytest.mark.skipif(pytest.env not in ["stage"], reason="Only AC Stage has test data for now")

pytestmark = [pytest.mark.regression_ac, pytest.mark.ac_citiverify]


@pytest.fixture(scope="module")
def set_up(app):
    vendor_id = get_test_data('citiverify', 'id')
    user_name = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')

    app.ac_user.login_as_raterlabs_user(user_name=user_name, password=password)
    url = RL_URL[pytest.env] + "/vendor/view/{vendor_id}".format(vendor_id=vendor_id)

    app.driver.get(url)

    app.navigation.click_link("Restart / ACH Change Request")
    app.navigation.click_link("Impersonate")

    app.driver.get(RL_URL[pytest.env] + "/vendors/ach")


def test_citiverify_required_fields(app, set_up):
    app.verification.text_present_on_page("ACH Routing Information")

    app.vendor_pages.ach_clear_routing_number()
    app.vendor_pages.ach_clear_account_number(action='Submit')

    app.verification.text_present_on_page("Account Number is a required field.")
    app.verification.text_present_on_page("Routing Number is a required field.")


def test_citiverify_invalid_char(app, set_up):
    app.vendor_pages.ach_fill_out_bank_data(routing_number='gjkfjkgjf', account_number='gdfgfgggggggggggg',
                                            action='Submit')

    app.verification.text_present_on_page("Invalid format for Routing Number.  Valid format is 9 numeric digits.")
    app.verification.text_present_on_page(
        "Invalid format for Account Number.  Valid format is between 1 and 17 numeric digits")


def test_citiverify_invalid_lenght(app, set_up):
    app.vendor_pages.ach_fill_out_bank_data(routing_number='12210527', account_number='0000001',
                                            action='Submit')

    app.verification.text_present_on_page(
        "Invalid format for Routing Number.  Valid format is 9 numeric digits.")


@pytest.mark.parametrize('account_number',
                         ['0000000003','0000000004', '0000000005', '0000000006', '0000000007',
                          '0000000010', '0000000011', '0000000012', '0000000013', '0000000014','0000000015'])
def test_citiverify_invalid_data(app, set_up, account_number):
    app.vendor_pages.ach_fill_out_bank_data(routing_number='122105278', account_number=account_number,
                                            action='Submit')

    app.verification.text_present_on_page(
        "Your bank account number can be found on one of your checking account checks.")
    app.verification.text_present_on_page(
        "Please see the sample check images below to determine how to find your bank account number")

    app.verification.text_present_on_page(
        "Your ACH routing number can be found on one of your checking account checks.")
    app.verification.text_present_on_page(
        "Please see the sample check images below to determine how to find your ACH routing number")

    app.verification.text_present_on_page("Your account information was unable to be verified.")


@pytest.mark.parametrize('routing_number, account_number',
                         [
                          ("122105278", "0000000016"),
                          ("122105278", "0000000017"),
                          ("122105278", "0000000019"),
                          ("122105278", "0000000020"),
                          ("122105278", "0000000021"),
                          ("122105278", "0000000022"),
                         ])
def test_citiverify_valid_data(app, set_up, routing_number, account_number):
    app.vendor_pages.ach_fill_out_bank_data(routing_number=routing_number, account_number=account_number,
                                            action='Submit')
    app.verification.text_present_on_page("ACH Routing Information", is_not=False)
    app.navigation.click_link('Stop Impersonating')

    app.verification.current_url_contains(RL_URL[pytest.env] + "/vendor/view/")

    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": routing_number,
                                                      "Account Number": account_number})

    app.navigation.click_link("Restart / ACH Change Request")
    app.navigation.click_link("Impersonate")

    app.driver.get(RL_URL[pytest.env] + "/vendors/ach")


@pytest.mark.parametrize('routing_number, account_number',
                         [
                          ("122105278", "0000000001"),
                          # ("122105278", "0000000002"),
                          ("122105278", "0000000008"),
                          ("122105278", "0000000009")
                         ])
def test_citiverify_file_required(app, set_up, routing_number, account_number):
    app.vendor_pages.ach_fill_out_bank_data(routing_number=routing_number, account_number=account_number,
                                            action='Submit')

    app.verification.text_present_on_page('Click here to upload images (either scans or photographs) of your bank check. Supported file type "png", "jpg", "jpeg", "gif", "pdf"')

    app.verification.text_present_on_page("We need additional information before we can validate your account information. "
                                          "Please upload a complete image of a check (front side), "
                                          "showing your ACH information (Routing/Account numbers), as well as your name.")

    file_name = get_data_file("/checks/google.jpg")
    app.vendor_pages.upload_check_image(file_name)
    app.vendor_pages.ach_fill_out_bank_data(action='Submit')

    app.verification.text_present_on_page("ACH Routing Information", is_not=False)
    app.navigation.click_link('Stop Impersonating')

    app.verification.current_url_contains(RL_URL[pytest.env] + "/vendor/view/")

    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": routing_number + " (Not Verified)",
                                                      "Account Number": account_number + " (Not Verified)",
                                                      "Check Image": "google.jpg"})

    app.navigation.click_link("Restart / ACH Change Request")
    app.navigation.click_link("Impersonate")

    app.driver.get(RL_URL[pytest.env] + "/vendors/ach")


@pytest.mark.parametrize('file_type',
                         ['gif','jpeg','jpg','pdf','png'])
def test_citiverify_check_image_file_type(app, set_up, file_type):
    app.vendor_pages.ach_fill_out_bank_data(routing_number="122105278", account_number="0000000001",
                                            action='Submit')

    app.verification.text_present_on_page('Click here to upload images (either scans or photographs) of your bank check. Supported file type "png", "jpg", "jpeg", "gif", "pdf"')

    file_name = get_data_file("/checks/google.{}".format(file_type))
    app.vendor_pages.upload_check_image(file_name)
    app.vendor_pages.ach_fill_out_bank_data(action='Submit')

    app.verification.text_present_on_page("ACH Routing Information", is_not=False)
    app.navigation.click_link('Stop Impersonating')

    app.verification.current_url_contains(RL_URL[pytest.env] + "/vendor/view/")

    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": "122105278 (Not Verified)",
                                                      "Account Number": "0000000001 (Not Verified)",
                                                      "Check Image": "google.{}".format(file_type)})

    app.navigation.click_link("Restart / ACH Change Request")
    app.navigation.click_link("Impersonate")

    app.driver.get(RL_URL[pytest.env] + "/vendors/ach")


def test_citiverify_reject_check_image(app, set_up):
    app.vendor_pages.ach_fill_out_bank_data(routing_number="122105278", account_number="0000000001",
                                            action='Submit')

    app.verification.text_present_on_page(
        'Click here to upload images (either scans or photographs) of your bank check. Supported file type "png", "jpg", "jpeg", "gif", "pdf"')

    file_name = get_data_file("/checks/google.pdf")
    app.vendor_pages.upload_check_image(file_name)
    app.vendor_pages.ach_fill_out_bank_data(action='Submit')

    app.verification.text_present_on_page("ACH Routing Information", is_not=False)
    app.navigation.click_link('Stop Impersonating')

    app.verification.current_url_contains(RL_URL[pytest.env] + "/vendor/view/")

    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": "122105278 (Not Verified)",
                                                      "Account Number": "0000000001 (Not Verified)",
                                                      "Check Image": "google.pdf"})

    app.navigation.click_link('Reject')

    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": "",
                                                      "Account Number": ""})

    app.navigation.click_link("Restart / ACH Change Request")
    app.navigation.click_link("Impersonate")

    app.driver.get(RL_URL[pytest.env] + "/vendors/ach")


def test_citiverify_complete_ach_verification(app, set_up):
    app.vendor_pages.ach_fill_out_bank_data(routing_number="122105278", account_number="0000000001",
                                            action='Submit')

    app.verification.text_present_on_page(
        'Click here to upload images (either scans or photographs) of your bank check. Supported file type "png", "jpg", "jpeg", "gif", "pdf"')

    file_name = get_data_file("/checks/google.pdf")
    app.vendor_pages.upload_check_image(file_name)
    app.vendor_pages.ach_fill_out_bank_data(action='Submit')

    app.verification.text_present_on_page("ACH Routing Information", is_not=False)
    app.navigation.click_link('Stop Impersonating')

    app.verification.current_url_contains(RL_URL[pytest.env] + "/vendor/view/")

    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": "122105278 (Not Verified)",
                                                      "Account Number": "0000000001 (Not Verified)",
                                                      "Check Image": "google.pdf"})

    app.navigation.click_link('Complete ACH Verification;')
    app.vendor_pages.verify_bank_info_on_vendor_page({"Routing Number": "122105278",
                                                      "Account Number": "0000000001",
                                                      "Check Image": "google.pdf"})

    app.navigation.click_link("Restart / ACH Change Request")
    app.navigation.click_link("Impersonate")

    app.driver.get(RL_URL[pytest.env] + "/vendors/ach")
