"""
Create new contributor with Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import gevent

ENV = 'integration'
NEW_USER_URL = f'https://tasks.{ENV}.cf3.work/users/new'
PASSWORD = ""

TEAM_LIST = [*range(1, 20)]

RANGE = range(1, 1000)

CONCURRENCY = 2

HEADLESS = True


def main(team_id):

    options = webdriver.ChromeOptions()
    options.add_argument('--no-cache')
    options.add_argument('--window-size=1600,1200')
    if HEADLESS:
        options.add_argument('--headless')
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(chrome_options=options)

    wait = WebDriverWait(driver, 30)

    for user_id in RANGE:

        driver.delete_all_cookies()

        NEW_USERNAME = f'qa+performance+worker{team_id}+{user_id}@figure-eight.com'
        print(f'Creating {NEW_USERNAME}')

        driver.get(NEW_USER_URL)
        wait.until(EC.visibility_of_element_located((By.ID, "user-name")), "user-name").send_keys(NEW_USERNAME)
        wait.until(EC.visibility_of_element_located((By.ID, "user-email")), "user-email").send_keys(NEW_USERNAME)
        wait.until(EC.visibility_of_element_located((By.ID, "user_password")), "user_password").send_keys(PASSWORD)
        wait.until(EC.visibility_of_element_located((By.ID, "user_password_confirmation")), "user_password_confirmation").send_keys(PASSWORD)
        driver.execute_script("document.getElementById('terms').click()")
        driver.execute_script("document.getElementsByName('commit')[0].click()")
        gevent.sleep(3)
        if driver.find_elements('xpath',"//div[text()='has already been taken']"):
            print(f'Username {NEW_USERNAME} already taken')
            continue
        wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[text()='Sign In']")), "Signed UP")
        print(f'Created {NEW_USERNAME}')

    driver.quit()


if __name__ == '__main__':

    i = 0
    while i < len(TEAM_LIST):
        c_teams = (TEAM_LIST[i:i+CONCURRENCY])
        gevent.joinall([gevent.spawn(main, t) for t in c_teams])
        i += CONCURRENCY
