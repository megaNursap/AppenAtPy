import datetime
import logging
import random
import time

import allure
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data
from adap.perf_platform.utils.logging import get_logger
from adap.ui_automation.utils.js_utils import *
from adap.ui_automation.utils.selenium_utils import click_element_by_xpath, find_elements, get_attribute_by_xpath, \
    send_keys_by_xpath, find_element, send_keys_by_css_selector, find_element_by_css_selector

LOGGER = get_logger(__name__)


def login_and_open_qf_page(app, account):
    username = get_test_data(account, 'email')
    password = get_test_data(account, 'password')
    team_id = get_test_data(account, 'teams')[0]['id']

    if not app.quality_flow.qf_is_enabled_to_team(team_id):
        app.quality_flow.enable_qf_for_team(team_id)
        time.sleep(3)

    app.user.login_as_customer(username, password)

    app.mainMenu.menu_item_is_disabled('quality', is_not=True)
    app.mainMenu.quality_flow_page()


def create_new_project_qf_api(account, prefix):
    username = get_test_data(account, 'email')
    password = get_test_data(account, 'password')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)
    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    faker = Faker()

    project_name = f"{prefix} {_today} {faker.zipcode()} "

    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    team_id = get_test_data(account, 'teams')[0]['id']
    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    return data


def feedback_judgements_qa_job(app, random_reject=0):
    if random_reject:
        questions_on_page = app.driver.find_elements('xpath',
                                                     '//div[@class="cml jsawesome" and .//h1[text()="Feedback"]]')
        indexes_to_select = random.sample(range(0, len(questions_on_page)), k=random_reject)
        LOGGER.info(f"QA select units: {indexes_to_select}")
        for r in sorted(indexes_to_select):
            el = questions_on_page[r].find_element('xpath', ".//input")
            element_to_the_middle(app.driver, el)
            time.sleep(2)
            el.click()
            time.sleep(1)


class QFFilters:
    _FILTER_MENU_BTN = "//a[.//span[text()='Filters']]"
    _FILTER_BY_NAME = "//div[@role='button']/../..//div[text()='{filter_name}']"
    _REMOVE_FILTERS = "//span[contains(text(), 'Filter')]/..//button"
    _COMPARE_TYPE = ".DatasetTab > div:nth-child(3) > div:nth-child(1) [data-test-id='option-unitDisplayId-select-{compare_type}']"

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def _expend_all_filters(self):
        second_level_btns = find_elements(self.driver, "//div[text()='Filters']/..//div[@role='button']/..")
        for _second in second_level_btns:
            _second.click()

    def expend_filter_type(self, filter_type):
        second_level_btn = find_elements(self.driver,
                                         f"//div[text()='Filters']/parent::*//*[text()='{filter_type}']/parent::*//*[@role='button']")
        second_level_btn.click()

    def select_compare_type(self, filter_type, filter_name, compare_type, filter_value):
        _second_level_btn = find_element(self.driver,
                                         f"//div[@data-react-beautiful-dnd-droppable]//*[text()='{filter_type}']")
        _second_level_btn.click()

        _filter_name = find_element(self.driver, self._FILTER_BY_NAME.format(filter_name=filter_name))
        _filter_name.click()

        _filter_name_dropdown = find_element(self.driver,
                                             f"//div[@role='button']/../..//div[text()='{filter_name}']/parent::*/parent::*/div[2]//*[@tabindex='0']")
        _filter_name_dropdown.click()
        _compare_type_select = find_element_by_css_selector(self.driver, self._COMPARE_TYPE.format(compare_type=compare_type.lower()))
        _compare_type_select.click()
        send_keys_by_xpath(self.driver,
                           f"//div[@role='button']/../..//div[text()='{filter_name}']/parent::*/parent::*/div[2]/div/div[2]//input",
                           filter_value)

    def select_action_filter(self, filter_name, action=None):
        index = self._get_index_action_filter(filter_name)
        if action:
            click_element_by_xpath(self.driver, f"//div[@data-react-beautiful-dnd-droppable]/div[{index}]//*[text()='{action}']")
            time.sleep(4)

    def _get_index_action_filter(self, filter_name):
        switch = {
            "Unit ID": 2,
            "replica": 3,
            "dataset Row Type": 4,
            "Status": 5,
            "source File Batch Number": 6,
            "row Number": 7,
            "MD5 Hash": 8,
            "created At": 9,
            "unit Segment Type": 10,
            "unit Segment ID": 11,
            "Question ID": 12,
        }
        return switch.get(filter_name, None)

    def open_filter_menu(self):
        with allure.step(f'Open Filters menu'):
            click_element_by_xpath(self.driver, self._FILTER_MENU_BTN)
            time.sleep(1)

    def get_all_filters(self):
        with allure.step(f'Get current filter structure'):
            self.open_filter_menu()
            self._expend_all_filters()
            time.sleep(1)

            all_filters = find_elements(self.driver, "//div[text()='Filters']/..//div[@role='button']/../..")
            _filters = [x.text for x in all_filters]

            return _filters

    def remove_current_filter(self):
        with allure.step(f'Remove all filters'):
            click_element_by_xpath(self.driver, self._REMOVE_FILTERS)
            time.sleep(4)

    def select_filter(self, filter_type, filter_name, compare_type, filter_value, action=None):
        # supports only input type for now
        with allure.step(f'Set up filter'):
            self.open_filter_menu()

            self.select_compare_type(filter_type, filter_name, compare_type, filter_value)

            if action:
                self.select_action_filter(filter_name, action)
                time.sleep(4)

    def apply_saved_filter(self, filter_name, action=None):
        # supports only input type for now
        with allure.step(f'Apply saved filter'):
            self.open_filter_menu()
            self.app.navigation.click_link('Saved Filters')
            send_keys_by_css_selector(self.driver, "[placeholder='Search Saved Filter']", filter_name)
            click_element_by_xpath(self.driver, "//*[@type='radio']/parent::*/div")
            if action:
                self.app.navigation.click_link(action)
                time.sleep(4)

    def delete_saved_filter(self, filter_name, action=None):
        # supports only input type for now
        with allure.step(f'Apply saved filter'):
            self.open_filter_menu()
            self.app.navigation.click_link('Saved Filters')
            send_keys_by_css_selector(self.driver, "[placeholder='Search Saved Filter']", filter_name, True)
            click_element_by_xpath(self.driver, "//*[@type='radio']/parent::*/parent::*//*[local-name()='svg']")
            if action:
                self.app.navigation.click_link(action)

class QFActionMenu:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def click_actions_menu(self, menu):
        with allure.step(f'Click actions menu: {menu}'):
            self.app.navigation.click_link('Actions')
            click_element_by_xpath(self.driver, f"//li[text()='{menu}']")


class QFCustomizeTable:
    _OPEN_TABLE = "//span[text()='Table' or text()='Columns']"
    _TABLE_PARAMS = "//label[@for and text()='{}']/..//input[@id]"
    _LABEL_PARAMS = "//label[@for and text()='{}']"

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def customize_data_table_view(self, select_fields=[], mode='only'):
        with allure.step(f'Select {mode} fields'):
            all_params = ['unit', 'source', 'latest', 'earliest', 'history']
            click_element_by_xpath(self.driver, self._OPEN_TABLE)
            for param in all_params:
                filter_type = find_elements(self.driver, self._TABLE_PARAMS.format(param))
                if not filter_type: continue
                current_status = get_attribute_by_xpath(self.driver, self._TABLE_PARAMS.format(param), 'checked')
                if ((param in select_fields) and (current_status != 'true')) \
                        or ((current_status == 'true') and (param not in select_fields)):
                    click_element_by_xpath(self.driver, self._LABEL_PARAMS.format(param))

                # if status is checked - do double-click to enable all nested columns
                if (current_status == 'true') and (param in select_fields):
                    click_element_by_xpath(self.driver, self._LABEL_PARAMS.format(param))
                    click_element_by_xpath(self.driver, self._LABEL_PARAMS.format(param))

            click_element_by_xpath(self.driver, self._OPEN_TABLE)
            time.sleep(2)


class QFUnitTable:
    _SELECT_ALL_UNITS = "//thead//th[.//input[@type='checkbox']]//label"
    _CHECKBOX_UNIT = ".//td[.//input[@type='checkbox']]//label"
    _FIND_UNIT_BY_VALUE_IN_COLUMN = "//tbody//tr[.//td[{column_value}][contains(.,'{value}')]]"
    _DATA_TABLE_COLUMNS = "//thead//tr[{th_index}]//th[.//div[text()]]"

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def select_all_units(self):
        click_element_by_xpath(self.driver, self._SELECT_ALL_UNITS)

    def find_table_row_by(self, by='column_index', column_value=None, value=None, index=0):
        with allure.step(f'Find row with unit by {by} = {column_value}: {value}'):
            if by == 'column_index':
                row = find_elements(self.driver,
                                    self._FIND_UNIT_BY_VALUE_IN_COLUMN.format(column_value=column_value, value=value))
                if len(row) > index:
                    return row[index]
                return None

    def _select_unit(self, unit):
        with allure.step(f'Select unit'):
            el = unit.find_elements('xpath', self._CHECKBOX_UNIT)
            assert len(el), "Checkbox has not been found"
            el[0].click()

    def _select_checkbox_by_index(self, index):
        with allure.step(f'Select unit from index {index}'):
            el = find_element(self.driver, f"//table/tbody/tr[{index}]//label")
            el.click()

    def _select_checkbox_by_unit_id(self, unit_id):
        with allure.step(f'Select unit from unit Id {unit_id}'):
            el = find_element(self.driver,
                              f"//table/tbody/tr//a[text()='{unit_id}']/parent::td/parent::tr/td[1]//label")
            el.click()

    def get_columns_unit_table(self, th_index=2):
        with allure.step('Get columns for data table'):
            header = find_elements(self.driver, self._DATA_TABLE_COLUMNS.format(th_index=th_index))
            return [x.text for x in header]

    def get_columns_unit_table_test_question(self, th_index=1):
        with allure.step('Get columns for data table'):
            header = find_elements(self.driver, self._DATA_TABLE_COLUMNS.format(th_index=th_index))
            return [x.text for x in header]

    def _get_table_rows(self):
        all_rows = find_elements(self.driver, "//tbody//tr")
        data = []
        for row in all_rows:
            data_columns = row.find_elements('xpath', ".//td[not (.//input)]")
            row_data = [x.text for x in data_columns]
            data.append(row_data)

        return data
