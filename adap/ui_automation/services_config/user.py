import re
import time

import allure
import pytest
from selenium.webdriver.common.keys import Keys
from adap.support.gmail.gmail_support import get_invite_link
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.ui_automation.utils.js_utils import mouse_click_element
from adap.ui_automation.utils.page_element_utils import click_rebrand_popover
from adap.ui_automation.utils.selenium_utils import *
from adap.perf_platform.utils.logging import get_logger
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

log = get_logger(__name__)


class User:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.customer = Customer(self)
        self.contributor = Contributors(self)
        self.task = Tasks(self)
        self.user_id = None
        self.current_user = None

    def login_as_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Login as customer: %s' % user_name):
            self.customer.login_as(user_name, password)

    def switch_old_to_new_after_login_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Switch ui as customer: %s' % user_name):
            self.customer.switch_old_to_new_after_login(user_name, password)

    def switch_new_to_old_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Switch ui as customer: %s' % user_name):
            self.customer.switch_new_to_old(user_name, password)

    def switch_using_read_only_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Switch ui as customer: %s' % user_name):
            self.customer.switch_using_read_only(user_name, password)

    def login_as_failed_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Login as customer: %s' % user_name):
            self.customer.login_as_failed(user_name, password)

    def login_as_empty_email_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Login as customer: %s' % user_name):
            self.customer.login_as_empty_email(user_name, password)

    def login_as_empty_password_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Login as customer: %s' % user_name):
            self.customer.login_as_empty_password(user_name, password)

    def register_as_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_as(user_name, email, password, confirm_password)

    def register_name_special_char_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_name_special_char(user_name, email, password, confirm_password)

    def register_name_long_char_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_name_long_char(user_name, email, password, confirm_password)

    def register_name_only_space_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_name_only_space(user_name, email, password, confirm_password)

    def register_email_existing_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_email_existing(user_name, email, password, confirm_password)

    def register_password_not_meet_requirement_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_password_not_meet_requirement(user_name, email, password, confirm_password)

    def register_password_and_confirm_password_not_match(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_password_and_confirm_password_not_match(user_name, email, password, confirm_password)

    def register_all_fields_empty_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_all_fields_empty(user_name, email, password, confirm_password)

    def register_checkbox_not_ticked_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_checkbox_not_ticked(user_name, email, password, confirm_password)

    def register_incorrect_email_format_customer(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_incorrect_email_format(user_name, email, password, confirm_password)

    def register_as_click_tnc(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_click_tnc(user_name, email, password, confirm_password)

    def register_as_click_privacy(self, user_name=None, email=None, password=None, confirm_password=None, close_guide=True):
        with allure.step('Register as customer: %s' % user_name):
            self.customer.register_click_privacy(user_name, email, password, confirm_password)

    def forgot_password_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Forgot password as customer: %s' % user_name):
            self.customer.forgot_password(user_name, password)

    def forgot_password_email_not_registered_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Forgot password as customer: %s' % user_name):
            self.customer.forgot_password_email_not_registered(user_name, password)

    def forgot_password_click_continue_but_email_empty_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Forgot password as customer: %s' % user_name):
            self.customer.forgot_password_click_continue_email_empty(user_name, password)

    def forgot_password_click_signin_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Forgot password as customer: %s' % user_name):
            self.customer.forgot_password_click_signin(user_name, password)

    def forgot_password_invalid_email_format_customer(self, user_name=None, password=None, close_guide=True):
        with allure.step('Forgot password as customer: %s' % user_name):
            self.customer.forgot_password_invalid_email_format(user_name, password)

    def login_as_contributor(self, user_name=None, password=None):
        with allure.step('Login as contributor: %s' % user_name):
            self.contributor.login_as(user_name, password)
            self.current_user = user_name

    def login_as_contributor_tasks(self, user_name=None, password=None):
        with allure.step('Login as contributor (task page): %s' % user_name):
            create_screenshot(self.driver, "before_login")
            self.task.login_as(user_name, password)
            self.close_guide()
            self.current_user = user_name

    def logout(self):
        with allure.step('Logout '):
            if 'task-force' in self.app.driver.current_url:
                logout = self.driver.find_elements('xpath',
                    "//a[contains(@href, '/task-force/') and text()='Sign Out']")
                assert len(logout) > 0, "Sign Out button has not been found for task force"
                logout[0].click()
                time.sleep(5)
            elif ('client' in self.app.driver.current_url) or ('secure' in self.app.driver.current_url):
                self.app.mainMenu.account_menu()
                self.app.mainMenu.sign_out()
                time.sleep(1)
            elif 'annotate' in self.app.driver.current_url:
                self.contributor.logout()
            elif 'account' in self.app.driver.current_url:
                self.task.logout()
            self.current_user = None

    def close_guide(self):
        log.debug({
            'message': 'close_guide',
            'user_id': self.app.user.user_id})
        with allure.step('Close guide'):
            self.driver.implicitly_wait(0.5)

            click_rebrand_popover(self.driver)

            # try:
            #     task_completed = find_elements(self.driver,
            #                                    "//div[@id='initial-tour-guider']//div[@class='guiders_buttons_container']//a[text()='Close']")
            #     if len(task_completed) > 0:
            #         task_completed[0].click()
            # except:
            #     print("error tool_bar")

            home_alert = self.driver.find_elements('xpath',
                "//*[text()='Home']/..//*[local-name() = 'svg']")
            if len(home_alert) > 0:
                home_alert[0].click()

            try:
                welcome_alert = self.driver.find_elements('xpath',"//div[@id='initial-tour-guider']/div[1]//a")
                if len(welcome_alert) > 0:
                    welcome_alert[0].click()
            except:
                print("error welcome_alert")

            try:
                tool_bar = self.driver.find_elements('xpath',"//div[@id='tour-toolbar']//a")
                if len(tool_bar) > 0:
                    tool_bar[-1].click()
            except:
                print("error tool_bar")

            self.driver.implicitly_wait(7)

    def reset_password(self, user_name=None, password=None):
        pass

    def verify_user_name(self, username):
        with allure.step('Verify username: %s' % username):
            time.sleep(2)

            if ('client' in self.app.driver.current_url) or ('secure' in self.app.driver.current_url):
                el = self.app.driver.find_elements('xpath',
                    "//h5[text()='Username/Team:']/..//a[text()='%s']" % username)
            elif 'annotate' in self.app.driver.current_url:
                # contributors or tasks page
                # el = self.app.driver.find_elements('xpath',"//button//span[contains(.,'%s')]" % username)
                el = find_elements(self.driver, "//button//span[contains(.,'%s')]" % username)

            elif 'account' in self.app.driver.current_url or 'view' in self.app.driver.current_url:
                # contributors or tasks page
                el = self.app.driver.find_elements('xpath',
                    "//li[@class='dropdown account-links']/a[text()='%s ']" % username)

            assert len(el) > 0, " Username %s is not displayed on the page" % username

    def verify_user_team_name(self, user_name=None, do_assert=True):
        with allure.step('Verify user Team name: %s' % user_name):
            el = self.app.driver.find_elements('xpath',
                "//h5[text()='Team:']/..//span[contains(text(),'%s')]" % user_name)
            total_el = len(el)
            if do_assert:
                assert total_el > 0, " Team %s is not displayed on the page" % user_name
            else:
                return total_el > 0

    def switch_user_team(self, user_name=None):
        self.app.mainMenu.account_menu()
        el = find_element(self.driver, "//span[text()='%s']" % user_name)
        mouse_click_element(self.app.driver, el)

    def get_jobs_by_api_key(self, api_key, team_id=None):
        with allure.step('Get jobs by api key: %s' % api_key):
            _job = JobAPI(api_key)
            jobs_list = []
            page = 1
            findJobs = True
            # jobs = _job.get_jobs_for_user()
            # count_job = len(jobs.json_response)

            while findJobs:
                jobs = _job.get_jobs_for_user(page, team_id)
                count_job = len(jobs.json_response)

                if count_job == 0:
                    findJobs = False
                    return jobs_list

                for current_job in jobs.json_response:
                    jobs_list.append(current_job['id'])
                page += 1

            return jobs_list

    def verify_new_account(self, address, env):
        time.sleep(10)
        urls = get_invite_link(address, env)
        assert len(urls) > 0, 'No invite link found'

        driver = set_up_driver()
        driver.get(urls[0])

        time.sleep(4)
        driver.quit()

    def invite_user(self, user_email):
        with allure.step('Invite new user: %s' % user_email):
            find_element(self.driver, "//input[@name='email']").send_keys(user_email)
            find_element(self.driver, "//a[text()='Send Invite']").click()
            time.sleep(3)
            find_element(self.driver, "//a[text()='Invite']").click()
            time.sleep(3)
            self.driver.refresh()
            time.sleep(2)

    def activate_invited_user(self, user_name, user_email, user_password):
        with allure.step('Activate new user being invited: %s' % user_email):
            find_element(self.driver, "//input[@id='user-name']").send_keys(user_name)
            find_element(self.driver, "//input[@id='user-email']").send_keys(user_email)
            find_element(self.driver, "//input[@name='user[password]']").send_keys(user_password)
            try:
                find_element(self.driver, "//input[@name='user[password_confirmation]']").send_keys(user_password)
            except:
                print("no password confirmation")

            try:
                find_element(self.driver, "//input[@name='terms']/..").click()
            except:
                print("no Terms checkbox")

            find_element(self.driver, "//input[@value='Create Account' or @value='Create Free Account']").click()
            time.sleep(2)

    def remove_user_from_team(self, email):
        with allure.step('Remove user %s from team' % email):
            user_found = False
            current_page = None
            next_page = ""
            try:
                while not user_found and current_page != next_page:
                    current_page = self.driver.page_source
                    user = self.driver.find_elements('xpath',"//tr[.//td[text()='%s']]" % email)
                    if len(user) > 0:
                        user_found = True
                        user[0].find_element('xpath',
                            ".//td[.//span[text()='Remove']]//*[local-name() = 'svg']").click()
                        time.sleep(2)
                        find_element(self.driver, "//a[text()='Yes']").click()
                        time.sleep(2)
                        self.driver.refresh()
                        time.sleep(3)
                    else:
                        find_element(self.driver, "//li[contains(@class, 'b-Pagination__Next')]").click()
                        time.sleep(2)
                        next_page = self.driver.page_source
            except:
                print("Something went wrong!")

    def search_user(self, user):
        with allure.step(f'Search user: {user}'):
            search_field = find_element(self.driver, "//input[@id='query']")
            search_field.clear()
            time.sleep(4)
            search_field.send_keys(user, Keys.RETURN)
            time.sleep(4)

    def create_new_team(self, team_name, user):
        with allure.step('Create new team for user: %s' % user):
            self.search_user(user=user)
            current_team = self.driver.find_elements('xpath',"//td[text()='N/A (no team)']")
            if len(current_team) > 0:
                find_element(self.driver, "//a[text()='Upgrade']").click()
                find_element(self.driver, "//input[@id='organization-name']").send_keys(team_name)
                find_element(self.driver, "//a[@id='create-organization']").click()
                time.sleep(4)

    def search_user_and_go_to_team_page(self, user, team_id):
        with allure.step('Search user and go to his team page'):
            self.search_user(user=user)
            current_team = self.driver.find_elements('xpath',"//a[contains(@href, '/admin/teams/%s')]" % team_id)
            if len(current_team) > 0:
                current_team[0].click()
            time.sleep(2)

    def click_edit_team(self):
        with allure.step('Click pencil to edit team'):
            edit_btn = find_element(self.driver, "//a[@class='b-team-details__edit']")
            edit_btn.click()
            time.sleep(3)

    def click_edit_user(self, user):
        with allure.step('Click pencil to edit user'):
            edit_btn = find_element(self.driver, f"//td[contains(text(), '{user}')]/..//*[@id='edit']")
            edit_btn.click()
            time.sleep(3)

    def get_value_for_team(self, category):
        with allure.step('Get current value %s' % category):
            current_value = find_element(self.driver, "//input[@name='%s']" % category)
            time.sleep(1)
            return current_value.get_attribute('value')

    def update_value_for_team(self, category, new_value):
        with allure.step('Update team name to be new name %s' % category):
            input_textbox = find_element(self.driver, "//input[@name='%s']" % category)
            input_textbox.clear()
            input_textbox.send_keys(new_value)
            time.sleep(2)

    def update_role_for_team(self, role, value):
        with allure.step('Set up team role %s' % role):
            current_value = self.driver.find_element('xpath',"//*[(text()='%s')]/..//input" % role)
            if current_value.is_selected() != value:
                checkbox = self.driver.find_element('xpath',"//*[(text()='%s')]/..//label" % role)
                checkbox.click()

    def update_team_plan(self, new_plan):
        with allure.step('Update team plan to be new plan %s' % new_plan):
            current_plan = find_element(self.driver, "//label[text()='Plan']/..//div[text()]")
            print("current plan is:", current_plan.text)
            current_plan.click()
            plan = find_elements(self.driver,
                                 "//li[text()='%s']" % new_plan)
            assert len(plan), "Plan %s has not been found" % new_plan
            time.sleep(2)
            plan[0].click()
            time.sleep(2)

    def get_team_plan(self):
        with allure.step('Get team plan to be new plan %s'):
            current_plan = find_element(self.driver, "//label[text()='Plan']/..//div[text()]")
            return current_plan.text

    def update_feature_flag_or_additional_role(self, role):
        with allure.step('Update team feature flag and additional role'):
            self.app.navigation.click_checkbox_by_text(role)
            time.sleep(2)

    # this is for fed, to get user plan name
    def get_user_plan_name_for_fed(self):
        with allure.step('Get user plan name'):
            find_element(self.driver, "//a[contains(@href, '/make/admin/users')]//*[local-name()='svg']").click()
            time.sleep(2)
            user_plan = find_element(self.driver, "//input[@name='paidPlan']")
            return user_plan.get_attribute('value')

    # this is for fed, get team plan on team edit page
    def get_team_plan_name_for_fed(self):
        with allure.step('Get team plan name'):
            find_elements(self.driver, "//a[contains(@href, '/make/admin/teams')]")[1].click()
            time.sleep(2)
            team_plan = find_element(self.driver, "//div[@id='s2id_akon_team_plan']//span[text()]")
            return team_plan.text

    def add_paypal_account(self, paypal_account, password):
        with allure.step('Link Paypal account to user'):
            profile_window = self.driver.window_handles[0]

            self.app.navigation.click_link('Connect')

            paypal_window = self.driver.window_handles[1]
            self.app.navigation.switch_to_window(paypal_window)

            self.driver.find_element('xpath',"//input[@id='email']").send_keys(paypal_account)

            self.driver.find_element('xpath',"//button[@id='btnNext']").click()
            self.driver.find_element('xpath',"//input[@id='password']").send_keys(password)
            self.driver.find_element('xpath',"//button[@id='btnLogin']").click()
            time.sleep(3)

            self.app.navigation.switch_to_window(profile_window)


class Customer:

    def __init__(self, user):
        self.app = user.app
        self.driver = self.app.driver
        if self.app.env == 'hipaa':
            self.URL = 'https://client.nxxgpxhq0rum22cd.staging.cf3.us/'
        elif self.app.env == 'fed':
            if pytest.customize_fed == 'true':
                self.URL = "https://" + pytest.customize_fed_url + "/make/sessions/new"
            else:
                self.URL = 'https://app.%s.secure.cf3.us/make/sessions/new' % pytest.env_fed
        else:
            self.URL = 'https://client.%s.cf3.us/' % self.app.env

    def login(self, user_name, password, submit=True):
        # time.sleep(5)

        create_screenshot(self.driver, "login")

        # try:
        #     self.driver.find_element('xpath',"//button[@id='details-button']").click()
        #     self.driver.find_element('xpath',"//a[@id='proceed-link']").click()
        # except:
        #     print("login")

        email = find_element(self.driver, '//input[@name="email"]')
        email.send_keys(user_name)
        create_screenshot(self.driver, "login_email")


        try:
            self.app.navigation.click_btn('Continue')
            create_screenshot(self.driver, "login_Continue")
        except:
            print("no Continue button")

        password_field = find_element(self.driver, '//input[@name="password"]')
        password_field.send_keys(password)
        create_screenshot(self.driver, "password_field")

        if submit:
            find_element(self.driver, '//a[text()="Sign In"]').click()
            time.sleep(5)
            create_screenshot(self.driver, "password_submit")

            click_rebrand_popover(self.driver)

            rebrand_flashalert = self.driver.find_elements('xpath',
                "//div[contains(@class, 'rebrand-Flashlert')]//*[local-name() = 'svg']")
            if len(rebrand_flashalert) > 0: rebrand_flashalert[1].click()

    def login_as(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            create_screenshot(self.driver, "login_as")
            go_to_page(self.driver, self.URL)
            create_screenshot(self.driver, "login_as2")
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//a[text()="Sign In"]').click()
            time.sleep(20)
            element_login = find_element(self.driver, '//h1[text()="Home"]')
            assert element_login.text == 'Home'

    def login_as_failed(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//a[text()="Sign In"]').click()

    def login_as_empty_email(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//a[@href="/sessions/new"]').click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.click()

    def login_as_empty_password(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            find_element(self.driver, '//a[@href="/sessions/new"]').click()
            email = find_element(self.driver, '//input[@name="password"]')
            email.click()

    def register_as(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.send_keys(email)
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            confirm_password_field = find_element(self.driver, '//input[@name="confirmPassword"]')
            confirm_password_field.send_keys(confirm_password)
            checkbox = find_element(self.driver, '//*[@type="checkbox"]/parent::*/label[1]')
            checkbox.click()
            #find_element(self.driver, '//*[text()="Home"]/..//*[local-name() = "svg"]').click()
            find_element(self.driver, '//a[text()="Sign Up"]').click()

    def register_name_special_char(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            time.sleep(10)
            special_character_error = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[4]/div[1]/div[1]/div/div')
            assert special_character_error.text == "Name can only contain letters, spaces, '-' and '_'"

    def register_name_long_char(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            time.sleep(10)
            special_character_error = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[4]/div[1]/div[1]/div/div')
            assert special_character_error.text == 'Name must be at most 30 characters long'

    def register_name_only_space(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            time.sleep(10)
            special_character_error = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[4]/div[1]/div[1]/div/div')
            assert special_character_error.text == 'Name must be at least 6 characters long'

    def register_email_existing(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.send_keys(email)
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            confirm_password_field = find_element(self.driver, '//input[@name="confirmPassword"]')
            confirm_password_field.send_keys(confirm_password)
            checkbox = find_element(self.driver, '//*[@type="checkbox"]/parent::*/label[1]')
            checkbox.click()
            find_element(self.driver, '//a[text()="Sign Up"]').click()

    def register_password_not_meet_requirement(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.click()
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            time.sleep(10)
            special_character_error = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[4]/div[1]/div[3]/div/div')
            assert special_character_error.text == 'Password must be at least 12 characters long'

    def register_password_and_confirm_password_not_match(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.click()
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            confirm_password_field = find_element(self.driver, '//input[@name="confirmPassword"]')
            confirm_password_field.send_keys(confirm_password)
            name = find_element(self.driver, '//input[@name="name"]')
            name.click()
            time.sleep(10)
            special_character_error = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[4]/div[1]/div[4]/div/div')
            assert special_character_error.text == 'Passwords must match'

    def register_all_fields_empty(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.click()
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.click()
            confirm_password_field = find_element(self.driver, '//input[@name="confirmPassword"]')
            confirm_password_field.click()
            checkbox = find_element(self.driver, '//*[@type="checkbox"]/parent::*/label[1]')
            checkbox.click()
            find_element(self.driver, '//a[text()="Sign Up"]').click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.click()

    def register_checkbox_not_ticked(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.send_keys(email)
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            confirm_password_field = find_element(self.driver, '//input[@name="confirmPassword"]')
            confirm_password_field.send_keys(confirm_password)
            find_element(self.driver, '//a[text()="Sign Up"]').click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.click()

    def register_incorrect_email_format(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            name = find_element(self.driver, '//input[@name="name"]')
            name.send_keys(user_name)
            email_field = find_element(self.driver, '//input[@name="email"]')
            email_field.send_keys(email)
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.click()
            time.sleep(10)
            special_character_error = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[4]/div[1]/div[2]/div/div')
            assert special_character_error.text == 'Email Address must be a valid email'

    def register_click_tnc(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            find_element(self.driver, '//a[text()="Terms of Service"]').click()
            # Store the original window handle
            original_window = self.driver.current_window_handle
            # Wait for the new tab to open
            #WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            # Switch to the new tab
            new_window = [window for window in self.driver.window_handles if window != original_window][0]
            self.driver.switch_to.window(new_window)
            time.sleep(10)
            # Perform the assertion
            element_tnc = find_element(self.driver, '//h1[text()="Appen contributor portal"]')
            assert element_tnc.text == 'Appen contributor portal'
            # Close the new tab and switch back to the original tab
            self.driver.close()
            self.driver.switch_to.window(original_window)

    def register_click_privacy(self, user_name=None, email=None, password=None, confirm_password=None):
        with allure.step("Register as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            sign_up_button = find_element(self.driver, '//a[text()="Sign Up"]')
            sign_up_button.click()
            find_element(self.driver, '//a[text()="Privacy Policy"]').click()
            # Store the original window handle
            original_window = self.driver.current_window_handle
            # Wait for the new tab to open
            #WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            # Switch to the new tab
            new_window = [window for window in self.driver.window_handles if window != original_window][0]
            self.driver.switch_to.window(new_window)
            time.sleep(10)
            # Perform the assertion
            element_privacy_policy = find_element(self.driver, '//h1[text()="Privacy Statement"]')
            assert element_privacy_policy.text == 'Privacy Statement'
            # Close the new tab and switch back to the original tab
            self.driver.close()
            self.driver.switch_to.window(original_window)

    def forgot_password(self, user_name=None, password=None):
        with allure.step("Forgot password as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            find_element(self.driver, '//a[text()="Forgot Password?"]').click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            back_to_sign_in_button = find_element(self.driver, '//a[text()="Back to Sign In"]')
            back_to_sign_in_button.click()

    def forgot_password_email_not_registered(self, user_name=None, password=None):
        with allure.step("Forgot password as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            find_element(self.driver, '//a[text()="Forgot Password?"]').click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            back_to_sign_in_button = find_element(self.driver, '//a[text()="Back to Sign In"]')
            back_to_sign_in_button.click()

    def forgot_password_click_continue_email_empty(self, user_name=None, password=None):
        with allure.step("Forgot password as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            find_element(self.driver, '//a[text()="Forgot Password?"]').click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.click()

    def forgot_password_click_signin(self, user_name=None, password=None):
        with allure.step("Forgot password as customer %s " % (user_name)):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            find_element(self.driver, '//a[text()="Forgot Password?"]').click()
            sign_in_button = find_element(self.driver, '//a[text()="Sign In"]')
            sign_in_button.click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.click()

    def forgot_password_invalid_email_format(self, user_name=None, password=None):
        with (allure.step("Forgot password as customer %s " % (user_name))):
            go_to_page(self.driver, self.URL)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            time.sleep(5)
            find_element(self.driver, '//a[text()="Forgot Password?"]').click()
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            time.sleep(10)
            invalid_email_format_error_message = find_element(self.driver, '//div[text()="Email Address must be a valid email"]')
            assert invalid_email_format_error_message.text == 'Email Address must be a valid email'

    def switch_old_to_new_after_login(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            create_screenshot(self.driver, "switch_ui")
            go_to_page(self.driver, self.URL)
            create_screenshot(self.driver, "switch_ui2")
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//a[text()="Sign In"]').click()
            time.sleep(10)
            find_element(self.driver, '//*[text()="Home"]/..//*[local-name() = "svg"]').click()
            self.driver.implicitly_wait(10)
            for attempt in range(5):
                try:
                    new_theme = find_element(self.driver, '//ul[@data-test-id="global-nav"]/following-sibling::a')
                    click_by_java_script(self.driver, new_theme)
                    return True  # Click successful
                except StaleElementReferenceException:
                    pass
            time.sleep(10)
            element_profile_dropdown = find_element(self.driver, '//*[@id="app"]/div[2]/div/header/div/div[2]/div/ul')
            assert element_profile_dropdown is not None, "Profile dropdown is there"

    def switch_new_to_old(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            self.driver.implicitly_wait(10)
            for attempt in range(5):
                try:
                    new_theme = find_element(self.driver, '//ul[@data-test-id="global-nav"]/following-sibling::a')
                    click_by_java_script(self.driver, new_theme)
                    return True  # Click successful
                except StaleElementReferenceException:
                    pass
            time.sleep(10)
            element_profile_sidebar = find_element(self.driver,'//*[@id="app"]/div[2]/div/div[1]/div/ul/div/div/div/div')
            assert element_profile_sidebar is not None, "Profile sidebar is there"

    def switch_using_read_only(self, user_name=None, password=None):
        with allure.step("Login as customer %s " % (user_name)):
            create_screenshot(self.driver, "switch_ui")
            go_to_page(self.driver, self.URL)
            create_screenshot(self.driver, "switch_ui2")
            time.sleep(10)
            element_profile_sidebar = find_element(self.driver,'//*[@id="app"]/div[2]/div/div[1]/div/ul/div/div/div/div')
            element_profile_sidebar.click()
            time.sleep(10)
            logout_old = find_element(self.driver, '//*[@id="app"]/div[2]/div/div[1]/div/ul/div/div/ul/li[17]/a')
            logout_old.click()
            time.sleep(10)
            email = find_element(self.driver, '//input[@name="email"]')
            email.send_keys(user_name)
            continue_button = find_element(self.driver, '//a[text()="Continue"]')
            continue_button.click()
            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//a[text()="Sign In"]').click()
            self.driver.implicitly_wait(10)
            for attempt in range(5):
                try:
                    new_theme = find_element(self.driver, '//ul[@data-test-id="global-nav"]/following-sibling::a')
                    click_by_java_script(self.driver, new_theme)
                    return True  # Click successful
                except StaleElementReferenceException:
                    pass
            time.sleep(10)
            element_profile_dropdown = find_element(self.driver, '//*[@id="app"]/div[2]/div/header/div/div[2]/div/ul')
            assert element_profile_dropdown is not None, "Profile dropdown is there"
            self.driver.implicitly_wait(10)
            for attempt in range(5):
                try:
                    new_theme = find_element(self.driver, '//ul[@data-test-id="global-nav"]/following-sibling::a')
                    click_by_java_script(self.driver, new_theme)
                    return True  # Click successful
                except StaleElementReferenceException:
                    pass
            time.sleep(10)
            element_profile_sidebar = find_element(self.driver,'//*[@id="app"]/div[2]/div/div[1]/div/ul/div/div/div/div')
            assert element_profile_sidebar is not None, "Profile sidebar is there"

    def open_home_page(self):
        with allure.step("Open home page"):
            go_to_page(self.driver, self.URL)
            time.sleep(2)

    def go_to_specific_page(self, custom_url):
        with allure.step("Going to a Custom URL"):
            go_to_page(self.driver, self.URL + custom_url)

    def get_customer_api_key(self):
        with allure.step('Get customer API Key'):
            self.driver.implicitly_wait(10)
            if '/account/api' in self.driver.current_url:
                try:
                    return get_text_by_xpath(self.driver,
                                             "//div[div[@class='b-ApiKeyInfo__type' and text()='Api']]//div[@class='b-ApiPage__field' or @class='b-ApiKeyInfo__key']")
                except:
                    return get_text_by_xpath(self.driver, "//h3[text()='API Key']/..//div[text()]")

            else:
                try:
                    go_to_page(self.driver, self.URL + 'account/api')
                    api_key = get_text_by_xpath(self.driver, "//div[@class='b-ApiPage__field']")
                    return api_key
                except:
                    assert False, "API KEY has not been found"

    def reset_password(self, current_password, new_password):
        self.driver.find_element('xpath',"//input[@name='currentPassword']").send_keys(current_password)
        self.driver.find_element('xpath',"//input[@name='newPassword']").send_keys(new_password)
        self.driver.find_element('xpath',"//input[@name='confirmPassword']").send_keys(new_password)
        self.app.navigation.click_link('Update')

    # fed cf_internal user go to contributor admin to generate reset password link
    def generate_reset_password_link(self, user_email):
        self.driver.find_element('xpath',"//input[@name='email']").send_keys(user_email)
        self.app.navigation.click_btn('Generate Link')
        pwd = self.app.driver.find_element('xpath',"//input[@name='link']")
        pwd_link = pwd.get_attribute('value')
        return pwd_link

    def reset_password_by_link(self, new_password):
        self.driver.find_element('xpath',"//input[@id='user_password']").send_keys(new_password)
        self.driver.find_element('xpath',"//input[@id='user_password_confirmation']").send_keys(new_password)
        self.driver.find_element('xpath',"//input[@value='Submit']").click()
        time.sleep(5)


class Contributors:

    def __init__(self, user):
        self.app = user.app
        self.driver = self.app.driver
        self.URL = 'https://annotate.%s.cf3.us/' % self.app.env

    def open_home_page(self):
        with allure.step("Open home page (contributor)"):
            go_to_page(self.driver, self.URL)
            time.sleep(2)

    def login(self, user_name, password):
        email = find_element(self.driver, '//input[@name="email" or @name="username"]')
        email.send_keys(user_name)
        time.sleep(1)
        password_field = find_element(self.driver, '//input[@name="password"]')
        password_field.send_keys(password)
        find_element(self.driver, '//*[contains(@class, "b-Login__submit-button") or @name="login"]').click()
        time.sleep(5)

    def login_as(self, user_name=None, password=None):
        with allure.step("Login at %s as %s " % (user_name, self.URL)):
            go_to_page(self.driver, self.URL)
            time.sleep(2)
            ac_page = find_elements(self.driver, "//h1[text()='New unified login!']")
            if len(ac_page) > 0:
                find_element(self.driver, "//a[text()='Continue to Sign In']").click()

            self.login(user_name, password)
            time.sleep(3)
            self.rebranded_alert()
            self.close_guide(self.driver)

    def close_guide(self, driver=None):
        driver = self.driver if not driver else driver
        driver.switch_to.frame(0)
        skip_btn = driver.find_elements('xpath',"//*[text()='Skip Tour']")
        if len(skip_btn) > 0:
            skip_btn[0].click()
        driver.switch_to.default_content()

    def skip_for_now_popup(self, driver=None):
        driver = self.driver if not driver else driver
        driver.switch_to.frame(0)
        skip_btn = driver.find_elements('xpath',"//*[text()='Skip For Now?']/../..//div[text()='Skip For Now']")
        if len(skip_btn) > 0:
            skip_btn[0].click()
        driver.switch_to.default_content()

    def alert_window(self):
        flash_alert_window = find_elements(self.app.driver,
                                           "//div[@class='b-FlashAlert b-PromoAlert b-FlashAlert--warning']//*[local-name() = 'svg']")
        if len(flash_alert_window) > 0:
            flash_alert_window[0].click()
            time.sleep(1)

    @allure.step('Open user menu')
    def open_user_menu(self):
        locator = "//button[@type='button']/span"
        click_element_by_xpath(
            self.driver,
            locator,
            f"User menu has not been found, locator: {locator}"
        )

    @allure.step('Open payments menu')
    def open_payments_menu(self):
        locator = "//span[@class='b-HeaderDollarSign']"
        click_element_by_xpath(
            self.driver,
            locator,
            f"User payments menu has not been found, locator: {locator}"
        )

    @allure.step('Get available for withdraw balance')
    def get_withdraw_balance(self):
        locator = "//span[@class='b-HeaderPaymentsPopover__Balance']"

        return get_text_by_xpath(self.driver, locator)

    @allure.step('Get pending payment balance')
    def get_pending_payment_balance(self):
        locator = "//span[@class='b-HeaderPaymentsPopover__Money']"

        return get_text_by_xpath(self.driver, locator)

    @allure.step('Fill out account profile settings')
    def fill_out_profile_settings(self, data=None):
        if not data:
            log.info('There is no profile data provided')
            return

        field_mapping = {
            'fullname': ("//input[@name='name']", lambda v: send_keys_by_xpath(self.driver, v, data['fullname'], True)),
            'address': (
            "//input[@name='address']", lambda v: send_keys_by_xpath(self.driver, v, data['address'], True)),
            'city': ("//input[@name='city']", lambda v: send_keys_by_xpath(self.driver, v, data['city'], True)),
            'zipcode': (
            "//input[@name='zipCode']", lambda v: send_keys_by_xpath(self.driver, v, data['zipcode'], True)),
            'country': (
                "//h5[contains(text(), 'Address')]/..//div[contains(@class,'Select-control')]//input",
                lambda v: click_and_send_keys_by_xpath(self.driver, v, (data['country'], Keys.ENTER)),
            ),
            'gender': (
                {
                    'male': "//input[@id='male']",
                    'female': "//input[@id='female']",
                    'other': "//input[@id='other']",
                },
                lambda v: click_element_by_xpath(self.driver, v[data['gender'].lower()]),
            ),
            'month_of_birth': (
                "(//h5[contains(text(), 'Date of birth')]/..//div[contains(@class,'Select-control')])[1]",
                lambda v: (
                    click_element_by_xpath(self.driver, v),
                    click_element_by_xpath(
                        self.driver,
                        f"//div[contains(@class,'Select-menu-outer')]//*[contains(text(), '{data['month_of_birth']}')]"
                    )
                ),
            ),
            'day_of_birth': (
                "(//h5[contains(text(), 'Date of birth')]/..//div[contains(@class,'Select-control')])[2]",
                lambda v: (
                    click_element_by_xpath(self.driver, v),
                    click_element_by_xpath(
                        self.driver,
                        f"//div[contains(@class,'Select-menu-outer')]//*[contains(text(), '{data['day_of_birth']}')]"
                    )
                ),
            ),
            'year_of_birth': (
                "(//h5[contains(text(), 'Date of birth')]/..//div[contains(@class,'Select-control')])[3]",
                lambda v: (
                    click_element_by_xpath(self.driver, v),
                    click_element_by_xpath(
                        self.driver,
                        f"//div[contains(@class,'Select-menu-outer')]//*[contains(text(), '{data['year_of_birth']}')]"
                    )
                ),
            ),
        }

        for field, (xpath, action) in field_mapping.items():
            if field in data:
                action(xpath)

    @allure.step('Fill out additional information')
    def fill_out_additional_information(self, data=None):
        if not data:
            log.info('There is no additional information provided')
            return

        self.driver.switch_to.frame(0)
        field_mapping = {
            'first_name': (
            "//input[@name='firstName']", lambda v: send_keys_by_xpath(self.driver, v, data['fullname'], True)),
            'last_name': (
            "//input[@name='lastName']", lambda v: send_keys_by_xpath(self.driver, v, data['last_name'], True)),
            'primary_language': ("//div[@id='primaryLanguage']",
                                 lambda v: (
                                     click_element_by_xpath(self.driver, v, timeout=0.5),
                                     send_keys_by_xpath(self.driver, f'{v}//input',
                                                        (data['primary_language'], Keys.ENTER))
                                 )
                                 ),
            'language_region': ("//div[@id='languageRegion']",
                                lambda v: (
                                    click_element_by_xpath(self.driver, v, timeout=0.5),
                                    send_keys_by_xpath(self.driver, f'{v}//input',
                                                       (data['language_region'], Keys.ENTER))
                                )
                                ),
            'country': ("//div[@id='country']",
                        lambda v: (
                            click_element_by_xpath(self.driver, v, timeout=0.5),
                            send_keys_by_xpath(self.driver, f'{v}//input', (data['country'], Keys.ENTER))
                        )
                        ),
            'state': ("//div[@id='state']",
                      lambda v: (
                          click_element_by_xpath(self.driver, v, timeout=0.5),
                          send_keys_by_xpath(self.driver, f'{v}//input', (data['state'], Keys.ENTER))
                      )
                      ),
            'city': ("//input[@name='city']", lambda v: send_keys_by_xpath(self.driver, v, data['city'], True)),
            'full_address': (
            "//textarea[@name='address']", lambda v: send_keys_by_xpath(self.driver, v, data['full_address'], True)),
            'postal_code': (
            "//input[@name='zipcode']", lambda v: send_keys_by_xpath(self.driver, v, data['postal_code'], True)),
            'phone': ("//input[@id='phoneNumber']", lambda v: send_keys_by_xpath(self.driver, v, data['phone'], True)),
        }

        for field, (xpath, action) in field_mapping.items():
            if field in data:
                action(xpath)

        self.driver.switch_to.default_content()

    @allure.step('Get account profile settings')
    def get_profile_settings(self):
        date_of_birth_locator = \
            "(//h5[contains(text(), 'Date of birth')]/..//div[contains(@class,'Select-control')])[{}]"

        def get_gender():
            male = (get_attribute_by_xpath(self.driver, "//input[@id='male']", 'checked'), 'Male')
            female = (get_attribute_by_xpath(self.driver, "//input[@id='female']", 'checked'), 'Female')
            other = (get_attribute_by_xpath(self.driver, "//input[@id='other']", 'checked'), 'Other')
            genders = (male, female, other)

            return next((g[1] for g in genders if g[0] is not None), None)

        data = {
            'fullname': get_attribute_by_xpath(self.driver, "//input[@name='name']", 'value'),
            'month_of_birth': get_text_by_xpath(self.driver, date_of_birth_locator.format(1)),
            'day_of_birth': int(get_text_by_xpath(self.driver, date_of_birth_locator.format(2))),
            'year_of_birth': int(get_text_by_xpath(self.driver, date_of_birth_locator.format(3))),
            'gender': get_gender(),
            'address': get_attribute_by_xpath(self.driver, "//input[@name='address']", 'value'),
            'city': get_attribute_by_xpath(self.driver, "//input[@name='city']", 'value'),
            'zipcode': int(get_attribute_by_xpath(self.driver, "//input[@name='zipCode']", 'value')),
            'country': get_text_by_xpath(
                self.driver,
                "//h5[contains(text(), 'Address')]/..//div[contains(@class,'Select-control')]"
            ),
        }

        return data

    def logout(self):
        self.open_user_menu()
        sign_out_btn = self.driver.find_elements('xpath',"//a[@class='b-UserInfo__signOutLink']")
        assert len(sign_out_btn) > 0, "Sign Out button has not been found"
        sign_out_btn[0].click()

    def open_first_available_job_from_task_wall(self):
        jobs = self.driver.find_elements('xpath',"//tbody//tr")
        assert len(jobs) > 0, "Available jobs have not been found"

        jobs[0].find_element('xpath',".//a").click()

        window_after = self.driver.window_handles[1]
        self.app.navigation.switch_to_window(window_after)

    def open_job_contains_text(self, text):
        self.driver.switch_to.frame(0)
        jobs = self.driver.find_elements('xpath',"//tbody//tr")
        assert len(jobs) > 0, "Available jobs have not been found"

        job_elements = list(filter(lambda x: str(text) in x.text, jobs))
        assert len(job_elements) > 0, "Can not find job"

        job_elements[0].find_element('xpath',".//a").click()

    def get_job_url_by_text(self, text):
        # find a job that contains a text and return its url
        self.open_job_contains_text(text)

        window_after = self.driver.window_handles[1]
        self.app.navigation.switch_to_window(window_after)
        url = self.driver.current_url

        self.driver.close()

        return url

    def rebranded_alert(self):
        rebranded_alert_el = find_elements(self.driver,
                                           "//div[@class='b-RebrandedModal__container']//h3[text()='Welcome Back!']")
        if rebranded_alert_el:
            self.app.navigation.click_bytext('Close')

    @allure.step('Get available jobs amount from the page')
    def get_available_jobs_amount(self):
        self.driver.switch_to.frame(0)
        rows = find_elements(self.driver, "//h1[contains(text(), 'Available Jobs')]/../..//tr")
        self.driver.switch_to.default_content()

        # first row is a table header, so skip it
        return len(rows[1:])

    @allure.step('Get available jobs amount from the page')
    def sort_jobs_by(self, by):
        self.driver.switch_to.frame(0)
        click_element_by_xpath(self.driver, f"//th[contains(text(), {by})]")
        self.driver.switch_to.default_content()
        time.sleep(1)


class Tasks:

    def __init__(self, user):
        self.app = user.app
        self.driver = self.app.driver
        if self.app.env == 'hipaa':
            self.URL = 'https://account.nxxgpxhq0rum22cd.staging.cf3.us/'
        elif self.app.env == 'fed':
            if pytest.customize_fed == 'true':
                self.URL = "https://" + pytest.customize_fed_url + "/task-force/sessions/new"
            else:
                self.URL = 'https://app.%s.secure.cf3.us/task-force/sessions/new' % pytest.env_fed
        else:
            self.URL = 'https://account.%s.cf3.us/' % self.app.env

    def open_home_page(self):
        with allure.step("Open home page (account)"):
            go_to_page(self.driver, self.URL)
            time.sleep(2)

    def login(self, user_name, password):
        ac_page = find_elements(self.driver, "//a[@href='https://connect.appen.com/qrp/public/home']")
        if len(ac_page) > 0:
            create_screenshot(self.driver, "login")

            email = find_element(self.driver, '//input[@name="username"]')
            email.send_keys(user_name)
            time.sleep(1)

            password_field = find_element(self.driver, '//input[@name="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//*[@type="submit"]').click()
            time.sleep(2)
        else:
            create_screenshot(self.driver, "login")
            email = find_element(self.driver, '//input[@type="email"]')
            email.send_keys(user_name)
            cont = find_elements(self.driver, '//*[@id="continue_button"]')
            if len(cont) > 0:
                cont[0].click()

            password_field = find_element(self.driver, '//input[@type="password"]')
            password_field.send_keys(password)
            find_element(self.driver, '//*[@type="submit"]').click()
            time.sleep(3)
        create_screenshot(self.driver, "after_login")
        User(self.app).close_guide()

    def login_as(self, user_name=None, password=None):
        with allure.step("Login at %s as %s " % (user_name, self.URL)):
            go_to_page(self.driver, self.URL)
            create_screenshot(self.driver, "open_url")
            time.sleep(2)
            # ac_page = find_elements(self.driver, "//a[@herf='https://connect.appen.com/qrp/public/home']")
            # if len(ac_page) > 0:
            #     email = find_element(self.driver, '//input[@name="username"]')
            #     email.send_keys(user_name)
            #     time.sleep(1)
            #
            #     password_field = find_element(self.driver, '//input[@name="password"]')
            #     password_field.send_keys(password)
            #     find_element(self.driver, '//*[@type="submit"]').click()
            #     time.sleep(2)
            # else:
            self.login(user_name, password)

    def logout(self):
        user_menu = self.driver.find_elements('xpath',
            "//li[@class='dropdown account-links'] | //a[@title='Account']/.. | //button[@id='DropdownButton1']"
        )
        assert len(user_menu) > 0, "User menu has not been found"
        click_by_action(self.driver, user_menu[0], 'dropdown-toggle')
        # user_menu[0].click()
        sign_out_btn = self.driver.find_elements('xpath',"//a[text()='Logout'] | //a[text()='Sign Out']")
        assert len(sign_out_btn) > 0, "Sign Out button has not been found"
        sign_out_btn[0].click()

    def wait_until_job_available_for_contributor(self, link, max_attempts=30, close_guide=True):
        error_msg = self.driver.find_elements('xpath',
            '//h1[text()="There is no work currently available in this task."]')
        running_time = 0
        while len(error_msg) > 0 and running_time < max_attempts:
            time.sleep(5)
            # self.driver.get(link)
            self.app.navigation.refresh_page()
            error_msg = self.driver.find_elements('xpath',
                '//h1[text()="There is no work currently available in this task."]')
            running_time += 1
        if close_guide:
            User(self.app).close_guide()
        time.sleep(2)

    def submit_quiz_answer_and_continue(self):
        with allure.step("Submit quiz answer and continue"):
            click_element_by_css_selector(self.driver, "[name='qf_submit_and_continue']")

    def account_open_job_by_id(self, job_id):
        found_job = False
        last_page = False
        while not found_job and not last_page:
            # find job on current page
            log.debug({
                'message': 'find job on the current page',
                'user_id': self.app.user.user_id})
            _job = find_elements(self.driver, "//tr[@id='task-%s']" % job_id)
            if _job:
                found_job = True
                # open link
                # account_window = self.driver.window_handles[0]
                log.debug({
                    'message': 'click on the job link',
                    'user_id': self.app.user.user_id})
                _job[0].find_element('xpath',".//a").click()
                log.debug({
                    'message': 'switch_to the new window',
                    'user_id': self.app.user.user_id})
                job_window = self.app.driver.window_handles[1]
                self.app.navigation.switch_to_window(job_window)
                return
            else:
                # check if it is the last page
                log.debug({
                    'message': 'check if it is the last page',
                    'user_id': self.app.user.user_id})
                tasks_info = find_element(self.driver, "//*[@id='available-tasks_info']").text
                num_tasks = re.findall('[0-9]+', tasks_info)
                if num_tasks[-1] == num_tasks[-2]:
                    last_page = True
                else:
                    # click - next page
                    log.debug({
                        'message': 'click next page',
                        'user_id': self.app.user.user_id})
                    find_element(self.driver, "//a[@id='available-tasks_next']").click()

        if last_page:
            log.error("Job %s has not been found" % job_id)
            assert False

    def skip_tour(self):
        _skip_tour_btn = find_elements(self.driver, "//button[text()='Skip Tour']")
        if _skip_tour_btn: _skip_tour_btn[0].click()

    def click_on_sorting_desk_by_title(self, sorting_desk_title):
        with allure.step("Click on sorting desk by title"):
            sorting_desk_elements = self.driver.find_elements('xpath',f"//th[text()='{sorting_desk_title}']")
            assert sorting_desk_elements, (
                f"Sorting desk has not been found. "
                f"Current URL - {self.driver.current_url}\n"
                f"Page source - {self.driver.page_source}"
            )
            sorting_desk_elements[0].click()
            time.sleep(1)

    def find_job_link_by_job_id(self, job_id):
        with allure.step("Find job link by job id"):
            job_links = self.driver.find_elements('xpath',f"//tbody//tr[@id='task-{job_id}']//a")
            assert job_links, "Job link has not been found"

            return job_links[0].get_attribute('href')
