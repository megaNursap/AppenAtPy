import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from adap.ui_automation.utils.selenium_utils import find_element, find_elements


class PartnerHome:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        # XPATH

    PROJECT_NAME = "//input[@name='project.name']"
    PROJECT_ALIAS = "//input[@name='project.alias']"
    WORKDAY_TASK_ID = "//input[@id='workdayId']"
    PROJECT_DESCRIPTION = "//textarea[@id='project-description']"
    PROJECT_TYPE = "//select[@name='project.workType']"
    PROJECT_RATE_TYPE = "//select[@id='select-ratetype']"
    PROJECT_BUSINESS_UNIT = "//select[@name='project.businessUnit']"

    elements1 = {
        "Project Name":
            {"xpath": PROJECT_NAME,
             "type": "input"
             },
        "Project Alias":
            {"xpath": PROJECT_ALIAS,
             "type": "input"
             },
        "Workday ID":
            {
                "xpath": WORKDAY_TASK_ID,
                "type": "input"
            },
        "Project Type":
            {"xpath": PROJECT_TYPE,
             "type": "dropdown"
             },
        "Project Rate Type":
            {"xpath": PROJECT_RATE_TYPE,
             "type": "dropdown"
             },
        "Project Business Unit":
            {"xpath": PROJECT_BUSINESS_UNIT,
             "type": "dropdown"
             }
    }

    def click_on_project_link(self, project_name):
        with allure.step('Create new project using old setup - %s' % project_name):
            el = find_elements(self.app.driver, "//a[contains(text(),'Max')]")
            assert len(el) > 0, "Link %s has not been found" % el[0]
            if len(el) > 0:
                el[0].click()
            project_link = find_elements(self.app.driver, "//a[contains(text(),'%s')]" % project_name)
            assert len(project_link) > 0, "Link %s has not been found" % project_link[0]
            if len(project_link) > 0:
                project_link[0].click()
            time.sleep(2)

    def get_project_name_on_project_list(self):
        first_project_name = ""
        link = find_elements(self.app.driver,
                             "//table//td[.//div[@Class='td-info']]/a")
        if len(link) > 0:
            first_project_name = link[0].text
        assert len(link) > 0, "Link %s has not been found" % link[0]
        return first_project_name


    def fill_in_project_description(self, project_description):
        with allure.step('Fill in your project description - %s' % project_description):
            self.driver.switch_to.frame(0)
            el = find_elements(self.driver,
                               "//body[@class='cke_editable cke_editable_themed cke_contents_ltr cke_show_borders']")
            if len(el) > 0:
                el[0].send_keys(project_description)
            time.sleep(3)
            self.driver.switch_to.default_content()

    def fill_out_fields_project(self, data={}):
        with allure.step('Fill out fields. Project overview page. %s' % data):
            self.app.navigation_old_ui.enter_data_v1(data=data, elements=self.elements1)

    def get_partner_data_info(self):
        with allure.step('Get partner data on the page'):
            headers = [x.text for x in find_elements(self.driver, "//thead//th")]
            print(headers)

            _result = []

            for row in find_elements(self.driver, "//tbody//tr"):
                columns = row.find_elements('xpath',".//td")
                index = 0
                _data = {}
                for column in columns:
                    try:
                        _data[headers[index]] = column.text
                    except:
                        _data[headers[index]] = ''
                    index += 1
                _result.append(_data)

            return _result

    def create_group(self, group_name, group_description=None):
        with allure.step('Create new group: %s' % group_name):
            try:
                self.app.navigation.click_link('Create Group')
            except:
                print("new UI")

            find_element(self.driver, "//input[@name='group.name']").send_keys(group_name)
            if not group_description: group_description = group_name
            find_element(self.driver, "//input[@name='group.description']").send_keys(group_description)
            find_element(self.driver, "//input[@name='save']").click()
            time.sleep(2)

    def _find_customer(self, customer):
        with allure.step('Find customer %s' % customer):
            self.app.navigation.click_link('Max')
            time.sleep(3)
            return find_elements(self.driver, "//tr[.//a[contains(@href,'/qrp/core/customer/view/') and "
                                              "text()='%s']]" % customer)

    def click_edit_customer(self, customer):
        with allure.step('Click Edit customer  %s' % customer):
            row_customer = self._find_customer(customer)
            assert len(row_customer) > 0, "Customer %s has not been found" % customer
            row_customer[0].find_element('xpath',".//img[@src='/qrp/images/icon_edit.gif']").click()

    def open_customer(self, customer):
        with allure.step('Open customer  %s' % customer):
            row_customer = self._find_customer(customer)
            assert len(row_customer) > 0, "Customer %s has not been found" % customer
            row_customer[0].find_element('xpath',".//a[contains(@href,'/qrp/core/customer/view')]").click()

    def add_group_to_customer(self, group_name):
        with allure.step('Add group %s' % group_name):
            self.app.navigation.click_link('Add Group')

            find_element(self.driver, "//select[@name='selectedGroupId']//option[text()='%s']" % group_name).click()
            find_element(self.driver, "//input[@name='ajaxAddGroup']").click()

    def delete_group_from_customer(self, group_name):
        with allure.step('Delete group %s from customer' % group_name):
            find_element(self.driver, "//table[@id='group-table']//tr[.//td[text()='%s']]//input[@name='ajaxRemoveGroup']" % group_name).click()

    def find_group_by(self, group, search_type='name'):
        with allure.step('Find group %s by %s' % (group, search_type)):
            self.app.navigation.click_link('Max')
            time.sleep(2)
            if search_type == 'id':
                return find_elements(self.driver, "//tr[.//a[@href='/qrp/core/partners/experiment_group?group.id=%s']]" % group)
            elif search_type == 'name':
                return find_elements(self.driver, "//tr[.//a[contains(@href,'/qrp/core/partners/experiment_group') and "
                                                  "text()='%s']]" % group)
            return None

    def click_edit_group(self, group, search_type='name'):
        with allure.step('Click Edit group %s' % group):
            row_group = self.find_group_by(group, search_type)
            assert len(row_group)>0, "Group %s has not been found" % group
            row_group[0].find_element('xpath',".//img[@src='/qrp/images/icon_edit.gif']").click()

    def edit_group(self, data, group, search_type='name'):
        with allure.step('Edit group %s' % group):
            self.click_edit_group(group, search_type)
            for param, value in data.items():
                find_element(self.driver, "//input[@name='group.%s']" % param).send_keys(value)
            find_element(self.driver, "//input[@name='save']").click()
            time.sleep(2)

    def open_experiment_for_project(self, project_name):
        with allure.step('Open experiment list for project %s ' % project_name):
            self.app.navigation_old_ui.type_in_input_field_by("name", "search", project_name)
            self.app.navigation_old_ui.click_input_btn("Go")

            el = find_elements(self.driver, "//tr[.//td[contains(text(),'%s')]]" % project_name)
            assert len(el)>0, "Project %s has not been found" % project_name

            el[0].find_element('xpath',".//a[contains(@href, '/qrp/core/partners/experiment/view')]").click()
            time.sleep(2)

    def add_experiment_group(self, group_name):
        with allure.step('Add experiment group %s ' % group_name):
            self.app.navigation.click_link("Add Group")
            time.sleep(1)
            el = find_elements(self.driver, "//select[@name='selectedGroupId']//option[text()='%s']" % group_name)
            assert len(el)>0, "Group has not been found %s" % group_name
            el[0].click()
            find_element(self.driver, "//input[@name='ajaxAddGroup']").click()

