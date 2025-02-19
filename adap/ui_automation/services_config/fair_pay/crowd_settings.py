import time
from datetime import date

import allure

from adap.ui_automation.utils.selenium_utils import find_elements


class CrowdSettings:
    def __init__(self, fair_pay):
        self.fair_pay = fair_pay
        self.app = self.fair_pay.app

    def check_checkbox_is_selected_by_name(self, checkbox_name: str):
        with allure.step(f"Check that checkbox is selected by id. Checkbox_id - {checkbox_name}"):
            checkbox_elements = find_elements(self.app.driver, f"//*[(text()='{checkbox_name}')]/..//input")
            return checkbox_elements[0].is_selected()

    def enable_disable_checkbox_by_name(self, checkbox_name: str, enable=True):
        with allure.step(
            f"Enable checkbox by name if enable=True, else disable. Checkbox name - {checkbox_name}, enable - {enable}"
        ):
            self.app.user.update_role_for_team(checkbox_name, enable)

    def click_edit_general_crowd_settings_by_title(self, setting_title: str):
        with allure.step(f"Click edit general crowd settings by title: {setting_title}"):
            edit_buttons = find_elements(
                self.app.driver, f"//*[text()='{setting_title}']/..//a[text()='Edit']"
            )
            assert edit_buttons, f"Button '{setting_title}' has not been found"
            edit_buttons[0].click()
            time.sleep(2)

    def select_general_crowd_contributor_level(self, contributor_level: str):
        with allure.step(f"Select general crowd contributor level: {contributor_level}"):
            self.click_edit_general_crowd_settings_by_title(setting_title="Contributor Level")
            levels = find_elements(self.app.driver, f"//a[text()='{contributor_level}']")
            assert levels, f"Contributor Level '{contributor_level}' has not been found"
            levels[0].click()
            self.app.navigation.click_link(link_name="Ok")

    def _add_remove(
            self,
            crowd_setting_title,
            main_checkbox_name,
            btn_name,
            names,
            select,
            all_checkboxes,
            select_all
    ):
        with allure.step(f"Add/remove by list names: {names}"):

            self.click_edit_general_crowd_settings_by_title(setting_title=crowd_setting_title)
            time.sleep(2)

            #  disable all
            checkbox = self.app.driver.find_elements('xpath',f"//*[(text()='{main_checkbox_name}')]/..//label")
            checkbox[0].click()
            self.enable_disable_checkbox_by_name(checkbox_name=main_checkbox_name, enable=False)

            if all_checkboxes:
                self.enable_disable_checkbox_by_name(checkbox_name=main_checkbox_name, enable=select_all)
            else:
                for name in names:
                    self.enable_disable_checkbox_by_name(checkbox_name=name, enable=select)

            time.sleep(2)
            self.app.navigation.click_btn(btn_name=btn_name)

    def add_remove_general_crowd_contributor_channels(
            self,
            contributor_channels: list = None,
            select_channels: bool = True,
            all_channels: bool = False,
            select_all_channels: bool = True
    ):
        with allure.step(
            f"Add/remove general crowd contributor channels by contributor channels list names: {contributor_channels}"
        ):

            self._add_remove(
                crowd_setting_title='Contributor Channels',
                main_checkbox_name='Channel Name',
                btn_name='Ok',
                names=contributor_channels,
                select=select_channels,
                all_checkboxes=all_channels,
                select_all=select_all_channels
            )

    def add_remove_general_crowd_geography_countries(
            self,
            country_names: list = None,
            select_countries: bool = True,
            all_countries: bool = False,
            select_all_countries: bool = True
    ):
        with allure.step(f"Add/remove countries by country names list - {country_names}"):
            self._add_remove(
                crowd_setting_title='Geography based filters',
                main_checkbox_name='Country',
                btn_name='Save & Close',
                names=country_names,
                select=select_countries,
                all_checkboxes=all_countries,
                select_all=select_all_countries
            )

    def select_general_crowd_language(self, language: str):
        with allure.step(f"Select general crowd language - {language}"):
            self.click_edit_general_crowd_settings_by_title(setting_title="Language based filters")
            see_all_languages = find_elements(self.app.driver, "//div[@tabindex='0']")
            assert see_all_languages, f"All languages field '{language}' has not been found"
            see_all_languages[0].click()
            time.sleep(2)
            languages = find_elements(self.app.driver, f"//*[text()='{language}']")
            assert languages, f"Language '{language}' has not been found"
            languages[0].click()
            time.sleep(2)
            self.app.navigation.click_btn(btn_name="Ok")

    def create_custom_channel(self):
        with allure.step("Create custom channel"):
            self.app.navigation.click_link("Add Custom Channel")
            auto_select_contr_els = find_elements(self.app.driver, "//*[text()='Automatically select contributors']")
            assert auto_select_contr_els, "Automatically select contributors element has not been found"
            auto_select_contr_els[0].click()

            ch_name = "new_channel" + date.today().strftime("%m/%d/%Y")
            channel_mame_els = find_elements(self.app.driver, "//input[@name='channelName']")
            assert channel_mame_els, "Channel Name element has not been found"
            channel_mame_els[0].send_keys(ch_name)

            job_filter_els = find_elements(self.app.driver, "//input[@name='jobFilter']")
            assert job_filter_els, "Job Filter element has not been found"
            job_filter_els[0].click()

            job_els = find_elements(self.app.driver, "//*[contains(text(),'Name Your Job')]")
            assert job_els, "Job element has not been found"
            job_els[0].click()

            self.app.navigation.click_link("Create")
            time.sleep(1)
            return ch_name

    def select_custom_channel(self, custom_channel_name: str):
        with allure.step(f"Select custom channel : '{custom_channel_name}'"):
            custom_channel_els = find_elements(self.app.driver, f"//*[text()='{custom_channel_name}']/..//input/..")
            assert custom_channel_els, "Automatically select contributors element has not been found"
            if not custom_channel_els[0].is_selected():
                custom_channel_els[0].click()

            time.sleep(1)

    def set_ac_project_id(self, project_id):
        with allure.step(f"Set AC project ID '{project_id}'"):
            ac_project_els = find_elements(self.app.driver, "//a[contains(text(),'Edit')]")
            assert ac_project_els, "AC Project ID element has not been found"
            ac_project_els[0].click()
            project_els = find_elements(self.app.driver, "//input[@name='appenConnectProjectId']")
            assert project_els, "Project ID element has not been found"
            project_els[0].clear()
            project_els[0].send_keys(project_id)
            time.sleep(1)
            self.app.navigation.click_link("Save")
            time.sleep(1)
