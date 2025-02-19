import pandas as pd

from adap.ui_automation.services_config.quality_flow.components import QFUnitTable, QFActionMenu, QFFilters
from adap.ui_automation.utils.selenium_utils import *


class QualityFlowProjectCrowd(QFUnitTable, QFActionMenu, QFFilters):
    _AC_PROJECT_ID = "//input[@name='acId']"
    _PROJECT_TARGETING = "//span[text()='{}']"
    _CONTRIBUTOR_GROUP_NAME = "//input[@name='name']"
    _CONTRIBUTOR_GROUP_DESCRIPTION = "//textarea[@name='description']"
    _CONTRIBUTOR_GROUP_TABLE_COLUMNS = "//thead//th[.//div[text()]]"
    _LOCALE = "//label[text()='{}']/..//input"

    def __init__(self, project, app):
        self.project = project
        self.app = app
        self.driver = self.app.driver

    def send_ac_project_id(self, project_id, action='Check ID'):
        with allure.step(f'Send AC Project ID {project_id}'):
            send_keys_by_xpath(self.driver, self._AC_PROJECT_ID, project_id, clear_current=True)
            if action:
                self.app.navigation.click_link(action)
                time.sleep(3)

    def select_project_targeting_settings(self, name):
        with allure.step(f'Select project targeting settings {name}'):
            click_element_by_xpath(self.driver, self._PROJECT_TARGETING.format(name))

    def get_all_units_on_page(self):
        with allure.step('Get details about all units on the page'):
            if 'curatedCrowd/group' in self.driver.current_url:  # contributor group table
                columns = self.get_columns_contributor_group_table()
            else:
                columns = self.get_columns_unit_table()

            data = self._get_table_rows()
            print(columns)
            print(data)
            return pd.DataFrame(data, columns=columns)

    def get_columns_contributor_group_table(self):
        with allure.step('Get columns for contributor group table'):
            header = find_elements(self.driver, self._CONTRIBUTOR_GROUP_TABLE_COLUMNS)
            return [x.text for x in header]

    def select_data_units_by(self, by='EMAIL AND AC USER ID', values=[]):
        with allure.step(f'Select units by {by}: {values}'):
            columns = self.get_columns_unit_table()
            column_index = columns.index(by) + 2

            for value in values:

                if by == 'EMAIL AND AC USER ID':
                    value = value.split("\n")[0]

                unit = self.find_table_row_by(by='column_index', column_value=column_index, value=value)
                assert unit, f"Unit {value} has not been found"
                self._select_unit(unit)
                time.sleep(1)

    def fill_out_contributor_group_details(self, name=None, description=None, action=None):
        with allure.step(f'Create new contributor group with : name - {name}, description - {description}'):
            if name:
                send_keys_by_xpath(self.driver, self._CONTRIBUTOR_GROUP_NAME, name, clear_current=True)

            if description:
                send_keys_by_xpath(self.driver, self._CONTRIBUTOR_GROUP_DESCRIPTION, name, clear_current=True)

            if action:
                self.app.navigation.click_link(action)

    def assign_contributor_to_jobs(self, contributor, jobs):
        with allure.step(f'Assign contributor {contributor} to jobs {jobs}'):
            contributor = contributor.split("\n")[0]
            row = find_elements(self.driver, f"//tr[.//td[text()='{contributor}']]//td")
            assert len(row), f"Contributor {contributor} has not been found"

            columns = [x.text.lower() for x in find_elements(self.driver,
                                                             "//thead[.//div[text()='jobs']]//tr[2]//th[.//div[text()] or .//span[text()]]")]
            print("-=-=", columns)

            for job in jobs:
                print(columns.index(job.lower()))
                toggle = row[columns.index(job.lower())].find_element('xpath', ".//label")
                toggle.click()
                time.sleep(2)

    def select_project_locale(self, locale, action=False):
        with allure.step(f'Select project locale {locale}'):
            _locale_array = locale.split(',')

            for _locale in _locale_array:
                click_element_by_xpath(self.driver, self._LOCALE.format(_locale))

            if action:
                self.app.navigation.click_link(action)

    def get_all_curated_contributors_projects(self):
        with allure.step(f'Get data for all curated contributors projects'):
            rows = find_elements(self.driver, "//tbody//tr")
            results = []

            for row in rows:
                columns = row.find_elements('xpath', './/td')
                project_id = columns[0].text
                name = columns[0].text
                results.append({
                    "id": project_id,
                    "name": name
                })

            return results

    def select_action_by_project_name(self, project_name, action):
        with allure.step(f'Select three dots'):
            click_element_by_xpath(self.driver, f"//*[text()='{project_name}']/parent::*/parent::*/td[8]//a")
        with allure.step(f'Select action'):
            click_element_by_xpath(self.driver, f"//li[text()='{action}']")

    def select_action_for_project(self, by='id', value=None, action=None):
        with allure.step(f'Select action for project by {by}: {value}'):
            if by == 'id':
                project = find_elements(self.driver, f"//tr[.//td[text()='{value}']]")
                assert len(project), f"Project {value} has not been found"

                gear = project[0].find_element('xpath',
                                               f"//tr[.//td[text()='{value}']]//td[.//a]//*[local-name()='svg']")
                gear.click()

                project[0].find_element('xpath', f".//li[text()='{action}']").click()

                time.sleep(3)
