import time

import allure

from adap.ui_automation.utils.js_utils import scroll_to_page_bottom, scroll_to_element
from adap.ui_automation.utils.selenium_utils import find_element, find_elements, get_text_by_xpath, \
    clear_text_field_by_xpath, click_element_by_xpath


class VendorPages:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.navigation = self.app.navigation

    def links_in_main_and_sub_tabs(self):
        link_texts_main_tab = []
        link_texts_main_n_sub_tabs = {}
        links_main_nav = find_elements(self.app.driver, "//div[@id='navigation']//ul/li")
        assert len(links_main_nav) > 0, "Link %s has not been found" % links_main_nav
        for i in range(0, len(links_main_nav)):
            link_texts_main_tab.append(links_main_nav[i].text)
        for i in range(0, len(link_texts_main_tab)):
            el = find_elements(self.app.driver, "//a[contains(text(),'%s')]" % link_texts_main_tab[i])
            assert len(el) > 0, "Link %s has not been found" % link_texts_main_tab[i]
            el[0].click()
            time.sleep(2)
            el1 = find_elements(self.app.driver, "//*[@id='sub-navigation']/ul/li")
            assert len(el1) > 0, "Link %s has not been found " % el1
            sub_nav_page_headings = []
            for j in range(0,len(el1)):
                sub_nav_page_headings.append(el1[j].text)
                link_texts_main_n_sub_tabs[link_texts_main_tab[i]] = sub_nav_page_headings
        return link_texts_main_n_sub_tabs

    def qualified_projects_vendor(self):
        my_projects_button = find_elements(self.app.driver, "//div[contains(text(),'My projects')]")
        assert len(my_projects_button) > 0, "Link %s has not been found" % my_projects_button
        my_projects_button[0].click()
        number_of_qualified_projects = find_elements(self.app.driver, "//tbody/tr")
        return number_of_qualified_projects

    def open_an_invoice(self, index=0):
        invoices = find_elements(self.app.driver, "//h4[contains(text(),'Invoices')]/following-sibling::div//a")
        assert len(invoices) > 0, "There are no available invoices"
        invoices[index].click()

    def navigate_to_suggested_projects(self):
        suggested_projects_button = find_elements(self.app.driver, "//div[contains(text(),'Suggested')]")
        assert len(suggested_projects_button) > 0, "Link %s has not been found" % suggested_projects_button
        suggested_projects_button[0].click()

    def applied_projects_vendor(self):
        applied_projects_button = find_elements(self.app.driver, "//div[contains(text(),'Applied')]")
        assert len(applied_projects_button) > 0, "Link %s has not been found" % applied_projects_button
        applied_projects_button[0].click()
        applied_projects = find_elements(self.app.driver, "//tbody/tr")
        return applied_projects

    def all_projects_vendor(self):
        all_projects_button = find_elements(self.app.driver, "//div[contains(text(),'All projects')]")
        assert len(all_projects_button) > 0, "Link %s has not been found" % all_projects_button
        all_projects_button[0].click()
        time.sleep(5)
        all_available_projects = find_elements(self.app.driver, "//tbody/tr")
        return all_available_projects

    def _find_vendor_by(self, vendor, status=None, by='email'):
        clear_text_field_by_xpath(self.driver, "//input[@id='search']")
        if by == 'email':
            find_element(self.driver, "//select[@name='searchParameter']//option[@value='EMAIL']").click()
        elif by == 'id':
            find_element(self.driver, "//select[@name='searchParameter']//option[@value='ID']").click()
        find_element(self.driver, "//input[@id='search']").send_keys(vendor)
        time.sleep(1)
        if status:
            find_element(self.driver, "//*[@name='status' and @id='status']").click()
            find_element(self.driver, "//option[text()='%s']" % status).click()
            time.sleep(1)
        self.app.navigation_old_ui.click_input_btn("Go")
        self.app.verification.wait_untill_text_present_on_the_page('Rows Per Page:', 100)
        _v = find_elements(self.driver, "//tr[.//td[.//a[@href and text()='%s']]]" % vendor)
        assert len(_v)>0, "Vendor %s has not been found" % vendor
        return _v[0]

    def open_vendor_profile_by(self, vendor, search_type='name', status=None):
        with allure.step('Open vendor by name %s' % vendor):
            if search_type == 'name':
                _vendor = self._find_vendor_by(vendor, status)
            elif search_type == 'id':
                _vendor = self._find_vendor_by(vendor, status, search_type)
            _vendor.find_element('xpath',
                ".//a[contains(@href, '/qrp/core/vendor/view/') and text()='%s']" % vendor) \
                .click()
            time.sleep(10)

    def get_project_mapping_for_current_vendor(self):
        with allure.step('Get all projects for current vendor'):
            rows = find_elements(self.driver, '//table[@id="project-table"]//tbody//tr[@class="project-row"]')

            res = {}

            for row in rows:
                columns = row.find_elements('xpath',".//td")
                name = columns[0].text
                locale = columns[1].text
                status = columns[5].text

                res[name] = {
                    "locale":locale,
                    "status": status
                }

            return res


    def find_and_get_vendor_status_by_id(self, user_id):
        el = self._find_vendor_by(user_id, by='id')
        return get_text_by_xpath(el, '//td[position()=(last()-1)]')

    def get_profile_user_status(self):
        return get_text_by_xpath(self.driver, '//div[contains(@class, "user-status")]')

    def get_profile_user_termination_date(self):
        return get_text_by_xpath(self.driver, "//th[contains(text(), 'Termination Date')]/../td")

    def get_profile_user_termination_reason(self):
        return get_text_by_xpath(self.driver, "//th[contains(text(), 'Termination Reason')]/../td")

    def get_profile_user_termination_note(self):
        return get_text_by_xpath(self.driver, "//th[contains(text(), 'Termination Note')]/../td")

    def get_profile_paypal_email(self):
        return get_text_by_xpath(self.driver, "//th[contains(text(), 'Paypal')]/../td")

    def get_profile_direct_pay(self):
        return get_text_by_xpath(self.driver, "//th[contains(text(), 'Direct Pay')]/../td")

    def unterminate_user(self):
        click_element_by_xpath(self.driver, "//input[@name='unterminate']")

    def add_group_to_vendor(self,group_name):
        with allure.step('Add group %s to vendor' % (group_name)):
            self.app.navigation.click_link("Locales & Groups")
            self.app.navigation.click_link("Add Group")
            find_element(self.driver, "//select[@name='selectedGroupId']//option[text()='%s']" % group_name).click()
            find_element(self.driver, "//input[@name='ajaxAddGroup']").click()
            time.sleep(3)

    def add_locale_to_vendor(self, locale):
        """
        locale
        {
        "selectedLocaleId": "",
        "selectedTranslateToLocaleId": "",
        "spokenFluency": "",
        "writtenFluency": ""
        }
        """
        with allure.step('Add group %s to vendor' % (locale)):
            self.app.navigation.click_link("Locales & Groups")
            self.app.navigation.click_link("Add Locale")
            time.sleep(2)
            for name, value in locale.items():
                if name == "languageCertified":
                    find_element(self.driver, "//input[@name='languageCertified']").click()
                elif  name == "languageScore":
                    find_element(self.driver, "//input[@name='languageScore']").send_keys(value)
                else:
                    # find_element(self.driver,
                    #              "//select[@name='%s']" % (name)).click()
                    time.sleep(1)
                    find_element(self.driver,
                                 "//select[@name='%s']//option[text()='%s']" % (name, value)).click()
                time.sleep(1)
            find_element(self.driver, "//input[@name='ajaxAddLocale']").click()

    def get_roles(self):
        with allure.step('Get roles for current vendor'):
            roles = find_elements(self.driver, "//tr//th[text()='Roles']/..")
            assert len(roles) > 0, "roles not found"
            return roles[0].find_elements('xpath',".//td")[0].get_attribute('innerText')

    def get_vendor_id(self):
        with allure.step('Get vendor id for current vendor'):
            vendor = find_elements(self.driver, "//tr//th[text()='ATS ID']/..")
            assert len(vendor) > 0, "vendor not found"
            return vendor[0].find_elements('xpath',".//div")[0].text

    def screen_user_take_action_on_project(self, project_name, action, btn_type='submit'):
        with allure.step('Click button for project to take action on it'):
            bt = find_elements(
                self.driver,
                "//*[contains(text(),'%s')]/..//input[@type='%s' and @value='%s']" % (project_name, btn_type, action)
            )
            assert len(bt) > 0, "bt not found"
            scroll_to_element(self.driver, bt[0])
            time.sleep(1)
            bt[0].click()
            time.sleep(1)

    def vendor_qualification_action(self, action):
        with allure.step('Click button for qualification status'):
            bt = find_elements(self.driver, "//th[text()='Screen user']/..//input[@type='submit' and @value='%s']" % action)
            assert len(bt) > 0, "bt not found"
            bt[0].click()
            time.sleep(1)

    def add_vendor_to_project(self, project_name, locale, action='Add'):
        with allure.step('Add vendor to project'):
            self.app.navigation.click_link('Add Project')
            time.sleep(2)

            project = find_elements(self.driver, "//select[@name='selectedProjectId']//option[text()='%s']" % project_name)
            assert len(project), "Project: %s has not been found" % project_name
            project[0].click()
            time.sleep(1)

            locale = find_elements(self.driver,
                                    "//select[@name='selectedMappingLocaleId']//option[text()='%s']" % locale)
            assert len(locale), "Locale: %s has not been found" % locale
            locale[0].click()

            if action:
                 el = find_elements(self.driver,"//tr[@class='add-project-row']/.//input[@value='%s']" % action)
                 assert len(el)>0, "Button %s has not been found" % action
                 el[0].click()

            time.sleep(2)


    def get_locale(self):
        with allure.step('Get Locale for current vendor'):
            time.sleep(3)
            rows = find_elements(self.driver, "//table[@id='locale-table']//tr[@class='locale-row']")
            result = []
            for row in rows:
                _locale = row.find_elements('xpath',".//td")[0].text
                _translate_locale = row.find_elements('xpath',".//td")[1].text
                _spoken_fluency = row.find_elements('xpath',".//td[@class='spoken-fluency']")[0].text
                _written_fluency = row.find_elements('xpath',".//td[@class='written-fluency']")[0].text
                _ = {
                    "locale":_locale,
                    "translate_locale": _translate_locale,
                    "spoken_fluency": _spoken_fluency,
                    "written_fluency": _written_fluency
                }
                result.append(_)
            return result

    def get_vendor_status(self):
        with allure.step('Get vendor status'):
            return find_element(self.driver, "//div[contains(@class, 'user-status')]").text

    def edit_locale(self):
        pass

    def revoke_vendor_from_group(self, group_name):
        pass

    def open_projects_tab(self, tab):
        with allure.step('Open project tab %s' % tab):
            _projects_button = find_elements(self.app.driver, "//div[contains(text(),'%s')]" % tab)
            assert len(_projects_button) > 0, "Link %s has not been found" % tab
            _projects_button[0].click()

    def search_project_by_name(self, name):
        with allure.step('Search project by name: %s' % name):
            find_element(self.driver, "//input[@name='projectName']").send_keys(name)
            time.sleep(3)

    def project_found_on_page(self, name):
        return True if len(self.driver.find_elements('xpath',
            "//table//h2[contains(text(),'%s')]" % name)) > 0 else False

    def select_language_option(self, option, action='Proceed'):
        self.driver.switch_to.default_content()
        click_element_by_xpath(self.driver, "//select[@id='locale-select']/option[text()='Select One...']")
        click_element_by_xpath(self.driver, "//select[@id='locale-select']/option[text()='%s']" % option)

        if action == 'Proceed':
            click_element_by_xpath(
                self.driver,
                "//div[@id='locale_selection_wrapper']/..//button[contains(text(), 'Proceed')]"
            )
            time.sleep(3)

        return self

    def close_process_status_popup(self):
        click_element_by_xpath(
            self.driver,
            "//span[contains(text(), 'Process Status')]/../..//button[contains(text(), 'Close')]")

        return self

    def open_project_by_name(self, name):
        with allure.step('Open project by name'):
            _project = self._find_project("name", name)
            assert len(_project) > 0, "Project  %s has not been found"
            _project[0].find_element('xpath',".//div[text()='%s']" % name).click()

    def click_action_for_project(self, name, action):
        with allure.step('Click action for project %s %s' % (name, action)):
            _project = find_elements(self.driver, "//tbody//tr[.//td[.//h2[contains(.,'%s')]]]" % name)
            assert len(_project), "Project %s has not been found" % name

            _options = _project[0].find_elements('xpath',".//button[contains(.,'Options')]")
            if len(_options) > 0:
                _options[0].click()

            _btn = _project[0].find_elements('xpath',".//button[.='%s']" % action)
            if len(_btn) == 0:
                _btn = _project[0].find_elements('xpath',".//*[.='%s']" % action)
            if len(_btn) == 0:
                _btn = find_elements(self.driver,"//li[contains(.,'%s')]" % action)
            if len(_btn) == 0:
                _btn = find_elements(self.driver, f".//*[text()='{action}']")

            assert len(_btn), "Button %s has not been found" % action

            _btn[0].click()

    def answer_the_question_radio_btn(self, question, answer):
        with allure.step('Question: %s , answer: %s' % (question, answer)):
            q = find_elements(self.driver, "//tr[.//th[contains(text(),'%s')]]" % (question))
            assert len(q), "Question: %s has not been found" % question

            _answer = q[0].find_elements('xpath',".//input[@value='%s']" % answer)
            assert len(_answer), "Answer: %s has not been found" % answer
            _answer[0].click()

    def wait_until_project_available_for_vendor(self):
        pass

    def ach_fill_out_bank_data(self, routing_number=None, account_number=None, action=None):
        with allure.step('Fill out ach info: %s %s' % (routing_number, account_number)):
            if routing_number:
                el = find_elements(self.driver, "//input[@name='profile.bankRoutingNumber']")
                assert "Routing number has nor been found"
                el[0].clear()
                el[0].send_keys(routing_number)

            if account_number:
                el = find_elements(self.driver, "//input[@name='profile.bankAccountNumber']")
                assert "Account number has nor been found"
                el[0].clear()
                el[0].send_keys(account_number)

            if action == 'Submit':
                btn = find_elements(self.driver, "//input[@name='saveAch' or @name='checkUpload']")
                assert "Submit button has nor been found"
                btn[0].click()
                time.sleep(2)

    def ach_clear_routing_number(self, action=None):
        with allure.step('ach_clean_routing_number'):
            el = find_elements(self.driver, "//input[@name='profile.bankRoutingNumber']")
            assert "Routing number has nor been found"
            el[0].clear()

            if action == 'Submit':
                btn = find_elements(self.driver, "//input[@name='saveAch']")
                assert "Submit button has nor been found"
                btn[0].click()

    def ach_clear_account_number(self, action=None):
        with allure.step('ach_clear_account_number'):
            el = find_elements(self.driver, "//input[@name='profile.bankAccountNumber']")
            assert "Account number has nor been found"
            el[0].clear()

            if action == 'Submit':
                btn = find_elements(self.driver, "//input[@name='saveAch']")
                assert "Submit button has nor been found"
                btn[0].click()

    def verify_bank_info_on_vendor_page(self, data):
        with allure.step('verify_bank_info_on_vendor_page:  %s' % data):
            for key, value in data.items():
                el = find_elements(self.driver, "//table[@class='profile-section']//tr[.//th[text()='%s']]//td" % key)
                assert el, "%s has not been found" % key

                assert el[0].text == value, "{key}: Expected value - {value}; Actual value - {actual}".format(key=key,
                                                                                                              value=value,
                                                                                                              actual=el[0].text)

    def upload_check_image(self, file_name):
        with allure.step('upload check image:  %s' % file_name):
            el = find_elements(self.app.driver, "//input[@name='checkImage']")
            assert len(el) >0, "Upload file btn has not been found"
            el[0].send_keys(file_name)
