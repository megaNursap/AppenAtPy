import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys

from adap.api_automation.utils.http_util import HttpMethod
from adap.support.generate_test_data.adap.verify_email import verify_user_email_akon
from adap.ui_automation.utils.page_element_utils import click_rebrand_popover
from adap.ui_automation.utils.selenium_utils import set_up_driver, get_text_by_xpath

task_stack = {}
org_info_cash = {}
team_info_cash = {}


def login(driver, user, user_password):
    try:
        driver.find_element('xpath',"//button[@id='details-button']").click()
        driver.find_element('xpath',"//a[@id='proceed-link']").click()
    except:
        print("login")

    email = driver.find_element('xpath','//input[@type="email"]')
    email.send_keys(user)

    password = driver.find_element('xpath','//input[@type="password"]')
    password.send_keys(user_password)

    driver.find_element('xpath','//input[@type="submit"]').click()
    time.sleep(2)
    popover_content = driver.find_elements('xpath','//div[@class="popover-content"]')
    if len(popover_content) > 0:
        popover_content[0].find_element('xpath',"./button[@class='b-TourSteps__tourTipExit']").click()

    try:
        click_rebrand_popover(driver)
    except:
        print("no guide")


def activate_user(user_name, user_email, URL, USER_PASSWORD):
    driver = set_up_driver()
    driver.get(URL)
    try:
        driver.find_element('xpath',"//button[@id='details-button']").click()
        driver.find_element('xpath',"//a[@id='proceed-link']").click()
    except:
        print('activate_user')
    driver.find_element('xpath',"//a[text()='Sign up!']").click()
    time.sleep(1)
    driver.find_element('xpath',"//input[@id='user-name']").send_keys(user_name)
    driver.find_element('xpath',"//input[@id='user-email']").send_keys(user_email)
    driver.find_element('xpath',"//input[@name='user[password]']").send_keys(USER_PASSWORD)
    driver.find_element('xpath',"//input[@name='user[password_confirmation]']").send_keys(USER_PASSWORD)
    if 'task-force' in driver.current_url:
        driver.find_element('xpath',"//input[@value='Create My Account']").click()
    else:
        driver.find_element('xpath',"//input[@value='Create Account']").click()
    time.sleep(3)
    print("User %s was activated" % user_name)
    driver.quit()


def invite_user(driver, user_email, user_name):
    driver.find_element('xpath',"//input[@name='email']").send_keys(user_email)
    driver.find_element('xpath',"//a[text()='Send Invite']").click()
    time.sleep(3)
    driver.find_element('xpath',"//a[text()='Invite']").click()
    time.sleep(5)
    print("User %s was invited" % user_name)
    driver.refresh()
    time.sleep(2)


def create_users(users_to_invite, users_info, URL, ADMIN_USER, ADMIN_PASSWORD, USER_PASSWORD):
    driver = set_up_driver()
    driver.get(URL)
    login(driver, ADMIN_USER, ADMIN_PASSWORD)
    driver.get(URL + "/account/teams")

    for user in users_to_invite:
        user_email = users_info[user]["email"]
        user_name = users_info[user]["user_name"]
        invite_user(driver, user_email, user_name)
    driver.quit()

    for user in users_to_invite:
        user_email = users_info[user]["email"]
        user_name = users_info[user]["user_name"]
        activate_user(user_name, user_email, URL, USER_PASSWORD)


def find_data_on_the_page(driver, user_email, msg):
    search_field = driver.find_element('xpath',"//input[@id='query']")
    search_field.clear()
    search_field.send_keys(user_email, Keys.RETURN)
    time.sleep(5)
    no_users_found = driver.find_elements('xpath',"//div[text()='%s']" % msg)
    return no_users_found


def find_users_to_invite(users, driver, URL):
    print("find_users_to_invite started")
    driver.get(URL + "/admin/users")
    time.sleep(4)

    users_to_invite = []
    for nick_name, settings in users.items():
        print(nick_name + " in progress")
        if nick_name in ['cf_internal_role', 'teams_details']: continue
        if settings.get('contributor', False): continue
        user_email = settings.get('email', False)
        no_users_found = find_data_on_the_page(driver, user_email, msg='No users were found.')
        if no_users_found:
            print("CREATE NEW USER!!!")
            users_to_invite.append(nick_name)
        else:
            #  user exist, check if we need to change team
            pass

    task_stack['user_to_invite'] = set(users_to_invite)
    print("find_users_to_invite finished")


def find_org_to_create(users, driver, URL):
    driver.get(URL + "/admin/organizations")
    time.sleep(4)

    orgs_to_create = []
    for nick_name, settings in users.items():
        if nick_name == 'cf_internal_role': continue

        org_name = settings.get('org_name', None)
        if org_name in ["cf_internal", "", None]: continue

        no_org_found = find_data_on_the_page(driver, org_name, msg='No organizations were found.')
        if no_org_found:
            print("CREATE NEW ORG!!! ", org_name)
            orgs_to_create.append({'name': org_name, 'admin': settings.get('email', None)})

    task_stack['create_org'] = orgs_to_create
    # return {"create_org": set(orgs_to_create)}


def find_team_to_create(users, driver, URL):
    driver.get(URL + "/admin/teams")
    time.sleep(4)

    team_to_create = []
    team_move_to_org = {}
    add_user_to_team = {}
    for nick_name, settings in users.items():
        if nick_name == 'cf_internal_role': continue
        if settings.get('teams', False):
            for team in settings['teams']:
                if team['name'] in ["cf_internal", ""]: continue
                team_role = team.get('role', 'standart')
                if add_user_to_team.get(team['name'], False) != False:
                    _teams = add_user_to_team[team['name']]
                    _teams.append({nick_name: team_role})
                    add_user_to_team[team['name']] = _teams
                else:
                    add_user_to_team[team['name']] = [{nick_name: team_role}]

                no_team_found = find_data_on_the_page(driver, team['name'], msg='No teams were found.')

                if no_team_found:
                    print("CREATE NEW TEAM!!! ", team['name'])
                    team_to_create.append(team['name'])

                    org_name = settings.get('org_name', None)
                    if org_name not in ["cf_internal", "", None]:
                        if team_move_to_org.get(org_name, False) != False:
                            _teams = team_move_to_org[org_name]
                            _teams.append(team['name'])
                            team_move_to_org[org_name] = _teams
                        else:
                            team_move_to_org[org_name] = [team['name']]

    task_stack['create_team'] = set(team_to_create)
    task_stack['move_team'] = team_move_to_org
    task_stack['add_user_team'] = add_user_to_team


def remove_user_from_team(email, driver):
    print("REMOVE USER FROM CF:", email)
    user_found = False
    current_page = None
    next_page = ""
    try:
        while not user_found and current_page != next_page:
            current_page = driver.page_source
            user = driver.find_elements('xpath',"//tr[.//td[text()='%s']]" % email)
            if len(user) > 0:
                user_found = True
                user[0].find_element('xpath',".//td[.//span[text()='Remove']]//*[local-name() = 'svg']").click()
                time.sleep(2)
                driver.find_element('xpath',"//a[text()='Yes']").click()
                time.sleep(2)
                driver.refresh()
                time.sleep(3)
            else:
                driver.find_element('xpath',"//li[contains(@class, 'b-Pagination__Next')]").click()
                time.sleep(2)
                next_page = driver.page_source
    except:
        print("Something went wrong!")


def create_new_team(team_name, user, driver, URL):
    print("CREATE NEW TEAM:", team_name)
    driver.get(URL + "/admin/users")
    user_not_found = find_data_on_the_page(driver, user, 'No users were found.')
    if not user_not_found:
        # user should not be part of any teams, team = N/A (no team)
        current_team = driver.find_elements('xpath',"//td[text()='N/A (no team)']")
        if len(current_team) > 0:
            driver.find_element('xpath',"//a[text()='Upgrade']").click()
            # create new team
            driver.find_element('xpath',"//input[@id='organization-name']").send_keys(team_name)
            driver.find_element('xpath',"//a[@id='create-organization']").click()
            time.sleep(4)


def invite_user_to_team(team_name, user, driver, URL):
    print("INVITE USER TO TEAM: ", user, team_name)
    driver.get(URL + "/admin/teams")
    no_team_found = find_data_on_the_page(driver, team_name, 'No teams were found.')
    if len(no_team_found) == 0:
        print("open team")
        # open team
        driver.find_element('xpath',"//td//a[text()='%s']" % team_name).click()
        time.sleep(3)
        # add user
        driver.find_element('xpath',"//a[text()='Add User']").click()
        driver.find_element('xpath',"//input[@id='user-email']").send_keys(user)
        driver.find_element('xpath',"//a[@id='add-user-to-team']").click()
        driver.find_element('xpath',"//a[text()='Add']").click()


def create_team(new_teams, team_users, user_info, URL, ADMIN_USER, ADMIN_PASSWORD):
    print("CREATE TEAMS", new_teams)
    driver = set_up_driver()
    driver.get(URL)
    login(driver, ADMIN_USER, ADMIN_PASSWORD)
    removed_users = []
    for team in new_teams:
        driver.get(URL + "/account/teams")
        print("... in progress ", team)
        # team_users = team_users.get(team, False)
        print(team_users)
        # if not team_users: continue

        for user in team_users[team]:
            user_name = list(user.keys())[0]
            if user.keys() in removed_users: continue
            remove_user_from_team(user_info[user_name]['email'], driver)
            removed_users.append(user_name)

        team_created = False
        for user in team_users[team]:
            user_name = list(user.keys())[0]
            if not team_created:
                create_new_team(team, user_info[user_name]['email'], driver, URL)
                time.sleep(10)
                team_created = True
            else:
                invite_user_to_team(team, user_info[user_name]['email'], driver, URL)

        del team_users[team]

    # #  TODO add user to existing teams
    # for team, users in team_users.items():
    #     print("invite users to existing team", users)
    #     for user in users:
    #         print('...', user)
    #         remove_user_from_team(user_info[user]['email'], driver)
    #         invite_user_to_team(team, user_info[user]['email'], driver)

    driver.quit()


def add_admin_to_org(orgs, URL, ADMIN_USER, ADMIN_PASSWORD):
    print("ADD ORG ADMIN")
    driver = set_up_driver()
    driver.get(URL)

    login(driver, ADMIN_USER, ADMIN_PASSWORD)
    time.sleep(4)

    for org in orgs:
        # add admin
        if org.get('admin', None):
            driver.get(URL + "/admin/organizations")
            search_field = driver.find_element('xpath',"//input[@id='query']")
            search_field.clear()
            search_field.send_keys(org['name'], Keys.RETURN)
            time.sleep(5)

            driver.find_element('xpath',"//a[text()='%s']" % org['name']).click()
            time.sleep(2)

            print("add admin %s to org: %s ", (org['admin'], org['name']))
            current_url = driver.current_url
            driver.get(current_url + "/admins")
            driver.find_element('xpath',"//a[text()='Add Admin']").click()

            driver.find_element('xpath',"//input[@name='email']").send_keys(org['admin'])
            driver.find_element('xpath',"//button[text()='Add']").click()
            time.sleep(10)

    driver.quit()


def create_orgs(orgs, URL, ADMIN_USER, ADMIN_PASSWORD):
    print("CREATE ORGS")
    driver = set_up_driver()
    driver.get(URL)

    login(driver, ADMIN_USER, ADMIN_PASSWORD)
    time.sleep(4)

    for org in orgs:
        print('.. org in progress', org['name'])
        driver.get(URL + "/admin/organizations")
        time.sleep(2)
        driver.find_element('xpath',"//a[text()='Add Organization']").click()
        time.sleep(2)
        driver.find_element('xpath',"//input[@id='organization_name']").send_keys(org['name'])
        driver.find_element('xpath',"//input[@value='Save']").click()
        time.sleep(2)

    driver.quit()


def create_orgs_adap(orgs, url, admin_user, admin_passwors):
    print("CREATE ORGS started")
    driver = set_up_driver()
    driver.get(url)

    login(driver, admin_user, admin_passwors)
    time.sleep(4)

    for org_name, org_details in orgs.items():
        print('.. org in progress', org_name)
        driver.get(url + "/admin/organizations")
        time.sleep(2)

        driver.find_element('xpath',"//a[text()='Add Organization']").click()
        time.sleep(2)

        driver.find_element('xpath',"//input[@id='organization_name']").send_keys(org_name)
        driver.find_element('xpath',"//input[@value='Save']").click()
        time.sleep(2)

        # add teams
        for team in org_details['teams']:
            # try:
                team_name = team['team_name']

                driver.find_element('xpath',"//a[text()='Add Teams']").click()
                driver.find_element('xpath',"//input[@class='b-search__input']").send_keys(team_name)
                driver.find_element('xpath',"//button[text()='Search']").click()

                time.sleep(2)

                not_found = driver.find_elements('xpath',"//div[text()='No Results. Search Again.']")
                if len(not_found) == 0:
                    _team = driver.find_elements('xpath',"//li[text()='%s']/..//label" % team_name)
                    if len(_team) == 0:
                        print("Team %s has not been found" % team_name)
                    else:
                        _team[0].click()
                        driver.find_element('xpath',"//a[text()='Add']").click()
                        time.sleep(1)
                        driver.find_element('xpath',"//a[text()='Confirm']").click()
                        time.sleep(3)
                else:
                    driver.find_elements('xpath',"//a[@data-dismiss='modal' and text()='Cancel']")[1].click()
                    print("Team %s has not been found" % team_name)
            #
            # except:
            #     print("Error: add team to org ", team)

        # add admins to org
        driver.find_element('xpath',"//a[text()='Admins']").click()
        for admin in org_details['admins']:
            try:
                driver.find_element('xpath',"//a[text()='Add Admin']").click()
                driver.find_element('xpath',"//input[@name='email']").send_keys(admin)
                driver.find_element('xpath',"//button[text()='Add']").click()

                errors = driver.find_elements('xpath',"//div[contains(@class, 'b-alert__danger')]")
                if len(errors)>0: print("Error to add admin to org:" + errors[0].text)
            except:
                if len(driver.find_elements('xpath',"//button[text()='Cancel']")) > 0:
                    driver.find_element('xpath',"//button[text()='Cancel']")
                print("Error: add admin to org ", admin)

        # add settings to org
        driver.find_element('xpath',"//a[text()='Settings']").click()
        updated = False
        for settings_name, settings_value in org_details['settings'].items():
           try:
               current_value = driver.find_element('xpath',"//input[@name='%s' and @class]" % settings_name).is_selected()
               if current_value != settings_value:
                   driver.find_element('xpath',"//input[@name='%s' and @class]/.." % settings_name).click()
                   updated = True
           except:
               print("Error: setup param to org", settings_name)

        if updated:
            driver.find_elements('xpath',"//input[@value='Save']")[1].click()
    driver.quit()
    print("CREATE ORGS finished")



def move_teams(teams_to_move, URL, ADMIN_USER, ADMIN_PASSWORD):
    print("MOVE TEAMS")
    driver = set_up_driver()
    driver.get(URL)

    login(driver, ADMIN_USER, ADMIN_PASSWORD)
    time.sleep(4)

    for org, teams in teams_to_move.items():
        print('.. to org', org)
        driver.get(URL + "/admin/organizations")
        time.sleep(2)

        search_field = driver.find_element('xpath',"//input[@id='query']")
        search_field.clear()
        search_field.send_keys(org, Keys.RETURN)
        time.sleep(5)

        driver.find_element('xpath',"//a[text()='%s']" % org).click()
        time.sleep(2)

        for team in teams:
            print('...team', team)
            driver.find_element('xpath',"//a[text()='Add Teams']").click()

            driver.find_element('xpath',"//input[@class='b-search__input']").send_keys(team)
            time.sleep(1)
            driver.find_element('xpath',"//button[text()='Search']").click()
            time.sleep(4)

            driver.find_element('xpath',"//li[text()='%s']//span[@class='icon-checked']" % team).click()
            driver.find_element('xpath',"//a[text()='Add']").click()
            time.sleep(1)
            driver.find_element('xpath',"//a[text()='Confirm']").click()
            time.sleep(2)

    driver.quit()


def grab_api_key(driver, regenerate, URL):
    driver.get(URL + "/account/api")
    time.sleep(4)
    if regenerate:
        driver.find_element('xpath',"//a[text()='Generate New']").click()
        time.sleep(1)
    try:
        api_key = driver.find_element('xpath',"//div[@class='b-ApiPage__field']").text
    except:
        api_key = get_text_by_xpath(driver, "//h3[text()='API Key']/..//div[text()]")
    return api_key


def find_key(driver, user_info, regenerate, URL, USER_PASSWORD):
    user_name = user_info['email']
    login(driver, user_name, USER_PASSWORD)

    popover_content = driver.find_elements('xpath','//div[@class="popover-content"]')
    if len(popover_content) > 0:
        popover_content[0].find_element('xpath',"./button[@class='b-TourSteps__tourTipExit']").click()

    api_key = grab_api_key(driver, regenerate, URL)
    return api_key


def find_org_id(org_name, driver, URL):
    if org_info_cash.get(org_name, False):
        return org_info_cash[org_name]
    else:
        driver.get(URL + "/admin/organizations")

        open_team_org_by_name(driver, org_name)
        current_id = driver.current_url.split('/')[-1]
        org_info_cash[org_name] = current_id
        return current_id


def find_team_id(team_name, driver, URL):
    if team_info_cash.get(team_name, False):
        return team_info_cash[team_name]
    else:
        driver.get(URL + "/admin/teams")
        open_team_org_by_name(driver, team_name)
        current_id = driver.current_url.split('/')[-1]
        team_info_cash[team_name] = current_id
        return current_id


def open_team_org_by_name(driver, team_name):
    try:
        search_field = driver.find_element('xpath',"//input[@id='query']")
        search_field.clear()
        search_field.send_keys(team_name, Keys.RETURN)
        time.sleep(5)
        driver.find_element('xpath',"//a[text()='%s']" % team_name).click()
        time.sleep(2)
    except:
        print("Something went wrong: open_team_org_by_name, %s" % team_name)


def signup_adap(user_email, user_name, password, url):
    service = HttpMethod(session=True)

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache"
    }

    sign_up = service.get(f'{url}/users/new', headers=headers)

    sign_up_soup = BeautifulSoup(sign_up.text, 'html.parser')
    authenticity_token = sign_up_soup.find('input', {'name': 'authenticity_token'}).get('value')
    signup_form_data = {
        "authenticity_token": authenticity_token,
        "user[name]": user_name,
        "user[email]": user_email,
        "user[password]": password,
        "user[password_confirmation]": password,
        "user[force_disposable_email_check]": 'false',
        "terms": 'on',
        "commit": 'Create My Free Account'
    }
    sign_up_commit = service.post(
        f'{url}/users',
        allow_redirects=True,
        headers=headers,
        data=signup_form_data
    )

    assert sign_up_commit.status_code == 200


def create_users_adap(users_to_invite, users_info, user_password, url, env, admin_api_key):
    print("create_users_adap started")
    error_user = []
    for user in users_to_invite:
        try:
            user_email = users_info[user]["email"]
            user_name = users_info[user]["user_name"]
            signup_adap(user_email, user_name, user_password, url)
            time.sleep(5)
            verify_user_email_akon(user_email, env, admin_api_key)
        except:
            error_user.append(user)
            print("Error: create user %s" % user)

    print("ERRORS: create_users_adap - ", error_user)
    print("create_users_adap finished")


def update_user_roles(users_to_invite, users_info, url, admin, admin_password):
    print("update_user_roles started")
    driver = set_up_driver()
    driver.get(url)
    login(driver, admin, admin_password)

    time.sleep(4)

    for user in users_to_invite:
        print(user + " in progress")
        driver.get(url + "/admin/users")
        try:
            click_rebrand_popover(driver)
        except:
            print("no guide")

        user_email = users_info[user].get('email', False)
        no_users_found = find_data_on_the_page(driver, user_email, msg='No users were found.')
        if not no_users_found:
            edit_btn = driver.find_element('xpath',"//a[contains(@href,'/edit')]")
            edit_btn.click()

            time.sleep(2)

            setup_roles = users_info[user].get('user_roles', False)
            updated = False

            if setup_roles:
                for role, value in setup_roles.items():
                    current_value = driver.find_element('xpath',"//input[@id='%s']" % role)
                    if current_value.is_selected() != value:
                        checkbox = driver.find_element('xpath',"//input[@id='%s']/..//label" % role)
                        checkbox.click()
                        updated = True

            time.sleep(2)
            if updated:
                driver.find_element('xpath',"//a[text()='Save Changes']").click()
            time.sleep(1)

    driver.close()
    print("update_user_roles finished")


def update_team_roles(teams_info, url, admin, admin_password):
    print("update_team_roles started")
    driver = set_up_driver()
    driver.get(url)
    login(driver, admin, admin_password)

    time.sleep(4)

    for team, team_info in teams_info.items():

        print(team + " in progress")
        driver.get(url + "/admin/teams")

        try:
            click_rebrand_popover(driver)
        except:
            print("no guide")

        no_team_found = find_data_on_the_page(driver, team, msg='No teams were found.')

        if not no_team_found:
            edit_btn = driver.find_element('xpath',"//a[contains(@href,'/teams') and text()='%s']" % team)
            team_id = edit_btn.get_attribute('href').split('/')[-1]

            driver.get(url+f"/admin/teams/{team_id}/edit")
            time.sleep(2)

            setup_roles = team_info.get('roles', False)
            setup_additional_roles = team_info.get('add_roles', False)

            updated = False

            if setup_roles:
                for role, value in setup_roles.items():
                    current_value = driver.find_element('xpath',"//input[@id='%s']" % role)
                    if current_value.is_selected() != value:
                        checkbox = driver.find_element('xpath',"//input[@id='%s']/..//label" % role)
                        checkbox.click()
                        updated = True

            if setup_additional_roles:
                for role, value in setup_additional_roles.items():
                    current_value = driver.find_element('xpath',"//input[@id='%s']" % role)
                    if current_value.is_selected() != value:
                        checkbox = driver.find_element('xpath',"//input[@id='%s']/..//label" % role)
                        checkbox.click()
                        updated = True

            time.sleep(2)

            # setup plan, pro
            current_plan = driver.find_element('xpath',"//div[contains(@class,'b-TeamEditPage__dropdown')]//span")
            setting_value = 'pro'
            if current_plan.text != setting_value:
                updated = True
                current_plan.click()
                plan = driver.find_element('xpath',
                                     "//a[.//div[text()='%s']]" % setting_value)
                plan.click()
                time.sleep(1)

            if updated:
                driver.find_element('xpath',"//a[text()='Save Changes']").click()
            time.sleep(1)

    driver.close()
    print("update_team_roles finished")

