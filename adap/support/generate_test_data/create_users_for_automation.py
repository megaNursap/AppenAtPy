import json
import os

from adap.api_automation.utils.data_util import load_key, encrypt_users_file, dencrypt_users_file
from adap.settings import Config
from adap.support.generate_test_data.create_fed_users import update_user_creadentials_file, \
    update_teams_and_orgs_ids_adap
from adap.support.generate_test_data.find_api_keys import login
from adap.support.generate_test_data.utils_fed_users.generate_random_names import generate_random_test_data
from adap.support.generate_test_data.utils_fed_users.create_user_utils import *


def main(users_file):
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

        driver = set_up_driver()
        driver.get(URL)
        login(driver, ADMIN_USER, ADMIN_PASSWORD)

        find_users_to_invite(users, driver, URL)

        driver.quit()

        print("--------   TODO   -------")

        # create users in akon db
        create_users_adap(users_to_invite=task_stack['user_to_invite'],
                          users_info=users,
                          user_password=USER_PASSWORD,
                          url=URL,
                          env=ENV,
                          admin_api_key=ADMIN_API_KEY)

        # # # set up user roles
        update_user_roles(users_to_invite=task_stack['user_to_invite'],
                          users_info=users,
                          url=URL,
                          admin=ADMIN_USER,
                          admin_password=ADMIN_PASSWORD)

        # # set up teams roles
        update_team_roles(teams_info=users['teams_details'],
                          url=URL,
                          admin=ADMIN_USER,
                          admin_password=ADMIN_PASSWORD)

        create_orgs_adap(orgs=users['org_details'],
                         url=URL,
                         admin_user=ADMIN_USER,
                         admin_passwors=ADMIN_PASSWORD)

    update_user_creadentials_file(users_file, URL=URL, USER_PASSWORD=USER_PASSWORD)
    update_teams_and_orgs_ids_adap(users_file, URL=URL, ADMIN_USER=ADMIN_USER, ADMIN_PASSWORD=ADMIN_PASSWORD)


if __name__ == "__main__":
    """
      1. create cfinternal user manually
      2. as a example of data that should be created use file - account_new_staging.json
         - (optional) - to create new example file use script copy_test_accounts.py
      3. prepare data that needed for this script
           - cfinternal email; 
           - cfinternal password;
           - cfinternal api_key;
           - env, where new data will be created
           - file with data example, absolute path;
           - change URL pattern if it is not "'https://client.{ENV}.cf3.us'"
      4. generate random data (optional) - if users in FILE already exist in app, you can generate random user name, team name...  
      5. main function (generate new data)
             - find_users_to_invite - find all users from FILE and verify they don't exist (selenium)
             - create_users_adap - create new users and verify emails
             - update_user_roles - open new users and update user's roles based on FILE info (selenium)
             - update_team_roles - open new teams (teams were create automatically during users creation process) 
                                   and updates teams roles (selenium)
                                   all teams info in FILE, 'teams_details'
             - create_orgs_adap - create new organizations from FILE 'org_details' and set up roles        
             - update_user_creadentials_file - open new users and grab api key; and save it in FILE (selenium)
             - update_teams_and_orgs_ids_adap - open new teams, orgs and get ids; and save it in FILE (selenium)
      6. encrypt_users_file - encrypt all new data                                                         
    """

    ENV = input("env: ")
    ADMIN_USER = input("admin username: ")
    ADMIN_PASSWORD = input("admin password: ")
    ADMIN_API_KEY = input("Provide admin api key: ")
    USER_PASSWORD = input("Provide password for new users: ")
    FILE = input("Provide file name with users: ")

    URL = f"https://client.{ENV}.cf3.us"

    path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
    key = load_key(path_key)

    if input("Do you want to generate random data? (yes/no) ") == 'yes':
        # data in FILE will be overwritten with random valus (user_name; email; team name; org name)
        generate_random_test_data(FILE)

    #  main function -
    main(FILE)
    encrypt_users_file(FILE, key)
    print("user,team,organization created successfully")


