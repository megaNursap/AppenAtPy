import time

import allure
from selenium.webdriver import ActionChains

from adap.ui_automation.utils.selenium_utils import find_elements, find_element
from adap.ui_automation.utils.js_utils import mouse_over_element, element_to_the_middle, mouse_click_element


class Payment:
    # XPATH
    # WORKDAY_TASK = "//input[@name='hasWorkdayTaskId']/../span[@class='overlay']"
    PROJECT_WORKDAY_TASK = "//input[@name='workdayTaskId']"
    RATE_TYPE = "//input[@name='rateType']"
    PROJECT_BUSINESS_UNIT = "//input[@name='businessUnit']"
    DEFAULT_PAY_RATES = "//*[text()='Default Pay Rates']/..//div[contains(@class,'overlay')]"
    CUSTOM_PAY_RATES = "//*[text()='Custom Pay Rates']/..//div[contains(@class,'overlay')]"
    HIRING_TARGET = "//input[@name='hiringTarget']"
    SPOKEN_FLUENCY = "//label[text()='Spoken Fluency']/..//input[contains(@id,'react-select')]"
    WRITTEN_FLUENCY = "//label[text()='Written Fluency']/..//input[contains(@id,'react-select')]"
    "//label[contains(text(),'Written Fluency')]/..//input[contains(@id,'react-select') or @value='NATIVE_OR_BILINGUAL']"
    CERTIFIED_FLUENCY = "//input[@name='certifiedFluency']/..//span[@class='overlay']"
    USER_GROUP = "//label[text()='User Group']/..//input[contains(@id,'react-select')]"
    TASK_TYPE = "//label[text()='Task Type']/..//input[contains(@id,'react-select')]"
    WORKDAY_TASK_ID_OPT = "//input[@name='workdayTaskId']"
    RATE = "//input[@name='rate']"
    AVAILABLE_PRODUCTIVE_DATA = "//input[@name='hasProductivityData']/../span[@class='overlay']"
    PM_APPROVE_LEVEL = "//input[@name='pmApprovalAtLineLevel']/../span[@class='overlay']"
    ADD_NOTES = "//input[@name='hasNotesToFinance']/../span[@class='overlay']"
    NOTES = "//textarea[@name='notesToFinance']"
    # INVOICE_TYPE = "//input[@name='invoiceType']"
    INVOICE_TYPE = "//label[text()='Invoice type']/../..//input[contains(@id, 'react')]"
    AUTO_APPROVE_INVOICE = "//input[@name='autoApproveInvoices']/../span[@class='overlay']"
    PROJECT_MANAGER_APPROVAL = "//input[@name='pmApprovalAtLineLevel']/../span[@class='overlay']"
    BASE_AUTO_APPROVAL = "//label[text()='Base auto-approval on']/..//input[contains(@id,'react-select')]"
    ACCEPTABLE_THRESHOLD = "//input[@id='varianceThreshold']"
    BASE_AUTO_GENERATION = "//label[text()='Base auto-generation on']/..//input[contains(@id,'react-select')]"

    elements = {
        # "Workday Task ID":
        #     {"xpath": WORKDAY_TASK,
        #      "type": "checkbox"
        #      },
        "PROJECT WORKDAY TASK ID":
            {"xpath": PROJECT_WORKDAY_TASK,
             "type": "input"
             },
        "Rate Type":
            {"xpath": RATE_TYPE,
             "type": "dropdown"
             },
        "Project Business Unit":
            {"xpath": PROJECT_BUSINESS_UNIT,
             "type": "dropdown"
             },
        "Default Pay Rates":
            {"xpath": DEFAULT_PAY_RATES,
             "type": "checkbox"
             },
        "Custom Pay Rates":
            {"xpath": CUSTOM_PAY_RATES,
             "type": "checkbox"
             },
        "Hiring Target":
            {"xpath": HIRING_TARGET,
             "type": "dropdown"
             },
        "Spoken Fluency":
            {"xpath": SPOKEN_FLUENCY,
             "type": "dropdown"
             },
        "Written Fluency":
            {"xpath": WRITTEN_FLUENCY,
             "type": "dropdown"
             },
        "Require certified fluency":
            {"xpath": CERTIFIED_FLUENCY,
             "type": "checkbox"
             },
        "User Group":
            {"xpath": USER_GROUP,
             "type": "dropdown"
             },
        "Task Type":
            {"xpath": TASK_TYPE,
             "type": "dropdown"
             },
        "Workday Task ID (optional)":
            {"xpath": WORKDAY_TASK_ID_OPT,
             "type": "input"
             },
        "Rate":
            {"xpath": RATE,
             "type": "input"
             },
        "Available Productivity Data":
            {"xpath": AVAILABLE_PRODUCTIVE_DATA,
             "type": "checkbox"
             },
        "Check PM Approve Level": {
            "xpath": PM_APPROVE_LEVEL,
            "type": 'checkbox'
        },
        "Add Notes to Finance": {
            "xpath": ADD_NOTES,
            "type": 'checkbox'
        },
        "Notes to Finance": {
            "xpath": NOTES,
            "type": 'input'
        },
        "Auto-approve Invoices": {
            "xpath": AUTO_APPROVE_INVOICE,
            "type": 'checkbox'
        },
        "Invoice Type":{
            "xpath": INVOICE_TYPE,
            "type": "dropdown"
        },
        "Project manager approval at line item level": {
            "xpath": PROJECT_MANAGER_APPROVAL,
            "type": 'checkbox'
        },
        "Base auto-approval on":{
            "xpath": BASE_AUTO_APPROVAL,
            "type": "dropdown"
        },
        "Acceptable Var. Threshold": {
            "xpath": ACCEPTABLE_THRESHOLD,
            "type": "input"
        },
        "Base auto-generation on":{
            "xpath": BASE_AUTO_APPROVAL,
            "type": "dropdown"
        }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data, action=None):
        xpath = "//h2[text()='Add Pay Rate' or text()='Copy Pay Rate' or text()='Edit Pay Rate' or text()='Rate' or " \
                "text()='Invoice Template Setup']/../..//button[text()='Save']"
        self.project.enter_data(data=data, elements=self.elements)
        if action == 'Save':
            find_elements(self.app.driver,
                          xpath)[0].click()

    def select_default_pay_rates(self, country, dialect):
        with allure.step(f"Select default pay rate {dialect}"):
            radio_btn = find_elements(self.app.driver, "//div[text()='Default Pay Rates']")
            radio_btn[0].click()

            el = find_elements(self.app.driver, "//label[text()='Hiring Target']/..//input/..")
            el[0].click()
            time.sleep(2)
            dialect_el = find_elements(self.app.driver, "//div[contains(@id, 'react-select') and contains(.,'%s') and "
                                                        "contains(.,'%s')]" % (country, dialect))

            assert len(dialect_el), "Dialect %s has not been found" % dialect
            dialect_el[0].click()
            time.sleep(1)

    # Function to select the the default pay rate for individual country
    def select_pay_rate(self, tenant, bus_unit, rate_type, rate, state=None, action=None):
        if not state:
            row = find_elements(self.app.driver, "//tr[td[contains(text(),'%s')]]"
                                                 "[td[contains(text(),'%s')]]"
                                                 "[td[contains(text(),'%s')]]"
                                                 "[td/span[contains(text(),'%s')]]//span[@class='overlay']" % (
                                tenant, bus_unit, rate_type, rate))

        else:
            row = find_elements(self.app.driver, "//tr[td[contains(text(),'%s')]]"
                                                 "[td[contains(text(),'%s')]]"
                                                 "[td[contains(text(),'%s')]]"
                                                 "[td/span[contains(text(),'%s')]]"
                                                 "[td[contains(text(),'%s')]]//span[@class='overlay']" % (
                                tenant, bus_unit, rate_type, rate, state))

        assert len(row) > 0, f"pay rate {rate} has not been found"
        row[0].click()
        time.sleep(2)

        if action == 'Save':
            button = find_elements(self.app.driver,
                                       "//button[@data-testid='payrates-modal--save-button']")
            assert len(button) > 0, f"Button {action} not found"
            button[0].click()
            time.sleep(3)


    # Verifying the number of rows in pay rate setup table on Invoice & payment page
    def payrate_setup_table_num_of_rows(self):
        rows = find_elements(self.app.driver, "//tbody[@role='rowgroup']/tr")
        num_of_rows = len(rows)
        return num_of_rows

    def verify_pay_rate_is_present_on_page(self, hiring_target, input_fluency, input_grp, input_work, input_taskid,
                                           input_rate, state=None, is_not=True):
        if state:
            found = find_elements(self.app.driver,
                                  "//tr[//td[@class='sticky-column last-sticky-column'][contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]" % (
                                  hiring_target, state, input_fluency, input_grp, input_work, input_taskid, input_rate))
        else:
            found = find_elements(self.app.driver,
                                  "//tr[//td[@class='sticky-column last-sticky-column'][contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]"
                                  "[.//td/div[contains(.,'%s')]]" % (
                                  hiring_target, input_fluency, input_grp, input_work, input_taskid, input_rate))
        if is_not:
            assert len(found) > 0, "\n The pay rate is NOT displayed on the page(but it should)"
        else:
            assert len(found) == 0, "\n The pay rate is displayed on the page (but it must not!)"

    def select_custom_pay_rates(self, country, dialect):
        with allure.step(f"Set Hiring Target to {country} -> {dialect}"):
            el = find_elements(self.app.driver, "//label[text()='Hiring Target']/..//input/..")
            el[0].click()
            time.sleep(2)
            print(self.app.driver.page_source)
            # dialect_el = find_elements(self.app.driver, f"//div[text()[1]='{country}' and contains(text()[2],'{dialect}')]")
            dialect_el = find_elements(self.app.driver, f"//div[contains(@id, 'react-select') and .//div[contains(.,'{country}') and contains(.,'{dialect}')]]")

            assert len(dialect_el), "Dialect %s has not been found" % dialect
            # dialect_el[0].click()
            mouse_click_element(self.app.driver, dialect_el[0])

    def load_project(self, data):
        self.project.load_project(data=data, elements=self.elements)

    def remove_data_from_fields(self, data):
        self.project.remove_data(data, self.elements)

    def __find_pay_rate(self, hiring_target, input_fluency, input_grp, input_work, input_taskid, input_rate, action,
                        custom_pay_rate=True, state=None):
        tr = find_elements(self.app.driver, "//div[text()='Pay Rates Setup']/..//tbody//tr")
        for row in tr:
            columns = row.find_elements('xpath',".//td")
            _hiring_target = columns[2].text
            if custom_pay_rate:
                _spoken_and_written_fluency = columns[3].text
                _group = columns[4].text
                _work_type = columns[5].text
                _workday_task_id = columns[6].text
                _rate = columns[7].text
            else:
                _state = columns[2].text
                _spoken_and_written_fluency = columns[3].text
                _group = columns[4].text
                _work_type = columns[5].text
                _workday_task_id = columns[6].text
                _rate = columns[7].text
            if state:
                if _hiring_target == hiring_target and _state == state and _spoken_and_written_fluency == input_fluency \
                        and _group == input_grp and _work_type == input_work and _workday_task_id == input_taskid \
                        and (input_rate in _rate):
                    settings = row.find_element('xpath',
                        ".//div[contains(@class, 'settings-icon-container')]//*[local-name() = 'svg']")
                else:
                    print("not find default pay rate")
                    return None
            else:
                if _hiring_target == hiring_target and _spoken_and_written_fluency == input_fluency and \
                        _group == input_grp and _work_type == input_work and _workday_task_id == input_taskid \
                        and (input_rate in _rate):
                    settings = row.find_element('xpath',
                        ".//div[contains(@class, 'settings-icon-container')]//*[local-name() = 'svg']")
                else:
                    print("not find custom pay rate")
                    return None
            mouse_over_element(self.app.driver, settings)
            time.sleep(1)
            settings = row.find_elements('xpath',
                ".//div[contains(@class, 'settings-icon-container')]//div[text()='%s']//.." % action)
            settings[0].click()
            time.sleep(2)
            return None

    def delete_pay_rate(self, hiring_target, input_fluency, input_grp, input_work, input_taskid,
                        input_rate, custom_pay_rate=True, state=None):
        self.__find_pay_rate(hiring_target, input_fluency, input_grp, input_work, input_taskid,
                             input_rate, "Delete", custom_pay_rate, state)
        time.sleep(1)

    def click_edit_pay_rate(self, hiring_target, input_fluency, input_grp, input_work, input_taskid,
                            input_rate, custom_pay_rate=True, state=None):
        self.__find_pay_rate(hiring_target, input_fluency, input_grp, input_work, input_taskid,
                             input_rate, "Edit", custom_pay_rate, state)
        time.sleep(1)

    def click_copy_pay_rate(self, hiring_target, input_fluency, input_grp, input_work, input_taskid,
                            input_rate, custom_pay_rate=True, state=None):
        self.__find_pay_rate(hiring_target, input_fluency, input_grp, input_work, input_taskid,
                             input_rate, "Copy", custom_pay_rate, state)
        time.sleep(1)

    def click_cancel_copy_pay_rate(self):
        find_elements(self.app.driver, "//h2[text()='Copy Pay Rate']/../..//button[text()='Cancel']")[0].click()

    def click_cancel_edit_pay_rate(self):
        find_elements(self.app.driver, "//h2[text()='Edit Pay Rate']/../..//button[text()='Cancel']")[0].click()

    def click_cancel_add_pay_rate(self):
        find_elements(self.app.driver, "//h2[text()='Add Pay Rate']/../..//button[text()='Cancel']")[0].click()

    def choose_invoice_type(self, value, action=None):
        el = find_elements(self.app.driver,
                           "//div[@data-testid='invoice-template-setup-modal-invoice-type-select']//*[local-name() = 'svg']")
        assert len(el), "Dropdown to choose invoice type is not found"
        el[0].click()
        print(self.app.driver.page_source)
        option = find_elements(self.app.driver,
                               "//div[contains(@id,'react-select')][.//div[text()='%s']]" % value)
        assert len(option), "Value %s has not been found" % value
        option[0].click()
        time.sleep(1)
        if action == 'Save':
            find_elements(self.app.driver, "//h2[text()='Invoice Template Setup']/../..//button[text()='Save']")[
                0].click()
            time.sleep(1)

    def element_is_enable(self, data):
        self.project.element_is_enable(data=data, elements=self.elements)

    def get_options_for_dropdown(self, field):
        el = find_elements(self.app.driver,
                           "//label[text()='%s']/../..//div[contains(@class,'container')]" % field)
        assert len(el), "Dropdown to choose invoice type is not found"
        el[0].click()
        options = find_elements(self.app.driver,
                                "//div[contains(@id,'react-select')]")
        result = []
        for el in options:
            _title = el.get_attribute('title')
            _name = el.find_element('xpath',".//div[not(@class)]").text

            result.append({
                "name": _name,
                "title": _title
            })

        return result

    def auto_approve_is_disable(self):
        el = find_elements(self.app.driver,
                           "//div[@title='Enabled only when “Available Productivity Data” is checked.'][.//div[text()='Auto-approve Invoices']]")

        if len(el) > 0: return True
        return False

    def click_edit_invoice_config(self):
        config = find_element(self.app.driver, "//div[text()='Invoice Configuration']")
        element_to_the_middle(self.app.driver, config)
        time.sleep(2)

        div = find_elements(self.app.driver, "//div[@class='invoice_configuration_actions']/..")

        action = ActionChains(self.app.driver)
        self.app.driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
        action.click(div[0]).pause(5).perform()
        time.sleep(1)

        el = find_elements(self.app.driver, "//div[@class='invoice_configuration_actions']//*[local-name() = 'svg']")
        mouse_over_element(self.app.driver, el[0])
        el[0].click()
        time.sleep(2)

        btn = find_elements(self.app.driver, "//div[@class='invoice_configuration_actions']//div[text()='Edit']")
        btn[0].click()

    def save_invoice_config(self):
        btn =  find_elements(self.app.driver, "//div[contains(@class,'styles_modal')]//button[text()='Save']")
        assert len(btn)> 0, "Button has not been found"
        btn[0].click()

    def btn_set_template_is_disabled(self):
        el = find_elements(self.app.driver,
                           "//div[@title='For now, request configuration of invoicing settings to the finance team using the e-mail template available.']//button[text()='Set Template']")

        if len(el) > 0: return True
        return False

