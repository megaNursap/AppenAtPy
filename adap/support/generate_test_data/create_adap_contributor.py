import time

import pytest

from adap.api_automation.utils.data_util import get_user
from adap.support.generate_test_data.adap.verify_email import verify_user_email_akon
from adap.support.generate_test_data.utils_fed_users.create_user_utils import signup_adap
from scripts.one_offs.create_contributors_api import sign_up


def create_adap_contributor(**kwargs):
    sign_up(kwargs['user_email'], kwargs['user_password'], kwargs['url'], validate=False)
    time.sleep(5)
    verify_user_email_akon(kwargs['user_email'], kwargs['env'], kwargs['admin_api_key'])


def main():
    create_adap_contributor(user_email=USER_EMAIL,
                          user_name=USER_NAME,
                          user_password=USER_PASSWORD,
                          url=URL,
                          env=ENV,
                          admin_api_key=ADMIN_API_KEY)


if __name__ == "__main__":
    """  
      Required params:
       - ENV - sandbox or integration or staging
       - email - contributor email    
       - name -  contributor name
       - password - contributor name                        
    """
    ENV = input("ENV (e.g. sandbox, integration or staging): ")

    if ENV not in ['sandbox', 'integration', 'staging']:
        print("Invalid ENV!! Please, use sandbox, integration or staging env!!!")
        exit(1)

    USER_EMAIL = input("Provide email for new users: ")
    USER_NAME = input("Provide name for new users: ")
    USER_PASSWORD = input("Provide password for new users: ")

    pytest.appen = 'false'
    pytest.env = ENV

    default_user = get_user('cf_internal_role', env=ENV)
    ADMIN_API_KEY = default_user.get('api_key')

    urls = {"sandbox":"https://account.sandbox.cf3.us/users",
           "integration": "https://account.integration.cf3.us/users",
            "staging": "https://account.staging.cf3.us/users"}

    URL = urls[ENV]

    main()

    print("\n\n")
    print(f"Done! \nRequestor created - {USER_EMAIL}")
    print("Password:", USER_PASSWORD)