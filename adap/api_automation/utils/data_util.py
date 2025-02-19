import json
import datetime
from dateutil import parser

import allure
import pytest
import os
import zipfile
import string
import random
import pandas as pd
import csv
from faker import Faker
from cryptography.fernet import Fernet
from adap.settings import Config
import shutil

encrypted_fields = [
    'api_key',
    'password',
    'jwt_token',
    'x_storage_refs_token',
    'worker_password',
    'auth_key',
    'payoneer_program_id',
    'keycloak_client_secret',
    'client_secret',
    'bypass'
]


def get_secret():
    secret = ''
    if Config.KEY:
        secret = Config.KEY
    elif getattr(pytest, 'key', ''):
        secret = pytest.key
    else:
        secret_file = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
        if os.path.isfile(secret_file):
            secret = load_key(secret_file)
    return secret


def retrive_data(data_file):
    with open(data_file, "r") as read_file:
        data = json.load(read_file)
    return data


def make_list(json_response, field):
    list_x = []
    for i in range(0, len(json_response) - 1):
        list_x.append(json_response[i].get(field))

    return list_x


def get_data_file(file_name, env=None):
    try:
        return DataTricks(env).path_test_data + file_name
    except:
        return None


def get_test_data(user_name, data_type, key=None, env=None):
    try:
        if not env:
            env = pytest.env

        # users = pytest.data.users
        users = DataTricks(env=env).users

        if data_type in encrypted_fields:
            if not key and pytest.key:
                key = pytest.key
            else:
                path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
                if os.path.isfile(path_key):
                    key = load_key(path_key)
            try:
                return decrypt(users[user_name][data_type], key)
            except:
                return None

        return users[user_name][data_type]

    except:
        return None


def get_test_account_data_generally(user_name, data_type, env, key=None):
    try:
        users = DataTricks(env=env).users

        if data_type in encrypted_fields:
            if not key:
                path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
                if os.path.isfile(path_key):
                    key = load_key(path_key)
            try:
                return decrypt(users[user_name][data_type], key)
            except:
                return None

        return users[user_name][data_type]

    except:
        return None


def get_user_api_key(user_name, decrypt_key=True, key=None):
    # todo add error exception
    users = pytest.data.users

    if not key and pytest.key:
        key = pytest.key
    else:
        path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
        if os.path.isfile(path_key):
            key = load_key(path_key)

    try:
        if decrypt_key:
            return decrypt(users[user_name]['api_key'], key)
        else:
            return users[user_name]['api_key']
    except:
        return None


def get_user_team_id(user_name, index=0):
    users = pytest.data.users
    try:
        return users[user_name]['teams'][index]['id']
    except:
        return None


def get_user_team_name(user_name, index=0):
    users = pytest.data.users
    try:
        return users[user_name]['teams'][index]['name']
    except:
        return None


def get_user_name(user_name):
    users = pytest.data.users
    try:
        return users[user_name]['user_name']
    except:
        return None


def get_predefined_source_report_wf(username):
    users = pytest.data.users
    try:
        return users[username]['wf_source_report']
    except ValueError:
        return None


def get_akon_id(user_name):
    users = pytest.data.users
    try:
        return users[user_name]['akon_id']
    except:
        return None


def get_user_worker_id(user_name):
    users = pytest.data.users
    try:
        return users[user_name]['worker_id']
    except:
        return None


def get_user_org_id(user_name):
    users = pytest.data.users
    try:
        return users[user_name]['org_id']
    except:
        return None


def get_template_id():
    users = pytest.data.users
    try:
        return users['template_job']['template_id']
    except:
        return None


def get_template_job_id():
    users = pytest.data.users
    return users['template_job']['job_id']


def get_user_info(user_name):
    # todo add error exception
    users = pytest.data.users
    try:
        return users[user_name]
    except:
        return None


def get_user_email(user_name):
    # todo add error exception
    users = pytest.data.users
    try:
        return users[user_name]['email']
    except:
        return None


def get_user_id(user_name):
    # todo add error exception
    users = pytest.data.users
    try:
        return users[user_name]['id']
    except:
        return None


def get_user_password(user_name, decrypt_password=True, key=None):
    # todo add error exception
    users = pytest.data.users

    if not key and pytest.key:
        key = pytest.key
    else:
        path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
        if os.path.isfile(path_key):
            key = load_key(path_key)

    try:
        if decrypt_password:
            return decrypt(users[user_name]['password'], key)
        else:
            return users[user_name]['password']
    except:
        return None


def decrypt_user_new_password(new_password, key=None):
    if not key and pytest.key:
        key = pytest.key
    else:
        path_key = os.path.abspath(Config.PROJECT_ROOT + "/qa_secret.key")
        if os.path.isfile(path_key):
            key = load_key(path_key)
    return decrypt(new_password, key)


def read_data_from_file(data_file):
    file_type = data_file.rpartition(".")[-1]
    if file_type == 'json':
        data = pd.read_json(data_file, lines=True)
    elif file_type == 'csv':
        data = pd.read_csv(data_file)
    elif file_type == 'xlsx':
        data = pd.read_excel(data_file)
    elif file_type == 'tsv':
        data = pd.read_csv(data_file, sep='\t')
    else:
        raise "Data format %s is not supported" % file_type
    return data


def count_row_in_file(data_file):
    data = read_data_from_file(data_file)
    return len(data)


def unzip_file(data_file):
    with zipfile.ZipFile(data_file, 'r') as zip_ref:
        zip_ref.extractall(data_file + "/..")
    return


def get_headers_in_csv(data_file):
    with open(data_file, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
    return headers


def file_exists(data_file):
    return os.path.exists(data_file)


def generate_random_string(length=3):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_test_data(data):
    for k, v in data.items():
        if v == "random_int":
            new_value = random.randint(1, 100000)
            data[k] = new_value
        if v == "random_string":
            new_value = generate_random_string()
            data[k] = new_value
    return data


def generate_random_wf_name(length=3):
    faker = Faker()
    return faker.company() + ' ' + faker.zipcode()


def get_hosted_channel_id(user_name, multiple):
    users = pytest.data.users
    if multiple is True:
        return users[user_name]['hosted_channels']
    else:
        return users[user_name]['hosted_channel']


def save_file_with_content(file_name, content):
    open(file_name, 'wb').write(content)


def copy_file_with_new_name(src, tmpdir, new_name):
    new_name = str(tmpdir) + "/" + new_name
    return shutil.copy(src, new_name)


def read_csv_file(file_name, row_name):
    with allure.step('Read input csv file'):
        result = []
        with open(file_name, 'r') as file:
            csv.register_dialect('customDialect',
                                 delimiter=',',
                                 quoting=csv.QUOTE_ALL)
            reader = csv.DictReader(file, dialect='customDialect')
            for row in reader:
                result.append(row[row_name])
        return result


def read_json_file(file_name, field_name, read_nested_field=True, nested_field_name='name'):
    with allure.step('Read input json file'):
        value_list = []
        with open(file_name) as json_file:
            data = json.load(json_file)
            [value_list.append(value_info) for value_info in data[field_name]]
        if read_nested_field:
            list_of_nested_value = [nested_value[nested_field_name] for nested_value in value_list if
                                    nested_field_name in nested_value]
            return list_of_nested_value
        else:
            return value_list


def input_list_contains_output_list(list_input, list_output, modify_list=False, value_modify="customer_id_for_"):
    if modify_list:
        new_list = [f'{value_modify}{e}' for e in list_output]
        return any(item.lower() in list_input for item in new_list)
    else:
        return all(item.lower() in list_input for item in list_output)


# ----------------------------------------
# ----------------------------------------
# ----------------------------------------
# ----------   encryption ----------------
# ----------------------------------------
# ----------------------------------------
# ----------------------------------------


def generate_key():
    return Fernet.generate_key()


def load_key(secret_key_file):
    with open(secret_key_file, 'r') as f:
        return f.read()


def encrypt(msg, key):
    f = Fernet(key)
    return f.encrypt(msg.encode())


def decrypt(msg, key):
    if not isinstance(key, bytes):
        key = key.encode('utf-8')
    if not isinstance(msg, bytes):
        msg = msg.encode('utf-8')
    f = Fernet(key)
    return f.decrypt(msg).decode('utf-8')


def encrypt_users_file(file_name, key):
    with open(file_name, "r+") as read_file:
        users = json.load(read_file)

    for name, param in users.items():
        for param_key, param_value in param.items():
            if param_key in encrypted_fields:
                if param_value:
                    new_value = encrypt(param_value, key)
                    users[name][param_key] = new_value.decode('utf-8')

    os.remove(file_name)
    with open(file_name, 'w') as f:
        json.dump(users, f, indent=2)


def dencrypt_users_file(file_name, key):
    with open(file_name, "r+") as read_file:
        users = json.load(read_file)

    for name, param in users.items():
        for param_key, param_value in param.items():
            if param_key in encrypted_fields:
                if param_value:
                    new_value = decrypt(param_value, key)
                    users[name][param_key] = new_value

    os.remove(file_name)
    with open(file_name, 'w') as f:
        json.dump(users, f, indent=2)


def decrypt_message(message):
    key = get_secret()
    return decrypt(message, key)


class DataTricks:
    def __init__(self, env=None):
        if env is None:
            env = pytest.env

        if getattr(pytest, 'appen', None) != 'true':
            if env == 'adap_ac':
                self.path_test_data = f"{Config.PROJECT_ROOT}/integration/data"
                self.predefined_data = {}
            elif env == 'gap':
                self.path_test_data = f"{Config.PROJECT_ROOT}/gap/data"
                self.predefined_data = {}
            else:
                self.path_test_data = f"{Config.APP_DIR}/data"
                self.predefined_data = retrive_data(self.path_test_data + "/predefined_data.json")
        else:
            self.path_test_data = f"{Config.PROJECT_ROOT}/appen_connect/data"
            self.predefined_data = {}

        if env == 'fed':
            self.users_file = "/account_%s.json" % pytest.env_fed
        elif "devspace" in env:
            self.users_file = '/account_devspace.json'
        else:
            self.users_file = "/account_%s.json" % env

        self.users = retrive_data(self.path_test_data + self.users_file)


def get_user(username, env=Config.ENV, key=''):
    key = key or get_secret()
    user_data = DataTricks(env).users.get(username)
    for k, v in user_data.items():
        if k in encrypted_fields:
            user_data[k] = decrypt(v, key)

    return user_data


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def generate_random_msg(n):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(n))


def sorted_list_of_dict_by_value(current_list, value, reverse=False):
    new_list = sorted(current_list, key=lambda i: i[value].lower() if isinstance(i[value], str) else i[value],
                      reverse=reverse)
    return new_list


def find_dict_in_array_by_value(current_list, key, value):
    for el in current_list:
        if el.get(key, False) == value: return el
    return None


def convert_date_format(current_date, current_format, new_format):
    """
    current_date - string, e.g. 2022-08-01'
    current_format - string with format, e.g. '%Y-%m-%d'
    new_format - string with format, e.g.'%m-%d-%Y'
    """
    _date = datetime.datetime.strptime(current_date, current_format)
    return _date.strftime(new_format)


def convert_date_format_iso8601(current_date, new_format):
    """
    current_date - string, date in format ISO 8601,  2009-05-28T16:15:00
    new_format - string with format, e.g.'%m-%d-%Y'
    """
    _date = parser.parse(current_date)
    return _date.strftime(new_format)


def convert_str_to_int(text):
    try:
        return int(text)
    except:
        return 0

def convert_audio_datatime_to_second(value):
    h, m, s, mm = value.replace(".", ":").split(':')
    converted_second = (
        int(datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(mm)).total_seconds()))
    return converted_second

def generate_data_for_contributor_experience_user(pr_language="eng", rg_language="USA", country='United States of America', state='CA', city='Seatle', phone_prefix='415'):
    faker = Faker()
    name = faker.name().split(' ')
    # characters = list("abVd!123_45")
    # random.shuffle(characters)
    firstname = name[0].replace('.','')
    lastname = name[1]
    # email = "".join(['integration+', firstname.lower(), random.choice(characters), "@figure-eight.com"])
    # password = "".join(characters)
    address = faker.street_address()
    zipcode = faker.postcode()
    phone_number = phone_prefix+faker.phone_number()[2:]

    password = get_test_data('test_ui_account', 'password')
    _today = datetime.datetime.today()
    prefix = 'ce_' + _today.strftime("%Y%m%d") + "_" + str(random.randint(1000, 9999))
    email = "integration+" + prefix + "@figure-eight.com"

    user = {"email": email,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
            "primary_language": pr_language,
            "region_language": rg_language,
            "country": country,
            "state": state,
            "address": address,
            "city": city,
            "zipcode": zipcode,
            "phone_number": phone_number}
    return user

