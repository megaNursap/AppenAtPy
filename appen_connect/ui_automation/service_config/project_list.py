import allure

from adap.ui_automation.utils.js_utils import *
from adap.ui_automation.utils.selenium_utils import *


class ProjectList:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def _find_project(self, search_type, value):
        if search_type == 'name':
            return find_elements(self.driver, "//tbody//tr[.//td[.//div[text()='%s']]]" % value)
        elif search_type == 'id':
            return find_elements(self.driver, "//tbody//tr[.//td[text()='%s']]" % value)

    def open_project_by_name(self, name):
        with allure.step(f'Open project by name {name}'):
            _project = self._find_project("name", name)
            assert len(_project) > 0, "Project  %s has not been found"
            _project[0].find_element('xpath',".//div[text()='%s']" % name).click()

    def open_project_by_id(self, project_id):
        with allure.step(f'Open project by project id {project_id}'):
            _project = self._find_project("id", project_id)
            assert len(_project) > 0, "Project  %s has not been found"
            _project[0].find_element('xpath',".//td//div//div").click()

    def get_projects_on_page(self):
        with allure.step('Get projects on the page'):
            projects = find_elements(self.driver, "//tbody[@role='rowgroup']//tr")
            _projects = []
            for row in projects:
                info = row.find_elements('xpath',".//td")
                _id = info[1].text
                _name = info[2].find_element('xpath',".//div/div[text()]").get_attribute("textContent")
                _description = info[2].find_element('xpath',".//div[text()]").text
                _type = info[3].text
                _customer = info[4].text
                _status = info[5].text


                _projects.append({
                    "id": _id,
                    "name": _name,
                    "description": _description,
                    "type": _type,
                    "program": _customer,
                    "status": _status
                })
            return _projects

    def count_projects_on_page(self):
        with allure.step('Get number of projects on the page'):
            return len(find_elements(self.driver, "//tbody[@role='rowgroup']//tr"))

    def click_action_for_project(self, search_field, search_value, action):
        with allure.step('Click action for project'):
            _project = self._find_project(search_field, search_value)
            assert len(_project) > 0, "Project  %s has not been found" % search_value
            menu = _project[0].find_element('xpath',".//div//span//*[local-name()='svg']")
            mouse_over_element(self.driver, menu)
            time.sleep(1)
            mouse_click_element(self.driver, menu)
            time.sleep(2)
            action_menu = _project[0].find_element('xpath',".//div[@role='button']//div[text()='%s']/.." % action)
            action_menu.click()
            time.sleep(2)

    def click_toggle_for_project_details(self, search_field, search_value):
        with allure.step('Expand project details'):
            _project = self._find_project(search_field, search_value)
            _project[0].find_element('xpath',".//span[@title='Toggle Row Expanded']").click()

    def click_more_less_for_project(self, search_field, search_value, click_type):
        with allure.step('Expand project details'):
            _project = self._find_project(search_field, search_value)
            _project[0].find_element('xpath',".//span[@type='button' and text()='%s']" % click_type).click()

    def get_project_expanded_details(self, search_field='name', search_value=None):
        with allure.step('Get project info'):
            project = self._find_project(search_type=search_field, value=search_value)
            info = project[0].find_elements('xpath',".//td")
            _id = info[1].text
            _name = info[2].find_element('xpath',".//div/div[text()]").text
            _description = ''.join([x.text for x in info[2].find_elements('xpath',".//label[text()='Project description']/..//p")])
            _type = info[3].text
            # _alias = info[3].find_element('xpath',".//label[text()='Alias']/..").text
            _customer = info[4].text
            # _type_of_project = info[4].find_element('xpath',".//label[text()='Type of Project']/..").text
            _status = info[5].text

            return {
                "id": _id,
                "name": _name,
                "description": _description,
                "type": _type.split('Alias')[0].strip(),
                "customer": _customer.split('TYPE OF PROJECT')[0].strip(),
                "status": _status
                # "alias": _alias.replace('ALIAS', '').strip(),
                # "type_of_project": _type_of_project.replace('TYPE OF PROJECT', '').strip()
            }

    def open_context_menu_for_project(self, search_field, search_value):
        with allure.step('Click action for project'):
            _project = self._find_project(search_field, search_value)
            assert len(_project) > 0, "Project  %s has not been found" % search_value
            menu = _project[0].find_element('xpath',".//div//span//*[local-name()='svg']")
            mouse_over_element(self.driver, menu)
            time.sleep(1)
            mouse_click_element(self.driver, menu)
            time.sleep(2)
            result = {}
            for menu in _project[0].find_elements('xpath',".//div[@role='button']"):
                active_status = menu.find_elements('xpath',
                    "./..//div[@title='This will be available soon.' or @title='This option is not available.']")
                result[menu.text] = False if len(active_status) == 0 else True
            return result

    def order_project_list_by(self, column_name):
        with allure.step('Order Project list by %s' % column_name):
            column = find_elements(self.driver, "//thead//th[.//div[text()='%s']]" % column_name)
            assert len(column) > 0, "Column %s has not been found"
            column[0].click()
            time.sleep(2)

    def filter_project_list_by(self, name=None, program=None, status=None):
        with allure.step('Filter projects:'):
            if name:
                name_input = find_element(self.driver, "//input[@name='filterByText']")
                name_input.clear()
                name_input.send_keys(name)

            if program:
                program_input = find_elements(self.driver,
                                               "//button[text()='Create New Project']/..//div[@data-baseweb='block']")
                program_input[1].click()
                time.sleep(2)
                option = find_elements(self.app.driver,
                                       "//div[@data-baseweb='block' and text()='%s']" % program)
                                       # "[.//div[text()='%s']]" % customer)

                if not len(option) :
                    option = find_elements(self.app.driver,
                                           "//div[contains(@id, 'react-select')][.//div[text()='%s']]" % program)

                assert len(option), "Value %s has not been found" % program
                option[0].click()

            if status:
                status_input = find_elements(self.driver,
                                             "//button[text()='Create New Project']/..//div[@data-baseweb='block']")
                status_input[2].click()
                time.sleep(2)
                option = find_elements(self.app.driver,
                                       "//div[@data-baseweb='block' and text()='%s']" % status)
                if not len(option):
                    option = find_elements(self.app.driver,
                                           "//div[contains(@id, 'react-select')][.//div[text()='%s']]" % status)

                assert len(option), "Value %s has not been found" % status

                option[0].click()
            time.sleep(5)

    def sort_projects_by(self, field_name):
        with allure.step('Sort projects by %s' % field_name):
            field = find_elements(self.driver, "//th[.//div[text()='%s']]//button" % field_name)
            assert len(field) > 0, "Field has not been found"
            field[0].click()

    def get_project_info(self, search_field='name', search_value=None):
        with allure.step('Get project info'):
            project = self._find_project(search_type=search_field, value=search_value)
            info = project[0].find_elements('xpath',".//td")
            _id = info[1].text
            _name = info[2].find_element('xpath',".//div/div[text()]").text
            _description = info[2].find_element('xpath',".//div[text()]").text
            _type = info[3].text
            _customer = info[4].text
            _status = info[5].text

            return {
                "id": _id,
                "name": _name,
                "description": _description,
                "type": _type,
                "customer": _customer,
                "status": _status
            }

    def get_num_pages(self):
        with allure.step('Get number of pages'):
            el = find_elements(self.driver, "//button[@type='button'][not(*)]")
            if len(el) == 0: return None
            return el[-1].text


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
