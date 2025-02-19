import time

import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from adap.ui_automation.utils.selenium_utils import find_elements, find_element, move_to_element_with_offset, \
    enable_download_in_headless_chrome
from adap.ui_automation.utils.js_utils import mouse_click_element, mouse_over_element


class Workflow:
    x_add_first_job = 416
    y_add_first_job = 300

    def __init__(self, app):
        self.app = app
        self.driver = app.driver
        self.select_operator = SelectOperator(self)
        self.routing = Routing(self)
        self.data = Data(self)

    def fill_up_wf_name(self, wf_name):
        with allure.step('Fill up WF name: %s' % wf_name):
            # input_field = find_elements(self.driver, "//div[contains(@class, 'b-Modal__dialog')]//input")
            input_field = find_elements(self.driver, "//div[contains(@role, 'document')]//input")
            if len(input_field) > 0:
                input_field[0].send_keys(wf_name)
                self.app.navigation.click_link("Create")
            else:
                assert False
            time.sleep(3)

    def search_wf_by_name(self, wf_name):
        with allure.step('Search WF by name: %s' % wf_name):
            search_field = find_element(self.driver, "//input[@name='workflowsFilter']")
            search_field.clear()
            search_field.send_keys(wf_name, Keys.RETURN)
            time.sleep(5)

    def clean_wf_search_field(self):
        with allure.step('Clean WF search field'):
            search_field = find_element(self.driver, "//input[@name='workflowsFilter']")
            search_field.clear()
            search_field.send_keys(Keys.RETURN)
            time.sleep(1)

    def pick_wf_by_name(self, wf_name):
        with allure.step('Pick WF by name: %s' % wf_name):
            job = find_elements(self.driver, "//tbody//a[text()='%s']" % wf_name)
            assert len(job), "WF %s has not been found" % wf_name
            job[0].click()
            time.sleep(2)

    def open_wf_with_name(self, wf_name):
        with allure.step('Open WF with name: %s' % wf_name):
            time.sleep(2)
            self.search_wf_by_name(wf_name)
            self.pick_wf_by_name(wf_name)

    def grab_wf_id(self):
        with allure.step('Grab WF ID from current URL'):
            url = self.app.driver.current_url.split("/")
            return url[len(url) - 2]

    def open_wf_by_id(self, wf_id):
        with allure.step('Open WF by id: %s' % wf_id):
            self.search_wf_by_name(wf_id)
            el = find_elements(self.driver, "//a[contains(@href,'/workflows/%s')]" % (wf_id))
            assert len(el) > 0, "WF has not been found: %s" % wf_id
            el[0].click()
            time.sleep(8)

    def click_on_canvas_coordinates(self, X, Y, mode='canvas'):
        with allure.step('Click on coordinates (%s, %s) within canvas' % (X, Y)):
            if mode == 'canvas':
                canvas = find_elements(self.driver, "//*[contains(@class,'upper-canvas')]")
            else:
                canvas = find_elements(self.driver, "//body")
            assert len(canvas) > 0, "Canvas has not been found"
            mouse_click_element(self.driver, canvas[0])
            time.sleep(2)
            move_to_element_with_offset(self.driver, canvas[0], X, Y)
            time.sleep(7)

    def find_wf_name_for_job(self, job_id):
        with allure.step('Find WF name on the "jobs" page: %s' % job_id):
            self.app.mainMenu.jobs_page()
            self.app.job.search_jobs_by_id(job_id)
            print(job_id)
            el = find_elements(self.driver, "//tr[.//h5[text()='%s']]//a[contains(@href,'workflows')]/.." % job_id)
            if len(el) > 0: return el[0].text
            return None

    def get_wf_status_ui(self):
        # el = find_elements(self.driver, "//span[@class='b-WorkflowHeaderStatus__status']")
        # if len(el) > 0:
        #     return el[0].text

        # new UI
        nav_status = find_elements(self.app.driver, "//h5//*[local-name() = 'svg']")
        if len(nav_status) > 0:
           nav_status[0].click()
        time.sleep(1)
        print(self.app.driver.page_source)

        status = find_elements(self.app.driver,
                               "//div[contains(text(), 'Status:')]")
        if len(status) > 0:
            current_status = status[0].get_attribute('innerHTML')
            return current_status.split("Status: ")[1]

        assert False, "WF's status has not been found on the page"

    def open_job_from_launch_page(self, job_id):
        with allure.step('Open Job %s from WF Launch page' % job_id):
            link = find_elements(self.driver, "//div[contains(@data-auto-test-id,'workflow-operation-card')][.//div[text()='%s']]//a" % job_id)
            assert len(link) > 0, "Job %s has not been found" % job_id
            link[0].click()
            window_after = self.driver.window_handles[1]
            self.app.navigation.switch_to_window(window_after)
            time.sleep(5)
            self.app.user.close_guide()
            time.sleep(5)

    def download_report(self, name):
        with allure.step('Download WF report %s' % name):
            el = find_elements(self.driver,
                               "//*[text()='%s']/..//a[text()='Download Report']"% name)
            assert len(el) > 0, "Report %s has not been found" % name
            el[0].click()
            # try:
            #     instances = self.driver.window_handles
            #     self.driver.switch_to.window(instances[1])
            #     enable_download_in_headless_chrome(self.driver, self.app.temp_path_file)
            #     self.driver.switch_to_window(instances[0])
            # except:
            enable_download_in_headless_chrome(self.driver, str(self.app.temp_path_file))
            time.sleep(50)

    def regenerate_report(self, name):
        with allure.step('Regenerate WF report %s' % name):
            el = find_elements(self.driver,
                               "//*[text()='%s']/..//a[text()='Regenerate Report']" % name)
            assert len(el) > 0, "Report %s has not been found" % name
            el[0].click()

    def pause_wf(self):
        with allure.step('Pause WF'):
            self.app.navigation.click_link("Pause Workflow")
            time.sleep(2)
            try:
                el = find_elements(self.app.driver,
                                   "//div[@id='js-modal-overlay']//a[text()='Pause Workflow']")
                el[0].click()
            # self.app.navigation.click_link("Pause Workflow")
            except:
                print("Done")

    def verify_wf_sorted_by(self, column, order='desc'):
        with allure.step('Verify WF sorted by %s in %s order' % (column, order)):
            time.sleep(3)
            header_index = [head.text for head in find_elements(self.driver, "//th")].index(column)
            values = [v.text for v in find_elements(self.driver, "//tbody//tr/td[%s]" % (header_index + 1))]
            reverse = False if order == 'desc' else True
            assert sorted(values, reverse=reverse) == values, 'Records were not sorted in %s order' % order

    def verify_wf_details(self, details):
        with allure.step('Verify WF\'s details'):
            actual_detail = [e.text for e in find_elements(self.driver, "//tr[.//button[@aria-expanded='true']]//div["
                                                                        "@class='b-WorkflowListItemDropdown__label']")]

            for expected_detail in details:
                if expected_detail not in actual_detail:
                    assert False, "%s has not been found" % expected_detail

    def click_on_gear_for_wf(self, wf, sub_menu=None):
        with allure.step('Click on the gear for WF: %s' % wf):
            if isinstance(wf, int):  # find WF by ID
                # xpath = "//tr[@id='%s']//button//*[local-name() = 'svg']" % wf
                xpath = "//tr[.//a[@href='/workflows/%s']]" % wf

            else:  # find WF by name
                xpath = "//tr[.//a[text()='%s']]" % wf

            print(xpath)
            el = find_elements(self.driver, xpath+"//a[@href='/workflows' or @href='/']//*[local-name() = 'svg']")
            assert len(el) > 0, "Element %s has not been found" % wf
            el[0].click()
            time.sleep(1)

            if sub_menu:
                menu = find_elements(self.driver, xpath+"//li[text()='%s']" % sub_menu)
                assert len(menu) > 0, "Submenu %s has not been found" % sub_menu
                menu[0].click()
                time.sleep(1)

    def click_btn_rename_wf(self):
        rename_btn = find_elements(self.driver, "//h3[.//span[text()]]//a//*[local-name()='svg']")
        assert len(rename_btn) > 0, "Rename WF button has not been found"
        rename_btn[0].click()

    def rename_wf(self, new_name):
        with allure.step('Rename WF'):
            input = find_element(self.driver, "//input[@name='name']")
            input.clear()
            input.send_keys(new_name)

    def count_wf_on_page(self):
        with allure.step('Count WF on the current page'):
            wf_rows = find_elements(self.driver, "//tbody//tr[@id]")
            return len(wf_rows)

    def get_all_operators_on_launch_page(self):
        '''
        get info about all operators(jobs/modules) on the launch page
        :return: dict with operators info
        '''
        with allure.step('Get all operator(jobs/models) on the launch page'):
            time.sleep(3)
            operators = find_elements(self.driver, "//div[contains(@data-auto-test-id,'workflow-operations')]/div[contains(@data-auto-test-id,'workflow-operation-card')]")
            assert len(operators) > 0, "No operators have been found"
            oper_info = {}
            for oper in operators:
                op_type = oper.find_element('xpath',".//div[contains(@data-auto-test-id,'workflow-operation-type')]").text
                op_id = oper.find_element('xpath',".//div[contains(@data-auto-test-id,'workflow-operation-id')]").text
                try:
                    op_name = oper.find_element('xpath',".//div[contains(@data-auto-test-id,'workflow-operation-title')]").text
                except:
                    op_name = oper.find_element('xpath',".//a/../following-sibling::div[1]").text
                price, judgements = '', ''
                if op_type == 'JOB':
                    price = oper.find_element('xpath',
                        ".//div[text()='Price per Judgment']/following-sibling::div").text
                    judgements = oper.find_element('xpath',
                        ".//div[text()='Judgment per Row']/following-sibling::div").text
                oper_info[op_id] = {'type': op_type,
                                    'name': op_name,
                                    'price': price,
                                    'judgements': judgements}
            return oper_info

    def get_rows_to_order(self):
        with allure.step('Get rows to order'):
            current_rows = find_element(self.driver, "//input[@name='RowsToOrder']").get_attribute('value')
            max_rows = find_element(self.driver, "//input[@name='RowsToOrder']/following-sibling::span").text
            _current_rows = 0 if current_rows == '' else int(current_rows)
            _max_rows = 0 if max_rows[3:] == '' else int(max_rows[3:])
            print("max_rows:%s" % max_rows)
            return {"rows": _current_rows,
                    "max_rows": _max_rows}

    def set_rows_to_order(self, num):
        with allure.step('Set rows to order'):
            el = find_element(self.driver, "//input[@name='RowsToOrder']")
            el.clear()
            time.sleep(1)
            el.send_keys(num)

    def get_estimated_cost(self):
        with allure.step('Get current estimated cost'):
            cost = find_element(self.driver, "//div[text()='Estimated Contributor Cost']/following-sibling::div").text
            return cost[1:]

    def click_copy_icon(self, workflow_id):
        copy_icon = find_elements(self.driver, "//a[contains(@href,'/workflows/%s/connect')]/..//*[local-name() = 'svg']" % workflow_id)
        assert len(copy_icon) > 0, "Copy icon button has not been found"
        copy_icon[2].click()
        time.sleep(2)

    def fill_up_copy_wf_name(self, wf_name):
        with allure.step('Fill up copy WF name: %s' % wf_name):
            input_field = find_elements(self.app.driver,"//div[@id='js-modal-overlay']//input[@name='name']")
            if len(input_field) > 0:
                input_field[0].clear()
                input_field[0].send_keys(wf_name)
            else:
                assert False
            time.sleep(3)

class Data:

    def __init__(self, wf):
        self.wf = wf
        self.app = wf.app
        self.driver = wf.driver

    def delete_file_from_data(self, file_name):
        with allure.step('Delete file %s from WF data' % file_name):
            el = find_elements(self.driver,
                               "//tr[.//div[text()='%s']]//a[3]" % file_name)
            assert len(el) > 0, "File %s has not been found" % file_name
            mouse_click_element(self.driver, el[0])
            time.sleep(3)
            self.app.navigation.click_link("Delete")

    def delete_btn_disabled(self, file_name, is_not=False):
        el = find_elements(self.driver,
                           "//tr[.//div[text()='%s']]//a[3]" % file_name)
        assert len(el) > 0, "File %s has not been found" % file_name

        _class = el[0].get_attribute('class')
        active = _class.find('disabled')

        if is_not:
            assert active == -1, "Delete icon is disabled for file %s" % file_name
        else:
            assert active, "Delete icon is not disabled for file %s" % file_name

    def review_file(self, file_name, wf_id):
        with allure.step('Review data file %s for WF %s' % (file_name, wf_id)):
            el = find_elements(self.driver,
                               "//tr[.//div[text()='%s']]//a[contains(@href,'/workflows/%s/data/')]" % (
                                   file_name, wf_id))
            assert len(el) > 0, "File %s has not been found" % file_name
            # el[0].click()
            mouse_click_element(self.driver, el[0])
            time.sleep(3)

    def download_file(self, file_name):
        with allure.step('Download file: %s' % file_name):
            el = find_elements(self.driver,
                               "//tr[.//div[text()='%s']]//a[2]" % (
                                   file_name))
            assert len(el) > 0, "File %s has not been found" % file_name
            mouse_click_element(self.driver, el[0])
            time.sleep(2)


    def count_rows_for_uploaded_file(self, file_name):
        with allure.step('Get number of uploaded rows: %s' % file_name):
            if file_name == "all":
                count = 0
                files = find_elements(self.driver, "//tbody//tr")
                assert len(files) > 0, "No uploaded data has been found"
                for f in files:
                    el = f.find_element('xpath',".//td[2]/div")

                    count += int(el.text)
                return count
            else:

                el = find_elements(self.driver,
                                   "//tr[.//div[text()='%s']]//td[2]/div" % (
                                       file_name))
                assert len(el)>0, "File %s has not been found" % file_name
                return int(el[0].text)


class SelectOperator:

    def __init__(self, wf):
        self.wf = wf
        self.app = wf.app
        self.driver = wf.driver

    def search_job_into_side_bar(self, job):
        with allure.step('Search job into side bar'):
            el = find_element(self.driver, "//input[@name='query']")
            el.clear()
            el.send_keys(job)
            time.sleep(5)

    def verify_job_is_present_on_the_list(self, job_id, mode=True):
        with allure.step('Verify job %s is present on the result list' % job_id):
            el = find_elements(self.driver,
                               "//div[@data-source-id='%s']" % job_id)
            if mode:
                assert len(el) > 0, "Job %s has not been found" % job_id
            else:
                assert len(el) == 0, "Job %s has been found" % job_id

    def verify_job_status_on_the_list(self, job_id, job_status="Available"):
        with allure.step('Verify job status is %s ' % job_status):
            el = find_elements(self.driver,
                               "//div[@data-source-id='%s']" % job_id)
            assert len(el) > 0, "Job %s has not been found" % job_id

            status = el[0].find_element('xpath',"//div[@data-source-id='%s']/child::div[1]/child::div[2]" % job_id).text
            if job_status == "Available" and status != "": assert False, "Job status is not Available"
            if job_status == "Currently Unavailable" and status != "Currently Unavailable": assert False, "Job status is not Currently Unavailable"
            if job_status == "Not trained" and status != "Not trained": assert False, "Model status is not Not trained"
            if job_status == "Trained" and status != "": assert False, "Model status is not Trained"

    def connect_job_to_wf(self, job_id, xoffset, yoffset):
        with allure.step('Connect job to WF'):
            if isinstance(job_id, int):  # find WF by ID
                el = find_elements(self.driver,
                                   "//div[@data-source-id='%s']" % job_id)
            else:
                el = find_elements(self.driver,
                                   "//div[@data-source-id][.//div[text()='%s']]" % job_id)

            assert len(el) > 0, "Job %s has not been found" % job_id
            canvas = find_elements(self.driver, "//body")
            action = ActionChains(self.driver)
            action.click_and_hold(el[0]).pause(2).move_to_element_with_offset(canvas[0], xoffset,
                                                                              yoffset).release().perform()
            time.sleep(3)

    def filter_jobs_by_tag(self, tag):
        with allure.step('Select %s as a filter'):
            filter_el = find_elements(self.driver, "//input[@name='tag']/..//*[local-name()='svg']")
            assert len(filter_el) > 0, "Tag filter has not been found on the page"
            filter_el[0].click()

            el = find_elements(self.driver,
                               "//input[@name='tag']/../..//li[text()='%s']" % tag)
            assert len(el) > 0, "Tag %s has not been found on the page" % tag
            el[0].click()
            time.sleep(3)

    def filter_jobs_by_project(self, project):
        with allure.step('Select project %s as a filter'):
            filter_el = find_elements(self.driver, "//input[@name='project']/..//*[local-name()='svg']")
            assert len(filter_el) > 0, "Project filter has not been found on the page"
            filter_el[0].click()

            el = find_elements(self.driver,
                               "//input[@name='project']/../..//li[text()='%s']" % project)
            assert len(el) > 0, "Project %s has not been found on the page" % project
            el[0].click()
            time.sleep(3)

    def open_job_from_select_operator_panel(self, job_id):
        with allure.step('Open job %s from the "Add Operator" panel'):
            el = find_elements(self.driver,
                               "//a[@class='b-DataSourceCard__externalLink' and contains(@href,'/jobs/%s')]" % job_id)
            assert len(el) > 0, "Job %s has not been found " % job_id
            el[0].click()
            time.sleep(2)


class Routing:

    def __init__(self, wf):
        self.wf = wf
        self.app = wf.app
        self.driver = wf.driver

    def select_routing_method(self, name):
        with allure.step('Select routing method: %s' % name):
            find_element(self.driver, "//label[text()='Routing method']/..//div[@tabindex]").click()
            el = find_elements(self.driver, "//*[text()='%s']" % name)
            assert len(el) > 0, "Routing method has not been found"
            el[0].click()

    def add_filter(self, comparison_field, operator, value, connector=None, index=0):
        with allure.step('Add filter: %s, %s, %s ' % (comparison_field, operator, value)):
            current_rule = find_elements(self.driver, "//fieldset")[index]

            if connector and index == 1:
                current_rule.find_element('xpath',".//div[contains(@data-test-id, 'connector')]").click()
                el = current_rule.find_elements('xpath','.//li[text()="%s"]' % connector)
                assert len(el) > 0, "connector %s has not been found" % comparison_field
                el[0].click()

            current_rule.find_element('xpath',".//div[contains(@data-test-id,'comparisonField')]").click()
            el = current_rule.find_elements('xpath',".//span[text()='%s']/.." % comparison_field)
            assert len(el) > 0, "comparison_field %s has not been found" % comparison_field
            el[0].click()

            current_rule.find_element('xpath',".//div[contains(@data-test-id,'comparisonOperation')]").click()
            el = current_rule.find_elements('xpath','.//li[text()="%s"]' % operator)
            assert len(el) > 0, "operator %s has not been found" % operator
            el[0].click()

            try:
                value_field = current_rule.find_element('xpath',".//span[text()='Select row value (Required)']")
                value_field.click()
                if value != "":
                    select_value = current_rule.find_elements('xpath',".//li[text()='%s']" % value)
                    assert len(select_value) > 0, "Value %s has not been found" % value
                    select_value[0].click()
            except:
                value_field = current_rule.find_element('xpath',".//input[contains(@name,'comparisonValue')]")
                current_value = value_field.get_attribute('value')
                if current_value: value_field.clear()
                value_field.send_keys(value)
            time.sleep(2)

    def add_operator(self):
        with allure.step('Routing: add operation'):
            el = find_elements(self.driver, "//a[text()='Add Operator']")
            assert len(el) > 0, "Add Operation link has not been found"
            el[0].click()
            time.sleep(2)

    def add_condition(self):
        with allure.step('Routing: add operation'):
            el = find_elements(self.driver, "//span[text()='Add Condition']/..")
            assert len(el) > 0, "Add Operation link has not been found"
            el[0].click()
            time.sleep(2)

    def delete_operation(self):
        with allure.step('Routing: delete operation'):
            el = find_elements(self.driver,
                               "//div[contains(@data-auto-test-id,'workflow-rule-connector')]/following-sibling::a")
            assert len(el) > 0, "Delete Operation link has not been found"
            el[0].click()

    def close_routing_panel(self):
        with allure.step('Routing: Close panel'):
            # btn = find_elements(self.driver, "//div[contains(@class,'b-SlidingSidebar')]//*[local-name() = 'svg' and "
            #                                  "contains(@class, 'b-SelectDataSourceSidebar__closeIcon')]")
            btn = find_elements(self.driver, "//h2[text()='Add Operator']/following-sibling::a")
            assert len(btn), "Close Routing panel button has not been found"
            btn[0].click()
            time.sleep(2)

    def get_all_routing_rules(self):
        with allure.step('Routing: Get all Routing Rules'):
            rules = find_elements(self.driver, ".//fieldset")

            assert len(rules) > 0, "No rules have been found"

            rules_info = []
            for rule in rules:
                connector = rule.find_elements('xpath',".//div[contains(@data-test-id, 'connector')]/div[1]")
                if connector:
                    connector_value = connector[0].text
                else:
                    connector_value = None

                comparison = rule.find_element('xpath',".//div[contains(@data-test-id, 'comparisonField')]/div[1]")
                comparison_value = comparison.text

                operation = rule.find_element('xpath',".//div[contains(@data-test-id, 'comparisonOperation')]/div[1]")
                operation_value = operation.text

                value = rule.find_element('xpath',".//input[contains(@name,'comparisonValue')]").text

                error = rule.find_elements('xpath',".//div[contains(text(), 'Cannot set identical routing rules')]")

                if error:
                    err_msg = error[0].text
                else:
                    err_msg = None

                rules_info.append({
                    "connector": connector_value,
                    "comparison": comparison_value,
                    "operation": operation_value,
                    "value": value,
                    "error": err_msg
                })

            return rules_info

    def select_connector(self, value):
        with allure.step('Routing: Select connector'):
            rules = find_elements(self.driver, ".//fieldset")
            assert len(rules) > 1, "At least 2 rules should exist"
            rules[1].find_element('xpath',
                ".//div[contains(@data-test-id,'connector')]").click()
            el = find_elements(self.driver,
                               ".//li[text()='%s']" % value)
            assert len(el) > 0, "connector %s has not been found" % value
            el[0].click()

    def delete_rule_by_index(self, index):
        with allure.step('Routing: Delete rule by index %s' % index):
            rules = find_elements(self.driver, ".//fieldset")
            assert len(rules) > 2, "At least 2 rules should exist"
            # del_btn = rules[index].find_element('xpath',
            #     ".//*[local-name() = 'svg' and contains(@class, 'b-RoutingRulesForm__deleteIcon')]")
            del_btn = rules[index].find_element('xpath',
                "//div[contains(@data-auto-test-id,'workflow-rule-connector')]/following-sibling::a")
            mouse_over_element(self.driver, del_btn)
            time.sleep(1)
            mouse_click_element(self.driver, del_btn)

    def set_random_rows(self, random_num):
        with allure.step('Routing: Set random rows %s' % random_num):
            random_rows = find_elements(self.driver, "//input[contains(@name,'comparisonValue')]")
            assert len(random_rows), "Element has not been found"
            # random_rows[0].clear()
            current_value = random_rows[0].get_attribute('value')
            for i in range(len(current_value)):
                random_rows[0].send_keys(Keys.BACK_SPACE)
            random_rows[0].send_keys(random_num)
            el = find_element(self.driver, "//input[contains(@name,'comparisonValue')]/..").click()
