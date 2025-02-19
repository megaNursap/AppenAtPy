import random
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *
from appen_connect.ui_automation.service_config.application import AC
from appen_connect.ui_automation.service_config.vendor_profile.registration_flow import *


USER_NAME = "sandbox+new_account_" + str(random.randint(10000000000, 99999999999)) + "@figure-eight.com"
VERIFICATION_CODE = {"stage":"4FC81D",
                     "qa":"CA0016"}


def register_vendor(app, password, first_name, last_name, country, state, verification_code):
    print(f"Vendor {USER_NAME} will be created")
    app.vendor_profile.registration_flow.register_user(user_name=USER_NAME,
                                                       user_password=password,
                                                       user_first_name=first_name,
                                                       user_last_name=last_name,
                                                       residence_value=country,
                                                       state=state)
    app.vendor_profile.registration_flow.fill_out_fields({"CERTIFY DATA PRIVACY": 1,
                                                          "CERTIFY SSN": 1}, action="Create Account")
    app.vendor_profile.registration_flow.fill_out_fields({"VERIFICATION CODE": verification_code}, action="Verify Email")
    app.navigation.click_btn("Go to Login page")
    print("\n\n")
    print(f"Done! \n Vendor created - {USER_NAME}")
    print("Password:", password)


if __name__ == "__main__":
    """
    selenium script for vendor creation on AC QA or Stage environment
    - vendor email will be generate automatically based on pattern - 
                  "sandbox+new_account_<random number btw 10000000000 and 99999999999>@figure-eight.com"
    Required params:
       - ENV - qa or stage
    Optional params (if keep it empty, script will use default values)
       - Password - password for new vendor; default value - password for qa automation accounts  
       - First name - default value = 'firstname'
       - Last name - default value = 'lastname'
       - Country of residence - default value = 'United States of America'
       - State - if country does't have states - keep it empty;  default value for USA = 'Alabama'
    """

    ENV = input("ENV (e.g. qa or stage): ")

    if ENV not in ['qa', 'stage']:
        print("Invalid ENV!! Please, use qa or stage env!!!")
        exit(1)

    pytest.appen = 'true'
    pytest.env = ENV

    default_user = get_user('test_ui_account', env=ENV)
    DEFAULT_PASSWORD = default_user.get('password')

    PSW = input(f"Password for new vendor (if you want to use default password ({DEFAULT_PASSWORD}), keep it empty): ") or DEFAULT_PASSWORD
    FIRST_NAME = input("First name (if you want to use default name 'firstname', keep it empty): ") or 'firstname'
    LAST_NAME = input("Last name (if you want to use default name 'lastname', keep it empty): ") or 'lastname'
    RESIDENCE = input(
        "Country of residence (if you want to use default value - United States of America, keep it empty): ") or 'United States of America'
    STATE = input("State (if you want to use default value - Alabama, keep it empty): ") or 'Alabama'

    app = AC(pytest.env)

    register_vendor(app,
                    PSW,
                    FIRST_NAME,
                    LAST_NAME,
                    RESIDENCE,
                    STATE,
                    VERIFICATION_CODE[ENV])
