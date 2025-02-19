import json
import os
import time

from adap.api_automation.utils.data_util import DataTricks
from selenium import webdriver

def login(driver, user, user_password):

    email = driver.find_element('xpath','//input[@type="email"]')
    email.send_keys(user)

    password = driver.find_element('xpath','//input[@type="password"]')
    password.send_keys(user_password)

    driver.find_element('xpath','//input[@type="submit"]').click()

    time.sleep(2)

def logout(driver):
    driver.find_element('xpath','//div[@class="rebrand-DropdownButton rebrand-AccountLinkNew__accountMenu"]').click()
    driver.find_element('xpath','//a[text()="Sign Out"]').click()


def grab_api_key(driver, regenerate):
    driver.get(base_url+"account/api")
    time.sleep(1)
    if regenerate:
        driver.find_element('xpath',"//a[text()='Generate New']").click()
        time.sleep(1)
    api_key = driver.find_element('xpath',"//div[@class='b-ApiPage__field']").text
    return api_key


def find_key(driver,user_info, regenerate):
    user_name = user_info['email']
    user_password = user_info['password']
    login(driver, user_name, user_password)

    popover_content = driver.find_elements('xpath','//div[@class="rebrand-popover-content"]')
    if len(popover_content) > 0:
        popover_content[0].find_element('xpath',"./button[@class='rebrand-TourSteps__tourTipExit']").click()

    api_key = grab_api_key(driver, regenerate)
    return api_key

def main(env, regenerate=False):

    data = DataTricks(env)
    users_file = data.path_test_data + data.users_file

    global base_url
    base_url= 'https://client.%s.cf3.us/' % env

    with open(users_file, "r+") as read_file:
        users = json.load(read_file)

    file_updated = False

    for k,v in users.items():
        password = v.get('password', False)
        api_key = v.get('api_key', False)
        print(k)
        if not password or not api_key: continue
        print('...in progress')

        try:
            if password is not None and password != '' and api_key is not None:
                driver = webdriver.Chrome()
                driver.get(base_url)
                new_api_key = find_key(driver,v, regenerate)
                if new_api_key != api_key:
                    users[k]['api_key'] = new_api_key
                    file_updated = True
        except:
            print('ERROR')
        driver.quit()

    if file_updated:
        os.remove(users_file)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)

if __name__ == "__main__":
    main('sandbox', regenerate=False)

