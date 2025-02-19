import random
import time

import allure

from adap.e2e_automation.services_config.workflow_ui_judgments import open_job_link, close_guide
from adap.ui_automation.utils.selenium_utils import find_elements, find_element, create_screenshot

XPATH_TQ_IFRAME = "//iframe[contains(@name,'tq_page')]"

def find_tq_job(job, wfs):
    found = False
    for wf in wfs['workflows']:
        tq_job = None
        for s in wf["steps"]:
            if s["data_processor_id"] == str(job):
                found = True
            if found and s["data_processor_id"] \
                    and (s["data_processor_type"] == 'Builder::Job')\
                    and (s["data_processor_id"] != str(job)):
                tq_job = s["data_processor_id"]
            if found and tq_job: return tq_job
    return False


def generate_tq_for_job(job_url, contributor, expected_answers):
    driver = open_job_link(job_url, contributor)
    close_guide(driver)

    total = expected_answers["total_count"]
    skipped = expected_answers["skipped"]
    answers = expected_answers["answers_by_index"]

    for q in range(total):
        job_completed = find_elements(driver, "//*[text()='There is no work currently available in this task.']")
        if job_completed:
            break
        try:
            index_answ = list(map(lambda i: i > 0, answers)).index(True)
            answers[index_answ] -= 1

            el = find_elements(driver, "//div[@class='cml_row'][.//input[not(@value='skip_this_question') and not("
                                       "@value='tq_confirm_completion')]]/label")
            el[index_answ].click()
        except:
            if skipped:
                find_elements(driver, "//div[@class='cml_row'][.//input[@value='skip_this_question']]/label")[0].click()
                reason = find_element(driver, "//textarea[contains(@class, 'skip_question_reason')]")
                reason.send_keys("test TQG")
                skipped -= 1

        find_elements(driver, "//input[@value='tq_confirm_completion']/..")[0].click()
        find_element(driver, "//input[@type='submit']").click()

        time.sleep(3)
    driver.quit()


class Quality:

    def __init__(self, job):
        self.job = job
        self.app = job.app

    def switch_to_tq_iframe(self):
        iframe = find_element(self.app.driver, XPATH_TQ_IFRAME)
        self.app.driver.switch_to.frame(iframe)

    def download_tq_report(self):
        pass

    def upload_tq_report(self):
        pass

    def open_tq_unit_by_id(self, id):
        with allure.step("Open test question's unit by ID: %s" % id):
            if id == "random":
                """
                  open random unit and return unit id
                """
                tq_rows = find_elements(self.app.driver, "//tbody//tr")
                if len(tq_rows) == 0:
                    assert False, "Test questions have not been found"
                random_row = random.randint(1, len(tq_rows)-1)
                unit = tq_rows[random_row].find_element('xpath',".//a")
                unit_id = unit.text
                unit.click()
                time.sleep(3)
                return unit_id
            elif id == 'first row':
                tq_rows = find_elements(self.app.driver, "//tbody//tr")
                if len(tq_rows) == 0:
                    assert False, "Test questions have not been found"
                first_unit = tq_rows[0].find_element('xpath',".//a")
                first_unit_id = first_unit.text
                first_unit.click()
                time.sleep(3)
                return first_unit_id
            else:
                unit = find_elements(self.app.driver, "//tbody//a[text()='%s']" % id)
                if len(unit) == 0:
                    assert False, "Test question %s has not been found" % id
                unit[0].click()
                time.sleep(3)

    def create_random_tqs(self, number_tq=1):
        with allure.step("Create %s test questions" % number_tq):
            print(" %s test questions wil be created" % number_tq)
            # there is no tqs
            time.sleep(3)
            page_text = "Add Test Questions"
            element = find_elements(self.app.driver, "//*[text()[contains(.,\"%s\")]]" % page_text)

            if len(element):
                try:
                    el = find_elements(self.app.driver, "//h5[text()='Create']/..")
                    assert len(el) > 0, "Create TQ button has not been found"
                    el[0].click()
                except:
                    self.app.navigation.click_link("Create Test Questions")
            else:  # add more tqs
                try:
                    self.app.navigation.click_link("Create More")
                except:
                    # find_element(self.app.driver, "//button[.//span[text()='Add More']]").click()
                    find_element(self.app.driver, "//*[text()='Add More']").click()

                    el = find_elements(self.app.driver, "//a[.//h4[text()='Create']]")
                    assert len(el) > 0, "Create TQ button has not been found"
                    el[0].click()

            time.sleep(2)
            for i in range(number_tq):
                self.switch_to_tq_iframe()
                el = find_elements(self.app.driver, "//input[contains(@name,'unit[data]') and @type='checkbox']")
                if len(el) > 0:
                    el[0].click()
                time.sleep(1)
                self.app.navigation.click_link("Save & Create Another")
                time.sleep(5)
                self.app.driver.switch_to.default_content()
            time.sleep(4)

    def grab_tq_info(self):
        """
          Collect info about TQ : answers
        """
        with allure.step("Grab info about TQ"):
            self.switch_to_tq_iframe()
            ans = {}
            rows = find_elements(self.app.driver, "//div[@id='unit[data]']//div[@class='cml_row']//input")
            for el in rows:
                ans[el.get_attribute('value')] = el.get_attribute('checked')
                time.sleep(2)
            self.app.driver.switch_to.default_content()
            return ans

    def click_answer(self, value):
        self.switch_to_tq_iframe()

        el = find_elements(self.app.driver, "//input[@value='%s']" % value)
        if len(el) > 0:
            el[0].click()
        else:
            assert False, "Answer with value '%s' has not been found"

        self.app.driver.switch_to.default_content()

    def disable_enable_last_tq_on_quality_page(self):
        """
          Disable/Enable last tq on QUALITY page, if disabled - enable, else disable
        """
        with allure.step("Disable/Enable last test question on QUALITY page"):
            el = find_elements(self.app.driver, "//input[@type='checkbox']/..")
            if len(el) > 0:
                el[-1].click()
            else:
                assert False, "Element has not been found"

    def disable_tq(self, unit_id=None):
        """
          Disable tq: if unit_id=None, disable tq on edit page
        """
        with allure.step("Disable test question"):
            if unit_id is None:
                el = find_elements(self.app.driver, "//input[@id='tq-switcher']")
                if len(el) > 0:
                    el[0].click()
                else:
                    assert False, "Element has not been found"
            else:
                unit = find_elements(self.app.driver, "//tr[.//a[text()='%s']]//button" % unit_id)
                if len(unit) == 0:
                    unit = find_elements(self.app.driver, "//tr[.//a[text()='%s']]//input[@type='checkbox']/.." % unit_id)
                if len(unit) == 0:
                    assert False, "Test question %s has not been found" % id
                unit[0].click()

    def enable_tq(self, unit_id=None):
        """
          Enable tq: if unit_id=None, disable tq on edit page
        """
        with allure.step("Disable test question"):
            if unit_id is None:
                el = find_elements(self.app.driver, "//input[@id='tq-switcher']")
                if len(el) > 0:
                    el[0].click()
                else:
                    assert False, "Element has not been found"
            else:
                unit = find_elements(self.app.driver, "//tr[.//a[text()='%s']]//input[@type='checkbox']/.." % unit_id)
                if len(unit) == 0:
                    assert False, "Test question %s has not been found" % unit_id
                unit[0].click()

    def get_number_of_active_tq(self):
        with allure.step('Get number of active TQs'):
            el = find_elements(self.app.driver,
                               "//h4[text()='Total Active:']/following-sibling::div//h4")

            assert len(el) > 0, "Element has not been found"
            return int(el[0].text)
            # quize_active = find_elements(self.app.driver, "//a[text()='Launch a test run']")
            # if len(quize_active)>0:
            #     self.app.navigation.click_link('View Answer Distribution')
            #     time.sleep(1)
            #     _s = find_elements(self.app.driver, "//span[@class='b-AnswerDistributionModal__title b-AnswerDistributionModal__title--thin']")[0].text
            #
            #     find_element(self.app.driver,"//div[@class='modal-header b-Modal__header']//*[local-name()='svg']").click()
            #     return int(_s.split(" Test Questions")[0][1:])
            # else:
            #     el = find_elements(self.app.driver, "//span[@class='b-QualityMessagingLegacy__message']")
            #     assert len(el)>0, "Element has not been found"
            #     _s = el[0].text
            #
            #     return int(_s.split(" of ")[0])

    def get_random_unit_id(self, enable='true'):
        time.sleep(3)
        if enable == 'true':
            _ = "b-Switch--checked"
        else:
            _ = "b-Switch"
        # units = find_elements(self.app.driver, "//tbody//tr[.//label[contains(@class,'%s')]]" % _)
        units = find_elements(self.app.driver, "//tbody//tr")

        if len(units) == 0:
            assert False, "Test questions have not been found"
        random_row = random.randint(1, len(units))
        unit = units[random_row].find_element('xpath',".//a")
        unit_id = unit.text
        return unit_id

    def click_generate_tq(self):
        with allure.step("Click: Generate TQ"):
            page_text = "Add Test Questions"
            element = find_elements(self.app.driver, "//*[text()[contains(.,\"%s\")]]" % page_text)
            if len(element):
                el = find_elements(self.app.driver, "//h5[text()='Generate']/..")
                assert len(el) > 0, "Generate TQ button has not been found"
                el[0].click()
            else:
                try:
                    find_element(self.app.driver, "//*[text()='Add More']").click()
                    el = find_elements(self.app.driver, "//h4[text()='Generate']")
                    assert len(el) > 0, "Generate TQ button has not been found"
                    el[0].click()
                except:
                   pass

    def order_tq(self, num, channel):
        time.sleep(2)
        tq_num = find_elements(self.app.driver, "//input[@name='orderCount']")
        if tq_num:
            tq_num[0].clear()
            tq_num[0].send_keys(num)

        if channel == 'Appen Trusted Contributors':
            find_element(self.app.driver, "//label[.//span[text()='Appen Trusted Contributors']]").click()
        else:
            find_element(self.app.driver, "//label[.//span[text()='Custom Channels']]").click()
            chs = channel.split(',')
            for c in chs:
                find_element(self.app.driver, "//label[text()='%s']" % c).click()
        time.sleep(1)

    def order_more_tg_btn_is_disable(self):
        find_element(self.app.driver, "//*[text()='Add More']").click()
        time.sleep(1)
        el = find_elements(self.app.driver, "//h4[text()='Generate']/..")
        assert len(el) > 0, "Order more TQs button has not been found"
        print(el[0].is_enabled())
        return not el[0].is_enabled()

    def get_count_tqs_by_type(self, tq_type):
        if tq_type == 'Total Active':
            el = find_elements(self.app.driver,
                               "//h4[text()='Total Active:']//..//div//h4")
        else:
            el = find_elements(self.app.driver, "//div[text()='%s']//div" % tq_type)
        assert len(el) > 0, "Test Questions info: %s has not been found" % tq_type
        return el[0].text

    def click_to_create_tq(self):
        with allure.step("Click create tq button"):
            try:
                el = find_elements(self.app.driver, "//h5[text()='Create']/..")
                assert len(el) > 0, "Create TQ button has not been found"
                el[0].click()
            except:
                find_element(self.app.driver, "//button[.//*[text()='Add More']]").click()
                el = find_elements(self.app.driver, "//a[.//h4[text()='Create']]")
                assert len(el) > 0, "Create TQ button has not been found"
                el[0].click()

            time.sleep(8)

    def get_passing_threshold(self):
        with allure.step("Get current passing threshold value"):
            el = find_elements(self.app.driver,
                               "//input[@class='b-TestQuestion-TokenThresholdPercents__thresholdinput']")
            assert len(el) > 0, "Did not find threshold"
            return el[0]

    def edit_passing_threshold_successfully(self, threshold):
        with allure.step("Edit passing threshold value"):
            el = find_elements(self.app.driver,
                               "//input[contains(@class, 'b-TestQuestion-TokenThresholdPercents__thresholdinput')]")
            assert el, "Did not find threshold"
            el[0].clear()
            time.sleep(1)
            el[0].send_keys(threshold)
            time.sleep(1)
            error_message = find_elements(self.app.driver,
                                          "//input[contains(@class, 'b-TestQuestion-TokenThresholdPercents--error')]")
            if len(error_message) == 0:
                return True
            else:
                return False

    def click_sortable_header_by_name(self, header_name):
        with allure.step("Click sortable header for name %s" % header_name):
            header = find_elements(self.app.driver,
                                   "//th//div[text()='%s']" % header_name)
            assert len(header) > 0, "Header with name %s is not found" % header_name
            header[0].click()
            time.sleep(2)

    def click_tq_dropdown(self):
        with allure.step("Click test question dropdown button"):
            btn = find_elements(self.app.driver,
                                "//button[contains(@class, 'b-TestQuestion-Dropdown-DropdownButton__button')]//*[local-name() = 'svg']")
            assert len(btn) > 0, "Dropdown button is not found"
            btn[0].click()
            time.sleep(2)

    def find_all_tq_dropdown_list_items(self):
        with allure.step("Find test question dropdown items"):
            list_items = []
            items = find_elements(self.app.driver,
                                  "//button[@class='b-TestQuestion-Dropdown-SelectList-ListItem__button']")
            assert len(items) > 0, "Dropdown list item is not found"
            for i in range(len(items)):
                list_items.append(items[i].text)
            return list_items

    def click_tq_dropdown_list_item(self, item_name):
        with allure.step("Click test question dropdown item with name %s" % item_name):
            item = find_elements(self.app.driver,
                                 "//button[@class='b-TestQuestion-Dropdown-SelectList-ListItem__button' and text()='%s']" % item_name)
            assert len(item) > 0, "Dropdown list item is not found"
            item[0].click()
            time.sleep(2)

    def get_accuracy_status(self):
        with allure.step("Get details of accuracy status"):
            item = find_elements(self.app.driver,
                                 "//div[@class='b-TestQuestion-AccuracyStatus']")
            assert len(item) > 0, "Accuracy detail status not found"
            return item[0].text

    def get_span_title_in_accuracy_mode(self):
        with allure.step("Get span title in accuracy mode"):
            span_title = find_elements(self.app.driver,
                                       "//div[@class='b-TestQuestion-AccuracySpans-AccuracySpan__span-title']")
            assert len(span_title) > 0, "Span title not found"
            return span_title[0].text

    def get_span_pass_in_accuracy_mode(self):
        with allure.step("Get span title in accuracy mode"):
            span_pass = find_elements(self.app.driver,
                                      "//span[@class='b-TestQuestion-AccuracySpans-AccuracySpan__span-pass']")
            assert len(span_pass) > 0, "Span pass not found"
            return span_pass[0].text

    def get_span_classname_in_accuracy_mode(self):
        with allure.step("Get span class name in accuracy mode"):
            span_classname = find_elements(self.app.driver,
                                           "//span[@class='b-TestQuestion-AccuracySpans-AccuracySpan__span-classnames']")
            assert len(span_classname) > 0, "Span class name not found"
            return span_classname[0].text

    def get_tq_judgment_status(self):
        with allure.step("Get test question judgment status"):
            judgment_status = find_elements(self.app.driver,
                                            "//div[@class='b-TestQuestion-JudgmentStatus__statusText']")
            assert len(judgment_status) > 0, "judgment status not found"
            return judgment_status[0].text

    def get_tq_judgment_grade(self):
        with allure.step("Get test question judgment grade"):
            judgment_grade = find_elements(self.app.driver,
                                           "//div[@class='b-TestQuestion-JudgmentStatus__grade']")
            assert len(judgment_grade) > 0, "judgment grade not found"
            return judgment_grade[0].text

    def get_span_status(self):
        with allure.step("Get test question span status"):
            span_status = find_elements(self.app.driver,
                                        "//div[@class='b-TestQuestion-SpanStatus__statusText']")
            assert len(span_status) > 0, "Span status not found"
            return span_status[0].text
