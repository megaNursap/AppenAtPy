import json
import datetime
import os

from faker import Faker

cash_names = {}
RANDOM_MODE = ['email', 'user_name', 'org_name', 'teams', "main_team"]


def generate_fake_email(nick_name):
    today = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    return "%s+%s@appen.com" % (nick_name, today)


def generate_fake_name(nick_name):
    today = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    return "%s %s" % (nick_name, today)


def generate_fake_org_name():
    today = datetime.datetime.now().strftime("%Y%m%d%H%M")
    faker = Faker()
    return "org-%s-%s" % (faker.zipcode(), today)


def generate_fake_team_name():
    today = datetime.datetime.now().strftime("%Y%m%d%H%M")
    faker = Faker()
    return "%s team %s" % (faker.zipcode(), today)


def update_user_creadentials_file_with_random_data(users_file, users, random_mode, nickname_filter=None):
    print("... GENERATE RANDOM USER CREDENTIALS")
    file_updated = False
    for k, user_info in users.items():
        if k == 'cf_internal_role': continue

        if nickname_filter and k != nickname_filter: continue
        print('...in progress')
        if k == 'teams_details':
            _temp_teams = {}
            for team_name, team_info in user_info.items():
                _temp_team_info = team_info
                _temp_team_info['org_name'] = cash_names.get(team_info['org_name'], team_info['org_name'])
                _temp_teams[cash_names[team_name]] = _temp_team_info
            users['teams_details'] = _temp_teams
        elif k == 'org_details':
            _temp_orgs = {}
            for org_name, org_info in user_info.items():
                new_teams = []
                for _team in org_info['teams']:
                    _team_name = _team['team_name']
                    new_teams.append({
                        'team_id': _team['team_id'],
                        'team_name': cash_names.get(_team['team_name'], _team['team_name'])
                    })

                new_admins = []
                for _admin in org_info['admins']:
                    new_admins.append(cash_names.get(_admin,_admin))


                _temp_orgs[cash_names.get(org_name, org_name)] = {
                    "id": org_info['id'],
                    "teams": new_teams,
                    "admins": new_admins,
                    "settings": org_info['settings']
                }
            users['org_details'] = _temp_orgs
        else:
            for param_key, param_value in user_info.items():
                if param_key in random_mode:
                    file_updated = True
                    if users[k][param_key]:
                        if param_key == 'teams':
                            new_teams = []
                            for team in param_value:
                                if team.get('name', False):
                                    current_name = team['name']
                                    if current_name != 'cf_internal':
                                       team['name'] = cash_names[current_name]
                                new_teams.append(team)
                            users[k][param_key] = new_teams
                        else:
                            users[k][param_key] = cash_names[param_value]

    if file_updated:
        os.remove(users_file)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)


def generate_random_test_data(users_file, random_mode=RANDOM_MODE, nickname_filter=None, add_prefix=None):
    # add_prefix  - if param not None, not generate random data, just add_prefix to existing data
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

    for nick_name, user_info in users.items():

        if nick_name == 'cf_internal_role': continue
        if nickname_filter and nick_name != nickname_filter: continue


        if  user_info.get('email') and (not cash_names.get(user_info['email'], False)) and ("email" in random_mode):
            cash_names[user_info['email']] = generate_fake_email(nick_name)

        if user_info.get('user_name') and not cash_names.get(user_info['user_name'], False)  and "user_name" in random_mode:
            cash_names[user_info['user_name']] = generate_fake_name(nick_name)

        if user_info.get('org_name', False) and "org_name" in random_mode:
            org_name = user_info.get('org_name', False)
            if not cash_names.get(org_name, False):
                cash_names[user_info['org_name']] = generate_fake_org_name()

        if 'teams' in random_mode:
            teams = (user_info.get('teams', False))
            if teams:
                for team in teams:
                    if team.get('name', False) and team.get('name') != 'cf_internal' and team.get('name') != '':
                        if not cash_names.get(team['name']):
                           cash_names[team['name']] = generate_fake_team_name()

        if nick_name == 'teams_details':
            for team, team_info in user_info.items():
                if team_info.get('org_name'):
                    if not cash_names.get(team_info['org_name']):
                        cash_names[team_info['org_name']] = generate_fake_org_name()




    # update file
    #
    update_user_creadentials_file_with_random_data(users_file, users, RANDOM_MODE, nickname_filter=nickname_filter)



