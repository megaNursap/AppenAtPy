import time

from adap.support.generate_test_data.utils_fed_users.create_user_utils import login, open_team_org_by_name
from adap.ui_automation.utils.selenium_utils import set_up_driver, find_elements, find_element
from dictor import dictor
from str2bool import str2bool

update_teams = {}

def update_setting_info(teams_info, new_roles, role_type, team):
    if new_roles:
        if teams_info[team['name']][role_type]:
            current_roles = update_teams[team['name']][role_type]
            current_roles.update(new_roles)
            teams_info[team['name']][role_type] = current_roles
        else:
            teams_info[team['name']][role_type] = new_roles

def set_up_roles(driver, team_roles):
    edit_btn = find_element(driver, "//a[@class='b-team-details__edit']")
    edit_btn.click()
    time.sleep(2)
    for setting_type, setting_value in team_roles.items():
        if setting_type == 'plan':
            current_plan = find_element(driver, "//div[@id='s2id_akon_team_plan']//span[text()]")
            if current_plan.text != setting_value:
                current_plan.click()
                plan = find_elements(driver,
                                     "//li[not (contains(@class,'unselectable'))][.//div[text()='%s']]" % setting_value)
                assert len(plan), "Plan %s has not been found" % setting_value
                plan[0].click()
                time.sleep(1)

        if setting_type in ['roles', 'add_roles']:
            for role, value in setting_value.items():
                if setting_type == 'roles':
                    xpath_role = "//label[text()='%s']/..//input[@type='checkbox']" % role
                else:
                    xpath_role = "//label[contains(., '%s')]//input[@type='checkbox']" % role

                current_role = find_elements(driver, xpath_role)
                for i in current_role:
                    if i.is_selected() != str2bool(value):
                        i.find_element('xpath',"./..").click()
                        time.sleep(1)

    save_btn = find_element(driver, "//input[@value='Save Changes']")
    save_btn.click()


def set_up_team_roles(data, URL, ADMIN_USER, ADMIN_PASSWORD):
    for nick_name, settings in data.items():
        teams = dictor(settings, 'teams')
        if teams:
            for team in teams:
                if team['name'] == 'cf_internal': continue

                team_plan = team.get('plan', None)
                team_roles = team.get('roles', None)
                team_add_roles = team.get('add_roles', None)

                if not update_teams.get(team['name'], False):
                    update_teams[team['name']] = {'plan': team_plan,
                                                  'roles': team_roles,
                                                  'add_roles': team_add_roles}
                else:
                    if team_plan:
                        update_teams[team['name']]['plan'] = team_plan
                        print("Set up team plan: %s for %s team " % (team_plan, team['name']))

                    update_setting_info(update_teams, team_roles, 'roles', team)
                    update_setting_info(update_teams, team_add_roles, 'add_roles', team)


    driver = set_up_driver()
    driver.get(URL)
    login(driver, ADMIN_USER, ADMIN_PASSWORD)

    for t_name, t_settings in update_teams.items():
        driver.get(URL + "/admin/teams")
        try:
            open_team_org_by_name(driver, t_name)
            set_up_roles(driver, t_settings)
        except:
           print("Team %s has not been found" % t_name)

    driver.quit()
