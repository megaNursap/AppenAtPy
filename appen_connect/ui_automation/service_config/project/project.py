import time
from faker import Faker
import datetime
import allure
from selenium.webdriver.common.keys import Keys
from appen_connect.ui_automation.service_config.project.process import Process
from appen_connect.ui_automation.service_config.project.project_invoice_payment import Payment
from appen_connect.ui_automation.service_config.project.project_overview import Overview
from appen_connect.ui_automation.service_config.project.project_recruitment import Recruitment
from appen_connect.ui_automation.service_config.project.project_registration import Registration
from appen_connect.ui_automation.service_config.project.project_support import Support
from appen_connect.ui_automation.service_config.project.project_tools import Tools
from appen_connect.ui_automation.service_config.project.project_user import UserProject
from adap.ui_automation.utils.js_utils import mouse_over_element, set_innerHTML
from adap.ui_automation.utils.selenium_utils import find_elements, find_element


class Project:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.overview = Overview(self)
        self.registration = Registration(self)
        self.tools = Tools(self)
        self.recruitment = Recruitment(self)
        self.payment = Payment(self)
        self.user_project = UserProject(self)
        self.support = Support(self)
        self.process = Process(self)


    def create_new_project(self, use_old_interface=False):
        with allure.step('Create new project'):
            self.app.navigation.click_link('Partner Home')
            self.app.navigation.switch_to_frame("page-wrapper")
            self.app.navigation.click_btn('Create New Project')

            self.driver.switch_to.parent_frame()
            if use_old_interface:
                self.app.navigation.click_link('Use previous interface')
            else:
                self.app.navigation.click_link('Try new setup experience')
                iframe = find_element(self.driver, "//iframe[@name='page-wrapper']")
                self.driver.switch_to.frame(iframe)

            time.sleep(1)


    def identify_customer(self, pytest_env):
        customer = 'Appen Internal'
        if pytest_env == "prod":
            customer = 'Avalon'
        return customer

    def enter_data(self, data, elements, index=0):
        with allure.step('Fill out fields. Project overview page. %s' % data):
            print(elements)
            for field, value in data.items():
                if value:
                    if elements[field]['type'] == 'dropdown':
                        print(field)
                        el = find_elements(self.app.driver,
                                           "//label[.='%s' or .//h5[text()='%s']]/..//div[contains(@class,'container') or contains(@data-baseweb, 'container') or contains(@data-baseweb, 'select')]" % (
                                               field, field))
                        print("-=-=-", el)
                        if len(el) == 0 and elements[field]['xpath']:
                            print("here")
                            el = find_elements(self.app.driver, elements[field]['xpath'])

                        if len(el) == 0:
                            print("here0")
                            el = find_elements(self.app.driver,
                                               "//label[contains(text(),'%s') or .//h5[text()='%s']]/../..//div[contains(@class,'container') or contains(@data-baseweb, 'container') or contains(@data-baseweb, 'select')]" % (
                                                   field, field))
                        if len(el) == 0:
                            print("here1")
                            el = find_elements(self.app.driver,
                                               "//label[contains(.,'%s') or .//h5[text()='%s']]/../..//div[contains(@class,'container') or contains(@data-baseweb, 'container') or contains(@data-baseweb, 'select')]" % (
                                                   field, field))


                        assert len(el), "Field %s has not been found" % field
                        el[index].click()

                        time.sleep(2)
                        option = find_elements(self.app.driver,
                                               '//div[contains(@id,"react-select")][.//div[text()="%s"]]' % value)

                        if len(option) == 0:
                            print("-=-=1")
                            option = find_elements(self.app.driver,
                                                       '//li[.//div[contains(@data-baseweb,"block") and contains(text(),"%s")]]' % value)

                        if len(option) == 0:
                            print("-=-=2")
                            option = find_elements(self.app.driver,
                                                   "//div[contains(@data-baseweb,'block') and contains(text(),'%s')]/..//input/.." % value)

                        if len(option) == 0:
                            print("-=-=3")
                            option = find_elements(self.app.driver,
                                                   "//div[contains(@data-baseweb,'block') and contains(.,'%s')]" % value)

                        # if len(option) == 0:
                        #     print("-=-=4")
                        #     option = find_elements(self.app.driver, "//input[@aria-autocomplete='list']")

                        # "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % value)

                        # print(self.driver.page_source)
                        # for e in option:
                        #     print(e.get_attribute('innerHTML'))
                        assert len(option), "Value %s has not been found" % value
                        option[0].click()
                        time.sleep(1)


                    elif elements[field]['type'] in ['input', 'calendar', 'file']:
                        # enable_element_by_type(self.app.driver, elements[field]['type'])
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        try:
                            el[index].clear()
                        except:
                            print("Error to clear element")
                        if elements[field]['type'] != 'file':
                            el = find_elements(self.app.driver, elements[field]['xpath'])
                            current_value = el[index].get_attribute('value')
                            if current_value:
                                for i in range(len(current_value) + 1):
                                    try:
                                        el[index].send_keys(Keys.BACK_SPACE)
                                    except:
                                        print("done")
                        try:
                            #  for calendars
                            el = find_elements(self.app.driver, elements[field]['xpath'])
                            el[index].click()
                        except:
                            print("done")
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), f"Element {field} with xpath \"{elements[field]['xpath']}\" not found"
                        el[index].send_keys(value)
                    elif elements[field]['type'] == 'checkbox':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        el[index].click()
                    elif elements[field]['type'] == 'textarea':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        if len(el) >= 0:
                            assert len(el), "Field %s has not been found" % field
                            el[index].send_keys(value)
                        else:
                            self.textarea_populate(value, elements[field]['xpath'])
                    time.sleep(2)

    def manage_ordered_list(self, switch_on=True):
        with allure.step("Click button 'Ordered'"):
            el = find_elements(self.app.driver, "//div[contains(@class,'rdw-option-wrapper') and @aria-selected]")
            assert len(el), "Button 'Ordered List' not found"
            is_turned_on = el[0].get_attribute('aria-selected')
            if switch_on:
                if 'false' in is_turned_on:
                    el[0].click()
            else:
                if 'true' in is_turned_on:
                    el[0].click()

    def remove_data(self, data, elements):
        with allure.step('Remove data: %s' % data):
            for field in data:
                el = find_elements(self.app.driver, elements[field]['xpath'])
                assert len(el), "Field %s has not been found" % field
                current_value = el[0].get_attribute('value')
                for i in range(len(current_value)):
                    el[0].send_keys(Keys.BACK_SPACE)

    def textarea_populate(self, value_list, xpath):
        with allure.step('Enter ordered data'):
            el = find_elements(self.app.driver, xpath)
            assert len(el) > 0, f"Textarea {xpath} not found"
            data = str(value_list).split('|')
            opt_lst = find_elements(self.app.driver,
                                    "//div[contains(@class,'public-DraftStyleDefault-block')]//span[@data-text]")
            # assert len(opt_lst), 'Textarea is empty'
            for index in range(len(opt_lst)):
                set_innerHTML(self.app.driver, opt_lst[index], ' ')
                set_innerHTML(self.app.driver, opt_lst[index], data[index])

    def project_setup_status(self):
        el = find_elements(self.app.driver, "//h1[text()='Project Setup']/..//div[contains(text(),'%')]")
        assert len(el), "Project status has not been found"
        return el[0].text

    def secure_ip_disable(self):
        # checking the presence of secure IP Access
        secure_ip = find_elements(self.app.driver,
                                  "//input[@name='hasIPRestrictions']")
        assert len(secure_ip), "Secure IP Access has not been found"

        # checking secure IP is disabled
        el = find_elements(self.app.driver,
                           "//div[(@title='Option available only when a Secure Facility Tenant is configured.')]")
        if len(el) > 0: return True
        return False

    def verify_project_info(self, data):
        with allure.step('Verify project info: %s' % data):
            for section, value in data.items():
                el = find_elements(self.app.driver, "//label[text()='%s']/../div" % section)
                if len(el) == 0:
                    el = find_elements(self.app.driver, "//label[text()='%s']/../p" % section)
                    assert len(el), "Field %s has not been found" % section

                if section == "Project Name":
                    expected_result = value + f" ({data['Project Alias']})"
                    assert el[0].text == expected_result, "{section}:Expected result: %s; Actual result: %s" % (
                    expected_result, el[0].text)
                else:
                    assert el[0].text == value, f"{section}: Expected result: %s; Actual result: %s" % (
                    value, el[0].text)

    def get_project_info_for_section(self, section):
        with allure.step('get project info for section: %s' % section):
            el = find_elements(self.app.driver, "//label[text()='%s']/../div" % section)
            if len(el) == 0:
                el = find_elements(self.app.driver, "//label[text()='%s']/../p" % section)
            if len(el) == 0:
                el = find_elements(self.app.driver, "//label[text()='%s']/.." % section)
            assert len(el), "Field %s has not been found" % section
            return el[0].text

    def navigate_pages(self, tab):
        with allure.step('navigate_tab: %s' % tab):
            el = find_elements(self.app.driver, "//div[.//h3]//span[text()='%s']" % tab)
            assert len(el), "%s tab has not been found " % tab
            el[0].click()

    def checkbox_by_text_is_selected_ac(self, name):
        with allure.step('Get checkbox status by text: %s' % name):
            el = find_elements(self.app.driver, "//label[.//div[text()='%s']]//input[@type='checkbox']" % name)
            if len(el) > 0:
                return el[0].is_selected()
            else:
                assert False, "Checkbox with text - %s has not been found" % name

    def load_project(self, data, elements):
        with allure.step('Verify Load Project. %s' % data):
            for field, value in data.items():
                if value:

                    if elements[field]['type'] == 'input' or elements[field]['type'] == 'calendar' or elements[field][
                        'type'] == 'textarea':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        current_value = el[0].get_attribute('value')
                        if field == "Project Name":
                            # assert current_value.startswith({data['Customer']}), f"Field {field} should start from {data['Customer']}"
                            assert value in current_value, f"Field {field} should contain {value}"
                            # assert current_value.endswith(f"({data['Project Alias']})"), f"Field {field} should end with ({data['Project Alias']})"
                        else:
                            assert current_value == value, f"{field}: Load Expected result: {value}; Actual result: {current_value}"
                    elif elements[field]['type'] == 'checkbox':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        current_value = el[0].get_attribute("checked")
                        print("=======", current_value)
                        if current_value != value:
                            el = find_elements(self.app.driver,
                                               "//label[text()='%s']/..//div[text() and contains(@class, 'singleValue')]" % field)
                            current_value = el[0].get_attribute('textContent')
                        assert current_value == value, f"{field}: Checkbox Problem. Expected result: %s; Actual result: %s" % (
                            value, current_value)
                    elif elements[field]['type'] == 'dropdown':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        current_value = el[0].get_attribute('value')
                        if current_value != value:
                            el = find_elements(self.app.driver,
                                               "//label[text()='%s']/..//div[text() and contains(@class, 'singleValue')]" % field)

                            if len(el) == 0:
                                el = find_elements(self.app.driver,
                                                   "//label[text()='%s']/../..//div[text() and contains(@class, 'singleValue')]" % field)

                            current_value = el[0].get_attribute('textContent')
                        assert current_value == value, f"{field}: Load Expected result: {value}; Actual result: {current_value}"
                    time.sleep(2)

    def click_on_step(self, link_name, on_bottom=True):
        with allure.step('Click on Step: %s' % link_name):
            link = find_elements(self.app.driver,
                                 f"//div[(normalize-space(text())='{link_name}')]")
                                 # f"or ./span[contains(text(),'{link_name}')] "
                                 # f"or //button[@data-testid='step-footer--next-button' and contains(text(),'{link_name}')]"
                                 # )
            if len(link) == 0:
                link = find_elements(self.app.driver, f"//span[contains(text(),'{link_name}')] ")

            if len(link) == 0:
                link = find_elements(self.app.driver,
                                     f"//button[@data-testid='step-footer--next-button' and contains(text(),'{link_name}')]")

            if len(link) == 0:
                link = find_elements(self.app.driver, f"//div[@data-testid and normalize-space(text())='{link_name}']")

            if len(link) == 0:
                link = find_elements(self.app.driver,
                                 f"//div[contains(text(),'{link_name}')]")

            # if link_name == 'User Project Page':
            #     link = find_elements(self.driver, "//div[@data-testid and text()='%s']" % link_name)
            assert len(link) > 0, f"Link to Step {link_name} has not been found"
            if len(link) > 0:
                link[0].click()
            time.sleep(4)

    def project_config_table_data(self, table, skipTail=2):
        with allure.step('return the rows in the table %s' % table):

            headers = []
            table_el = find_elements(self.app.driver,
                                     "//h3[contains(text(),'%s')]/../table[@class='stat-table']" % table)
            assert len(table_el), "Table is %s not found" % table_el
            th = table_el[0].find_elements('xpath',".//th")
            assert len(th), "Header %s not found " % th
            for i in th:
                headers.append(i.text)
            rows = table_el[0].find_elements('xpath',".//tr")
            assert len(rows), "Rows %s not found " % rows
            data = []
            for i, tr in enumerate(rows):
                if (i + skipTail) >= len(rows):
                    break
                # parse row
                row_map = {}
                for j, cell in enumerate(tr.find_elements('xpath',".//td")):
                    if len(headers) > j:
                        h = headers[j]
                        row_map[h] = cell.text
                # aggregate rows
                data.append(row_map)

            return data

    def verify_input_row_match_config_table_row(self, expected_row, actual_data_table):
        for actual_row in actual_data_table:
            matched_items = dict(actual_row.items() & expected_row.items())
            if matched_items == expected_row:
                return True
        return False

    def close_error_msg(self):
        el = find_elements(self.app.driver, "//img[@role='button' and @alt='hide error']")
        for i in range(0, len(el)):
            el[i].click()
        time.sleep(1)

    def get_header_info(self):
        project_status = self.get_project_info_for_section('Status')
        el = find_elements(self.app.driver, "//div[text()='%s']/../p" % project_status)
        assert len(el) > 0, "Project header not found"
        return el[0].text

    def get_action_in_header_info(self, action_name):
        el = find_elements(self.app.driver, "//button[text()='Enable Project']/../..//span")
        mouse_over_element(self.driver, el[0])
        if action_name == 'Delete':
            actions = find_elements(self.app.driver,
                                    "//div[@title='This option is not available.']//div[@role='button']//div[text()='%s']" % action_name)
        else:
            actions = find_elements(self.app.driver, "//div[@role='button']//div[text()='%s']" % action_name)
        assert len(actions) > 0, "action with name %s is not found" % action_name
        return actions[0]

    def click_header_info(self, header):
        el = find_elements(self.app.driver, "//div[text()='%s']" % header)
        assert len(el), "Header has not been found"
        el[0].click()
        time.sleep(1)

    def apply_project(self):
        el = find_elements(self.app.driver, "//button[text()='Apply']")
        assert len(el), "Apply has not been found"
        el[0].click()
        time.sleep(4)
        el = find_elements(self.app.driver, "//button[text()='Continue To Registration']")
        assert len(el), "Continue To Registration has not been found"
        el[0].click()
        # right now, redirect takes time
        time.sleep(3)

    def work_this_project(self):
        el = find_elements(self.app.driver, "//button[text()='Work This']")
        assert len(el), "Work This has not been found"
        el[0].click()
        time.sleep(2)

    def get_count_registered_vendors(self):
        el = find_elements(self.app.driver, "//label[text()='Registered']/following-sibling::div")
        assert len(el) > 0, "Info: REGISTERED vendors has not been found"
        return el[0].text

    def get_count_qualified_vendors(self):
        el = find_elements(self.app.driver, "//label[text()='Qualified']/following-sibling::div")
        assert len(el) > 0, "Info: QUALIFIED vendors has not been found"
        return el[0].text
