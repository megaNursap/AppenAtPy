import json
import os

from adap.api_automation.utils.data_util import encrypt_users_file, load_key
from adap.settings import Config
from adap.support.generate_test_data.utils_fed_users.create_user_utils import *
from adap.support.generate_test_data.utils_fed_users.generate_random_names import generate_random_test_data
from adap.support.generate_test_data.utils_fed_users.update_team_roles import set_up_team_roles
from adap.ui_automation.utils.selenium_utils import set_up_driver


def update_user_creadentials_file(users_file, regenerate=False, URL=None, USER_PASSWORD=None):
    print("... UPDATE USER CREDENTIALS")
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

    file_updated = False
    for k, v in users.items():
        if k in ['cf_internal_role', 'teams_details', 'org_details']: continue
        if v.get('contributor', False): continue
        driver = set_up_driver()
        driver.get(URL)
        print('...in progress', v)
        try:
            new_api_key = find_key(driver, v, regenerate, URL, USER_PASSWORD)
            users[k]['api_key'] = new_api_key
            users[k]['password'] = USER_PASSWORD
            file_updated = True
        except:
            print('ERROR')
        driver.quit()

    if file_updated:
        os.remove(users_file)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)


def update_teams_and_orgs_ids(users_file):
    print("... UPDATE TEAMS AND ORG IDS")
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

    driver = set_up_driver()

    driver.get(URL)
    login(driver, ADMIN_USER, ADMIN_PASSWORD)

    file_updated = False
    for k, v in users.items():
        if users[k].get('org_name', False):
            if users[k]['org_name'] != 'cf_internal':
                try:
                    org_id = find_org_id(users[k]['org_name'], driver, URL)
                    users[k]['org_id'] = org_id
                    file_updated = True
                except:
                    print('ERROR')

        _ind = 0
        for team in users[k]['teams']:
            print('team id... ', team)
            team_id = find_team_id(team['name'], driver, URL)
            users[k]['teams'][_ind]['id'] = team_id
            print(team_id)
            _ind += 1
            file_updated = True

    driver.quit()

    if file_updated:
        os.remove(users_file)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)


def update_teams_and_orgs_ids_adap(users_file,  URL=None, ADMIN_USER=None, ADMIN_PASSWORD=None):
    print("... UPDATE TEAMS AND ORG IDS")
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

    driver = set_up_driver()

    driver.get(URL)
    login(driver, ADMIN_USER, ADMIN_PASSWORD)

    file_updated = False

    cash_teams = {}
    if users.get('teams_details'):
        for team, team_info in users['teams_details'].items():
            print('team name... ', team)
            team_id = find_team_id(team, driver, URL)
            users['teams_details'][team]['id'] = team_id
            print(team_id)
            cash_teams[team] = team_id
            file_updated = True

    if users.get('org_details'):
        for org_name, org_info in users['org_details'].items():
            if org_name == 'cf_internal': continue
            print('org name... ', team)
            try:
                org_id = find_org_id(org_name, driver, URL)
                users['org_details'][org_name]['id'] = org_id
                file_updated = True
            except:
                print('ERROR')

            # update team's id in org details
            updated_teams = []
            if org_info.get('teams'):
                for team in org_info['teams']:
                    updated_teams.append({'team_name': team['team_name'],
                                          'team_id': cash_teams.get(team['team_name'], "")})

                users['org_details'][org_name]['teams'] = updated_teams

    driver.quit()

    if len(cash_teams) > 0:
        #     update teams id for user accounts
        for user, user_info in users.items():
            if user in ['cf_internal', 'teams_details', 'org_details']: continue
            if users.get('contributor'): continue

            if user_info.get('teams'):
                updated_teams = []
                for team in user_info['teams']:
                    team_id = cash_teams.get(team['name'], "")
                    updated_teams.append({'name': team['name'],
                                          'id': team_id})

                users[user]['teams'] = updated_teams
            if user_info.get('main_team'):
               users[user]['main_team_id'] = cash_teams.get(user_info['main_team'], "")

    if file_updated:
        os.remove(users_file)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)


def main(users_file):
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

        driver = set_up_driver()
        driver.get(URL)
        login(driver, ADMIN_USER, ADMIN_PASSWORD)

        find_users_to_invite(users, driver, URL)
        find_org_to_create(users, driver, URL)
        find_team_to_create(users, driver, URL)

        driver.quit()
        print("--------   TODO   -------")
        print(task_stack)

        create_users(task_stack['user_to_invite'], users, URL, ADMIN_USER, ADMIN_PASSWORD, USER_PASSWORD)
        create_team(task_stack['create_team'], task_stack['add_user_team'], users, URL, ADMIN_USER, ADMIN_PASSWORD)

        if task_stack['create_org']:
            create_orgs(task_stack['create_org'], URL, ADMIN_USER, ADMIN_PASSWORD)

        if task_stack['move_team']:
            move_teams(task_stack['move_team'], URL, ADMIN_USER, ADMIN_PASSWORD)

        if task_stack['create_org']:
            add_admin_to_org(task_stack['create_org'], URL, ADMIN_USER, ADMIN_PASSWORD)

    set_up_team_roles(users, URL, ADMIN_USER, ADMIN_PASSWORD)
    update_user_creadentials_file(users_file)
    update_teams_and_orgs_ids(users_file)


if __name__ == "__main__":
    URL = 'https://app.qe72.secure.cf3.us/make'
    ADMIN_USER = input("admin username: ")
    ADMIN_PASSWORD = input("admin password: ")
    USER_PASSWORD = input("Provide password for new users: ")
    FILE = input("Provide file name with users: ")

    path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
    key = load_key(path_key)

    GENERATE_DATA = False
    if input("Do you want to generate random data? (yes/no) ") == 'yes':
        GENERATE_DATA = True
    if input("Is file with credentials decrypted? (yes/no) ") == 'yes':
        if GENERATE_DATA:  generate_random_test_data(FILE)
        main(FILE)
        encrypt_users_file(FILE, key)
        print("user,team,organization created successfully")
    else:
        print("Please, decrypt your file first!!!")
