import json
import time

from adap.api_automation.utils.http_util import HttpMethod
from adap.support.generate_test_data.utils_fed_users.create_user_utils import find_data_on_the_page
from adap.ui_automation.utils.selenium_utils import set_up_driver
from adap.support.generate_test_data.find_api_keys import login


def get_account_data(users_file, new_file):
    print("Get Account Data")
    new_data = {}

    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

        driver = set_up_driver()
        driver.get(URL)
        login(driver, ADMIN_USER, ADMIN_PASSWORD)

        service = HttpMethod(session=False)

        for user, user_data in users.items():
            if not user_data.get('user_name'): continue

            user_email = user_data.get('email')
            user_password = user_data.get('password')
            user_api_key = user_data.get('api_key', None)

            contributor = False
            if not user_api_key or user_api_key == 'no_logged_user':
                user_data['contributor'] = True
                new_data[user] = user_data
                continue

            response = service.get(f'https://api.{ENV}.cf3.us/v1/users/teams?key=%s' % user_api_key)
            user_teams = response.json_response

            driver.get(URL + "/admin/users")

            no_users_found = find_data_on_the_page(driver, user_email, msg='No users were found.')

            main_team = driver.find_element('xpath',"//td//a[contains(@href,'/admin/teams')]")
            team_name = main_team.text
            team_id = main_team.get_attribute('href').split('/')[-1]
            user_id = driver.find_elements('xpath','//tr[@id]//td')[0].text

            # user settings
            driver.get(URL + f"/admin/users/{user_id}/edit")
            # get roles
            roles = ['activeCheckbox','financeManagerCheckbox', 'organizationManagerCheckbox', 'cfInternalCheckbox','internalAppCheckbox', 'superAdminCheckbox']
            user_roles = {}
            for _role in roles:
                el = driver.find_elements('xpath',"//input[@id='%s' and @checked]" % _role)
                if len(el)>0:
                    value = True
                else:
                    value = False
                user_roles[_role] = value

            # plan
            plan = driver.find_element('xpath',"//input[@name='paidPlan']").get_attribute('value')

            _data = {
                "user_name": user_data.get('user_name'),
                "email": user_email,
                "password": user_password,
                "api_key": user_api_key,
                "contributor": contributor,
                "main_team": team_name,
                "main_team_id": team_id,
                "user_roles": user_roles,
                "user_plan": plan,
                "teams": user_teams
            }
            # additional params
            for _key, _value in user_data.items():
                if not _data.get(_key):
                    _data[_key] = _value

            new_data[user] = _data

            time.sleep(5)

    driver.close()

    print("get account data - done")
    print(users)

    with open(new_file, 'w+') as f:
        json.dump(new_data, f, indent=2)


def get_teams_data(users_file):
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

        teams = []
        teams_data = {}

        driver = set_up_driver()
        driver.get(URL)
        login(driver, ADMIN_USER, ADMIN_PASSWORD)

        for user, user_data in users.items():
            if user_data.get('teams'):

                if user_data['teams'][0]['id'] not in teams:
                    team_id = user_data['teams'][0]['id']
                    team_name = user_data['teams'][0]['name']

                    teams.append(user_data['teams'][0]['id'])

                    driver.get(URL + f"/admin/teams/{team_id}")

                    _team_org = driver.find_element('xpath',"//div[@id='admin-teams-wrapper']").text
                    org_name = ''
                    if "Organization: " in _team_org:
                        try:
                            org_name = _team_org.split('Organization:')[1].split("\n")[0].strip()
                        except:
                            print("Not able to find org name")

                    # find team roles
                    driver.get(URL + f"/admin/teams/{team_id}/edit")
                    time.sleep(1)

                    _roles = {}
                    _roles_on_page = driver.find_elements('xpath',"//div[@class='b-TeamEditPage__flags']//input")
                    for role in _roles_on_page:
                        role_id = role.get_attribute('id')
                        _roles[role_id] = role.is_selected()

                    _additional_roles = {}
                    _add_roles_on_page = driver.find_elements('xpath',"//div[@class='b-TeamEditPage__roles']//input")

                    for role in _add_roles_on_page:
                        role_id = role.get_attribute('id')
                        _additional_roles[role_id] = role.is_selected()


                    teams_data[team_name] = {
                        "id": team_id,
                        "org_name": org_name,
                        "roles": _roles,
                        "add_roles": _additional_roles
                    }

        users["teams_details"] = teams_data

        driver.close()

        print("get teams data - done")
        print(users)

    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)


def get_orgs_data(users_file):
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

        if users.get('teams_details'):
            _org = []
            for team, team_info in users['teams_details'].items():
                if team_info.get('org_name'):
                    _org.append(team_info['org_name'])

            if len(_org) > 0:
                driver = set_up_driver()
                driver.get(URL)
                login(driver, ADMIN_USER, ADMIN_PASSWORD)

                org_details = {}

                for org_name in _org:
                    driver.get(URL + f"/admin/organizations")
                    no_ogr_found = find_data_on_the_page(driver, org_name, msg='No users were found.')
                    org_on_page = driver.find_element('xpath',"//a[@href and text()='%s']" % org_name)
                    org_id = org_on_page.get_attribute('href').split('/')[-1]

                    driver.get(URL + f"/admin/organizations/{org_id}")

                    # find all teams in org
                    org_teams = []
                    el_teams = driver.find_elements('xpath',"//a[contains(@href,'/admin/teams/')]")
                    for _t in el_teams:
                        _team_name = _t.text
                        _team_id = _t.get_attribute('href').split('/')[-1]
                        org_teams.append({
                            "team_id": _team_id,
                            "team_name": _team_name
                        })

                    # find org admins
                    org_admins = []
                    driver.get(URL + f"/admin/organizations/{org_id}/admins")
                    el_admin = driver.find_elements('xpath',"//a[contains(@href,'/admin/users/')]")
                    for _a in el_admin:
                        org_admins.append(_a.text)

                    # find org settings
                    org_settings = {}
                    driver.get(URL + f"/admin/organizations/{org_id}/settings")
                    el_settings = driver.find_elements('xpath',"//input[contains(@class,'boolean')]")
                    for _s in el_settings:
                        _name = _s.get_attribute('name')
                        _value = _s.is_selected()
                        org_settings[_name] = _value

                    org_details[org_name] = {
                        "id": org_id,
                        "teams": org_teams,
                        "admins": org_admins,
                        "settings": org_settings
                    }

                users["org_details"] = org_details
                driver.close()

                with open(users_file, 'w') as f:
                    json.dump(users, f, indent=2)

        else:
           print("No teams data!!!")


if __name__ == "__main__":
    """
    Get data from ENV for users in RESOURCE_FILE and store updated data in DATA_FILE
    """
    ENV = 'integration'
    URL = f'https://client.{ENV}.cf3.us'

    ADMIN_USER = input("admin username: ")
    ADMIN_PASSWORD = input("admin password: ")
    ADMIN_API_KEY = input("admin api key: ")
    USER_PASSWORD = input("Provide password for new users: ")
    RESOURCE_FILE = input("Provide file name with existing users (e.g. account_integration.json; absolute path): ")
    DATA_FILE = input("Provide file name where new data will be stored (absolute path): ")

    # get info about users - roles, teams; generate new json file with as a result
    get_account_data(RESOURCE_FILE, DATA_FILE)

    # get info about teams - org, roles; use data from  new file from ^^ step
    get_teams_data(DATA_FILE)

    # get info about orgs
    get_orgs_data(DATA_FILE)


