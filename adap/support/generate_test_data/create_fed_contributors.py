import json
import os

from faker import Faker

from adap.api_automation.services_config.hosted_channel import HC
from adap.api_automation.utils.data_util import load_key, encrypt_users_file
from adap.settings import Config
from adap.support.generate_test_data.utils_fed_users.create_user_utils import activate_user
from adap.support.generate_test_data.utils_fed_users.generate_random_names import generate_randon_test_data
from adap.ui_automation.utils.pandas_utils import collect_data_from_file

faker = Faker()


def create_new_hc(api_key, env_fed):
    valid_hc_name = faker.company() + faker.zipcode()
    payload = {
        "name": valid_hc_name
    }
    hc_res = HC(api_key, env='fed', env_fed=env_fed).create_channel(payload)
    hc_res.assert_response_status(201)
    _channel = hc_res.json_response['id']
    return _channel


def invite_contributor(api_key, env_fed, email, _channel):
    payload = {
        "email": email
    }
    contributor_res = HC(api_key, env='fed', env_fed=env_fed).upload_contributor(_channel, payload)
    contributor_res.assert_response_status(201)


def update_contributors_email(data):
    updated_emails = [faker.email() for i in range(data.shape[0])]
    data['email'] = updated_emails
    return data


def create_contributors_from_csv(file, api_key, env_fed, url, new_password):
    _df = collect_data_from_file(file)

    generate_random_emails = False
    if input("Do you want to generate random emails? (yes/no) ") == 'yes':
        generate_random_emails = True

    if generate_random_emails:
        _df = update_contributors_email(_df)

    if input("Do you want to create new hosted channel? (yes/no) ") == 'yes':
        hc_id = create_new_hc(api_key, env_fed)
    else:
        hc_id = input("Provide hosted channel ID: ")

    _df['channel_id'] = hc_id

    emails = _df['email']
    # update csv file
    _df.to_csv(file, index_label=False, index=False)

    res = HC(api_key, env='fed', env_fed=env_fed).upload_list_of_contributors(file)
    assert res.status_code == 202

    print("Contributors were uploaded to the channel: %s" % hc_id)

    activate_cont = False
    if input("Do you want to activate contributors? (yes/no): ") == 'yes':
        activate_cont = True

    if activate_cont:
        for user in emails:
            activate_user(user, user, url, new_password)


def main(users_file, api_key, env_fed, url, new_password, hc_id):
    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

        user = users.get('test_contributor_task', False)
        if not user:
            print("test_contributor_task user has not been found")
            return False

        # create new channel
        if not hc_id:
           hc_id = create_new_hc(api_key, env_fed)
        # invite contributor
        invite_contributor(api_key, env_fed, user['email'], hc_id)
        # sign up as contributor
        activate_user(user['user_name'], user['email'], url, new_password)
        # update file
        users['test_contributor_task']['password'] = new_password
        users['test_contributor_task']['default_hc'] = hc_id

        os.remove(users_file)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)


if __name__ == "__main__":
    URL = 'https://app.qe83.secure.cf3.us/task-force'
    ENV = 'qe83'
    FILE = '/Users/msenyutina/work/QA_Automation/adap/data/account_qe83.json'
    # FILE = '/Users/msenyutina/work/QA_Automation/adap/data/hosted_channel/dod_data_58.csv'

    path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
    key = load_key(path_key)

    mode = input("Do you want to update json file (1) or create contributors (2):")
    API_KEY = input("Admin api key: ")
    USER_PASSWORD = input("Provide password for new users: ")

    if mode == '1':
        GENERATE_DATA = False

        if input("Do you want to generate random data? (yes/no) ") == 'yes':
            GENERATE_DATA = True

        if input("Do you want to create new hosted channel? (yes/no) ") == 'yes':
            HC_ID = None
        else:
            HC_ID = input("Provide hosted channel ID: ")

        if input("Is file with credentials decrypted? (yes/no) ") == 'yes':
            if GENERATE_DATA:  generate_randon_test_data(FILE, nickname_filter='test_contributor_task')
            main(FILE, API_KEY, ENV, URL, USER_PASSWORD, hc_id=HC_ID)
            encrypt_users_file(FILE, key)
            print("DONE!")
        else:
            print("Please, decrypt your file first!!!")

    elif mode == '2':
        create_contributors_from_csv(FILE, API_KEY, env_fed=ENV, url=URL, new_password=USER_PASSWORD)
        print("Done!!")
    else:
        print('Mode undefined')
