import time
import allure
from selenium.webdriver.common.keys import Keys

from adap.ui_automation.utils.js_utils import inner_scroll_to_element, scroll_to_element, get_text_excluding_children
from adap.ui_automation.utils.selenium_utils import find_elements, find_element, click_element_by_xpath


class FileUpload:
    CLIENT = ""
    UPLOAD_TYPE = ""
    TEMPLATES = ""
    UPLOAD_FILE_INPUT = "//input[@data-testid='unified-upload--file-selection-form--upload-file']"
    UPLOAD_MAP_INPUT = "//span[contains(@class,'ant-upload-btn')]//input[@type='file']"
    TEMPLATE_NAME = "//input[@name='templateName']"
    DEMONIATOR_INPUT = "//input[@name='calculateByRows']"
    COLUMN_WITH_AC_PROJECT_ID = ""
    COLUMN_WITH_AC_USER_ID = ""
    COLUMN_NAME = ""
    WORK_DATA = ""
    DATE_OF_WORK = "//input[@aria-label='Select a date.']"
    TIME_WORKED = ""
    DENOMINATOR = ""
    NUMERATOR = ""
    TIME_UNIT = ""
    MULTIPLY = "//input[@name='calculateByRows']"
    BUSINESS_VALUE = "//input[@name='businessValue']"
    SEARCH_PROJECT_ALIAS = "//div[@class='Search by project alias']"
    EXCEED_VALUE = "//input[@name='exceededValue']"
    TIME_VALUE = "//input[@name='timeValue']"
    WORK_DATE = ""
    FIXED_AMOUNT = "//label[@data-baseweb='checkbox'][.//input]"

    elements = {
        "Upload Type":
            {"xpath": UPLOAD_TYPE,
             "type": "dropdown"
             },
        "Client":
            {"xpath": CLIENT,
             "type": "dropdown"
             },
        "Templates":
            {"xpath": TEMPLATES,
             "type": "dropdown"
             },
        "Timezone":
            {"xpath": "",
             "type": "dropdown"
             },
        "Upload File":
            {"xpath": UPLOAD_FILE_INPUT,
             "type": "file"
             },
        "Upload mapped file":
            {"xpath": UPLOAD_MAP_INPUT,
             "type": "file"
             },
        "Template name":
            {"xpath": TEMPLATE_NAME,
             "type": "input"
             },
        "Denominator input":
            {"xpath": DEMONIATOR_INPUT,
             "type": "input"
             },
        "COLUMN WITH AC PROJECT ID":
            {"xpath": COLUMN_WITH_AC_PROJECT_ID,
             "type": "dropdown"
             },
        "COLUMN WITH AC USER ID":
            {"xpath": COLUMN_WITH_AC_USER_ID,
             "type": "dropdown"
             },
        "COLUMN NAME":
            {"xpath": COLUMN_NAME,
             "type": "dropdown"
             },
        "column with date of work date":
            {"xpath": WORK_DATA,
             "type": "dropdown"
             },
        "select a date":
            {"xpath": DATE_OF_WORK,
             "type": "calendar"
             },
        "Column with Units of Work Completed":
            {"xpath": TIME_WORKED,
             "type": "dropdown"
             },
        "column with denominator":
            {"xpath": DENOMINATOR,
             "type": "dropdown"
             },
        "column with numerator":
            {"xpath": NUMERATOR,
             "type": "dropdown"
             },
        "time unit":
            {"xpath": TIME_UNIT,
             "type": "dropdown"
             },
        "Business value":
            {"xpath": BUSINESS_VALUE,
             "type": "input"
             },
        "Search by project alias":
            {"xpath": SEARCH_PROJECT_ALIAS,
             "type": "input"
             },
        "Exceed value":
            {"xpath": EXCEED_VALUE,
             "type": "input"
             },
        "Time value":
            {"xpath": TIME_VALUE,
             "type": "input"
             },
        "round number":
            {"xpath": TIME_UNIT,
             "type": "dropdown"
             },
        "multiply by":
            {"xpath": MULTIPLY,
             "type": "input"
             },
        "column with Production Time":
            {
                "xpath": WORK_DATE,
                "type": "dropdown"
            },
        "fixedAmount": {
            "xpath": FIXED_AMOUNT,
            "type": "checkbox"
        }

    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def enter_data(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)
        time.sleep(4)

    def get_uploaded_files_on_selection_page(self):
        with allure.step('Get list of uploaded files from File selection page'):
            el = find_elements(self.app.driver, "//div[@class='ant-upload-list-item-info']//span[@title]")
            return [x.text for x in el]

    def _find_uploaded_file_selection_page(self, file_name, index=0):
        with allure.step('Find file by name: %s on selection page' % file_name):
            el = find_elements(self.app.driver,
                               "//div[@class='ant-upload-list-item-info']//span[text()='%s']/.." % file_name)
            assert len(el) > 0, "File %s has not been found" % file_name
            return el[index]

    def delete_file_from_selection_page(self, file_name, index=0):
        with allure.step('Delete file %s selection page' % file_name):
            el = self._find_uploaded_file_selection_page(file_name, index)
            el.find_element('xpath',".//button[@title='Remove file']").click()

    def get_template_preview_info(self):
        with allure.step('Get Template preview info form template page'):
            sections = find_elements(self.app.driver,
                                     "//h4[text()='Template Preview']/../..//h4")
            _resuls = []
            for s in sections[1:]:
                labels = s.find_elements('xpath',"./following-sibling::div")
                _ = [x.text for x in labels]
                _.insert(0, s.text)
                _resuls.append(_)
            return _resuls

    def get_column_connection_steps_info(self):
        with allure.step('Get column connection steps info'):
            sections = find_elements(self.app.driver, "//h4[@data-baseweb='block']")
            _resuls = [x.text for x in sections]
            return _resuls

    def _find_column_connection(self, file_name, index=0):
        with allure.step('Find column connection by name: %s on selection page' % file_name):
            el = find_elements(self.app.driver, "//h4[@data-baseweb='block' and text()='%s']/../../.." % file_name)
            assert len(el) > 0, "File %s has not been found" % file_name
            return el[index]

    def edit_column_connection(self, file_name, index=0):
        with allure.step('Click edit column connection %s ' % file_name):
            el = self._find_column_connection(file_name, index)
            scroll_to_element(self.driver, el)
            time.sleep(1)
            el.find_element('xpath',".//*[.='Edit']").click()

    def get_unmapped_data(self):
        with allure.step('Get unmapped data info'):
            return find_element(self.app.driver, "//div[text()='unmapped data']/preceding-sibling::div").text

    def get_rows_info(self):
        with allure.step('Get rows info on Preview page'):
            accepted_row = find_elements(self.driver, "//div[text()='accepted rows']/preceding-sibling::div")

            _accepted_row = accepted_row[0].text if len(accepted_row) > 0 else None

            skipped_row = find_elements(self.driver,
                                        "//div[text()='skipped rows']/preceding-sibling::div")
            _skipped_row = skipped_row[0].text if len(skipped_row) > 0 else None

            return {
                "skipped_row": _skipped_row,
                "accepted_row": _accepted_row
            }

    def get_list_of_uploaded_files_on_page(self):
        with allure.step('Get all uploaded files from the page'):
            uploaded_files = find_elements(self.driver, "//tbody[@role='rowgroup']//tr")
            _files = []
            for row in uploaded_files:
                info = row.find_elements('xpath',".//td")
                _id = info[1].text
                _name = info[2].find_element('xpath',".//div").get_attribute("textContent")
                _days_of_work = info[3].get_attribute("textContent")
                _project = info[4].get_attribute("textContent")
                _type = info[5].text
                _creation = info[6].get_attribute("textContent")
                _status = info[7].find_element('xpath',".//span[.]").get_attribute("textContent")

                _files.append({
                    "id": _id,
                    "name": _name,
                    "days_of_work": _days_of_work,
                    "project": _project,
                    "type": _type,
                    "creation": _creation,
                    "status": _status
                })
            return _files

    def open_toggle(self, tab_name):
        with allure.step('Open job tab %s' % tab_name):
            tab = find_elements(self.app.driver,
                                "//*[contains(text(),'%s')]" % tab_name.upper())
            assert len(tab) > 0, "Tab %s has not found" % tab_name.upper()
            tab[0].click()
            time.sleep(3)

    def search_project_alias(self, search_keyword, project_info):
        with allure.step('Search project'):
            el = find_elements(self.app.driver,
                               "//div[text() = 'Search by project alias']/../../..//*[local-name() = 'svg']")
            assert len(el) > 0, "Not found dropdown icon"
            el[0].click()
            time.sleep(1)
            el = find_elements(self.app.driver, "//input[@id='projectId']")
            el[0].send_keys(search_keyword)
            time.sleep(1)
            el = find_elements(self.app.driver, "//div[contains(text(), '%s')]" % project_info)
            assert len(el) > 0, "Not found project id"
            el[0].click()
            time.sleep(1)

    def count_items_in_specific_status(self, status):
        with allure.step('Count items in status %s' % status):
            items = find_elements(self.app.driver, "//div[text()='%s']" % status)
            return len(items)

    def check_checkbox_for_time_worked(self, checkbox_text):
        with allure.step('Check the checkbox for time worked'):
            checkbox = find_elements(self.app.driver, "//label[text()='%s']/../../span" % checkbox_text)
            if len(checkbox) == 0:
                checkbox = find_elements(self.app.driver, "//div[text()='%s']/.." % checkbox_text)
            assert len(checkbox) > 0, "Checkbox is not found"
            checkbox[0].click()
            time.sleep(1)

    def select_value_for_advanced(self, title, value):
        with allure.step('Select value for advanced option'):
            time.sleep(5)

            el = find_elements(self.app.driver,
                               "//div[@role='row'][.//h4[contains(text(), '%s')]]//span[.//input]" % title)
            assert len(el), "Field has not been found"
            el[0].click()
            time.sleep(2)
            find_element(self.app.driver, "//li[.//div[text()='%s']]" % value).click()

    def check_checkbox_for_units_of_work_complete(self, checkbox_text):
        with allure.step('Check the checkbox for units of work completed'):
            checkbox = find_elements(self.app.driver, "//div[text()='%s']/.." % checkbox_text)
            assert len(checkbox) > 0, "Checkbox is not found"
            checkbox[0].click()
            time.sleep(1)

    def get_time_worked_table(self):
        columns = [x.text for x in find_elements(self.driver, "//thead//th//label")]

        result = []
        _rows = find_elements(self.driver, "//tbody//tr")
        for row in _rows:
            _cols = row.find_elements('xpath',".//td//span")
            _row_data = {}
            for index, value in enumerate(_cols):
                _row_data[columns[index]] = value.text

            result.append(_row_data)

        return result

    def get_expected_status_of_upload_file(self, file_name, expected_status):
        with allure.step('Get status of upload file'):
            status = find_elements(self.app.driver,
                                   "//*[text()='%s']/../../..//span[.='%s']" % (file_name, expected_status))
            assert len(status) > 0, "Expected status is not found"

    def click_next_template(self, btn_name='Next: Template'):
        btn = find_elements(self.app.driver,
                            "//button[text()='%s']" % btn_name)
        assert len(btn), "Button has not been found"

        inner_scroll_to_element(self.app.driver, btn[0])
        time.sleep(1)
        btn = find_elements(self.app.driver,
                            "//button[text()='%s']" % btn_name)
        btn[0].click()

    def download_preview_file_on_upload_files_page(self, file_name):
        with allure.step('Download Preview File from Upload File page'):
            _file = find_elements(self.driver, "//tr[.//td[.='%s']]")
            el = _file.find_elements('xpath',".//*[local-name() = 'svg']")
            assert len(el), 'File has not been found: %s' % file_name
            el[0].click()

            el = _file.find_elements('xpath',".//div[text()='Download Preview File']")
            assert len(el), 'Menu has not been found'
            el[0].click()

    def get_report_status_for_file(self, file_name):
        with allure.step('Get status for file '):
            _file = find_elements(self.driver, "//div[@role='row'][.//div[.='%s']]" % file_name)
            assert len(_file), 'File has not been found: %s' % file_name

            status = _file[0].find_elements('xpath',".//span[@data-baseweb='tag']//div[text()]")
            result = status[0].text

            return result

    def _find_file_upload(self, search_type, value):
        if search_type == 'name':
            return find_elements(self.driver, "//*[@id='root']//tr[.//td[.//div[text()='%s']]]" % value)
        elif search_type == 'id':
            return find_elements(self.driver, "//body//tr[.//td[text()='%s']]" % value)

    def get_num_of_all_reports(self):
        with allure.step('Return number of all report in the system'):
            el = find_elements(self.driver, "//div[contains(text(), 'Showing')]")
            assert len(el) > 0, "Information has not been found"
            return int(el[0].text.split('of ')[1])

    def set_up_show_items(self, value):
        with allure.step('Set up: showing %s items on the page' % value):
            el = find_element(self.driver, "//div[contains(text(), 'Show')]")
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", el)
            time.sleep(2)

            option = find_elements(self.driver, "//div[contains(text(), 'Show %s items')]" % value)
            assert len(option) > 0, 'Option: Showing %s items has not been found'
            option[0].click()
            time.sleep(2)

    def count_file_upload_rows_on_page(self):
        with allure.step('Get number of file upload rows on the page'):
            return len(find_elements(self.driver, "//div[@role='rowgroup']/div"))

    def click_toggle_for_file_upload_details(self):
        with allure.step('Expand Uploaded file details'):
            self.driver.find_element('xpath',"(//div[@role='rowgroup']//button[@data-baseweb='button'])[1]").click()

    def filter_file_upload_list_by(self, project_name_or_id=None, upload_type=None, status=None):
        with allure.step('Filter uploaded files:'):
            filter = find_elements(self.driver, "//div[@data-baseweb='flex-grid'][.//button[.='Upload New File']]")
            assert len(filter), "Filter has not been found"

            if project_name_or_id:
                name_input = find_element(self.driver, "//input[@id='filterByText']")
                name_input.clear()
                name_input.send_keys(project_name_or_id)

            if upload_type:
                customer_input = filter[0].find_elements('xpath',".//div[@data-baseweb='flex-grid-item'][3]")
                customer_input[0].click()
                time.sleep(1)

                option = find_elements(self.app.driver,
                                       "//li[.//div[@data-baseweb='block' and .='%s']]" % upload_type)

                assert len(option), "Value %s has not been found" % upload_type
                option[0].click()

            if status:
                status_input = filter[0].find_elements('xpath',".//div[@data-baseweb='flex-grid-item'][4]")
                status_input[0].click()
                time.sleep(2)
                option = find_elements(self.app.driver,
                                       "//li[.//div[@data-baseweb='block' and .='%s']]" % status)

                assert len(option), "Value %s has not been found" % status
                option[0].click()

            time.sleep(5)

    def uploaded_file_status(self):
        with allure.step('Get uploaded files on the page'):
            rows = find_elements(self.driver, "//div[@role='rowgroup']/div")
            _uploaded_files_status = []
            for row in rows:
                info = row.find_elements('xpath',".//div[@role='gridcell'][8]")
                _status = info[0].text

                _uploaded_files_status.append({
                    "status": _status
                })
            return _uploaded_files_status

    def click_button(self, btn_name):
        with allure.step(f'click button {btn_name}'):
            click_element_by_xpath(self.driver, f"//div[text()='{btn_name}']")
