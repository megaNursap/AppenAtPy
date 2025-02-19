import time

import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert

from adap.ui_automation.utils.js_utils import mouse_over_element, element_to_the_middle, mouse_click_element, \
    drag_and_drop
from adap.ui_automation.utils.selenium_utils import find_elements, find_element, create_screenshot, \
    click_and_send_keys_by_xpath, select_option_value, click_element_by_xpath


class Recruitment:
    # XPATH
    COUNTRY = "//input[@id='react-select-19-input']"
    TENANT = "//input[@id='react-select-20-input']"
    LOCALE_LANGUAGE = "//label[@for='language']/..//input[contains(@id,'react')]"
    LANGUAGE_REGION = "//label[@for='dialect']/..//input[contains(@id,'react')]"
    LOCALE_LANGUAGE_TO = "//label[@for='languageTo']/..//input[contains(@id,'react')]"
    LANGUAGE_REGION_TO = "//label[@for='dialectTo']/..//input[contains(@id,'react')]"
    RESTRICT_TO_COUNTRY = "//label[@for='country']/..//input[contains(@id,'react')]"
    # ASSIGN_OWNER = "//input[@id='react-select-26-input']"
    ASSIGN_OWNER ="//input[@name='owner']"
    HIRING_DEADLINE = "//input[@id='hiringDeadline']"
    TARGET = "//input[@name='target']"
    BLOCKING_RULES = "//input[@name='hasBlockingRules']/../span[@class='overlay']"
    BLOCK_PROJECT = "//input[@name='blockingRule0projectId']"
    PERMANENT = "//input[@name='blockingRule[0].permanent']"
    INTELLIGENT_ATTRIBUTES = "//input[@name='hasIntelligentAttributes']/../span[@class='overlay']"
    TARGET_GROUP = "//input[@name='hasTargetScreening']/../span[@class='overlay']"
    TARGET_AUDIENCE = "//input[@name='profileTargetId']"
    LINKED_PROJECTS = "//input[@name='hasLinkedProjects']/../span[@class='overlay']"
    LINKED_PROJECT = "//input[@name='linkedProject0projectId']"
    DEMOGRAPHIC = "//input[@name='showDemographics']/../span[@class='overlay']"
    ADD_NOTES = "//input[@name='hasNotesToRecruiting']/../span[@class='overlay']"
    NOTES = "//textarea[@name='notesToRecruiting']"
    AUTOSCREEN = "//input[@name='hasAutoScreening']/../span[@class='overlay']"
    MAX_USERS_DAY = "//input[@id='maxUsersPerDay']"
    MAX_USERS = "//input[@id='maxActiveUsers']"
    TARGET_GROUP_NAME = "//input[@id='processName']"
    TARGET_GROUP_DESCRIPTION = "//textarea[@name='processDescription']"
    TARGET_HOURS_TASKS = "//input[@name='targetHoursTasks']"


    elements = {
        "Country":
            {"xpath": COUNTRY,
             "type": "dropdown"
             },
        "Tenant":
            {"xpath": TENANT,
             "type": "dropdown"
             },
        "Locale Language":
            {"xpath": LOCALE_LANGUAGE,
             "type": "dropdown"
             },
        "Language Region":
            {"xpath": LANGUAGE_REGION,
             "type": "dropdown"
             },
        "Locale Language To":
            {"xpath": LOCALE_LANGUAGE_TO,
             "type": "dropdown"
             },
        "Language Region To":
            {"xpath": LANGUAGE_REGION_TO,
             "type": "dropdown"
             },
        "Restrict to Country":
            {"xpath": RESTRICT_TO_COUNTRY,
             "type": "dropdown"
             },
        "Assign Owner":
            {"xpath": ASSIGN_OWNER,
             "type": "dropdown"
             },
        "Hiring Deadline":
            {"xpath": HIRING_DEADLINE,
             "type": "calendar"
             },
        "Target":
            {"xpath": TARGET,
             "type": "input"
             },
        "Target hours/Tasks":
            {"xpath":TARGET_HOURS_TASKS,
             "type":"input"
             },
        "Blocking Rules":
            {"xpath": BLOCKING_RULES,
             "type": "checkbox"
             },
        "BLOCK PROJECT":
            {"xpath": BLOCK_PROJECT,
             "type": "dropdown"
             },
        "Intelligent Attributes": {
            "xpath": INTELLIGENT_ATTRIBUTES,
            "type": "checkbox"
        },
        "Target Screening and Data Requirements": {
            "xpath": TARGET_GROUP,
            "type": "checkbox"
        },
        "Select target audience group": {
            "xpath": TARGET_AUDIENCE,
            "type": "dropdown"
        },
        "Add Notes to Recruiting Team": {
            "xpath": ADD_NOTES,
            "type": "checkbox"
        },
        "Recruiting Notes": {
            "xpath": NOTES,
            "type": "input"
        },
        "Linked Projects": {
            "xpath": LINKED_PROJECTS,
            "type": "checkbox"
        },
        "LINKED PROJECT": {
            "xpath": LINKED_PROJECT,
            "type": "dropdown"
        },
        "Add Custom Demographic Requirements": {
            "xpath": DEMOGRAPHIC,
            "type": "checkbox"
        },
        "Auto-screening Configuration": {
            "xpath": AUTOSCREEN,
            "type": "checkbox"
        },
        "Locale": {
            "xpath": '',
            "type": "dropdown"
        },
        "Max users per day": {
            "xpath": MAX_USERS_DAY,
            "type": "input"
        },
        "Max active users": {
            "xpath": MAX_USERS,
            "type": "input"
        },
        "Group Name": {
            "xpath": TARGET_GROUP_NAME,
            "type": "input"
        },
        "Group Description": {
            "xpath": TARGET_GROUP_DESCRIPTION,
            "type": "input"
        },
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.project.enter_data(data=data, elements=self.elements)

    def load_project(self, data):
        self.project.load_project(data=data, elements=self.elements)

    def add_tenant(self, country=None, tenant=None, action='Save'):
        self.project.enter_data({"Country": country, "Tenant": tenant}, self.elements)
        if action == 'Save':
            find_elements(self.app.driver, "//h2[text()='Add Tenant']/../..//button[text()='Save']")[0].click()

    def click_save_add_tenant(self):
        find_elements(self.app.driver, "//h2[text()='Add Tenant']/../..//button[text()='Save']")[0].click()

    def click_cancel_add_tenant(self):
        find_elements(self.app.driver, "//h2[text()='Add Tenant']/../..//button[text()='Cancel']")[0].click()

    def click_cancel_hiring_target(self):
        find_elements(self.app.driver, "//h2[text()='Add Hiring Target']/../..//button[text()='Cancel']")[0].click()

    def verify_locale_tenant_is_displayed(self, country, tenant, tenant_type, is_not=True, is_view_mode=False):
        time.sleep(2)
        if is_view_mode:
            tr = find_elements(self.app.driver, "//div[text()='Locale Tenants']/../..//tbody//tr"
                                                "[.//td[text()='%s']]"
                                                "[.//td[text()='%s']]"
                                                "[.//td[text()='%s']]" % (country, tenant, tenant_type))
        else:
            tr = find_elements(self.app.driver, "//div[text()='Locale Tenants']/..//tbody//tr"
                                                "[.//td[text()='%s']]"
                                                "[.//td[text()='%s']]"
                                                "[.//td[text()='%s']]" % (country, tenant, tenant_type))

        if is_not:
            assert len(tr) > 0, "Locale tenant is not displayed on the page"
        else:
            assert len(tr) == 0, "Locale tenant is displayed on the page"

    def __find_locale_tenant(self, country, tenant, tenant_type, action):
        tr = find_elements(self.app.driver, "//div[text()='Locale Tenants']/..//tbody//tr")
        for row in tr:
            columns = row.find_elements('xpath',".//td")
            _country = columns[0].text
            _tenant = columns[1].text
            _tenant_type = columns[2].text
            if country == _country and tenant == _tenant and tenant_type == _tenant_type:
                settings = row.find_element('xpath',
                    ".//div[contains(@class, 'settings-icon-container')]//*[local-name() = 'svg']")
                mouse_over_element(self.app.driver, settings)
                time.sleep(1)
                settings = row.find_element('xpath',
                    ".//div[contains(@class, 'settings-icon-container')]//div[text()='%s']//.." % action)
                settings.click()
                time.sleep(1)
                return

    def get_locale_tenant_count(self):
        tr = find_elements(self.app.driver, "//div[text()='Locale Tenants']/..//tbody//tr")
        return len(tr)

    def delete_tenant(self, country, tenant, tenant_type):
        self.__find_locale_tenant(country, tenant, tenant_type, "Delete")
        time.sleep(1)

    def edit_tenant(self, current_country, current_tenant, current_tenant_type, new_country=None, new_tenant=None):
        self.__find_locale_tenant(current_country, current_tenant, current_tenant_type, "Edit")
        self.project.enter_data({"Country": new_country, "Tenant": new_tenant}, self.elements)
        find_elements(self.app.driver, "//h2[text()='Add Tenant']/../..//button[text()='Save']")[0].click()
        time.sleep(1)

    def add_target(self, language=None, region=None, language_to=None, region_to=None, restrict_country=None,
                   owner=None, deadline=None, target=None, target_hours="4", action='Save'):
        self.app.navigation.click_btn('Add Target')
        self.project.enter_data({"Locale Language": language,
                                 "Language Region": region,
                                 "Locale Language To": language_to,
                                 "Language Region To": region_to,
                                 "Restrict to Country": restrict_country,
                                 "Assign Owner": owner,
                                 "Hiring Deadline": deadline,
                                 "Target": target,
                                 "Target hours/Tasks": target_hours #
                                 }, self.elements)
        if len(action):
            button = find_elements(self.app.driver, f"//h2[text()='Add Hiring Target']/../..//button[text()='Save']")
            assert len(button) > 0, f"Button {action} not found"
            button[0].click()
        time.sleep(1)

    def add_block_project(self, project, multiple_projects=False):
        new_project_input = find_elements(self.app.driver, "//label[text()='BLOCK PROJECT']/..//span[text()='Type a "
                                                           "project name']")
        if len(new_project_input) == 0:
            self.app.navigation.click_btn("Add Other Project")
            new_project_input = find_elements(self.app.driver, "//label[text()='BLOCK PROJECT']/..//div[text()='Type a "
                                                               "project name']")
        assert len(new_project_input) > 0, "Input field BLOCK PROJECT has not been found"
        if multiple_projects:
            new_project_input[-1].click()
        else:
            new_project_input[0].click()
        option = find_elements(self.app.driver,
                               "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % project)

        assert len(option), "Value %s has not been found" % project
        option[0].click()
        time.sleep(1)

    def get_list_of_available_block_projects(self):
        new_project_input = find_elements(self.app.driver, "//label[text()='BLOCK PROJECT']/..//span[text()='Type a "
                                                           "project name']")
        new_project_input[0].click()
        option = find_elements(self.app.driver, "//div[contains(@id,'react-select')]")
        projects = [x.text for x in option]
        new_project_input[0].click()
        return projects

    def remove_blocked_project(self, project):
        el = find_elements(self.app.driver,
                           "//label[text()='BLOCK PROJECT']/..//*[text()='%s']/../../../../..//*[local-name() = 'svg']" % project)
        el[0].click()
        time.sleep(1)

    def click_permanent_btn(self, project):
        el = find_elements(self.app.driver, "//div[contains(@class, 'container')][.//div[text()='%s']]/../..//input["
                                            "@name='blockingRule[0].permanent']/.." % project)
        assert len(el) > 0, "Permanent bth has not been found for project %s" % project
        el[0].click()
        time.sleep(1)

    def delete_block_project(self, project):
        el = find_elements(self.app.driver,
                           "//div[contains(@class, 'container')][.//div[text()='%s']]/../..//button[contains(@data-testid,'delete')]" % project)
        assert len(el) > 0, "Delete bth has not been found for project %s" % project
        el[0].click()
        time.sleep(1)

    def add_intelligent_attributes(self, value):
        self.app.navigation.click_link('Add Intelligent Attribute')
        select_option_value(self.app.driver, select_name='intelligentAttributeNameSelect', value=value)
        time.sleep(3)
        click_element_by_xpath(self.app.driver, "//input[@name='ajaxAddIntelligentAttribute']")



    def add_linked_project(self, project, multiple_projects=False, is_edit_mode=False):
        new_project_input = find_elements(self.app.driver, "//label[text()='LINKED PROJECT']/..//span[text()='Type a "
                                                           "project name' or text()='Name of your project']")
        if len(new_project_input) == 0:
            btn_add_project = find_elements(self.app.driver,
                                            "//label[text()='LINKED PROJECT']/..//button[text()='Add Other Project']")
            assert len(btn_add_project) > 0, "Button Add new project has not been found"
            if is_edit_mode:
                btn_add_project[-1].click()
            else:
                btn_add_project[0].click()
            new_project_input = find_elements(self.app.driver,
                                              "//label[text()='LINKED PROJECT']/..//span[text()='Type a "
                                              "project name' or text()='Name of your project']")
        assert len(new_project_input) > 0, "Input field LINKED PROJECT has not been found"
        if multiple_projects:
            new_project_input[-1].click()
        else:
            new_project_input[0].click()
        option = find_elements(self.app.driver,
                               "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % project)

        assert len(option), "Value %s has not been found" % project
        option[0].click()
        time.sleep(1)

    def delete_linked_project(self, project):
        el = find_elements(self.app.driver,
                           "//div[contains(@class, 'container')][.//div[text()='%s']]/../..//button[contains(@data-testid,'linked-projects--delete')]" % project)
        assert len(el) > 0, "Delete bth has not been found for project %s" % project
        el[0].click()
        time.sleep(1)

    def get_list_of_available_linked_projects(self):
        new_project_input = find_elements(self.app.driver, "//label[text()='LINKED PROJECT']/..//span[text()='Type a "
                                                           "project name' or text()='Name of your project']")
        new_project_input[0].click()
        option = find_elements(self.app.driver, "//div[contains(@id,'react-select')]")
        projects = [x.text for x in option]
        new_project_input[0].click()
        return projects

    def click_add_other_linked_project(self):
        btn_add_project = find_elements(self.app.driver,
                                        "//label[text()='LINKED PROJECT']/..//button[text()='Add Other Project']")
        assert len(btn_add_project) > 0, "Button Add new project has not been found"
        btn_add_project[0].click()

    def __find_target(self, language, dialect, rest_country, action):
        tr = find_elements(self.app.driver, "//div[text()='Hiring Targets']/..//tbody//tr")
        for row in tr:
            columns = row.find_elements('xpath',".//td")
            _language = columns[0].text
            _dialect = columns[1].text
            _rest_country = columns[2].text
            if language == _language and dialect == _dialect and rest_country == _rest_country:
                settings = row.find_element('xpath',
                    ".//div[contains(@class, 'settings-icon-container')]//*[local-name() = 'svg']")
                mouse_over_element(self.app.driver, settings)
                time.sleep(1)
                settings = row.find_element('xpath',
                    ".//div[contains(@class, 'settings-icon-container')]//div[text()='%s']//.." % action)
                settings.click()
                time.sleep(1)

    def edit_target(self, language, dialect, rest_country, new_language=None, new_region=None,
                    new_restrict_country=None,
                    new_owner=None, new_deadline=None, new_target=None):
        self.__find_target(language, dialect, rest_country, "Edit")
        self.project.enter_data({"Locale Language": new_language,
                                 "Language Region": new_region,
                                 "Restrict to Country": new_restrict_country,
                                 "Assign Owner": new_owner,
                                 "Hiring Deadline": new_deadline,
                                 "Target": new_target
                                 }, self.elements)
        find_elements(self.app.driver, "//h2[text()='Add Hiring Target']/../..//button[text()='Save']")[0].click()
        time.sleep(1)

    def click_save_ht(self):
        find_elements(self.app.driver, "//h2[text()='Add Hiring Target']/../..//button[text()='Save']")[0].click()
        time.sleep(1)

    def click_copy_target(self, language, dialect, rest_country):
        self.__find_target(language, dialect, rest_country, "Copy")

    def copy_target(self, language, dialect, rest_country, new_language=None, new_region=None,
                    new_restrict_country=None,
                    new_owner=None, new_deadline=None, new_target=None):
        self.__find_target(language, dialect, rest_country, "Copy")
        self.project.enter_data({"Locale Language": new_language,
                                 "Language Region": new_region,
                                 "Restrict to Country": new_restrict_country,
                                 "Assign Owner": new_owner,
                                 "Hiring Deadline": new_deadline,
                                 "Target": new_target
                                 }, self.elements)
        find_elements(self.app.driver, "//h2[text()='Add Hiring Target']/../..//button[text()='Save']")[0].click()
        time.sleep(1)

    def delete_target(self, language, dialect, rest_country):
        self.__find_target(language, dialect, rest_country, "Delete")
        time.sleep(1)

    def target_activate_pause(self, language, dialect, rest_country, option, timeout=1):
        self.__find_target(language, dialect, rest_country, option)
        time.sleep(timeout)

    def remove_licked_project(self, project):
        el = find_elements(self.app.driver,
                           "//label[text()='LINKED PROJECT']/..//*[text()='%s']/../../../../..//*[local-name() = 'svg']" % project)
        el[0].click()
        time.sleep(1)

    # Verifying the hiring target row is present on the page
    def verify_hiring_target_row_present_on_page(self, loc_lang_from, loc_dialect_from=None, loc_lang_to=None,
                                                 loc_dialect_to=None,
                                                 rest_to_country=None, deadline=None, target=None, status=None, row_is_present=True):
        xpath = "//tr[.//td[contains(.,'%s')]]" % loc_lang_from
        if loc_dialect_from:
            xpath += "[.//td[contains(.,'%s')]]" % loc_dialect_from
        if loc_lang_to:
            xpath += "[.//td[contains(.,'%s')]]" % loc_lang_to
        if loc_dialect_to:
            xpath += "[.//td[contains(.,'%s')]]" % loc_dialect_to
        if rest_to_country:
            xpath += "[.//td[contains(.,'%s')]]" % rest_to_country
        if deadline:
            xpath += "[.//td[contains(.,'%s')]]" % deadline
        if target:
            xpath += "[.//td/div[contains(.,'%s')]]" % target
        if status:
            xpath += "[.//td/p[contains(.,'%s')]]" % status

        found = find_elements(self.app.driver, xpath)

        if row_is_present == True:
            assert len(found), " Hiring target row has not been found"
        else:
            assert not len(found), " Hiring target row has been found"

    def get_current_num_of_selected_params_demographic(self):
        el = find_elements(self.app.driver, "//span[text()='Select options to add parameters']/../div")
        assert len(el), "element has not been found"
        time.sleep(1)
        return el[0].text

    def set_up_demographic_requirements(self, d_type='Requirements by group', view='PERCENTAGE', params=None):
        # set up type
        el = find_elements(self.app.driver, "//label[text()='DEMOGRAPHICS TYPE']/..//div[contains(@class, 'control')]")
        assert len(el), "DEMOGRAPHICS TYPE field has not been found"
        el[0].click()
        option = find_elements(self.app.driver,
                               "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % d_type)
        assert len(option), "Value %s has not been found" % d_type
        option[0].click()

        # set up view
        el = find_elements(self.app.driver, "//label[text()='VIEW AS']/..//div[text()='%s']" % view)
        assert len(el), "VIEW AS  %s btn has not been found" % view
        el[0].click()

        if params:
            param_field = find_elements(self.app.driver, "//span[text()='Select options to add parameters']/..")
            assert len(param_field), "Select options field has not been found"
            param_field[0].click()

            for add_param in params:
                el = find_elements(self.app.driver,
                                   "//div[contains(@id,'react-select')][.//div[text()='%s']]" % add_param)
                assert len(el), "Param %s has not been found" % add_param
                el[0].click()
                time.sleep(1)

            param_field = find_elements(self.app.driver, "//span[text()='Select options to add parameters']/..")
            param_field[0].click()

    def get_current_selected_params_demographic(self):
        els = find_elements(self.app.driver,
                            "//label[@for='demographicsType']/..//div[./div[text()]][./button[.//img[@alt='remove tag']]]")
        current_param = []
        for param in els:
            p = param.find_element('xpath',".//div[text()]")
            current_param.append(p.text)
        time.sleep(2)
        return current_param

    def delete_selected_demographic_param(self, name):
        els = find_elements(self.app.driver, "//div[text()='%s']/..//button" % name)
        assert len(els), "Param %s has not been found" % name
        els[0].click()
        time.sleep(1)

    def delete_all_selected_demographic_param(self, ):
        els = find_elements(self.app.driver,
                            "//label[text()='SELECT PARAMETERS']/..//div[contains(@class, 'indicatorContainer')]")
        assert len(els), "Element has not been found"
        els[0].click()
        time.sleep(1)

    def distribute_demograph(self, data):
        for param, value in data.items():
            el = find_elements(self.app.driver, "//tr[td[text()='%s']]" % param)
            assert len(el), "Param %s has not been found" % param
            inp_field = el[0].find_elements('xpath',".//input")
            for i in range(len(inp_field)):
                inp_field[i].clear()
                inp_field[i].send_keys(value)

    def get_saved_requirements(self, demographics_type='REQUIREMENTS BY GROUP'):
        el = find_elements(self.app.driver, "//label[text()='%s']/../p" % demographics_type)
        assert len(el), "REQUIREMENTS BY GROUP have not been found"
        return el[0].text

    def click_edit_saved_req(self):
        el = find_elements(self.app.driver,
                           "//label[text()='REQUIREMENTS BY GROUP' or text()='AGGREGATED REQUIREMENTS']")
        assert len(el), "REQUIREMENTS BY GROUP have not been found"
        el[0].click()
        time.sleep(1)
        el = find_elements(self.app.driver,
                           "//label[text()='REQUIREMENTS BY GROUP' or text()='AGGREGATED REQUIREMENTS']/../..//div[.//*[local-name() = 'svg']]")
        el[0].click()
        time.sleep(1)
        edit_btn = find_elements(self.app.driver,
                                 "//label[text()='REQUIREMENTS BY GROUP' or text()='AGGREGATED REQUIREMENTS']/../..//div[@role='button']//div[text()='Edit']")
        assert len(edit_btn), "Edit btn has not been found"
        mouse_click_element(self.app.driver, edit_btn[0])
        time.sleep(2)

    def click_clear_saved_req(self):
        el = find_elements(self.app.driver,
                           "//label[text()='REQUIREMENTS BY GROUP' or text()='AGGREGATED REQUIREMENTS']")
        assert len(el), "REQUIREMENTS BY GROUP or AGGREGATED REQUIREMENTS have not been found"
        el[0].click()
        time.sleep(1)
        el = find_elements(self.app.driver,
                           "//label[text()='REQUIREMENTS BY GROUP' or text()='AGGREGATED REQUIREMENTS']/../..//div[.//*[local-name() = 'svg']]")
        el[0].click()
        time.sleep(1)
        clear_btn = find_elements(self.app.driver,
                                  "//label[text()='REQUIREMENTS BY GROUP' or text()='AGGREGATED REQUIREMENTS']/../..//div[@role='button']//div[text()='Clear']")
        assert len(clear_btn), "Clear btn has not been found"
        mouse_click_element(self.app.driver, clear_btn[0])
        time.sleep(2)

    def get_current_distribution(self):
        tabels = find_elements(self.app.driver, "//div[contains(@class, 'styles_modal')]//table")
        assert len(tabels), "Info has not been found"
        current_distr = {}
        for t in tabels:
            req_name = t.find_elements('xpath',".//thead//th//div")[0].text
            rows = t.find_elements('xpath','.//tbody//tr')
            _params = {}
            for r in rows:
                param_name = r.find_element('xpath',"./td").text
                param_value = r.find_element('xpath',".//input").get_attribute('value')
                _params[param_name] = param_value

            current_distr[req_name] = _params

        return current_distr

    def click_distribute_evenly(self):
        el = find_elements(self.app.driver, "//input[@name='distributedEvenly']/..")
        assert len(el), "Element has not been found"
        el[0].click()
        time.sleep(2)


    def verify_regular_hiring_target_row_present_on_page(self, language, region, restrict_country,
                                                         deadline, target, assigned_owner='.', qualifying='', active='',
                                                         progress='', status='DISABLED'):
        if status == 'DRAFT':
            found = find_elements(self.app.driver, "//tr[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]"
                                                   "[.//td/div[contains(.,'%s')]]" % (
                                      language, region, restrict_country, deadline, target))
        else:
            found = find_elements(self.app.driver, "//tr[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]"
                                                   "[.//td[contains(.,'%s')]]" "[.//td/div[contains(.,'%s')]]" % (
                                      language, region, restrict_country, assigned_owner, deadline, target))
        assert len(found), "Hiring target row has not been found"
        if status == 'ENABLED':
            found_metric_qualifying = find_elements(self.app.driver,
                                                    "//tr/td[.//div/text()='%s']/preceding::tr/th[.//div/text()='QUALIFYING']"
                                                    % qualifying)
            assert len(found_metric_qualifying), "Qualifying metric has not been found"

            found_metric_active = find_elements(self.app.driver,
                                                "//tr/td[.//div/text()='%s']/preceding::tr/th[.//div/text()='ACTIVE']" % active)
            assert len(found_metric_active), "Active vendor metric has not been found"

            found_metric_progress = find_elements(self.app.driver,
                                                  "//tr/td[.//div/text()='%s']/preceding::tr/th[.//div/text()='PROGRESS']" % progress)

            assert len(found_metric_progress), "Progress vendors % has not been found"

    def get_hiring_progress(self):
        el = find_elements(self.app.driver, "//div[text()='Hiring Targets']/..//following-sibling::div")
        assert len(el), "Hiring progress metric has not been found"
        hiring_progress = el[0].get_attribute('innerText')
        return hiring_progress

    def close_error_msg(self):
        el = find_elements(self.app.driver, "//img[@role='button' and @alt='hide error']")
        assert len(el), "Error msg has not been found"
        el[0].click()

    def verify_demografics_header_view(self, type, target, engaged):
        found = find_elements(self.app.driver, "//tr[.//th[contains(.,'%s')]]"
                                               "[.//th[contains(.,'%s%s')]]" % (type, target, engaged))

        assert len(found), "Demographics Header '%s' '%s' '%s' has not been found )" % (type, target, engaged)

    def verify_demografics_row_view(self, type, engaged):
        found = find_elements(self.app.driver, "//tr[.//td[contains(.,'%s')]]"
                                               "[.//td[contains(.,'%s')]]" % (type, engaged))

        assert len(found), "Demographics Row '%s' '%s' has not been found )" % (type, engaged)

    def verify_demographics_select_view(self, view):
        el = find_elements(self.app.driver, "//div[text()='%s']" % view)
        assert len(el), " %s btn has not been found" % view
        el[0].click()

    def close_modal_window(self):
        find_elements(self.app.driver, "//img[@alt='Close modal']")[0].click()

    def click_save_auto_screening(self):
        find_elements(self.app.driver, "//h2[text()='Add Auto-screening Configuration']/../..//button[text()='Save']")[0].click()
        time.sleep(10)

    def click_cancel_auto_screening(self):
        find_elements(self.app.driver, "//h2[text()='Add Auto-screening Configuration']/../..//button[text()='Cancel']")[0].click()

    def get_autoscfreening_table_details(self):
        rows = find_elements(self.app.driver, "//thead[.//div[.='Locale']]/..//tbody//tr")
        auto_screening = []
        for row in rows:
            columns = row.find_elements('xpath',".//td")
            _locale = columns[0].text
            _users_day = columns[1].text
            _total_users = columns[2].text
            _={
                "locale":_locale,
                "users_per_day": _users_day,
                "users_total": _total_users
            }
            auto_screening.append(_)
        return auto_screening

    def __find_autoscreen_config(self, locale, action):
        tr = find_elements(self.app.driver, "//thead[.//div[text()='Locale']]/..//tbody//tr")
        for row in tr:
            columns = row.find_elements('xpath',".//td")
            _locale = columns[0].text
            if _locale == locale:
                settings = row.find_element('xpath',
                    ".//div[contains(@class, 'settings-icon-container')]//*[local-name() = 'svg']")
                mouse_over_element(self.app.driver, settings)
                time.sleep(1)
                settings = row.find_element('xpath',
                    ".//div[contains(@class, 'settings-icon-container')]//div[text()='%s']//.." % action)
                settings.click()
                time.sleep(1)
                return

    def delete_autoscreen_locale(self, locale):
        self.__find_autoscreen_config(locale, "Clear")
        time.sleep(1)

    def edit_autoscreen_locale(self, locale):
        self.__find_autoscreen_config(locale, "Edit")
        time.sleep(1)

    def click_create_new_target_group(self):
        with allure.step('Click: Create New Target Group'):
            btn = find_elements(self.app.driver, "//div[text()='Create new target Group']")
            assert len(btn), "Button:'Create New Target Group' has not been found"
            btn[0].click()

    def click_use_existing_target_group(self):
        with allure.step('Click: Use Existing Target Group'):
            btn = find_elements(self.app.driver, "//div[text()='Use existing target group']")
            assert len(btn), "Button:'Use Existing Target Group' has not been found"
            btn[0].click()

    def modal_window_action(self, action):
        with allure.step('Click btn in modal window: %s' % action):
            btn = find_elements(self.app.driver, "//div[contains(@class,'modal')]//button[text()='%s']" % action)
            assert len(btn), "Button: %s has not been found"
            btn[0].click()

    def new_target_group_details(self, data):
        with allure.step('Fill out new target group details'):
            self.project.enter_data(data=data, elements=self.elements)

    def _click_target_group_action(self, menu_action):
        process = find_element(self.app.driver, "//h2[contains(.,'Target Audience Builder')]/../..")

        action = ActionChains(self.app.driver)
        # action.move_to_element(process).perform()
        # time.sleep(2)

        gear = process.find_element('xpath',".//*[local-name() = 'svg']")
        action.click(gear).perform()

        menu = process.find_elements('xpath',".//div[@role='button'][.//div[text()='%s']]" % menu_action)
        assert len(menu) > 0, "%s button has not been found" % menu_action
        action.click(menu[0]).perform()
        time.sleep(2)

    def click_edit_target_group_details(self):
        with allure.step('Click Edit Target Group Details'):
            self._click_target_group_action('Edit Details')

    def edit_target_group_button_is_disable(self):
        with allure.step('Click Edit Target Group Details'):
            div = find_elements(self.app.driver, "//div[@class='target_group_actions']/..")

            action = ActionChains(self.app.driver)
            self.app.driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            action.click(div[0]).pause(5).perform()
            time.sleep(4)

            el = find_elements(self.app.driver,
                               "//div[@class='target_group_actions']//*[local-name() = 'svg']")
            mouse_over_element(self.app.driver, el[0])
            el[0].click()
            time.sleep(2)

            el = find_elements(self.app.driver, "//div[@title='Target audience groups can only be edited by their creators.']")
            return True if el else False


    def get_question_groups(self):
        with allure.step('Get group of questions'):
            groups = find_elements(self.app.driver, "//label[text()='Profile Questions']/../child::div[.//div]//div[text()]")
            return [x.text for x in groups]

    def open_question_group(self, name):
        with allure.step('Expand question group'):
            group = find_elements(self.app.driver, "//label[text()='Profile Questions']/../child::div[.//div[text()='%s']]//*[local-name() = 'svg']" % name)
            assert len(group), "Group %s has not been found" % name
            group[0].click()

    def add_question_to_builder(self, group, question):
        with allure.step('Add question %s to target builder'):
            el = find_elements(self.app.driver, "//label[text()='Profile Questions']/../child::div[.//div[text()='%s']]//p[text()='%s']" % (group, question))
            assert len(el), "Question %s has not been found" % question

            builder = find_element(self.app.driver, "//label[text()='Drag modules to build your target']")
            drag_and_drop(self.app.driver, el[0], builder)

            create_screenshot(self.app.driver, "profile")

    def get_questions_by_group(self, group):
        with allure.step('Get question for group'):
            pass

    def _edit_question(self, question, action):
        el = find_elements(self.app.driver,
                           "//div[text()='%s']/../..//div[contains(@class,'process_builder__card__actions')]" % question)
        assert len(el), "Question %s has not been found" % question
        el[0].click()

        btn = el[0].find_elements('xpath',".//div[text()='%s']" % action)
        assert len(el), "Button Edit has not been found"
        btn[0].click()

        time.sleep(2)

    def remove_question_from_builder(self, question):
        with allure.step('Remove question from builder'):
            self._edit_question(question, action='Remove')
            Alert(self.app.driver).accept()

    def edit_question_in_builder(self, question):
        with allure.step('Edit question in builder'):
            self._edit_question(question, action='Edit')

    def preview_question_in_builder(self, question):
        with allure.step('Edit question in builder'):
            self._edit_question(question, action='Preview')

    def save_question_in_builder(self, question):
        with allure.step('Save question in builder'):
            time.sleep(1)
            btn = find_elements(self.app.driver, "//div[text()='%s']/../../..//button[text()='Add & Close' or text()='Update & Close']" %question)
            assert len(btn), "Button 'Add & Close' has not been found for %s" % question
            btn[0].click()

    def cancel_question_in_builder(self, question):
        with allure.step('Save question in builder'):
            btn = find_elements(self.app.driver,
                                "//div[text()='Modes of transport']/../../..//button[text()='Cancel']")
            assert len(btn), "Button 'Cancel' has not been found for %s" % question
            btn[0].click()

    def set_up_answers_for_question(self, q_type, question, answers, action_checked=None, action_unchecked=None):
        with allure.step('Set up answers for question'):
            el_question = find_elements(self.app.driver, "//div[contains(@class,'target-builder-process')]//div[text()='%s']/../../.." % question)
            assert len(el_question), "Question %s has not been found" % question

            if q_type=='checkbox':
                for ans in answers:
                     _ans = el_question[0].find_elements('xpath',".//label[.//div[text()='%s']]//span[@class='overlay']" % ans)
                     _ans[0].click()

            actions = el_question[0].find_elements('xpath',".//label[text()='SELECT ACTION']/../child::div")

            if action_checked:
                actions[0].find_element('xpath',".//span[text()='Select action']").click()
                actions[0].find_element('xpath',".//div[text()='%s']" % action_checked).click()

            if action_unchecked:
                actions[1].find_element('xpath',".//span[text()='Select action']").click()
                actions[1].find_element('xpath',".//div[text()='%s']" % action_unchecked).click()

    def _target_group_action(self, target_action):
        div = find_elements(self.app.driver, "//div[@class='target_group_actions']/..")

        action = ActionChains(self.app.driver)
        self.app.driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
        action.click(div[0]).pause(5).perform()
        time.sleep(4)

        el = find_elements(self.app.driver,
                           "//div[@class='target_group_actions']//*[local-name() = 'svg']")
        mouse_over_element(self.app.driver, el[0])
        el[0].click()
        time.sleep(2)

        btn = find_elements(self.app.driver, "//div[@class='target_group_actions']//div[text()='%s']" % target_action)
        btn[0].click()

    def target_group_edit(self):
        with allure.step('Edit Target group'):
            self._target_group_action('Edit')

    def target_group_clear(self):
        with allure.step('Clear Target group'):
            self._target_group_action('Clear')

# save question
