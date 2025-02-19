import time

import allure
from selenium.webdriver.common.keys import Keys


from adap.ui_automation.utils.js_utils import mouse_over_element, mouse_click_element
from adap.ui_automation.utils.selenium_utils import find_element, find_elements

class Design:

    def __init__(self, job):
        self.job = job
        self.driver = self.job.app.driver
        self.app = job.app
        self.ge = GE(self)
        self.dc = DC(self)

    def verify_job_title(self, title):
        current_title = find_element(self.driver,"//input[@name='title']").get_attribute('value')
        assert title == current_title, "Expected title: %s \n Actual title: %s" %(title, current_title)

    def update_job_title(self, title):
        el = find_element(self.driver,"//input[@name='title']")
        self.driver.execute_script("arguments[0].value = '';", el)
        el.send_keys(title, Keys.RETURN)
        time.sleep(1)

    def verify_job_instructions(self, instructions_text, section):
        pass
        # instructions = find_element(self.driver, "//h1[text()='%s']/:following-sibling::p" % section)

        # print("00000000000000000")
        # "//*[following-sibling::h1[[text()='Steps']/:following-sibling::h1] and preceding-sibling::h1[text()='Steps']]"
        #
        # "//*[following-sibling::h1[text()='Rules & Tips'] and preceding-sibling::h1[text()='Steps']]"
        # print(instructions.get_attribute('innerhtml'))


    def update_job_instructions(self, instructions_text, section ,mode='add'):
        if mode == 'add':
            instructions = find_element(self.driver, "//h1[text()='%s']" % section)
            instructions.send_keys(Keys.RETURN, "%s" % instructions_text)
        elif mode == 'overwrite':
            pass


    def update_job_cml(self, new_cml):
        pass

    def add_cml_reference(self, reference):
        pass

    def insert_data(self, data):
        pass

    def show_custom_css(self):
        pass

    def hide_custom_css(self):
        pass

    def switch_to_code_editor(self):
        with allure.step('Switch to code editor mode'):
            code_editor = find_elements(self.driver, '//a[text()="Switch to Code Editor"]')
            if len(code_editor)>0:
                code_editor[0].click()
            else:
               print("Current mode: Code editor")

    def switch_to_grafical_editor(self):
        with allure.step('Switch to grafical editor mode'):
            grafical_editor = find_elements(self.driver, '//a[text()="Switch to Graphical Editor"]')
            if len(grafical_editor)>0:
                grafical_editor[0].click()
            else:
               print("Current mode: Grafical_editor")

    def delete_cml(self):
        with allure.step('Delete CML'):
            cml_lines = find_elements(self.driver, "//div[@class='ace_line']")
            for line in cml_lines:
                self.driver.execute_script('arguments[0].innerHTML = "";', line)

    def load_cml(self, new_cml):
        with allure.step('Load CML'):
            text_area = find_element(self.driver, "//textarea")
            text_area.send_keys(new_cml)

    def add_line_to_cml(self, line):
        with allure.step('Add %s to CML'):
            text_area = find_element(self.driver, "//textarea")
            text_area.send_keys(line)

    def get_alert_message(self):
        with allure.step('Find alert message'):
            alert_message = self.driver.find_elements('xpath',
                "//div[@class='b-alert b-alert__warning']//li")
            return alert_message

    def get_danger_message(self):
        with allure.step('Find danger message'):
            danger_message = self.driver.find_element('xpath',
                "//div[@class='b-alert b-alert__danger']").text
            return danger_message

    #not working, figure out how to save changes
    # def cml_replace_string(self, old_str, new_str):
    #     with allure.step('CML: Replace string "%s" on "%s"' % (old_str, new_str)):
    #         find_el = find_elements(self.driver, "//div[@class='cml-source-code']//span[contains(text(),'%s')]" % old_str)
    #         if len(find_el) == 0:
    #             assert False, "String '%s' has not been found on CML"
    #
    #         self.driver.execute_script("arguments[0].innerText='\"%s\"'" % new_str, find_el[0])






class GE:

    def __init__(self, design):
        self.job = design.job
        self.driver = self.job.app.driver
        self.app = design.app

    def click_button_for_section(self, btn_name, section):
        xp = "//div[contains(@class,'ge-Editor__content')]//div[@class='header' and .//span[text()='%s']]" % section

        el = find_element(self.driver, xp)
        mouse_over_element(self.driver, el)
        btn = find_element(self.driver, xp+"//button[@title='%s']"% btn_name)
        btn.click()

    def side_panel_open_general_options(self):
        el = find_element(self.driver, "//div[@id='side-panel-contents']//h2[text()='General Options']/i")
        el.click()


    def side_panel_open_conditional_logic(self):
        el = find_element(self.driver, "//div[@id='side-panel-contents']//h2[text()='Conditional Logic']/i")
        el.click()

    def add_choice_for_tq(self, label, value=None):
        self.job.app.navigation.click_btn("Add Choice")

        all_choices = find_elements(self.driver, "//div[contains(@class, 'child-element-settings')]")
        new_choice = all_choices[-1]

        label_el = new_choice.find_element('xpath',".//input[contains(@name, 'label')]")
        label_el.send_keys(label)

        if value:
            value_el = new_choice.find_element('xpath',".//input[contains(@name, 'value')]")
            value_el.send_keys(value)

        save = find_element(self.driver, "//button[@id='side-panel-save-btn']")
        save.click()
        time.sleep(1)

    def add_question(self, name):
        with allure.step('Add question %s'):
            el = find_elements(self.driver, "//div[@class='ge-Editor__elementListLink']//a[text()='%s']" % name)
            assert len(el) > 0, "Element has not been found by xpath: "
            el[-1].click()
            self.app.navigation.click_btn("Add question")


    def side_panel_save(self):
        pass

    def side_panel_cancel(self):
        pass

class DC:
    def __init__(self, design):
        self.job = design.job
        self.driver = self.job.app.driver
        self.app = design.app

    def switch_to_questions_tab(self):
        with allure.step('Switch to Questions tab'):
            questions_tab = find_element(self.driver, "//a[text()='2. Questions']")
            questions_tab.click()




