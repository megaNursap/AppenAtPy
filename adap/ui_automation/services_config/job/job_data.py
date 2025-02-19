import csv
import json
import time

import allure

from adap.ui_automation.utils.pandas_utils import collect_data_from_ui_table
from adap.ui_automation.utils.selenium_utils import find_element, find_elements

class Data:

    def __init__(self, job):
        self.job = job
        self.app = job.app

    def upload_file(self, file_name=None, close_modal_window=True, wait_time=60):
        with allure.step('Upload file: %s' % file_name):
            el = find_elements(self.app.driver, "//input[@type='file']")

            if len(el) > 0:
                el[0].send_keys(file_name)
            else:
                print("Not able to upload data file")
            time.sleep(wait_time)
            # if modal window "upload data" is still present - close it
            if close_modal_window:
                el = find_elements(self.app.driver,
                                   "//div[contains(@class, 'rebrand-Modal__header')]//*[local-name()='svg']")
                if len(el) > 0:
                    el[0].click()

    def verify_data_present(self, data):
        pass

    def open_unit_by_id(self, id):
        with allure.step('Open unit by id: %s' % id):
            unit = find_elements(self.app.driver, "//a[text()='%s']" % id)
            assert len(unit), "Unit %s has not been found" % id
            unit[0].click()

    def collect_data_from_job(self, job_id=None):
        # verify that user on DATA page
        # pagination
        pass

    def grab_data_info(self):
        with allure.step('Grab data info'):
            data_info = {"count_rows": 0}
            el = find_elements(self.app.driver, "//div[@class='rebrand-dataTables_info']")
            if len(el) > 0:
                rows = el[0].text.split(" ")
                data_info["count_rows"] = rows[-2]
            return data_info

    def find_all_units_with_status(self, status):
        with allure.step('Find all units with status:%s' % status):
            temp_data = collect_data_from_ui_table(self.app.driver, ignore_technical_columns=False)
            print(temp_data)
            return temp_data.loc[temp_data.state == status]

    def get_number_of_units_on_page(self):
        units = find_elements(self.app.driver, "//tbody//tr")
        return len(units)

    def sort_data_by_column(self, column_name, order='asc'):
        current_order = find_elements(self.app.driver, "//th[text()='%s']" % column_name)

        if len(current_order) == 0:
            current_order = find_elements(self.app.driver, "//th[.//div[text()='%s']]" % column_name)

        assert len(current_order) > 0, "Column %s has not been found"
        class_info = current_order[0].get_attribute('class')
        print(class_info)
        if order in class_info:
            print("Column %s is sorted already" % column_name)
        else:
            current_order[0].click()
        time.sleep(3)

    def split_column(self, column, delimiter=None, action='Split'):
        with allure.step('Split column by:%s, delimiter: %s' % (column, delimiter)):
            el_column = find_elements(self.app.driver, "//label[@for='column']/..//*[local-name() = 'svg']")
            assert len(el_column) > 0, "Column field has not been found"
            el_column[0].click()

            el = find_elements(self.app.driver, "//li[text()='%s']" % column)
            assert len(el) > 0, "Column field has not been found"
            el[0].click()

            if delimiter:
                find_element(self.app.driver, "//input[@name='delimiter']").send_keys(delimiter)

            if action:
                self.app.navigation.click_link(action)

            time.sleep(3)

    def get_contributor_ids_for_unit(self):
        with allure.step('Get contributor ids for unit'):
            result = []

            rows = find_elements(self.app.driver, "//div[@id='js-worker-table']//tbody//tr")
            assert len(rows), "Contributor info has not been found"

            for row in rows:
                _data = row.find_elements('xpath',".//td")
                _contributor_id = _data[0].text
                result.append(_contributor_id)

            return result

    def get_contributor_feedback(self, index=0):
        with allure.step('Get contributor feedback'):
            feedback_el = find_elements(self.app.driver, "//div[contains(@class, 'readonly-comment') or contains(@class, 'correction-feedback')]")
            assert feedback_el, f"The feedback absent for unit or missed"
            return feedback_el[index].text

    def get_acknowledge_result(self):
        with allure.step('Get acknowledge result of contributor'):
            acknowledge_job_result = []
            check_ack_radio_btn = False
            check_dispute_radio_btn = False
            ack_els = find_elements(self.app.driver, "//div[contains(@class, 'b-AcknowledgmentPanel')]")
            assert len(ack_els) > 0, "The Acknowledge box not present on Unit page"
            comment = ack_els[0].find_element('xpath',"./div[@class='b-Comment']/div[contains(@class,'b-Comment__readonly-comment')]")
            dispute_result = ack_els[0].find_element('xpath',".//input[@id='dispute']")
            acknowledge_result = ack_els[0].find_element('xpath',".//input[@id='acknowledge']")
            if dispute_result.get_attribute('checked'):
                check_dispute_radio_btn = True
            elif acknowledge_result.get_attribute('checked'):
                check_ack_radio_btn = True
            acknowledge_job_result = ({
                "acknowledge_result": check_ack_radio_btn,
                "dispute_result": check_dispute_radio_btn,
                "comment": comment.text
            })
            return acknowledge_job_result


