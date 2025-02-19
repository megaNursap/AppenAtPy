import time
import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from adap.ui_automation.utils.selenium_utils import find_elements, find_element, click_element_by_xpath
from adap.ui_automation.utils.js_utils import scroll_to_element, inner_scroll_to_element, element_to_the_middle, \
    mouse_over_element


class Dpr:
    CREATE_REPORT_END_DATE = "//label[@for='endDate']/../..//div[@data-baseweb='base-input']"
    CREATE_REPORT_PROGRAM = "//input[@id='react-select-7-input']"
    TEMPLATE_NAME = "//input[@name='programName']"
    METRIC_FORMULAS = "//label[.='Metric formulas']/..//input[contains(@id,'react-select')]"
    PROJECT_NAME = "//input[@name='projectName']"
    PROGRAM_NAME = "//input[@name='officialProgramName']"
    WORKFLOW_NAME = "//input[@name='workflowName']"
    PROJECT_ALIAS = "//label[.='PROJECT ALIAS (ID)']/../..//input"
    MARKET = "//label[.='Market']/../..//input"
    LANGUAGE = "//label[.='Language']/../..//input"
    METRICS = "//input[@name='metric']"

    elements = {
        "End Date":
            {"xpath": CREATE_REPORT_END_DATE,
             "type": "calendar"
             },
        "Template Name":
            {"xpath": CREATE_REPORT_END_DATE,
             "type": "dropdown"
             },
        "Report template name":
            {"xpath": TEMPLATE_NAME,
             "type": "input"
             },
        "Metric formula":
            {"xpath": TEMPLATE_NAME,
             "type": "dropdown"
             },
        "Project name":
            {"xpath": PROJECT_NAME,
             "type": "input"
             },
        "Program name":
            {"xpath": PROGRAM_NAME,
             "type": "input"
             },
        "Workflow name":
            {"xpath": WORKFLOW_NAME,
             "type": "input"
             },
        "PROJECT ALIAS (ID)":
            {"xpath": PROJECT_ALIAS,
             "type": "input_dropdown"
             },
        "Market":
            {"xpath": MARKET,
             "type": "input_dropdown"
             },
        "Language":
            {"xpath": LANGUAGE,
             "type": "input_dropdown"
             },
        "Metric":
            {"xpath": METRICS,
             "type": "dropdown"
             }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def enter_data(self, data=None, elements=elements):
        with allure.step('Fill out fields. Daily Performance Report page. %s' % data):
            for field, value in data.items():
                if value:
                    if elements[field]['type'] == 'dropdown':
                        el = find_elements(self.app.driver,
                                           "//label[.='%s']/../..//div[@data-baseweb='select']" % field)

                        assert len(el), "Field %s has not been found" % field
                        el[0].click()
                        time.sleep(3)
                        option = find_elements(self.app.driver, ".//div[text()='%s']" % value)
                        assert len(option), "Value %s has not been found" % value
                        option[0].click()
                    elif elements[field]['type'] == 'input':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        # el[0].clear()
                        current_value = el[0].get_attribute('value')
                        for i in range(len(current_value)):
                            el[0].send_keys(Keys.BACK_SPACE)
                        el[0].send_keys(value)
                    elif elements[field]['type'] == 'calendar':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        el[0].click()
                        time.sleep(5)
                        el = find_elements(self.driver, "//div[text()='%s']" % value)
                        assert len(el)>0, "Date %s has not been found" % value
                        el[0].click()
                    elif elements[field]['type'] == 'checkbox':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        el[0].click()
                    elif elements[field]['type'] == 'input_dropdown':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        el[0].clear()
                        el[0].send_keys(value)
                        time.sleep(3)

                        option = find_elements(self.app.driver,  "//div[contains(@id,'react-select')][.//div[contains(normalize-space(text()),'%s')] and .//input[@type='checkbox']]" % value)
                        if len(option) == 0: option = find_elements(self.app.driver,  "//li[.//div[@data-baseweb='block' and contains(text(),'%s')]]" % value)

                        assert len(option), "Value %s has not been found" % value
                        option[0].click()
                    time.sleep(2)

    def setup_filter(self, index, value):
        # el = find_elements(self.app.driver, '//div[contains(@class,"override_filter__control")]')
        el = find_elements(self.app.driver, '//div[@data-baseweb="select"]')


        assert len(el), "Field Filter by %s  has not been found" % value
        el[index].click()
        time.sleep(1)
        option = find_elements(self.app.driver, '//div[contains(text(),"%s")]' % value)
        assert len(option), "Value %s has not been found" % value
        option[0].click()
        time.sleep(2)

    def find_reports(self, program=None, status=None, report_type=None, owner=None):
        with allure.step('Find report: program = %s, status = %s' % (program, status)):
            if program != None:
                el = find_elements(self.app.driver, "//input[@name='filterByText']")
                assert len(el), "Field Search by Program or creator has not been found"
                current_value = el[0].get_attribute('value')
                for i in range(len(current_value)):
                    el[0].send_keys(Keys.BACK_SPACE)
                el[0].send_keys(program)
            time.sleep(1)

            if report_type:
                self.setup_filter(index=0, value=report_type)

            if status:
                self.setup_filter(index=1, value=status)

            if owner:
                self.setup_filter(index=2, value=owner)

            time.sleep(2)

    def _search_report_on_dpr_list(self, search_field='index', value=0):
        with allure.step('Search report on DPR list by %s=%s' % (search_field, value)):
            try:
                if search_field == 'id':
                    report = find_elements(self.driver, "//div[contains(text(),'%s')]/../../div[@role='row']" % value)[0]
                if search_field == 'index':
                    report = find_elements(self.driver, "//div[@role='rowgroup']//div[@role='row']")[int(value)]
                return report
            except:
                return None

    def get_report_info_by(self, search_field='id', value=None):
        with allure.step('Get report info by %s = %s' % (search_field, value)):
            report = self._search_report_on_dpr_list(search_field, value)
            if report:
                report_columns = report.find_elements('xpath',".//div[@role='gridcell']")
                _id = report_columns[0].text

                # try:
                #     _report_type = report_columns[1].find_element('xpath',".//span").text
                # except:
                #     _report_type = ""
                _report_type = report_columns[1].text
                #print ("REPORT_TYPE",_report_type)
                #print("TEMPLATE",report.find_element('xpath',".//div[@role='gridcell'][3]").text)

                # try:
                #     _name = report_columns[2].find_element('xpath',".//span").text
                # except:
                #     _name = ""
                _name = report_columns[2].text

                report_dates = report_columns[3].find_elements('xpath',".//div[@data-baseweb='block' and text()]")
                _date = [report_dates[0].text, report_dates[1].text]

                creation = report_columns[4].find_elements('xpath',".//div[@data-baseweb='block' and text()]")
                _date_creation = creation[0].text
                _author = creation[1].text

                # _status = report_columns[5].find_element('xpath',".//div[@type]").text
                _status = report_columns[5].find_element('xpath',"//span[@data-baseweb='tag']/span//div[@data-baseweb='block' and text()]").text

                return {"id": _id,
                        "type": _report_type,
                        "name": _name,
                        "date_start": _date[0],
                        "date_end": _date[1],
                        "create_date": _date_creation,
                        "create_author": _author,
                        "status": _status
                        }
            else:
                assert False, "Report has not been found"

    def click_download_for_report(self, search_field='id', value=None):
        with allure.step('Click Download button for report'):
            report = self._search_report_on_dpr_list(search_field, value)
            assert report, "Report has not been found"
            report.find_element('xpath',".//div/button[@data-baseweb='button']/div[text()='Download']").click()

    def click_error_details_for_report(self, search_field='id', value=None):
        with allure.step('Click Download button for report'):
            report = self._search_report_on_dpr_list(search_field, value)
            assert report, "Report has not been found"
            report.find_element('xpath',".//td//button[text()='Error Details']").click()

    def sort_dpr_list_by(self, column_name):
        with allure.step('Sort DPR list by %s' % column_name):
            column = find_elements(self.driver, "//div[contains(text(),'%s')]" % column_name)
            assert len(column) > 0, "Column %s has not been found"
            column[0].click()

    def count_report_on_page(self):
        with allure.step('Count number of reports on page'):
            return len(find_elements(self.driver, "//div[@role='rowgroup']//div[@role='row']"))

    def get_all_reports_from_dpr_list(self):
        with allure.step('Get all report on the page'):
            num_reports = self.count_report_on_page()
            _reports = []
            for index in range(num_reports):
                report_info = self.get_report_info_by('index', index)

                _reports.append(report_info)
            return _reports

    def new_report_configuration(self, enddate=None, program=None, action=None):
        self.enter_data({"End Date": enddate,
                         "Template Name": program
                         }, self.elements)
        time.sleep(10)
        if action:
            self.app.navigation.click_btn(action)

    def get_program_details(self):
        with allure.step('Get details for current program'):
            header = [el.text for el in find_elements(self.driver, '//thead//th//div')]
            rows = find_elements(self.driver, "//tbody//tr[@role='row']")
            _details = []
            for row in rows:
                i = 0
                project = {}
                for column in row.find_elements('xpath',".//td"):
                    try:
                        _info = column.text
                    except:
                        _info = [r.text for r in column.find_elements('xpath',".//div")]

                    project[header[i]] = _info
                    i += 1
                _details.append(project)

            return _details

    def set_up_show_items(self, value):
        with allure.step('Set up: show %s items on the page' % value):
            el = find_element(self.driver, "//div[contains(text(), 'Show')]")
            el.click()

            option = find_elements(self.driver, "//div[contains(text(), 'Show %s items')]" % value)
            assert len(option) > 0, 'Option: Show %s items has not been found'
            option[0].click()
            time.sleep(2)

    def get_num_of_all_reports(self):
        with allure.step('Return number of all report in the system'):
            el = find_elements(self.driver, "//div[contains(text(), 'Showing')]")
            assert len(el) > 0, "Information has not been found"
            return int(el[0].text.split('of ')[1])

    def get_num_pages(self):
        with allure.step('Get number of pages'):
            el = find_elements(self.driver, "//div[@data-baseweb='block']//button//span")
            if len(el)>0:
                el[len(el)-1].click()
            if len(el) == 0: return None
            el2 = find_elements(self.driver, "//div[@data-baseweb='block']//button//span")
            print("NUMBER OF PAGES",len(el2))
            return el2[-1].text

    def get_active_page_number(self):
        with allure.step('Get active page number'):
            el = find_elements(self.driver, "//div[@data-baseweb='block']//button//span")
            if len(el) == 0: return None
            return el[0].text

    def click_pagination_btn(self, value):
        with allure.step('Click pagination button: %s' % value):
            next_previous = find_elements(self.driver,
                                          "//div[@data-baseweb='block']//button//*[local-name()='svg']")
            if value == 'next':
                next_previous[1].click()
            elif value == 'previous':
                next_previous[0].click()
            else:
                btn = find_elements(self.driver,
                                    "//div[@data-baseweb='block']//button[.//span[text()='%s']]" % value)
                assert len(btn) > 0, "Button %s has not been found"
                btn[0].click()
            time.sleep(1)

    def click_generate_new_report(self, report_type='Daily Performance Report (DPR) - v1'):
        with allure.step('Click Generate new report %s ' % report_type):
            self.app.navigation.click_btn('Generate New Report')
            click_element_by_xpath(self.driver, f'//*[contains(text(),"{report_type}")]')

    def click_create_new_template(self):
        with allure.step('Click Create New Template'):
            el = find_elements(self.driver, "//div[@role='radiogroup']//div[text()='CREATE NEW TEMPLATE']")
            assert len(el)>0, "Button Create New Template has not been found"
            el[0].click()
            time.sleep(2)

    def choose_report_template(self, name):
        with allure.step('Choose report template: %s' % name):
            el = find_elements(self.driver, "//h3[text()='Choose Report Template']/..//input")
            assert len(el)>0, "Button Create New Template has not been found"
            el[0].click()
            time.sleep(1)
            option = find_elements(self.app.driver, ".//div[text()='%s']" % name)
            assert len(option), "Value %s has not been found" % name
            option[0].click()
            time.sleep(2)

    def get_projects_info(self):
        with allure.step('Get projects details from New Template'):
            projects = find_elements(self.driver, "//div[contains(text(), 'Program')]/../../..")

            result = []
            for pr in projects:
                _project = {}
                _name = ""
                for el in pr.find_elements('xpath',".//h3"):
                   _name += el.get_attribute('innerHTML')
                _project["name"] = _name
                for _type in ['Program', 'Workflows', 'Markets', 'Performance', 'Output']:
                    _value  = pr.find_elements('xpath',".//div[text()='%s']/following-sibling::div" % _type)
                    _project[_type]  = _value[1].get_attribute('innerHTML')

                result.append(_project)
            return result

    def add_metrics(self, metric_type, value):
        with allure.step('Add metrics'):
            _btn = find_elements(self.driver, "//h4[text()='%s']/../..//h5[text()='Add Metric']/.." % metric_type)
            assert len(_btn), "Add Metrics button has not been found"
            scroll_to_element(self.driver, _btn[0])
            time.sleep(1)
            _btn[0].click()

            el = find_elements(self.app.driver,
                               # "//h3[text()='%s']/../..//label[text()='Metric']/..//div[contains(@class,'container')]//span[text()='Select']" % metric_type)
            "//h4[text()='%s']/../..//label[.='metric']/../..//div[@data-baseweb='select'][.//div[@aria-selected and not(text())]]" % metric_type)

            assert len(el), "Field %s has not been found" % metric_type
            el[0].click()
            time.sleep(2)
            option = find_elements(self.app.driver, ".//div[text()='%s']" % value)
            assert len(option), "Value %s has not been found" % value
            option[0].click()

    def click_create_report_template(self):
        time.sleep(5)
        el = find_elements(self.driver, "//button[.='Exit']/../..//button[.='Create Report Template' or .='Save Report Template']")
        assert len(el), "Create Report Template button has not been found"
        # element_to_the_middle(self.driver, el[0])
        time.sleep(2)
        el[0].click()

    def click_edit_program(self, name):
        with allure.step('Click Edit program by name'):
            gear = find_elements(self.driver, "//h3[text()='%s']/../..//*[local-name() = 'svg']" % name)
            assert len(gear), "Gear has not been found"
            mouse_over_element(self.driver, gear[0])
            time.sleep(1)
            gear[0].click()


            action = ActionChains(self.driver)
            # action.move_to_element(process).perform()
            # time.sleep(2)

            # gear = process.find_element('xpath',".//*[local-name() = 'svg']")
            # action.click(gear).perform()

            menu = find_elements(self.driver, "//*[text()='Edit Project']")
            assert len(menu) > 0, "Edit project button has not been found"
            menu[0].click()
            # action.click(menu[0]).perform()
            time.sleep(2)

    def field_is_required(self, name):
        with allure.step('Field %s is required' % name):
            el = find_elements(self.driver, "//label[.='%s']/../..//*[contains(text(),'Required')]" % name)
            if len(el)>0: return True
            return False

    def click_btn(self, btn_name):
        btn = find_elements(self.app.driver,
                            "//button[.='%s']" % btn_name)

        assert len(btn) > 0, "Button %s has not been found"
        scroll_to_element(self.app.driver, btn[0])
        time.sleep(1)
        btn[0].click()
        time.sleep(2)
        self.app.navigation.accept_alert()
        status_modal_window = find_elements(self.app.driver,
                                            "//div[@class='rebrand-popover-content']//*[local-name() = 'svg']")
        if len(status_modal_window) > 0:
            status_modal_window[0].click()
            time.sleep(1)









