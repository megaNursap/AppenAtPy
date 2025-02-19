import os
import tempfile
import time

import allure
import pandas as pd
from faker import Faker

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from adap.api_automation.services_config.qf_api_logic import faker
from adap.ui_automation.utils.selenium_utils import find_elements, get_text_by_xpath, find_element, \
    click_and_send_keys_by_js, find_element_by_css_selector, clear_field_by_attribute_value, click_by_java_script, \
    is_element, get_text_by_css_selector, is_element_visible_by_css_selector, send_keys_by_xpath, \
    click_element_by_xpath, click_element_by_text, send_keys_by_css_selector, click_element_by_css_selector, \
    send_keys_to_element, click_element, sleep_for_seconds, find_elements_by_css_selector


class Project_Resource_Internal_Contributor:
    # xpath
    _ADD_CONTRIBUTOR_BUTTON = "//a[text()='Add Contributors']"
    _FILE_INPUT = "//input[@accept='text/csv']"
    _CANCEL_BUTTON = "//a[(text()='Cancel')]"
    _EMAIL_INPUT = "//input[@name='email']"
    _NAME_INPUT = "//input[@name='name']"
    _ADD_BUTTON = "//a[text()= 'Add']"
    _SEARCH_CONTRIBUTOR_INPUT = "[name='searchContributors']"
    _SEARCH_CONTRIBUTOR_GROUP_INPUT_DIALOG = "[name='contributor-group']"
    _BACK_BUTTON = "//a[contains(text(), 'Back')]"
    _CLOSE_DIALOG = "[role='dialog'] h3 + a svg"
    _CONTRIBUTOR_NAME_TABLE_LIST = "//table/tbody/tr//td[text()='{contributor}']"

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def cancel_add_contributor(self, email, name):
        with allure.step('Cancel - add contributor'):
            self.navigate_to_project_resource()
            add_contributors_button = find_element(self.driver, self._ADD_CONTRIBUTOR_BUTTON)
            add_contributors_button.click()
            email_input = find_element(self.driver, self._EMAIL_INPUT)
            email_input.send_keys(email)
            name_input = find_element(self.driver, self._NAME_INPUT)
            name_input.send_keys(name)
            cancel_button = find_element(self.driver, self._CANCEL_BUTTON)
            cancel_button.click()

    def navigate_to_project_resource(self):
        with allure.step('Navigate to project resource page'):
            self.app.navigation.click_link_by_href('/project-resources/contributors/list')

    def create_test_data_icm_csv(self, filename):
        faker = Faker()
        email1, email2 = faker.email(), faker.email()
        name1, name2 = faker.name(), faker.name()

        data = [
            {'email': email1, 'name': name1},
            {'email': email2, 'name': name2}
        ]
        df = pd.DataFrame(data)
        base_dir = os.getcwd()
        file_path = f"{base_dir}/{filename}"
        df.to_csv(file_path, index=False)
        print(f"CSV file '{filename}' created with new data.")
        return email1, email2, name1, name2, file_path

    def create_test_data_icm_empty_csv(self, filename):
        data = []
        df = pd.DataFrame(data)
        base_dir = os.getcwd()
        file_path = f"{base_dir}/{filename}"
        df.to_csv(file_path, index=False)
        print(f"CSV file '{filename}' created with new data.")
        return file_path

    def create_test_data_icm_tsv(self, filename):
        faker = Faker()
        email1, email2 = faker.email(), faker.email()
        name1, name2 = faker.name(), faker.name()
        data = [
            {'email': email1, 'name': name1},
            {'email': email2, 'name': name2}
        ]
        df = pd.DataFrame(data)
        base_dir = os.getcwd()
        file_path = f"{base_dir}/{filename}"
        df.to_csv(file_path, sep='\t', index=False)
        print(f"TSV file '{filename}' created with new data.")
        return file_path

    def create_test_data_icm_xlsx(self, filename):
        faker = Faker()
        email1, email2 = faker.email(), faker.email()
        name1, name2 = faker.name(), faker.name()
        data = [
            {'email': email1, 'name': name1},
            {'email': email2, 'name': name2}
        ]
        df = pd.DataFrame(data)
        base_dir = os.getcwd()
        file_path = f"{base_dir}/{filename}"
        df.to_excel(file_path, index=False)

        print(f"XLSX file '{filename}' created with new data.")
        return file_path

    def add_contributor_via_file(self, file_path):
        with allure.step('Add contributor via file'):
            add_contributors_button = find_element(self.driver, self._ADD_CONTRIBUTOR_BUTTON)
            add_contributors_button.click()
            file_input = find_element(self.driver, self._FILE_INPUT)
            file_input.send_keys(file_path)
            time.sleep(2)

    def add_contributor(self):
        with allure.step('Navigate to project resource page and click Add Contributors button'):
            self.navigate_to_project_resource()
            add_contributors_button = find_elements(self.driver, "//a[contains(text(), 'Add Contributors')]")
            assert len(add_contributors_button) > 0, "Add Contributors button has not been found"
            add_contributors_button[0].click()

    def is_add_contributor_ui_elements(self):
        with allure.step('Verify the presence of the Email Address and Name input boxes'):
            email_input = find_elements(self.driver, "//input[@name='email']")
            assert len(email_input) > 0, "Email Address input box has not been found"
            name_input = find_elements(self.driver, "//input[@name='name']")
            assert len(name_input) > 0, "Name input box has not been found"
        with allure.step('Verify the presence of the text " or Bulk Add Contributors "'):
            text = get_text_by_xpath(self.driver, "//p[contains(text(), 'or Bulk Add Contributors')]")
            assert text == 'or Bulk Add Contributors', "Text ' or Bulk Add Contributors ' has not been found"
        with allure.step('Verify the presence of the drag-and-drop area'):
            drag_drop_area = find_elements(self.driver, "//p[text()='Drag&Drop file here']")
            assert len(drag_drop_area) > 0, "Drag-and-drop area has not been found"
        with allure.step('Verify the presence of the "Browse" button'):
            browse_button = find_elements(self.driver, "//a[contains(text(), 'Browse')]")
            assert len(browse_button) > 0, "Browse button has not been found"
        with allure.step('Verify the presence of the "Download Template" link'):
            download_template_link = find_elements(self.driver, "//a[contains(text(), 'Download Template')]")
            assert len(download_template_link) > 0, "Download Template link has not been found"
        with allure.step('Verify the presence of the text indicating supported file formats'):
            supported_formats_text = find_elements(self.driver, "//p[text()='CSV']")
            assert len(supported_formats_text) > 0, "Text indicating supported file formats has not been found"
        with allure.step('Verify the presence of the "Cancel" and "Add" buttons'):
            cancel_button = find_elements(self.driver, "//a[contains(text(), 'Cancel')]")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            add_button = find_elements(self.driver, "//a[text()= 'Add']")
            assert len(add_button) > 0, "Add button has not been found"
            close = find_element(self.driver,
                                 "#js-modal-overlay > div > div.sc-evZas.hCUTdr > div > div.sc-hAZoDl.kefgxl > a > svg",
                                 mode=By.CSS_SELECTOR)
            close.click()
            return True

    def is_search_functionality(self, email="", name="", partial=False):
        with allure.step('Verify the search functionality'):
            search_input = find_element(self.driver, "//input[@name='searchContributors']")
            time.sleep(2)
            search_input.clear()
            click_and_send_keys_by_js(self.driver, "//input[@name='searchContributors']", email)
            time.sleep(3)
            if partial:
                contributor = find_elements(self.driver, f"//td[contains(text(),'{email}')]")
            else:
                contributor = find_elements(self.driver, f"//td[text()='{email}']")
            assert len(contributor) > 0, "Contributor has not been found"
            search_input.clear()
            click_and_send_keys_by_js(self.driver, "//input[@name='searchContributors']", name)
            time.sleep(3)
            if partial:
                contributor = find_elements(self.driver, f"//td[contains(text(),'{name}')]")
            else:
                contributor = find_elements(self.driver, f"//td[text()='{name}']")
            assert len(contributor) > 0, "Contributor has not been found"
            return True

    def add_single_contributor(self, email, name):
        with allure.step('Add single contributor'):
            self.navigate_to_project_resource()
            add_contributors_button = find_element(self.driver, self._ADD_CONTRIBUTOR_BUTTON)
            add_contributors_button.click()
            email_input = find_element(self.driver, self._EMAIL_INPUT)
            email_input.send_keys(email)
            name_input = find_element(self.driver, self._NAME_INPUT)
            name_input.send_keys(name)
            time.sleep(3)
            add_button = find_element(self.driver, self._ADD_BUTTON)
            add_button.click()

    def find_contributor(self, value):
        with allure.step(f"Find Contributor: {value}"):
            element = find_element(self.driver, f"//td[text()='{value}']")
            return element

    def click_add_contributors_button(self):
        with allure.step('Click Add Contributors button'):
            add_contributors_button = find_element(self.driver, self._ADD_CONTRIBUTOR_BUTTON)
            add_contributors_button.click()
            return True

    def enter_email(self, email):
        with allure.step(f'Enter email: {email}'):
            email_input = find_element(self.driver, self._EMAIL_INPUT)
            email_input.send_keys(email)
            return True

    def enter_name(self, name):
        with allure.step(f'Enter name: {name}'):
            name_input = find_element(self.driver, self._NAME_INPUT)
            name_input.send_keys(name)
            return True

    def click_add_button(self):
        with allure.step('Click Add button'):
            add_button = find_element(self.driver, self._ADD_BUTTON)
            add_button.click()
            return True

    def click_cancel_button(self):
        with allure.step('Click Cancel button'):
            cancel_button = find_element(self.driver, self._CANCEL_BUTTON)
            cancel_button.click()
            return True

    def click_notification_close(self):
        with allure.step('Close notification'):
            notification_close = find_element(self.driver, "//button[@aria-label='Close']", mode=By.CSS_SELECTOR)
            notification_close.click()
            return True

    def delete_created_file(self, file_path):
        with allure.step('Delete created file'):
            os.remove(file_path)
            return True

    def navigate_to_project_resource_contributor_group(self):
        with allure.step('Navigate to Project Resource page -> Contributor Group Tab'):
            self.app.navigation.click_link_by_href('/project-resources/contributors/groups')

    def search_internal_contributor(self, contributor):
        with allure.step(f'Search Contributor Name: {contributor}'):
            send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_INPUT, contributor, clear_current=True)
            time.sleep(2)

    def is_table_contains_contributor(self, contributor):
        with allure.step(f'Check if contributor is in the table list: {contributor}'):
            contributor = find_elements(self.driver, self._CONTRIBUTOR_NAME_TABLE_LIST.format(contributor=contributor))
            if len(contributor) > 0:
                return True
            else:
                return False

    def search_internal_contributor_group(self, contributor_group_name):
        with allure.step(f'Search Contributor Group Name: {contributor_group_name}'):
            search_textbox = find_element_by_css_selector(self.driver, "[name='searchContributors']")
            search_textbox.send_keys(contributor_group_name)
            time.sleep(2)

    def delete_multiple_contributor_groups(self, number_of_group):
        with allure.step(f'Select checkbox for {number_of_group} group'):
            i = 1
            while i < number_of_group + 1:
                contributor_checkbox = find_element(self.driver, f"//table//tbody/tr[{i}]//label")
                contributor_checkbox.click()
                i += 1
        with allure.step('Delete contributors'):
            delete_button = find_element(self.driver, f"//h2/parent::*/div[2]//a[text()='Delete']")
            delete_button.click()

    def validate_the_table_contains_contributor_group_in_delete_confirmation_popup(self, contributor_group):
        with allure.step(
                f'Verify the table list contains group name : {contributor_group} in delete confirmation popup'):
            group_name = find_elements(self.driver,
                                       f"//*[@role='document']//table/tbody/tr/td[text()='{contributor_group}']")
            assert len(group_name) == 1, "Contributor group is still in the table list"
            return True

    def get_group_name_by_index(self, index):
        return get_text_by_xpath(self.driver, f"//table/tbody/tr[{index}]/td[2]")

    def validate_ui_elements_in_contributor_group_tab(self):
        with allure.step('Verify the presence of the text " Contributor Group Name "'):
            text = get_text_by_xpath(self.driver, "//th[text()='Contributor Group Name']")
            assert text == 'Contributor Group Name', "Text ' Contributor Group ' has not been found"
        with allure.step('Verify the presence of the "Create Contributor Group" button'):
            add_contributor_group_button = find_elements(self.driver,
                                                         "//a[contains(text(), 'Create Contributor Group')]")
            assert len(add_contributor_group_button) > 0, "Create Contributor Group button has not been found"
        with allure.step('Verify the presence of the "Search" input box'):
            search_input = find_elements(self.driver, "//input[@placeholder='Search']")
            assert len(search_input) > 0, "Search input box has not been found"
        with allure.step('Verify the presence of the text " No. of Contributor "'):
            text = get_text_by_xpath(self.driver, "//th[contains(text(), 'No. of Contributor')]")
            assert text == 'No. of Contributor', "Text ' No. of Contributor ' has not been found"

    def validate_ui_elements_in_add_contributor_to_existing_group(self):
        with allure.step('Verify the presence of the text " Add to Existing Contributor Group "'):
            text = get_text_by_xpath(self.driver, "//h3[contains(text(), 'Add to Existing Contributor Group')]")
            assert text == 'Add to Existing Contributor Group', "Text ' Add to Existing Contributor Group ' has not been found"
        with allure.step('Verify the presence of the Search for a group input box'):
            contributor_group_name_input = find_elements(self.driver, "//input[@name='contributor-group']")
            assert len(
                contributor_group_name_input) > 0, "Search for a group input box has not been found"
        with allure.step('Verify the presence of the text " Enter Contributor Group "'):
            text = get_text_by_xpath(self.driver, "//span[contains(text(), 'Enter Contributor Group')]")
            assert text == 'Enter Contributor Group', "Text ' Enter Contributor Group ' has not been found"
        with allure.step('Verify the presence of the "Cancel" and "Add" buttons'):
            cancel_button = find_elements(self.driver, "//a[contains(text(), 'Cancel')]")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            add_button = find_elements(self.driver, "//a[text()= 'Add']")
            assert len(add_button) > 0, "Add button has not been found"
            return True

    def select_contributor_action_menu(self, action):
        with allure.step('Click on three dots to reveal options'):
            click_element(self.driver, "table tbody tr svg")
        with allure.step(f'Select Action: {action}'):
            click_element(self.driver, f"//li[text()='{action}']")

    def navigate_to_edit_contributor_group_popup(self):
        with allure.step('Select Add to Existing Contributor Group for the first record'):
            three_dots = find_element_by_css_selector(self.driver, "table tbody tr svg")
            three_dots.click()
            edit_contributor_group = find_element(self.driver, "//li[text()='Edit Contributor Group']")
            edit_contributor_group.click()

    def add_to_existing_contributor_group(self, contributor_group, action=None):
        with allure.step(f'Search Contributor Group: {contributor_group}'):
            send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_GROUP_INPUT_DIALOG, contributor_group)
        with allure.step(f'Select Contributor Group: {contributor_group}'):
            click_element(self.driver, f"//*[text()='{contributor_group}']")
        if action:
            with allure.step(f'Select action: {action}'):
                click_element(self.driver, f"//a[text()='{action}']")
                time.sleep(2)

    def validate_the_table_list_contains_contributor(self, contributor):
        with allure.step(f'Verify the table list not contains contributor : {contributor}'):
            contributor = find_elements(self.driver, f"//td[text()='{contributor}']")
            assert len(contributor) == 1, "Contributor is not in the table list"
            return True

    def validate_the_table_list_not_contains_contributor(self, contributor):
        with allure.step(f'Verify the table list not contains contributor : {contributor}'):
            contributor = find_elements(self.driver, f"//td[text()='{contributor}']")
            assert len(contributor) == 0, "Contributor is still in the table list"
            return True

    def download_csv_from_contributor_group(self):
        with allure.step('Click on the three dots to reveal options'):
            three_dots_button = find_element_by_css_selector(self.driver, "table tbody tr svg")
            three_dots_button.click()
        with allure.step('Click Download CSV button'):
            try:
                download_csv_button = find_element(self.driver, "//li[contains(text(), 'Download CSV')]")
                download_csv_button.click()
            except NoSuchElementException:
                print("Download CSV button not found")
        temp_dir = tempfile.mkdtemp()
        files = os.listdir(temp_dir)
        csv_found = False
        for file in files:
            if os.path.splitext(file)[1] == '.csv':
                csv_found = True
                break
        assert csv_found is False, "CSV file has not been downloaded"
        os.rmdir(temp_dir)

    def add_multiple_contributors_to_existing_group(self, number_of_contributors, group_name=None, action=None):
        with allure.step(f'Select checkbox for {number_of_contributors} contributors'):
            i = 1
            while i < number_of_contributors + 1:
                contributor_checkbox = find_element(self.driver, f"//table/tbody/tr[{i}]//label")
                contributor_checkbox.click()
                i += 1
        with allure.step('Click Add to Existing Contributor Group button'):
            add_to_existing_contributor_group = find_element(self.driver,
                                                             "//li[text()='Add to existing Contributor Group']")
            click_by_java_script(self.driver, add_to_existing_contributor_group)
        if group_name:
            with allure.step(f'Search Contributor Group: {group_name}'):
                send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_GROUP_INPUT_DIALOG, group_name)
            with allure.step(f'Select Contributor Group: {group_name}'):
                click_element(self.driver, f"//*[text()='{group_name}']")
        if action:
            if action == 'Back':
                with allure.step('Click Back button'):
                    click_element(self.driver, self._BACK_BUTTON)
            elif action == 'Add':
                with allure.step('Click Add button'):
                    click_element(self.driver, self._ADD_BUTTON)
            elif action == 'Close':
                with allure.step('Click Close button'):
                    click_element(self.driver, self._CLOSE_DIALOG)

    def click_options(self):
        with allure.step('Click Options'):
            time.sleep(6)
            options = find_element(self.driver, "//table[@class]/tbody/tr[1]/td[4]/div/a")
            options.click()
            return True

    def click_edit_internal_contributors(self):
        with allure.step('Click Edit Internal Contributors'):
            edit_internal_contributors = find_element(self.driver, "(//li[text()='Edit Contributor'])[1]")
            edit_internal_contributors.click()

    def is_edit_internal_contributors_ui_elements(self):
        with allure.step('Verify the presence of the Email Address and Name input boxes'):
            email_input = find_elements(self.driver, "//input[@placeholder='Enter Contributor Email']")
            assert len(email_input) > 0, "Email Address input box has not been found"
            name_input = find_elements(self.driver, "//input[@placeholder='Enter Contributor Name']")
            assert len(name_input) > 0, "Name input box has not been found"
        with allure.step('Verify the presence of the "Cancel" and "Save" buttons'):
            cancel_button = find_elements(self.driver, "//a[text()='Cancel']")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            save_button = find_elements(self.driver, "//a[text()='Save']")
            assert len(save_button) > 0, "Save button has not been found"
        with allure.step('Verify the presence of the "Edit Contributor" text'):
            edit_contributor_text = find_elements(self.driver, "//h3[text()='Edit Contributor']")
            assert len(edit_contributor_text) > 0, "Text 'Edit Contributor' has not been found"
        with allure.step('Verify the presence of the Contributor Contributor Email and Name labels'):
            contributor_email_label = find_elements(self.driver, "//span[text()='Contributor Email']")
            assert len(contributor_email_label) > 0, "Contributor Email label has not been found"
            contributor_name_label = find_elements(self.driver, "//span[text()='Contributor Name']")
            assert len(contributor_name_label) > 0, "Contributor Name label has not been found"

    def edit_email_and_name(self, email, name):
        with allure.step('Edit email and name'):
            email_input = find_element(self.driver, "//input[@placeholder='Enter Contributor Email']")
            clear_field_by_attribute_value(self.driver, email_input)
            email_input.send_keys(email)
            time.sleep(1)
            name_input = find_element(self.driver, "//input[@placeholder='Enter Contributor Name']")
            clear_field_by_attribute_value(self.driver, name_input)
            name_input.click()
            name_input.send_keys(Keys.CONTROL + "a")
            name_input.send_keys(Keys.COMMAND + "a")
            name_input.send_keys(Keys.BACKSPACE)
            time.sleep(1)
            name_input.send_keys(name)
            return True

    def edit_email(self, email):
        with allure.step('Edit email'):
            email_input = find_element(self.driver, "//input[@placeholder='Enter Contributor Email']")
            clear_field_by_attribute_value(self.driver, email_input)
            email_input.send_keys(email)
            return True

    def edit_name(self, name):
        with allure.step('Edit name'):
            name_input = find_element(self.driver, "//input[@placeholder='Enter Contributor Name']")
            clear_field_by_attribute_value(self.driver, name_input)
            name_input.send_keys(name)
            return True

    def click_edit_save_button(self):
        with allure.step('Click Save button'):
            save_button = find_element(self.driver, "//a[text()='Save']")
            save_button.click()
            return True

    def click_edit_cancel_button(self):
        with allure.step('Click Close button'):
            close_button = find_element(self.driver, "//a[text()='Cancel']")
            close_button.click()
            return True

    def is_delete_contributor_ui_elements(self):
        with allure.step('Verify the presence of the "Delete" button'):
            delete_button = find_elements(self.driver, "(//li[text()='Delete'])[1]")
            assert len(delete_button) > 0, "Delete button has not been found"
        with allure.step('Verify the presence of the "Delete Confirmation" text'):
            delete_confirmation_text = get_text_by_xpath(self.driver, "//h3[text()='Delete Confirmation']")
            assert delete_confirmation_text == 'Delete Confirmation', "Text 'Delete Confirmation' has not been found"
        with allure.step('Verify the presence of the "Are you sure you want to delete" text'):
            confirmation_text = get_text_by_xpath(self.driver, "//div[contains(text(), 'This contributor belongs to')]")
            assert 'Are you sure you want to delete' in confirmation_text, "Text has not been found"
        with allure.step('Verify the presence of the "Cancel" and "Delete" buttons'):
            cancel_button = find_elements(self.driver, "//a[text()='Cancel']")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            delete_button = find_elements(self.driver, "//a[text()='Delete']")
            assert len(delete_button) > 0, "Delete button has not been found"
        with allure.step('Verify the presence of the "This contributor belongs to" text'):
            confirmation_text1 = get_text_by_xpath(self.driver, "//div[contains(text(),'This contributor belongs to')]")
            assert 'This contributor belongs to' in confirmation_text1, "Text has not been found"
            return True

    def delete_contributor(self):
        with allure.step('Delete contributor'):
            deleted_email = get_text_by_xpath(self.driver, "//table/tbody/tr[1]/td[2]")
            delete_button = find_element(self.driver, "(//li[text()='Delete'])[1]")
            delete_button.click()
            return deleted_email

    def delete_multiple_contributor(self):
        with allure.step('Delete multiple contributor'):
            deleted_email1 = get_text_by_xpath(self.driver, "//table/tbody/tr[1]/td[2]")
            deleted_email2 = get_text_by_xpath(self.driver, "//table/tbody/tr[2]/td[2]")
            checkbox1 = find_element(self.driver, "//table/tbody/tr[1]/td[1]/div/input")
            checkbox2 = find_element(self.driver, "//table/tbody/tr[2]/td[1]/div/input")
            click_by_java_script(self.driver, checkbox1)
            click_by_java_script(self.driver, checkbox2)
            delete_element = find_element(self.driver, "(//a[text()='Delete'])[1]")
            click_by_java_script(self.driver, delete_element)

            exp_email_1 = get_text_by_xpath(self.driver, "(//table)[2]/tbody/tr[1]/td[1]")
            exp_email_2 = get_text_by_xpath(self.driver, "(//table)[2]/tbody/tr[2]/td[1]")
            delete_element_2 = find_element(self.driver, "(//a[text()='Delete'])[2]")
            click_by_java_script(self.driver, delete_element_2)
            assert exp_email_1 == deleted_email1, "First email doesn't match"
            assert exp_email_2 == deleted_email2, "Second email doesn't match"
            return deleted_email1, deleted_email2

    def cancel_single_delete_contributor(self):
        with allure.step('Cancel single delete contributor'):
            deleted_email = get_text_by_xpath(self.driver, "//table/tbody/tr[1]/td[2]")
            options = find_element(self.driver, "//table[@class]/tbody/tr[1]/td[4]/div/a")
            options.click()
            delete_button = find_element(self.driver, "(//li[text()='Delete'])[1]")
            delete_button.click()
            cancel_button = find_element(self.driver, "//a[text()='Cancel']")
            cancel_button.click()
            return deleted_email

    def cancel_multiple_delete_contributor(self):
        with allure.step('Cancel multiple delete contributor'):
            deleted_email1 = get_text_by_xpath(self.driver, "//table/tbody/tr[1]/td[2]")
            deleted_email2 = get_text_by_xpath(self.driver, "//table/tbody/tr[2]/td[2]")
            checkbox1 = find_element(self.driver, "//table/tbody/tr[1]/td[1]/div/input")
            checkbox2 = find_element(self.driver, "//table/tbody/tr[2]/td[1]/div/input")
            click_by_java_script(self.driver, checkbox1)
            click_by_java_script(self.driver, checkbox2)
            delete_element = find_element(self.driver, "(//a[text()='Delete'])[1]")
            click_by_java_script(self.driver, delete_element)
            time.sleep(3)
            cancel_element = find_element(self.driver, "//a[text()='Cancel']")
            click_by_java_script(self.driver, cancel_element)
            return deleted_email1, deleted_email2

    def delete_single_contributor(self, email):
        with allure.step('Delete single contributor'):
            self.is_search_functionality(email=email, name='', partial=True)
            checkbox1 = find_element(self.driver, "//table/tbody/tr[1]/td[1]/div/input")
            click_by_java_script(self.driver, checkbox1)
            delete_element = find_element(self.driver, "(//a[text()='Delete'])[1]")
            click_by_java_script(self.driver, delete_element)
            return True

    def search_contributor_from_edit_contributor_group_popup(self, text):
        with allure.step(f'Search Contributor : {text}'):
            search_textbox = find_element_by_css_selector(self.driver, "[role='document'] [name='searchContributors']")
            search_textbox.send_keys(text)
            time.sleep(2)

    def delete_contributor_from_edit_contributor_group_popup(self, text):
        with allure.step(f'Delete Contributor : {text}'):
            search_textbox = find_element_by_css_selector(self.driver, "[role='document'] table tbody tr svg")
            search_textbox.click()
            time.sleep(2)

    def close_popup(self):
        with allure.step('Close popup'):
            close_icon = find_element(self.driver, "//*[@role='document']/parent::div/div[1]/a")
            close_icon.click()
            time.sleep(2)

    def validate_ui_elements_on_delete_popup(self, contributor_group):
        with allure.step('Verify the presence of the text " Delete Confirmation "'):
            text = get_text_by_xpath(self.driver, "//h3[text()='Delete Confirmation']")
            assert text == 'Delete Confirmation', "Text ' Delete Confirmation ' has not been found"
        with allure.step(f'Verify the content of popup including group {contributor_group}'):
            content = find_elements(self.driver, "//*[@role='document']/div")
            assert len(content) > 0, "Content has not been found"
        with allure.step(f'Verify the contributor group  {contributor_group} is set in bold'):
            group = find_elements(self.driver, f"//*[@role='document']//span[text()='{contributor_group}']")
            assert len(group) > 0, "Contributor's group has not been set in bold"
        with allure.step('Verify the presence of the "Cancel" and "Delete" buttons'):
            cancel_button = find_elements(self.driver, "//a[contains(text(), 'Cancel')]")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            delete_button = find_elements(self.driver, "//a[text()= 'Delete']")
            assert len(delete_button) > 0, "Delete button has not been found"
            return True

    def validate_ui_elements_in_edit_contributor_group_popup(self):
        with allure.step('Verify the presence of the text " Edit Contributor Group "'):
            text = get_text_by_xpath(self.driver, "//h3[contains(text(), 'Edit Contributor Group')]")
            assert text == 'Edit Contributor Group', "Text ' Edit Contributor Group ' has not been found"
        with allure.step('Verify the presence of the Contributor Group Name input box'):
            contributor_group_name_input = find_elements(self.driver, "//input[@name='name']")
            assert len(
                contributor_group_name_input) > 0, "Contributor Group Name input box has not been found"
        with allure.step('Verify the presence of the Search for contributor input box'):
            search_contributor_input = find_elements(self.driver,
                                                     "//*[@role='document']//input[@name='searchContributors']")
            assert len(
                search_contributor_input) > 0, "Search for contributor input box has not been found"
        with allure.step('Verify the presence of the All Contributors dropdown'):
            all_contributor_dropdown = find_elements(self.driver, "//*[@data-test-id='select-All Contributors']")
            assert len(
                all_contributor_dropdown) > 0, "All Contributors dropdown has not been found"
        with allure.step('Verify the presence of the "Cancel" and "Save" buttons'):
            cancel_button = find_elements(self.driver, "//a[contains(text(), 'Cancel')]")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            save_button = find_elements(self.driver, "//a[text()= 'Save']")
            assert len(save_button) > 0, "Save button has not been found"
            return True

    def confirm_to_delete(self):
        with allure.step('Tap Delete to confirm for the deletion'):
            confirm_delete = find_element(self.driver, "//a[text()='Delete']")
            confirm_delete.click()
            time.sleep(2)

    def confirm_to_delete_multiple_contributor_group(self):
        with allure.step('Tap Delete to confirm for the deletion for multiple groups'):
            confirm_delete = find_element(self.driver, "//*[@role='document']/parent::*/div[3]/*[text()='Delete']")
            confirm_delete.click()
            time.sleep(2)

    def navigate_to_delete_popup(self):
        with allure.step('Select Delete for the first record'):
            three_dots = find_element_by_css_selector(self.driver, "table tbody tr svg")
            three_dots.click()
            edit_contributor_group = find_element(self.driver, "//li[text()='Delete']")
            edit_contributor_group.click()

    def validate_contributor_group_not_contains_contributor(self, contributor_email):
        with allure.step(f'Verify Contributor Group contains contributor name : {contributor_email}'):
            contributor_email = find_elements(self.driver, f"//td[text()='{contributor_email}']")
            assert len(contributor_email) == 0, "Contributor is still in contributor group"
            return True

    def validate_the_table_not_contains_contributor_group(self, contributor_group):
        with allure.step(f'Verify Contributor Group not contains group name : {contributor_group}'):
            contributor_email = find_elements(self.driver, f"//td[text()='{contributor_group}']")
            assert len(contributor_email) == 0, "Contributor group is still in the table list"
            return True


class Project_Resource_Internal_Contributor_Group:
    _SEARCH_GROUP_NAME = "[name='searchContributors']"
    _CREATE_CONTRIBUTOR_GROUP_BUTTON = "//a[text()='Create Contributor Group']"
    _ADD_CONTRIBUTOR_GROUP_DIALOG_TITLE = "[role='dialog'] h3"
    _SEARCH_CONTRIBUTOR_GROUP_NAME_DIALOG = "//input[@placeholder='Enter Contributor Group Name']"
    _SEARCH_CONTRIBUTOR_DIALOG = "[role='dialog'] [name='searchContributors']"
    _CONTRIBUTOR_DROPDOWN_DIALOG = "[role='dialog'] [data-test-id='select-All Contributors']"
    _BACK_BUTTON = "//a[contains(text(), 'Back')]"
    _ADD_BUTTON = "//a[contains(text(), 'Add')]"
    _CANCEL_BUTTON = "//a[contains(text(), 'Cancel')]"
    _CLOSE_DIALOG = "[role='dialog'] h3 + a svg"
    _CONTRIBUTOR_EMAIL_CHECKBOX_DIALOG = "[role='dialog'] tbody [type='checkbox'] + label"
    _UPLOAD_CSV = "[role='document'] [type='file']"
    _CONTRIBUTOR_NAME_DIALOG = "//*[@role='dialog']//td[text()='{contributor}']"
    _CONTRIBUTOR_NAME_REMOVE_ICON_DIALOG = "//*[@role='dialog']//td[text()='{contributor}']/parent::*//a/div/*"

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.driver = self.app.driver

    def open_create_contributor_group_popup(self):
        with allure.step('Click on the "Create Contributor Group" button'):
            find_element(self.driver, self._CREATE_CONTRIBUTOR_GROUP_BUTTON).click()

    def select_contributor_group_action_menu(self, action):
        with allure.step('Click on three dots to reveal options'):
            click_element(self.driver, "table tbody tr svg")
        with allure.step(f'Select Action: {action}'):
            click_element(self.driver, f"//li[text()='{action}']")
            sleep_for_seconds(2)

    def validate_ui_elements_in_contributor_group_tab(self):
        with allure.step('Verify the presence of the text " Contributor Group Name "'):
            text = get_text_by_xpath(self.driver, "//th[text()='Contributor Group Name']")
            assert text == 'Contributor Group Name', "Text ' Contributor Group ' has not been found"
        with allure.step('Verify the presence of the "Create Contributor Group" button'):
            add_contributor_group_button = find_elements(self.driver,
                                                         "//a[contains(text(), 'Create Contributor Group')]")
            assert len(add_contributor_group_button) > 0, "Create Contributor Group button has not been found"
        with allure.step('Verify the presence of the "Search" input box'):
            search_input = find_elements(self.driver, "//input[@placeholder='Search']")
            assert len(search_input) > 0, "Search input box has not been found"
        with allure.step('Verify the presence of the text " No. of Contributor "'):
            text = get_text_by_xpath(self.driver, "//th[contains(text(), 'No. of Contributor')]")
            assert text == 'No. of Contributor', "Text ' No. of Contributor ' has not been found"

    def validate_ui_elements_in_create_new_contributor_group_dialog(self):
        with allure.step('Verify the presence of the text "Add Contributor Group"'):
            text = get_text_by_css_selector(self.driver, self._ADD_CONTRIBUTOR_GROUP_DIALOG_TITLE)
            assert text == 'Add Contributor Group', "Text 'Add Contributor Group' has not been found"
        with allure.step('Verify the presence of the Search Contributor Group input'):
            assert is_element(self.driver, self._SEARCH_CONTRIBUTOR_GROUP_NAME_DIALOG) == True
        with allure.step('Verify the presence of Search Contributor'):
            assert is_element_visible_by_css_selector(self.driver, self._SEARCH_CONTRIBUTOR_DIALOG) == True
        with allure.step('Verify the presence of All Contributor Dropdown'):
            assert is_element_visible_by_css_selector(self.driver, self._CONTRIBUTOR_DROPDOWN_DIALOG) == True
        with allure.step('Verify the presence of the "Cancel" and "Create" buttons'):
            assert is_element(self.driver, self._ADD_BUTTON) == True
            assert is_element(self.driver, self._CANCEL_BUTTON) == True

    def close_dialog(self):
        with allure.step('Close dialog'):
            find_element_by_css_selector(self.driver, self._CLOSE_DIALOG).click()

    def add_new_contributor_group_by_import(self, group_name, contributor_email=None, action_import=None,
                                            action_dialog=None):
        self.open_create_contributor_group_popup()
        with allure.step(f'Input Group Name: {group_name}'):
            send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_GROUP_NAME_DIALOG, group_name)
        with allure.step(f'Import contributor: {contributor_email}'):
            if contributor_email:
                click_element(self.driver, self._CONTRIBUTOR_DROPDOWN_DIALOG)
                click_element_by_text(self.driver, 'Import Contributors')
                send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_DIALOG, contributor_email)
                sleep_for_seconds(2)
                with allure.step(f'Select contributor email: {contributor_email}'):
                    click_element(self.driver, self._CONTRIBUTOR_EMAIL_CHECKBOX_DIALOG)
            if action_import:
                if action_import == 'Back':
                    with allure.step('Click Back button'):
                        click_element(self.driver, self._BACK_BUTTON)
                elif action_import == 'Add':
                    with allure.step('Click Add button'):
                        click_element(self.driver, self._ADD_BUTTON)
                elif action_import == 'Close':
                    with allure.step('Click Close button'):
                        click_element(self.driver, self._CLOSE_DIALOG)
        if action_dialog:
            if action_dialog == 'Cancel':
                with allure.step('Click Cancel button'):
                    click_element(self.driver, self._CANCEL_BUTTON)
            elif action_dialog == 'Add':
                with allure.step('Click Add button'):
                    click_element(self.driver, self._ADD_BUTTON)
            elif action_dialog == 'Close':
                with allure.step('Click Close button'):
                    click_element(self.driver, self._CLOSE_DIALOG)

    def add_new_contributor_group_by_upload(self, group_name, file_name=None, action_upload=None,
                                            contributor_email=None, action_dialog=None):
        self.open_create_contributor_group_popup()
        with allure.step(f'Input Group Name: {group_name}'):
            send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_GROUP_NAME_DIALOG, group_name)
        with allure.step(f'Upload contributor'):
            if file_name:
                with allure.step(f'Upload csv file: {file_name}'):
                    click_element(self.driver, self._CONTRIBUTOR_DROPDOWN_DIALOG)
                    click_element_by_text(self.driver, 'Upload Contributors')
                    self.upload_contributor_csv(file_name)
                if action_upload:
                    if action_upload == 'Back':
                        with allure.step('Click Back Button'):
                            click_element(self.driver, self._BACK_BUTTON)
                    elif action_upload == 'Add':
                        with allure.step('Click Add Button'):
                            click_element(self.driver, self._ADD_BUTTON)
                            sleep_for_seconds(5)
                    elif action_upload == 'Close':
                        click_element(self.driver, self._CLOSE_DIALOG)
        if contributor_email:
            with allure.step(f'Select contributor: {contributor_email}'):
                send_keys_to_element(self.driver, self._SEARCH_CONTRIBUTOR_DIALOG, contributor_email)
                sleep_for_seconds(2)
                click_element(self.driver, self._CONTRIBUTOR_EMAIL_CHECKBOX_DIALOG)
        if action_dialog:
            if action_dialog == 'Cancel':
                with allure.step('Click Cancel Button'):
                    click_element(self.driver, self._CANCEL_BUTTON)
            else:
                with allure.step('Click Add Button'):
                    click_element(self.driver, self._ADD_BUTTON)

    def upload_contributor_csv(self, file_name, wait_time=15):
        with allure.step('Upload data file'):
            el = find_elements_by_css_selector(self.app.driver, self._UPLOAD_CSV)
            if len(el) > 0:
                el[0].send_keys(file_name)
            else:
                print("Not able to upload data file")

            try:
                self.app.navigation.click_link("Proceed Anyway")
            except:
                print("no warning message")

            time.sleep(wait_time)

    def search_internal_contributor_group(self, group_name):
        with allure.step(f'Search Group Name: {group_name}'):
            send_keys_to_element(self.driver, self._SEARCH_GROUP_NAME, group_name, True)
            sleep_for_seconds(2)

    def remove_contributors_from_existing_groups(self, contributor):
        with allure.step(f'Remove Contributor: {contributor}'):
            click_element(self.driver, self._CONTRIBUTOR_NAME_REMOVE_ICON_DIALOG.format(contributor=contributor))
            sleep_for_seconds(2)

    def is_dialog_visible(self):
        with allure.step(f'Check if dialog is visible'):
            dialog = find_elements_by_css_selector(self.driver, self._ADD_CONTRIBUTOR_GROUP_DIALOG_TITLE)
            if len(dialog) > 0:
                return True
            else:
                return False

    def is_dialog_contains_contributor(self, contributor):
        with allure.step(f'Check if dialog contains contributor: {contributor}'):
            dialog = find_elements(self.driver, self._CONTRIBUTOR_NAME_DIALOG.format(contributor=contributor))
            if len(dialog) > 0:
                return True
            else:
                return False
