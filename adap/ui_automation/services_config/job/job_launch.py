import time
import allure
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from adap.ui_automation.utils.js_utils import get_text_excluding_children, scroll_to_element, element_to_the_middle
from adap.ui_automation.utils.selenium_utils import find_elements

class Launch:

    def __init__(self, job):
        self.job = job
        self.driver = self.job.app.driver
        self.app = self.job.app

    def click_edit_settings_section(self, name):
        with allure.step('Edit section %s ' % name):
            el = find_elements(self.app.driver,
                               "//h3[contains(text(),'%s')]/..//following-sibling::a[text()='Edit']" % name)
            assert len(el) > 0, "Section %s has not been found" % name
            element_to_the_middle(self.driver, el[0])
            time.sleep(2)
            el[0].click()
            time.sleep(1)

    def fill_out_settings_field(self, field_name, value):
        el = find_elements(self.driver, "//div[@class='b-JobLaunchSettingsForm__field'][.//div["
                                        "@class='b-JobLaunchSettingsForm__title' and text()='%s']]//input" % field_name)
        assert len(el) > 0, "Input field %s has not been found" % field_name
        el[0].clear()
        el[0].send_keys(value)
        time.sleep(1)

    def enter_ac_project_id(self, project_id, action=None):
        el = find_elements(self.driver, "//input[@name='appenConnectProjectId']")
        assert len(el) > 0, "Appen Connect Project ID field %s has not been found"
        el[0].clear()
        el[0].send_keys(project_id)
        time.sleep(1)

        if action:
            self.app.navigation.click_link(action)

        time.sleep(3)

    def select_job_targeting_settings(self, target):
        with allure.step('Select target'):
            el = find_elements(self.driver, "//label[text()='Job Targeting Settings']/..//span[text()='%s']" % target)
            assert len(el) > 0, "Target %s has not been found" % target
            el[0].click()
            time.sleep(2)

    def select_crowd_channel(self, channel_name):
        with allure.step('Select crowd channel by name %s' % channel_name):
            el = find_elements(self.driver,  "//form//span[text()='%s']" % channel_name)
            if len(el) == 0:
                el = find_elements(self.driver, "//form//label[text()='%s']" % channel_name)
            assert len(el) > 0, "Target %s has not been found" % channel_name
            el[0].click()
            time.sleep(2)

    def set_crowd_channel_for_FP(self, external_checkbox=True,internal_checkbox=True, action=None,radio_btn=None):
        with allure.step('set_crowd_channel_for_FP'):
            #getting status for external checkbox
            ext=find_elements(self.app.driver,
                                     "//input[@id='externalCheckbox']")
            external_status=ext[0].is_selected()

            #getting status for internal checkbox
            inter = find_elements(self.app.driver,
                                     "//input[@id='internalCheckbox']")
            internal_status = inter[0].is_selected()

            #if external is True, provide the values for radio buttons
            if external_checkbox != external_status:
                el = find_elements(self.app.driver,
                                   "//label[@for='externalCheckbox' and not(text())]")
                el[0].click()

            if external_status:
                if radio_btn == "General":
                    el = find_elements(self.app.driver, "//input[@id='general']")
                    assert len(el) > 0, "General radio button has not been found"
                    el[0].click()

                if radio_btn == "Custom":
                    el = find_elements(self.app.driver, "//input[@id='custom']")
                    assert len(el) > 0, "custom radio button has not been found"
                    el[0].click()

            if internal_checkbox != internal_status:
                el = find_elements(self.app.driver,
                                       "//label[@for='internalCheckbox' and not(text())]")
                el[0].click()

            if action == 'Save & Close':
                self.app.navigation.click_btn("Save & Close")

            if action == 'Cancel':
                self.app.navigation.click_btn("Cancel")

    def click_edit_contributor_settings(self, contributor):
        with allure.step('verify edit %s setting is present' %contributor):
            el1 = find_elements(self.app.driver, "//div[contains(text(),'%s')]" % contributor)
            assert len(el1) > 0, "contributor has not been found"
            el1[0].click()
            time.sleep(1)

    def set_countries_for_crowd_setting_FP(self, countries_to_select, action="Select"):
        with allure.step('set_countries_for_crowd_setting_FP'):
            self.app.navigation.click_link("Select countries")

            for key, value in countries_to_select.items():
                self.app.navigation.click_link(key)
                # if key == "Exclude":
                #     time.sleep(1)
                #     el = find_elements(self.app.driver,
                #                        "//th[@class='b-GeoSettingsModal__actionsColumn']//*[local-name()='svg']")
                #     el[0].click()
                target = find_elements(self.app.driver, "//input[@placeholder='Search Countries']")
                assert len(target) > 0, "search countries box has not been found"
                target[0].click()
                for country in value:

                    target = find_elements(self.app.driver, "//input[@placeholder='Search Countries']")
                    input_value = target[0].get_attribute('value')
                    for i in range(len(input_value)):
                        target[0].send_keys(Keys.BACK_SPACE)
                        time.sleep(1)

                    target[0].send_keys(country)
                    time.sleep(2)
                    el = find_elements(self.app.driver, "//div[@title]")
                    # print(self.driver.page_source)
                    el[0].click()
                    time.sleep(2)

            if action:
               self.app.navigation.click_link(action)

        time.sleep(3)


    def set_max_hourly_pay_rate_FP(self, payrate):
        with allure.step('set_max_hourly_pay_rate_FP'):
            el = find_elements(self.app.driver, "//input[@name='hourlyPay']")
            assert len(el) > 0, "hourly pay rate box has not been found"
            el[0].clear()
            el[0].send_keys(payrate)

    def verify_text_value_for_fp_setting(self, data, is_not=True):
        with allure.step('verify "%s" is present= %s on the page' %(data, is_not)):
            for key, value in data.items():
                el1 = find_elements(self.app.driver, "//span[contains(text(),'%s')]" %key)
                assert len(el1), "Field %s has not been found" %key
                heading1 = el1[0].find_element('xpath',"./following-sibling::span").text
                result = (heading1 == value)
                if is_not:
                    if result:
                        print("\n %s is equal to %s" %(key,value))
                    else:
                        assert False, ("\n %s is not equal to %s. Actual value is: %s and expected value is: %s" %(key, value, key, heading1))
                if not is_not:
                    if not result:
                        print("\n %s is NOT equal to %s (as expected!)" %(key,value))
                    else:
                        assert False, ("\n %s is equal to %s  (but it must not!)" %(key,value))

    #this function is use to verify the values in view breakdown window on fair pay launch page,
    # data is dictionary variable and values must be provided like [{"contributor judgement": "$2- $3"}]
    def verify_range_value_for_view_breakdown_fp(self, data, is_not= True):
        with allure.step('verify "%s" is present= %s on the page' %(data, is_not)):
            for key, value in data.items():
                el1 = find_elements(self.app.driver, "//div[contains(@class,'b-Estimates__row')]"
                                                     "//div[contains(text(),'%s')]/following-sibling::div" % key)
                assert len(el1), "Field %s has not been found" % key
                heading1 = el1[0].text
                result = (heading1 == value)
                if is_not:
                    if result:
                        print("\n %s is equal to %s" %(key,value))
                    else:
                        assert False, ("\n %s is not equal to %s. Expected value is: %s and Actual value is: %s" % (key, value, value,heading1))
                if not is_not:
                    if not result:
                        print("\n %s is NOT equal to %s (as expected!)" %(key,value))
                    else:
                        assert False, ("\n %s is equal to %s  (but it must not!)" %(key,value))

    def get_allocate_funds_ele(self):
        with allure.step('get allocate funds input element'):
            ele = find_elements(self.app.driver,"//input[@name='costRecommendation']")
            assert ele, "allocate funds has not been found"
            return ele[0]

    def remove_allocate_funds(self):
        with allure.step('empty allocate funds field'):
            ele = self.get_allocate_funds_ele()
            for i in ele.get_attribute('value'):
                ele.send_keys(Keys.BACK_SPACE)

    def enter_allocate_funds(self, funds):
        with allure.step('enter allocate funds %s' % funds):
            self.remove_allocate_funds()
            ele = self.get_allocate_funds_ele()
            ele.send_keys(funds)
            ele.send_keys(Keys.TAB)
            time.sleep(1)

    #Function will get the text from allocate funds text box
    def get_allocate_funds(self):
        with allure.step('Get allocate funds'):
            return self.get_allocate_funds_ele().get_attribute('value')

    #Funtion to enter data in judgements per row
    def enter_judgements_per_row_for_FP_jobs(self, judgements):
        with allure.step('enter judgements per row %s' % judgements):
            el= find_elements(self.app.driver,"//input[@name='judgmentsPerRow']")
            assert (len(el) > 0), "Judgements per row has not been found"
            el[0].clear()
            el[0].send_keys(judgements)
            time.sleep(1)

    #Function to get status of allocate funds
    def is_allocate_funds_enabled(self):
        with allure.step('Get allocate funds status'):
            return self.get_allocate_funds_ele().is_enabled()

    def chop_estimated_range(self):
        cost_range=find_elements(self.app.driver,"//div[contains(text(),'Estimated Amount')]/following-sibling::div")[0].text
        bounds= dict()
        split_values= cost_range.split(' ')
        bounds['lower_bound'] = float(split_values[0][1:])
        bounds['upper_bound'] = float(split_values[2][1:])
        return bounds

    def get_estimated_cost(self):
        cost = find_elements(self.app.driver,"//div[contains(text(),'Estimated Amount')]/following-sibling::div")[0].text
        return cost.replace("$","")

    #Function to enter project number
    def enter_project_number(self, project_number):
        with allure.step('enter project number %s' % project_number):
            el= find_elements(self.app.driver,"//input[@name='projectNumber']")
            assert (len(el) > 0), "project number has not been found"
            el[0].clear()
            el[0].send_keys(project_number)
            time.sleep(1)

    def get_rows_from_invoice_info(self):
        el = find_elements(self.app.driver,"//div[contains(text(),'Your job has')]")
        assert (len(el) > 0), "Row numbers has not been found"
        row_text=el[0].text
        print("-=-=-",row_text)
        rows=row_text.split(" ")
        return int(rows[3])


    #Funtion to enter data in rows to order
    def enter_rows_to_order(self, rows):
        with allure.step('enter rows to order %s' % rows):
            el= find_elements(self.app.driver,"//input[@name='rowsToOrder']")
            assert (len(el) > 0), "Rows to order has not been found"
            actionChains = ActionChains(self.app.driver)
            actionChains.double_click(el[0]).perform()
            el[0].send_keys(rows)
            time.sleep(1)

    def get_rows_to_order_el(self):
        with allure.step('Get rows to order'):
            el = find_elements(self.app.driver, "//input[@name='rowsToOrder']")
            assert (len(el) > 0), "Rows to order has not been found"
            return el[0]

    #Function will get the text from rows to order text box
    def get_rows_to_order(self):
        with allure.step('Get rows to order'):
            el = self.get_rows_to_order_el()
            value = el.get_attribute('value')
            return value

    #Function will enter the appen connect project ID in launch page
    def enter_row_per_page_FP(self, id):
        with allure.step('enter project ID %s' % id):
            # el= find_elements(self.app.driver,"//div[contains(text(),'Appen Connect Project ID')]/../following-sibling::div//input[@name='rowsPerPage']")
            el= find_elements(self.app.driver,"//input[@name='rowsPerPage']")
            assert (len(el) > 0), "Project ID has not been found"
            el[0].clear()
            el[0].send_keys(id)
            time.sleep(1)

    def get_expected_costs(self):
        with allure.step("Get Expected costs"):
            cost_elements = find_elements(self.app.driver, "//h4[text()='Expected Cost']/..//*[contains(text(),'$')]")
            assert cost_elements, "Expected costs have not been found"
            return [cost.text for cost in cost_elements]

    def get_price_per_judgment(self):
        with allure.step("Get Price Per Judgment"):
            price_per_judgment_elements = find_elements(self.app.driver,"//input[@name='pricePerJudgmentInput']")
            assert price_per_judgment_elements, "Price Per Judgment has not been found"
            return price_per_judgment_elements[0].get_attribute('value')

    def set_price_per_judgment(self, value: str):
        with allure.step("Set Price Per Judgment"):
            price_per_judgment_elements = find_elements(self.app.driver,"//input[@name='pricePerJudgmentInput']")
            assert price_per_judgment_elements, "Price Per Judgment has not been found"
            for _ in self.get_price_per_judgment():
                price_per_judgment_elements[0].send_keys(Keys.BACK_SPACE)

            price_per_judgment_elements[0].send_keys(value)
            time.sleep(1)
