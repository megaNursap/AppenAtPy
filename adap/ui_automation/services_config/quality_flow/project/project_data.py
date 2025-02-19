import time

import allure
import pandas as pd

from adap.api_automation.utils.data_util import convert_str_to_int
from adap.ui_automation.services_config.quality_flow.components import QFUnitTable, QFCustomizeTable, QFFilters
from adap.ui_automation.utils.selenium_utils import find_elements, get_text_by_xpath, click_element_by_xpath, \
    send_keys_by_xpath, find_element, click_element_by_css_selector, send_keys_by_css_selector


class QualityFlowProjectData(QFUnitTable):
    _UNITS_COUNT_BY_TYPE = "//span[text()='{}']/../../following-sibling::span"
    _UNITS_COUNT_BY_TYPE_OLD = "//span[text()='{}']/../following-sibling::span"

    _DATASET_TAB = "[data-test-id='{tab_name}']"

    def __init__(self, project, app):
        super().__init__(app)
        self.project = project
        self.app = app
        self.driver = self.app.driver
        self.data_group = QFDataGroup(app)
        self.all_data = QFAllData(app)
        self.deleted = QFDataDeleted(app)
        self.score = QFScores(app)

    def open_data_tab(self, tab_name):
        with allure.step(f'Open dataset tab: {tab_name}'):
            click_element_by_css_selector(self.driver, self._DATASET_TAB.format(tab_name=tab_name))
            time.sleep(2)

    def get_dataset_info(self, segmented=False, judgments=False):
        with allure.step('Get details about uploaded data'):
            _total = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format('total units'))
            _new = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE_OLD.format('NEW'))
            _assigned = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE_OLD.format('UNITS RAW SUBMISSIONS'))
            _judgeable = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE_OLD.format('JUDGABLE'))

            result = {
                "new_units": convert_str_to_int(_new),
                "total_units": convert_str_to_int(_total),
                "assigned_units": convert_str_to_int(_assigned),
                "judgeable_units": convert_str_to_int(_judgeable)
            }

            if segmented:
                _total_unit_groups = get_text_by_xpath(self.driver,
                                                       self._UNITS_COUNT_BY_TYPE.format('total unit groups'))
                result['total_unit_groups'] = int(_total_unit_groups)

            if judgments:
                _rejected = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format('qa rejected'))
                _accepted = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format('qa accepted'))

                result['qa_rejected'] = int(_rejected)
                result['qa_accepted'] = int(_accepted)

            return result

    def search_data_unit(self):
        pass

    def unselect_all_data_units(self):
        pass

    def unselect_data_units_by(self):
        pass

    def sort_data_table_by(self):
        pass

    def click_action_for_data_table(self):
        pass


class QFAllData(QFUnitTable, QFCustomizeTable, QFFilters):
    _UPLOAD_DATA = "//input[@type='file' and @name='file']"
    _JOB_SEARCH = "//label[@for='selectJob']/..//input[@name='search']"
    _SAMPLE_TYPE = "//label[@for='sample']/following-sibling::div"
    _SAMPLE_TYPE_VALUE = "//label[@for='sample']/following-sibling::div//li[text()='{}']"
    _SAMPLE_VALUE = "//input[@name='sample-values']"

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.driver = self.app.driver

    def upload_data(self, file_name, wait_time=15):
        with allure.step('Upload data file'):
            el = find_elements(self.app.driver, self._UPLOAD_DATA)
            if len(el) > 0:
                el[0].send_keys(file_name)
            else:
                print("Not able to upload data file")

            try:
                self.app.navigation.click_link("Proceed Anyway")
            except:
                print("no warning message")

            time.sleep(wait_time)

    def select_data_units_by(self, by='UNIT ID', values=[]):
        with allure.step(f'Select units by {by}: {values}'):
            columns = self.get_columns_unit_table()
            column_index = columns.index(by) + 2

            for value in values:
                unit = self.find_table_row_by(by='column_index', column_value=column_index, value=value)
                assert unit, f"Unit {value} has not been found"
                self._select_unit(unit)
                time.sleep(1)

    def select_units_checkbox_by_unit_ids(self, unit_ids):
        with allure.step(f'Select checkbox for units {unit_ids}'):
            for unit_id in unit_ids:
                self._select_checkbox_by_unit_id(unit_id)

    def get_all_units_on_page(self, segmented_groups=False):
        with allure.step('Get details about all units on the page'):
            th_index = 1 if segmented_groups else 2
            columns = self.get_columns_unit_table(th_index=th_index)
            data = self._get_table_rows()
            print(columns)
            print(data)
            return pd.DataFrame(data, columns=columns)

    def click_actions_menu(self, menu):
        with allure.step(f'Click actions menu: {menu}'):
            self.app.navigation.click_link('Actions')
            click_element_by_xpath(self.driver, f"//li[text()='{menu}']")

    def save_filters(self, filter_name, action=None):
        with allure.step(f'Save filter with name: {filter_name}'):
            self.app.navigation.click_btn_by_text('Save Filters')
            send_keys_by_css_selector(self.driver, "[name='filterName']", filter_name)
            if action:
                self.app.navigation.click_link(action)

    def clear_filters(self, filter_name):
        with allure.step(f'Clear filter with name: {filter_name}'):
            click_element_by_xpath(self.driver, f"//*[text()='{filter_name}']/parent::*/button/div")

    def send_units_to_job(self, job_name, sample_type=None, sample_value=None, action=None):
        with allure.step(f'Send units to job {job_name}. {sample_type}  {sample_value}'):
            time.sleep(2)
            # send_keys_by_xpath(self.driver, self._JOB_SEARCH, value=job_name, clear_current=True)
            click_element_by_xpath(self.driver, self._JOB_SEARCH)
            click_element_by_xpath(self.driver, f"//li[text()='{job_name}']")

            if sample_type:
                click_element_by_xpath(self.driver, xpath=self._SAMPLE_TYPE)
                click_element_by_xpath(self.driver, self._SAMPLE_TYPE_VALUE.format(sample_value))

            if sample_value:
                send_keys_by_xpath(self.driver, self._SAMPLE_VALUE)

            if action:
                self.app.navigation.click_link(action)


class QFDataGroup(QFUnitTable):
    _DATA_GROUP_NAME = "//input[@name='NameInput']"
    _DATA_GROUP_TABLE_COLUMNS = "//thead//th[.//div[text()]]"
    _FIND_DATA_GROUP_BY = "//tbody[@role='rowgroup']//tr[.//td[1][.='{value}']]"
    _DATA_GROUP_MENU = ".//li[.='{value}']"

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.driver = self.app.driver

    def get_columns_data_table(self):
        with allure.step('Get columns for data table'):
            header = find_elements(self.driver, self._DATA_GROUP_TABLE_COLUMNS)
            return [x.text for x in header]

    def fill_out_data_group_details(self, name=None, action=None):
        with allure.step(f'Create new data group with : name - {name}'):
            if name:
                send_keys_by_xpath(self.driver, self._DATA_GROUP_NAME, name, clear_current=True)
            if action:
                self.app.navigation.click_link(action)

    # TODO refactor
    def get_all_data_groups_on_page(self):
        with allure.step('Get details about data groups on the page'):
            columns = self.get_columns_data_table()
            data = self._get_table_rows()
            return pd.DataFrame(data, columns=columns)

    def get_num_units_for_new_data_group(self):
        pass

    def find_data_group_by(self, by='name', value=None, index=0):
        with allure.step(f'Find data group by {by}: {value}'):
            if by == 'name':
                rows = find_elements(self.driver, self._FIND_DATA_GROUP_BY.format(value=value))
                assert len(rows) > index, f"Data group {value} has not been found"
                return rows[index]
            return None

    def click_menu_actions_for_data_group_by(self, menu, by='name', value=None, index=0):
        with allure.step(f'Click menu Actions for data group by {by}: {value}'):
            group = self.find_data_group_by(by=by, value=value, index=index)

            self.app.navigation.click_link('Actions')
            _menu = group.find_elements('xpath', self._DATA_GROUP_MENU.format(value=menu))
            assert len(_menu), f"Menu {menu} has not been found"
            _menu[0].click()

    def confirm_to_delete_data_group(self):
        with allure.step('Tap Delete to confirm for the deletion for multiple groups'):
            confirm_delete = find_element(self.driver, "//*[text()='YES, I WANT TO DELETE IT']")
            confirm_delete.click()


class QFDataDeleted(QFUnitTable):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.driver = self.app.driver

    def get_all_deleted_units_on_page(self):
        with allure.step('Get details about all deleted units on the page'):
            columns = self.get_columns_unit_table()

            data = self._get_table_rows()
            print(columns)
            print(data)
            return pd.DataFrame(data, columns=columns)


class QFScores(QFUnitTable):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.driver = self.app.driver

    def get_confidence_score_on_unit_id(self):
        #write code to get confidence score
        pass
    def get_agreement_score_on_unit_id(self):
        #write code to get confidence score
        pass
    def get_wawa_score_on_unit_id(self):
        #write code to get confidence score
        pass