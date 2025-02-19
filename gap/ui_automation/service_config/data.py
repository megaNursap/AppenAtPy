import logging
import time

import allure

from adap.ui_automation.utils.selenium_utils import find_element, find_elements, click_element_by_xpath, \
    send_keys_by_xpath

log = logging.getLogger(__name__)


class GData:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.projectid = None
        self.project_name = None
        self.project_displayid = None


    def gap_set_current_project(self, name, displayid, projectid):
        self.project_name = name
        self.project_displayid = displayid
        self.projectid = projectid


    def gap_upload_file(self, file_name=None, close_modal_window=True, wait_time=60):
        with allure.step('Upload file: %s' % file_name):
            # if 'welcome' in self.app.driver.current_url:
            #     el = find_elements(self.app.driver, "//input[@type=`'file' and @class='dz-hidden-input']")
            # else:
            el = find_elements(self.driver, "//input[@type='file']")

            if len(el) > 0:
                el[0].send_keys(file_name)
            else:
                log.info("Not able to upload data file")
            time.sleep(wait_time)
            # if modal window "upload data" is still present - close it
            if close_modal_window:
                el = find_elements(self.driver,
                                   "//div[contains(@class, 'rebrand-Modal__header')]//*[local-name()='svg']")
                if len(el) > 0:
                    el[0].click()


    def gap_verify_data_list_not_empty(self, do_assert=True):
        with allure.step("Verify Data List is not empty"):
            self.gap_redirect_to_data_list_if_not()
            el = find_elements(self.driver, "//div[@class='ant-empty-description']")
            total = len(el)
            if not do_assert:
                return total == 0
            assert total == 0, 'Data list is empty, but shall not be'


    def gap_redirect_to_data_list_if_not(self):
        with allure.step("Redirect to Data List if not there"):
            if not self.app.g_verify.gap_verify_current_url_contain('data-center'):
                self.app.g_nav.open_gap_project_tab('Data Center')
            self.app.g_verify.text_present_on_page("Data List")


    def gap_search_data_list(self, record_id=None, batch=None, current_node=None, data_type=None, data_status=None,
                             audit_status=None, audit_num=None):
        with allure.step("Search record"):
            self.gap_redirect_to_data_list_if_not()
            self.app.g_nav.gap_click_btn("Reset")
            params = [record_id, batch, current_node, data_type, data_status, audit_status, audit_num]
            flds = find_elements(self.driver, "//form[contains(@class,'ant-form')]//input")
            assert len(flds) > 0, "Data Search form not found"
            for index, value in enumerate(params):
                if value is None:
                    continue
                if index == 0:
                    flds[index].send_keys(value)
                else:
                    flds[index].click()
                    sel = find_elements(self.driver, f"//div[contains(text(),'{value}')]")
                    if len(sel) > 0:
                        sel[0].click()

            self.app.g_nav.gap_click_btn("Search")
            time.sleep(1)
            # not self.gap_verify_data_list_not_empty(do_assert=False), f"Record {record_id} not found"


    def gap_open_unit_by_id(self, record_id):
        with allure.step('Open unit by id: %s' % record_id):
            unit = find_elements(self.driver, "//a[text()='%s']" % record_id)
            assert len(unit), "Unit %s has not been found" % record_id
            unit[0].click()


    def gap_collect_data_from_job(self, job_id=None):
        # verify that user on DATA page
        # pagination
        pass


    def gap_grab_data_info(self):
        with allure.step('Grab data info'):
            data_info = {"count_rows": 0}
            el = find_elements(self.driver, "//div[@class='rebrand-dataTables_info']")
            if len(el) > 0:
                rows = el[0].text.split(" ")
                data_info["count_rows"] = rows[-2]
            return data_info


    # def find_all_units_with_status(self, status):
    #     with allure.step('Find all units with status:%s' % status):
    #         temp_data = collect_data_from_ui_table(self.app.driver, ignore_technical_columns=False)
    #         log.info(temp_data)
    #         return temp_data.loc[temp_data.state == status]

    def gap_get_number_of_units_on_page(self):
        units = find_elements(self.driver, "//tbody//tr")
        return len(units)


    def gap_sort_data_by_column(self, column_name, order='asc'):
        current_order = find_elements(self.driver, "//th[text()='%s']" % column_name)

        if len(current_order) == 0:
            current_order = find_elements(self.driver, "//th[.//div[text()='%s']]" % column_name)

        assert len(current_order) > 0, "Column %s has not been found"
        class_info = current_order[0].get_attribute('class')
        log.debug(class_info)
        if order in class_info:
            log.info("Column %s is sorted already" % column_name)
        else:
            current_order[0].click()
        time.sleep(3)


    def gap_split_column(self, column, delimiter=None, action='Split'):
        with allure.step('Split column by:%s, delimiter: %s' % (column, delimiter)):
            el_column = find_elements(self.driver, "//label[@for='column']/..//*[local-name() = 'svg']")
            assert len(el_column) > 0, "Column field has not been found"
            el_column[0].click()

            el = find_elements(self.driver, "//li[text()='%s']" % column)
            assert len(el) > 0, "Column field has not been found"
            el[0].click()

            if delimiter:
                find_element(self.driver, "//input[@name='delimiter']").send_keys(delimiter)

            if action:
                self.app.navigation.click_link(action)

            time.sleep(3)


    def gap_data_assign_to_workflow(self, dataid, workflow_data):
        with allure.step(f"Assign data to workflow"):
            self.gap_redirect_to_data_list_if_not()
            data_audit_status = 'Not Audited'
            num_of_records = 1
            workflow_name = workflow_data.get('workflow_name')
            log.info(f"Workflow name: {workflow_name}")
            workflow_display_id = workflow_data.get('workflow_display_id')
            log.info(f"Workflow display id: {workflow_display_id}")
            workflow_id = workflow_data.get('workflow_id')
            log.info(f"Workflow id: {workflow_id}")

            # self.gap_search_data_list(record_id=dataid, audit_status=data_audit_status)
            self.gap_search_data_list(record_id=dataid)
            click_element_by_xpath(self.driver, "//span[contains(text(),'Select all results filtered')]")
            click_element_by_xpath(self.driver, "//span[contains(text(),'Assign data')]")
            self.app.g_verify.text_present_on_page("selected records")
            # TODO select num of records
            click_element_by_xpath(self.driver, "//span[contains(text(),'Select Workflow')]")
            row = find_elements(self.driver, f"//tr[@data-row-key='{workflow_id}']")
            if not len(row) > 0:
                send_keys_by_xpath(self.driver, "//input[@id='flowName']", workflow_name)
                click_element_by_xpath(self.driver, "//div[@class='ant-modal-body']//*[text()='Search']")
                time.sleep(1)
                self.app.g_verify.text_present_on_page("Total 1 items")
                row = find_elements(self.driver, f"//tr[@data-row-key='{workflow_id}']")
            assert len(row) > 0, f"Workflow {workflow_name} not found"

            click_element_by_xpath(self.driver, f"//tr[@data-row-key='{workflow_id}']//input[@type='checkbox']")
            click_element_by_xpath(self.driver, "//span[contains(text(),'OK')]")
            send_keys_by_xpath(self.driver, "//*[contains(@class,'ant-form-horizontal')]//input[@id]", num_of_records)
            self.app.g_nav.gap_click_btn("Confirm")
            self.app.g_verify.text_present_on_page("Operation completed")
            self.app.g_nav.gap_click_btn("OK")
            click_element_by_xpath(self.driver, "//span[@class='ant-modal-close-x']")
            time.sleep(3)
            log.info("Verify current data record node")
            self.gap_verify_data_record_node(record_id=dataid, workflow_name=workflow_name)
            self.app.g_verify.text_present_on_page(f"Workflow detail [{workflow_display_id}]")


    def gap_verify_data_record_node(self, record_id, workflow_name):
        with allure.step(f"Verify record {record_id} assigned to {workflow_name}"):
            data_status = 'Acquirable'
            # check current page location
            cells = find_elements(self.driver, f"//tbody//tr[@data-row-key='{record_id}']//td")
            total_cells = len(cells)
            assert total_cells > 0, f"Record {record_id} not listed in data list"
            # verify data status
            time.sleep(2)
            self.app.g_verify.text_present_on_page(data_status)
            # redirect to workflow details
            click_element_by_xpath(self.driver, f"//tbody//tr[@data-row-key='{record_id}']//td//a")
