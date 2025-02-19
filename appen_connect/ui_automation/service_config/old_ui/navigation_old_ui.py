import time
import allure
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from adap.ui_automation.utils.selenium_utils import find_elements, go_to_page


class NavigationAcUi:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.navigation = self.app.navigation

    def click_input_btn(self, btn_name):
        with allure.step('Click button: %s' % btn_name):
            btn = find_elements(self.app.driver, "//input[@value='%s']" % btn_name)
            if len(btn) == 0:
                btn = find_elements(self.app.driver,
                                    "//button[text()='%s']" % btn_name)
            assert len(btn) > 0, "Button %s has not been found"
            btn[0].click()
            time.sleep(4)

    def links_in_main_tabs(self):
        link_texts_main_tab = []
        # link_texts_main_n_sub_tabs = {}
        links_main_nav = find_elements(self.app.driver, "//div[@id='navigation']//ul/li")
        assert len(links_main_nav) > 0, "Link %s has not been found" % links_main_nav
        for i in range(0, len(links_main_nav)):
            link_texts_main_tab.append(links_main_nav[i].text)
        return link_texts_main_tab

    def sub_tab_links(self, main_nav_links):
        with allure.step('Navigation links on this page. %s' % main_nav_links):
            for i in range(0, len(main_nav_links)):
                link_texts_main_n_sub_tabs = {}
                el = find_elements(self.app.driver, "//a[contains(text(),'%s')]" % main_nav_links[i])
                assert len(el) > 0, "Link %s has not been found" % main_nav_links[i]
                el[0].click()
                time.sleep(2)
                # if (find_elements(self.app.driver, " //span[contains(text(),'Cancel')]")):
                #     self.app.navigation.click_link("Cancel")
                el1 = find_elements(self.app.driver, "//*[@id='sub-navigation']/ul/li")
                assert len(el1) > 0, "Link %s has not been found " % el1
                sub_nav_page_headings = []
                for j in range(0, len(el1)):
                    sub_nav_page_headings.append(el1[j].text)
                    link_texts_main_n_sub_tabs[main_nav_links[i]] = sub_nav_page_headings
            return link_texts_main_n_sub_tabs

    def enter_data_v1(self, data, elements):
        with allure.step('Fill out fields. Project overview page. %s' % data):
            print(elements)
            for field, value in data.items():
                if value:
                    if elements[field]['type'] == 'dropdown':
                        el = find_elements(self.app.driver,
                                           elements[field]['xpath'])
                        print(elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        Select(el[0]).select_by_visible_text(value)
                        time.sleep(1)
                    elif elements[field]['type'] == 'input' or elements[field]['type'] == 'textarea' or elements[field][
                        'type'] == 'calendar':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        print(elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        el[0].send_keys(value)
                    elif elements[field]['type'] == 'checkbox':
                        el = find_elements(self.app.driver, elements[field]['xpath'])
                        assert len(el), "Field %s has not been found" % field
                        el[0].click()
                    time.sleep(2)

    def get_columns_of_table(self):
        columns_list = []
        table_columns = self.driver.find_elements(By.XPATH, "//table[@class='data-table']//th")
        assert len(table_columns), "Element is %s not found" % table_columns
        for i in table_columns:
            columns_list.append(i.text)
        return columns_list

    def click_edit(self, link_edit):
        with allure.step('Click edit: %s' % link_edit):
            link = find_elements(self.app.driver, "//div[@class='right']//img[@title='Click to edit.']")
            if len(link) > 0:
                link[0].click()
            assert len(link) > 0, "Link %s has not been found" % link_edit
            time.sleep(2)

    def type_in_input_field_by(self, selector, value, text):
        with allure.step('Type in input'):
            xpath = "//input[@{selector}='{value}']".format(selector=selector, value=value)
            el = find_elements(self.driver, xpath)
            assert len(el), "Input has not been found"
            el[0].clear()
            el[0].send_keys(text)
            time.sleep(2)

    def type_in_input_field_project_name(self, text):
        with allure.step(f'Type in input Project name:{text}'):
            xpath = "//span[text()='Any Project']"
            el = find_elements(self.driver, xpath)
            assert len(el), "Input has not been found"
            el[0].click()
            time.sleep(2)
            el = find_elements(self.driver, "//input[@class='select2-search__field']")
            assert len(el), "Input has not been found"
            el[0].clear()
            el[0].send_keys(text, Keys.RETURN)
            time.sleep(2)


