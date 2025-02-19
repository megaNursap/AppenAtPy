import time
from telnetlib import EC

import allure
import pandas as pd
from faker import Faker

from adap.ui_automation.services_config.quality_flow.components import QFUnitTable
from adap.ui_automation.utils.selenium_utils import *


class QFJob:
    _RETURN_TO_JOBS = "//*[text()='return to jobs']"
    _COPY_JOB_TITLE = "//input[@name='Enter a title for the new job']"
    _COPY_JOB_SETTINGS = "//div[text()='{settings_type}']/../.."
    _COPY_JOB_DATA_SOURCE = "//div[@data-test-id='select-DATA SOURCE']"

    def __init__(self, project, app):
        self.project = project
        self.app = app
        self.driver = self.app.driver
        self.data = QFJobData(self, app)
        self.design = QFJobDesign(self, app)
        self.quality = QFJobQuality(self, app)
        self.launch = QFJobLaunch(self, app)
        self.setting = QFJobSetting(self, app)
        # self.monitor = QFJobMonitor(self, app)

    def return_to_jobs(self):
        with allure.step(f'Click Return to jobs '):
            click_element_by_xpath(self.driver, self._RETURN_TO_JOBS)

    def click_copy_job(self, job_name):
        with allure.step(f'Click Copy job icon'):
            click_element_by_xpath(self.driver,
                                   f"//span[text()='{job_name}']/parent::*/parent::*/parent::*/div[2]/a[4]")

    def click_delete_job(self, job_name):
        with allure.step(f'Click Delete job icon'):
            click_element_by_xpath(self.driver,
                                   f"//span[text()='{job_name}']/parent::*/parent::*/parent::*/div[2]/a[1]")

    def click_preview_job(self, job_name):
        with allure.step(f'Click Preview job icon'):
            click_element_by_xpath(self.driver,
                                   f"//span[text()='{job_name}']/parent::*/parent::*/parent::*/div[2]/a[3]")

    def open_job_tab(self, tab_name):
        with allure.step(f'Open job tab {tab_name}'):
            adjust_tab_name = tab_name.lower()
            tab = find_elements(self.app.driver,
                                f"//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{adjust_tab_name}') and contains(@href,'/jobs/')]")
            assert len(tab) > 0, f"Tab {adjust_tab_name} has not found"
            tab[0].click()
            time.sleep(4)

    def grab_job_id_from_url(self):
        with allure.step(f'Grab Job ID from current URL'):
            url = self.driver.current_url
            _job_id = url.split('/')
            return _job_id[-2]

    def run_job(self, is_confirm=True):
        with allure.step('Run Job'):
            click_element_by_xpath(self.driver, "//span[contains(text(),'Run Job')]")
        if is_confirm:
            with allure.step('Confirm to Run Job'):
                click_element_by_xpath(self.driver, "//a[contains(text(),'Run Job')]")
                time.sleep(2)

    def copy_job(self, new_job_name=None,
                 data_source=None,
                 copy_job_design=None,
                 launch_settings=None,
                 contributors=None,
                 action=None):
        if new_job_name:
            send_keys_by_xpath(self.driver, self._COPY_JOB_TITLE, new_job_name)

        if data_source:
            click_element_by_xpath(self.driver, self._COPY_JOB_DATA_SOURCE)
            time.sleep(1)
            click_element_by_xpath(self.driver, f"//li[@data-test-id and text()='{data_source}']")

        if copy_job_design:
            click_element_by_xpath(self.driver, self._COPY_JOB_SETTINGS.format(settings_type="Design (including "
                                                                                             "Ontology)"))

        if launch_settings:
            click_element_by_xpath(self.driver, self._COPY_JOB_SETTINGS.format(settings_type="Contributor "
                                                                                             "Settings"))

        if contributors:
            click_element_by_xpath(self.driver, self._COPY_JOB_SETTINGS.format(settings_type="Prices & Rows "
                                                                                             "Settings"))

        if action:
            self.app.navigation.click_link(action)
            time.sleep(4)

    def open_processes_running_in_backgroud(self):
        with allure.step('Open Processes Running in Background'):
            click_element_by_xpath(self.driver, "//*[@id='app']/div[2]/div/div[2]/div/div[1]/div/div[1]/div[2]/a[2]")
            time.sleep(1)


class QFJobData(QFUnitTable):
    _UNITS_COUNT_BY_TYPE = "//span[text()='{data_type}']/../following-sibling::span"

    def __init__(self, job, app):
        super().__init__(app)
        self.job = job
        self.app = app
        self.driver = self.app.driver

    def get_job_dataset_info(self):
        with allure.step('Get details about job uploaded data'):
            _total = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format(data_type='total units'))
            _sample = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format(data_type='sample rate'))
            _frequency = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format(data_type='frequency'))
            _advanced = get_text_by_xpath(self.driver, self._UNITS_COUNT_BY_TYPE.format(data_type='Advanced filter'))

            return {
                "sample_units": int(_sample),
                "total_units": int(_total),
                "frequency": _frequency,
                "advanced_filter": int(_advanced)
            }

    def get_all_units_on_page(self):
        with allure.step('Get details about all units on the page'):
            columns = self.get_columns_unit_table()
            data = self._get_table_rows()
            print('job===')
            print(columns)
            print(data)
            return pd.DataFrame(data, columns=columns)

    def select_units_checkbox_by_unit_ids(self, unit_ids):
        with allure.step(f'Select checkbox for units {unit_ids}'):
            for unit_id in unit_ids:
                self._select_checkbox_by_unit_id(unit_id)

    def click_actions_menu(self, menu):
        with allure.step(f'Click actions menu: {menu}'):
            self.app.navigation.click_link('Actions')
            click_element_by_xpath(self.driver, f"//li[text()='{menu}']")

    def _select_contributors_checkbox_from_assign_units_popup(self, contributor):
        with allure.step(f'Select: {contributor} checkbox'):
            click_element_by_xpath(self.driver,
                                   f"//*[@role='document']//label[text()='{contributor}']/parent::div/label[1]")

    def assign_selected_units_to_contributors(self, contributors):
        time.sleep(1)
        with allure.step(f'Select Actions'):
            click_element_by_xpath(self.driver, "//*[@role='document']//*[@name='search']")
        with allure.step(f'Select: {contributors} checkbox'):
            for contributor in contributors:
                self._select_contributors_checkbox_from_assign_units_popup(contributor)
        with allure.step('Click Assign'):
            click_element_by_xpath(self.driver, "//*[@role='document']//*[@name='search']")
            click_element_by_css_selector(self.driver, "[role='document']+div a")
            time.sleep(2)

    def validate_ui_elements_of_assign_selected_units_to_contributors_popup(self):
        with allure.step('Verify the presence of the text " Assign Selected Units to Contributor(s) "'):
            text = get_text_by_xpath(self.driver, "//h3[contains(text(), 'Assign Selected Units to Contributor(s)')]")
            assert text == 'Assign Selected Units to Contributor(s)', "Text ' Assign Selected Units to Contributor(s) ' has not been found"
        with allure.step('Verify the presence of the Search for a group input box'):
            search_input = find_elements(self.driver, "//*[@role='document']//input[@name='search']")
            assert len(
                search_input) > 0, "Search for contributor input box has not been found"
        with allure.step('Verify the presence of the Assign Selected Units To Contributors button'):
            search_input = find_elements_by_css_selector(self.driver, "[role='document']+div a")
            assert len(
                search_input) > 0, "Search for contributor input box has not been found"


class QFJobDesign:
    def __init__(self, job, app):
        self.job = job
        self.app = app
        self.driver = self.app.driver

    def delete_multiple_choices(self):
        with allure.step('Hover on Multiple Choices and click Delete'):
            # info_element = find_elements(self.app.driver, "(//h5[@data-baseweb='block']/following-sibling::span)[1]")
            # hover = ActionChains(self.app.driver).move_to_element(info_element[0])
            # hover.perform()
            element = find_element_by_css_selector(self.app.driver, ".ge-Editor__content .cml--elements--radios .body")
            hover = ActionChains(self.driver).move_to_element(element)
            hover.perform()
            click_element_by_css_selector(self.driver,
                                          ".ge-Editor__content .cml--elements--radios [title='Delete'] svg")

    def is_multiple_choice_visible(self):
        element = find_elements_by_css_selector(self.app.driver, ".ge-Editor__content .cml--elements--radios")
        return False if len(element) == 0 else True

    def input_textbox_single_line_from_side_panel(self, question_text, required=None):
        with allure.step(f'Input question text: {question_text}'):
            send_keys_by_css_selector(self.driver, "#side-panel-contents .display-name-form input", question_text, True)

    def close_dialog_message(self):
        with allure.step('Close dialog message'):
            click_element_by_css_selector(self.driver, "#message button .b-svg-icon")


class QFJobQuality(QFUnitTable):
    _JUDGMENT_MODIFICATION = "//label[.//span[text()='{settings}']]"
    _ACTION = "//h4[text()='{action}']"
    _ACTION_POPUP = "//*[@role='document']//h4[text()='{action}']"
    _TEST_QUESTION_MODE = "//span[text()='{mode}']/parent::*/div"
    _TEST_QUESTION_CHECKBOX = "//span[text()='{option}']/parent::*/div"
    _IFRAME_BY_INDEX = "//*[@id='testQuestionArray.{index}']//iframe"
    _SKIP_TEST_QUESTION_CHECKBOX_BY_INDEX = "//*[@id='testQuestionArray.{index}']//p[text()='Skip Question']//parent::*/label"
    _HIDE_ANSWER_CHECKBOX_BY_INDEX = "//*[@id='testQuestionArray.{index}']//p[text()='Hide Answer']//parent::*/label"
    _TEST_QUESTION_MODE_DROPDOWN_BY_INDEX = "//*[@id='testQuestionArray.{index}']//p[text()='Mode']/parent::*//*[@data-test-id='select-mode']"
    _MINIMUM_MATCHING_ACCURACY_BY_INDEX = "//*[@id='testQuestionArray.{index}']//*[@name='MinimumMatchingAccuracy']"
    _QUESTION_TEXT_SINGLE_LINE_BY_INDEX = "//*[@id='testQuestionArray.{index}']//*[@type='text']"
    _REASON_TEST_SINGLE_LINE_BY_INDEX = "//*[@id='testQuestionArray.{index}']//*[@class='reason_textarea']"
    _STATUS_BY_INDEX = "//table/tbody/tr['{index}']/td[4]//input"

    def __init__(self, job, app):
        super().__init__(app)
        self.job = job
        self.app = app
        self.driver = self.app.driver

    def qa_job_set_judgment_modification(self, name):
        with allure.step(f'Set Judgment Modification for QA job: {name}'):
            if name == "Allow the QA contributor to modify the original contributor's judgments":
                click_element_by_xpath(self.driver, self._JUDGMENT_MODIFICATION.format(settings=name))
            else:
                click_element_by_xpath(self.driver, self._JUDGMENT_MODIFICATION.format(
                    settings="Do not allow QA Contributor to modify judgments and ..."))
                click_element_by_xpath(self.driver, self._JUDGMENT_MODIFICATION.format(settings=name))

    def select_action(self, action=None):
        with allure.step(f'Select Action: {action}'):
            click_element_by_xpath(self.driver, self._ACTION.format(action=action))

    def select_action_from_popup(self, action=None):
        with allure.step(f'Select Action from popup: {action}'):
            click_element_by_xpath(self.driver, self._ACTION_POPUP.format(action=action))

    def select_units_checkbox_by_unit_ids(self, unit_ids):
        with allure.step(f'Select checkbox for units {unit_ids}'):
            for unit_id in unit_ids:
                self._select_checkbox_by_unit_id(unit_id)

    def select_tq_mode(self, mode):
        with allure.step(f'Select mode {mode} for test question'):
            click_element_by_xpath(self.driver, self._TEST_QUESTION_MODE.format(mode=mode))

    def set_minimum_matching_accuracy(self, minimum_matching_accuracy):
        with allure.step('Minium Matching Accuracy'):
            send_keys_by_css_selector(self.driver, "[name='MinimumAccuracy']", minimum_matching_accuracy, True)

    def select_tq_checkbox(self, option):
        with allure.step(f'Select checkbox {option} for test question'):
            click_element_by_xpath(self.driver, self._TEST_QUESTION_CHECKBOX.format(option=option))

    def switch_on_off_hide_answer(self):
        with allure.step('Switch ON OFF Hide Answer'):
            click_element_by_xpath(self.driver, "//div[text()='Hide Answer']/parent::div//label")

    def click_actions_menu(self, menu):
        with allure.step(f'Click actions menu: {menu}'):
            self.app.navigation.click_link('Actions')
            click_element_by_xpath(self.driver, f"//span[text()='{menu}']")

    def configure_test_question_by_index(self, index, is_skip_tq=None, is_hide_answer=None, tq_mode=None):
        with allure.step(
                f'Edit TQ by index: {index} with Skip TQ: {is_skip_tq} and Hide Answer: {is_hide_answer} and TQ Mode: {tq_mode}'):
            if is_skip_tq is not None:
                click_element_by_xpath(self.driver, self._SKIP_TEST_QUESTION_CHECKBOX_BY_INDEX.format(index=index))
            if is_hide_answer is not None:
                click_element_by_xpath(self.driver, self._HIDE_ANSWER_CHECKBOX_BY_INDEX.format(index=index))
            if tq_mode is not None:
                click_element_by_xpath(self.driver, self._TEST_QUESTION_MODE_DROPDOWN_BY_INDEX.format(index=index))

    def configure_textbox_single_line_test_question_by_index(self, index, is_skip_tq=None, is_hide_answer=None,
                                                             tq_mode=None, minimum_matching_accuracy=None,
                                                             question_text=None, reason=None):
        with allure.step(
                f'Edit TQ by index: {index} with Skip TQ: {is_skip_tq} and Hide Answer: {is_hide_answer} and TQ Mode: {tq_mode}'):
            self.driver.switch_to.frame(index)
            if is_skip_tq is not None:
                click_element_by_xpath(self.driver, self._SKIP_TEST_QUESTION_CHECKBOX_BY_INDEX.format(index=index))
            if is_hide_answer is not None:
                click_element_by_xpath(self.driver, self._HIDE_ANSWER_CHECKBOX_BY_INDEX.format(index=index))
            if tq_mode is not None:
                click_element_by_xpath(self.driver, self._TEST_QUESTION_MODE_DROPDOWN_BY_INDEX.format(index=index))
            if minimum_matching_accuracy is not None:
                send_keys_by_css_selector(self.driver, self._MINIMUM_MATCHING_ACCURACY_BY_INDEX.format(index=index),
                                          minimum_matching_accuracy, True)
            if question_text is not None:
                send_keys_by_css_selector(self.driver, self._QUESTION_TEXT_SINGLE_LINE_BY_INDEX.format(index=index),
                                          question_text)
            if reason is not None:
                click_element_by_xpath(self.driver, self._REASON_TEST_SINGLE_LINE_BY_INDEX.format(index=index))
            self.driver.switch_to.default_content()

    def is_all_test_questions_enabled(self):
        with allure.step(f'Verify all test questions are enabled'):
            switches_status = []
            all_rows = find_elements(self.driver, "//table/tbody/tr")
            for i in range(len(all_rows)):
                row_status = find_element(self.driver, self._STATUS_BY_INDEX.format(index=i)).get_attribute('checked')
                print("row_status ", row_status)
                switches_status.append(row_status)
            return all(status == 'true' for status in switches_status)

    def get_all_test_question_units_on_page(self):
        with allure.step('Get details about all units on the page'):
            columns = ['QUESTION ID', 'LINKED UNIT ID', 'CONTESTED %', 'MISSED %', 'JUDGMENTS', 'LAST UPDATED', 'MODE']
            data = self._get_table_rows()
            print('job===')
            print(columns)
            print(data)
            return pd.DataFrame(data, columns=columns)

    def get_row_from_table(self):
        with allure.step('Get row from table'):
            all_rows = find_elements(self.driver, "//tbody//tr")
            return len(all_rows)

    def enable_all_test_questions(self):
        with allure.step('Enable all test questions'):
            click_element_by_xpath(self.driver,"//div[text()='Question ID']/parent::*/parent::*//preceding-sibling::*[1]/div/div/label")
            click_element_by_xpath(self.driver, "//div[text()='Actions']")
            click_element_by_xpath(self.driver, "//span[text()='Enable Selected']")

    def disable_all_test_questions(self):
        with allure.step('Disable all test questions'):
            click_element_by_xpath(self.driver,"//div[text()='Question ID']/parent::*/parent::*//preceding-sibling::*[1]/div/div/label")
            click_element_by_xpath(self.driver, "//div[text()='Actions']")
            click_element_by_xpath(self.driver, "//span[text()='Disable Selected']")


class QFJobLaunch:
    _INTERNAL_TARGET = "//label[text()='Internal']/..//input"
    _EXTERNAL_TARGET = "//label[text()='External']/..//input"
    _EXTERNAL_NETWORK = "//label[.//span[text()='{}']]"
    _LINK_FOR_INTERNAL_USERS = "//h5[text()='Link for internal users']/../a[contains(@href, '/quality/tasks')]"
    _JUDGEMENTS_PER_ROW = "//div[text()='Judgments per Row']/../..//input[@name='judgments']"
    _ROWS_PER_PAGE = "//div[text()='Rows per Page']/../..//input[@name='judgments']"
    _ASSIGNMENT_LEASE_EXPIRY = "//div[text()='Assignment Lease Expiry']/../..//input[@name='judgments']"
    _PAY_RATE = "//div[text()='Pay Rate']/../..//span[text()='Select ...']"
    _ALLOW_QA_OWN_WORK = "//div[text()='Allow Contributors to QA Their Own Work']/../..//label[.//input]"

    def __init__(self, job, app):
        self.job = job
        self.app = app
        self.driver = self.app.driver

    def select_crowd_settings(self, internal=None, external=None, external_network=None):
        with allure.step(
                f'Select Crowd Settings: internal= {internal}, external={external} network = {external_network}'):
            if internal is not None:
                el = find_elements(self.driver, self._INTERNAL_TARGET)
                assert len(el), f"Element {self._INTERNAL_TARGET} has not been found"
                current_internal_status = el[0].is_selected()

                if current_internal_status != internal:
                    el[0].find_element('xpath', "./..//label").click()

            if external is not None:
                el = find_elements(self.driver, self._EXTERNAL_TARGET)
                assert len(el), f"Element {self._EXTERNAL_TARGET} has not been found"
                current_external_status = el[0].is_selected()

                if current_external_status != external:
                    el[0].find_element('xpath', "./..//label").click()

            if external_network:
                click_element_by_xpath(self.driver, self._EXTERNAL_NETWORK.format(external_network))

    def grab_internal_link(self):
        with allure.step("Return internal link"):
            el = find_elements(self.driver, self._LINK_FOR_INTERNAL_USERS)
            assert len(el), "Link has not been found"
            return el[0].get_attribute('href')

    def fill_out_price_and_row_settings(self, judgements_per_row=None,
                                        row_per_page=None,
                                        assignment_lease_expiry=None,
                                        pay_rate=None,
                                        statistic_type=None):
        with allure.step("Set up Price & Row Settings"):
            if judgements_per_row:
                send_keys_by_xpath(self.driver, self._JUDGEMENTS_PER_ROW, judgements_per_row, clear_current=True)

            if row_per_page:
                send_keys_by_xpath(self.driver, self._ROWS_PER_PAGE, row_per_page, clear_current=True)

            if assignment_lease_expiry:
                send_keys_by_xpath(self.driver, self._ASSIGNMENT_LEASE_EXPIRY, assignment_lease_expiry,
                                   clear_current=True)

            if pay_rate:
                click_element_by_xpath(self.driver, self._PAY_RATE)
                click_element_by_xpath(self.driver, f"//li[text()='{pay_rate}']")

            if statistic_type:
                pass

    def allow_contributor_qa_their_own_work(self, allow=True):
        with allure.step("Allow Contributors to QA Their Own Work"):
            el = find_elements(self.driver, self._ALLOW_QA_OWN_WORK)
            assert len(el), "Element has not been found"

            current_status = el[0].get_attribute('checked')
            print('status', current_status)

            if current_status != allow:
                click_element_by_xpath(self.driver, self._ALLOW_QA_OWN_WORK)

    def set_up_project_id(self, project_id, action=None):
        with allure.step("Set up project id for job"):
            click_element_by_xpath(self.driver, "//div[@data-test-id='select-acId']")
            click_element_by_xpath(self.driver, f"//li[@data-test-id and contains(text(), {project_id})]")

            if action:
                self.app.navigation.click_link("Save And Add Project")


class QFJobSetting:
    _JOB_MODE = "//*[@type='radio']/parent::*/span[text()='{job_mode}']"
    _UPLOAD_CSV = "[role='document'] [type='file']"

    def __init__(self, job, app):
        self.job = job
        self.app = app
        self.driver = self.app.driver

    def start_data_routing(self):
        with allure.step('Start data routing'):
            click_element_by_xpath(self.driver, "//a[contains(text(),'Start data routing')]")
        with allure.step('Confirm to Start data routing'):
            click_element_by_xpath(self.driver, "//a[contains(text(),'Confirm Settings')]")
            time.sleep(2)

    def select_job_mode(self, job_mode):
        with allure.step(f'Select Mode: {job_mode}'):
            click_element_by_xpath(self.driver, self._JOB_MODE.format(job_mode=job_mode))

    def configure_test_question_quiz_mode_only_settings(self, minimum_accuracy=None,
                                                        total_test_question_in_quiz_mode=None):
        if minimum_accuracy is not None:
            with allure.step(f'Input Minimum Accuracy : {minimum_accuracy}'):
                set_value_by_css_selector(self.driver, "input[name='MinimumAccuracy']", minimum_accuracy)
        if total_test_question_in_quiz_mode is not None:
            with allure.step(f'Input Total Test Question In Quiz Mode : {total_test_question_in_quiz_mode}'):
                set_value_by_css_selector(self.driver, "[name='TotalTest']", total_test_question_in_quiz_mode)

    def configure_test_question_quiz_and_work_mode_settings(self, minimum_accuracy=None,
                                                            total_test_question_in_work=None,
                                                            test_question_frequency_in_work_in_pages=None,
                                                            total_test_question_in_quiz_mode=None):
        if minimum_accuracy is not None:
            with allure.step(f'Input Minimum Accuracy : {minimum_accuracy}'):
                send_keys_by_css_selector(self.driver, "[name='MinimumAccuracy']", minimum_accuracy)
        if total_test_question_in_work is not None:
            with allure.step(f'Input Total Test Question In Work Mode : {total_test_question_in_work}'):
                send_keys_by_css_selector(self.driver, "[name='totalTestQuestionInWork']", total_test_question_in_work)
        if test_question_frequency_in_work_in_pages is not None:
            with allure.step(
                    f'Input Test Test Question Frequency In Work In Pages : {test_question_frequency_in_work_in_pages}'):
                send_keys_by_css_selector(self.driver, "[name='testQuestionFrequencyInWorkInPages']",
                                          test_question_frequency_in_work_in_pages)
        if total_test_question_in_quiz_mode is not None:
            with allure.step(f'Input Total Test Question In Quiz Mode : {total_test_question_in_quiz_mode}'):
                send_keys_by_css_selector(self.driver, "[name='TotalTest']", total_test_question_in_quiz_mode)

    def configure_row_settings(self, judgement_per_row=None, row_per_page=None, assignment_lease_expiry=None,
                               timelimit_alert_threshold=None):
        if judgement_per_row is not None:
            with allure.step(f'Input Judgement Per Row: {judgement_per_row}'):
                send_keys_by_css_selector(self.driver, "[name='judgments']", judgement_per_row, True)
        if row_per_page is not None:
            with allure.step(f'Input Row Per Page : {row_per_page}'):
                send_keys_by_css_selector(self.driver, "[id=':r27:'][name='judgments']", row_per_page, True)
        if assignment_lease_expiry is not None:
            with allure.step(f'Input Assignment Lease Expiry : {assignment_lease_expiry}'):
                send_keys_by_css_selector(self.driver, "[name='AssignmentLeaseExpiry']", assignment_lease_expiry, True)
        if timelimit_alert_threshold is not None:
            with allure.step(f'Input Timelimit Alert Threshold : {timelimit_alert_threshold}'):
                send_keys_by_css_selector(self.driver, "[name='TimeLimitThresholdSec']", assignment_lease_expiry, True)

    def configure_dynamic_judgements(self, enable_questions=True, max_judgement_per_row=None, minimum_confidence=None,
                                     maximum_judgements=None):
        if enable_questions:
            with allure.step(f'Enable Dynamically Collect Judgments: {enable_questions}'):
                click_element_by_xpath(self.driver,
                                       "//*[text()='Dynamically Collect Judgments']/parent::*/parent::*//label")
        if max_judgement_per_row is not None:
            with allure.step(f'Input Max Judgement Per Row : {max_judgement_per_row}'):
                send_keys_by_css_selector(self.driver, "[name='maxDynamicJudgements']", max_judgement_per_row, True)
        if enable_questions is not None:
            with allure.step('Move Available Question to Selected Questions'):
                click_element_by_xpath(self.driver, "//*[text()='Available Questions']/parent::*//*[@data-tooltip]")
        if minimum_confidence is not None:
            with allure.step(f'Select Option Minimum Confidence with value : {minimum_confidence}'):
                click_element_by_xpath(self.driver, "//*[text()='Minimum Confidence']/parent::*/parent::*/label")
                send_keys_by_css_selector(self.driver, "[name='minimumConfidence']", minimum_confidence, True)
        if maximum_judgements is not None and minimum_confidence is None:
            with allure.step(f'Select Option Maximum Judgements with value : {maximum_judgements}'):
                click_element_by_xpath(self.driver, "//*[text()='Matching Judgments']/parent::*/parent::*/label")
                send_keys_by_css_selector(self.driver, "[name='matchingJudgements']", minimum_confidence, True)

    def enable_public_link(self, enabled=True):
        if enabled:
            with allure.step('Enable Public Link'):
                if is_text_present(self.driver, "Share Link is disabled"):
                    click_element_by_xpath(self.driver,
                                           "//h5[text()='Public link']/parent::*/parent::*//*[@type='checkbox']/parent::*")
        else:
            with allure.step('Disable Public Link'):
                if is_text_present(self.driver, "Share Link is enabled"):
                    click_element_by_xpath(self.driver,
                                           "//h5[text()='Public link']/parent::*/parent::*//*[@type='checkbox']")

    def get_public_link(self):
        if is_text_present(self.driver, "Share Link is enabled"):
            with allure.step('Get Public Link'):
                el = find_element_by_css_selector(self.driver, "[name='linkUrl']")
                return el.get_attribute("value")

    def click_actions_menu(self, menu):
        with allure.step(f'Click actions menu: {menu}'):
            self.app.navigation.click_link('Action')
            click_element_by_xpath(self.driver, f"//span[text()='{menu}']")

    def click_assign_contributor_menu(self, menu):
        with allure.step(f'Click actions menu: {menu}'):
            self.app.navigation.click_link('Assign Contributors')
            click_element_by_xpath(self.driver, f"//span[text()='{menu}']")

    def select_single_contributor_checkboxes_from_assign_contributor_popup(self, text):
        with allure.step(f'Search contributor: {text}'):
            send_keys_to_element(self.driver, "//*[@role='document']//*[@name='search']", text, clear_current=True)
            time.sleep(2)
            click_element(self.driver, "//*[@role='rowgroup']//label")

    def select_multiple_contributor_checkboxes_from_assign_contributor_popup(self, number_of_contributors):
        with allure.step(f'Select checkbox for {number_of_contributors} contributor(s)'):
            i = 1
            while i < number_of_contributors + 1:
                contributor_checkbox = find_element(self.driver, f"//*[@role='document']//table//tbody/tr[{i}]//label")
                contributor_checkbox.click()
                i += 1

    def get_contributor_by_index_from_assign_contributor_popup(self, index):
        return get_text_by_xpath(self.driver, f"//*[@role='document']//table/tbody/tr[{index}]/td[2]")

    def assign_current_job_to_contributor(self, contributor_email):
        with allure.step('Select All Contributors'):
            assign_contributors_dropdown = find_element(self.driver, "//*[text()='Assign Contributors']")
            assign_contributors_dropdown.click()
            all_contributors = find_element(self.driver, "//*[text()='All Contributors']")
            all_contributors.click()
        with allure.step(f'Search contributor: {contributor_email}'):
            search_box = find_element(self.driver, "//*[@role='document']//*[@name='search']")
            search_box.send_keys(contributor_email)
            time.sleep(2)
            contributor_checkbox = find_element(self.driver, "//*[@role='rowgroup']//label")
            contributor_checkbox.click()
        with allure.step('Click Assign'):
            assign_button = find_element(self.driver, "//*[text()='Assign']")
            assign_button.click()
            time.sleep(2)

    def assign_current_job_to_group_contributor(self, contributor_group_name):
        with allure.step('Select All Contributors'):
            assign_contributors_dropdown = find_element(self.driver, "//*[text()='Assign Contributors']")
            assign_contributors_dropdown.click()
            contributor_group = find_element(self.driver, "//*[text()='Contributor Groups']")
            contributor_group.click()
        with allure.step(f'Search contributor: {contributor_group_name}'):
            search_box = find_element(self.driver, "//*[@role='document']//*[@name='search']")
            search_box.send_keys(contributor_group_name)
            time.sleep(2)
            contributor_checkbox = find_element(self.driver, "//*[@role='rowgroup']//label")
            contributor_checkbox.click()
        with allure.step('Click Assign'):
            assign_button = find_element(self.driver, "//*[text()='Assign']")
            assign_button.click()
            time.sleep(2)

    def assign_current_job_to_multiple_contributor(self, number_of_contributors):
        with allure.step('Select All Contributors'):
            assign_contributors_dropdown = find_element(self.driver, "//*[text()='Assign Contributors']")
            assign_contributors_dropdown.click()
            all_contributors = find_element(self.driver, "//*[text()='All Contributors']")
            all_contributors.click()
        with allure.step(f'Select checkbox for {number_of_contributors} contributor(s)'):
            i = 1
            while i < number_of_contributors + 1:
                contributor_checkbox = find_element(self.driver, f"//*[@role='document']//table//tbody/tr[{i}]//label")
                contributor_checkbox.click()
                i += 1
        with allure.step('Click Assign'):
            assign_button = find_element(self.driver, "//*[text()='Assign']")
            assign_button.click()
            time.sleep(2)

    def get_contributor_name_by_index(self, index):
        return get_text_by_xpath(self.driver, f"//table/tbody/tr[{index}]/td[2]")

    def remove_contributor_from_current_job(self, contributor_email):
        with allure.step(f'Search and select checkbox for contributor: {contributor_email}'):
            search_box = find_element(self.driver, "//*[@name='search']")
            search_box.send_keys(contributor_email)
            time.sleep(1)
            contributor_checkbox = find_element(self.driver, "//*[@role='rowgroup']//label")
            contributor_checkbox.click()
        with allure.step(f'Remove contributor {contributor_email} out of table list'):
            action_dropdown = find_element(self.driver, "//*[text()='Action']")
            action_dropdown.click()
            remove_button = find_element(self.driver, "//*[text()='Remove']")
            remove_button.click()
            time.sleep(2)

    def select_checkboxes_by_contributor_email(self, contributors):
        time.sleep(2)
        i = 1
        for contributor in contributors:
            with allure.step(f'Select checkbox for {contributor} contributors'):
                contributor_checkbox = find_element(self.driver,
                                                    f"//table/tbody/tr/td[text()='{contributor}']/parent::*//label")
                contributor_checkbox.click()
                i += 1

    def remove_all_contributors_from_current_job(self):
        with allure.step(f'Select checkbox for all contributors'):
            time.sleep(2)
            all_contributor_checkbox = find_element(self.driver, f"//table/thead/tr//label")
            all_contributor_checkbox.click()
        with allure.step(f'Remove all contributors out of table list'):
            action_dropdown = find_element(self.driver, "//*[text()='Action']")
            action_dropdown.click()
            remove_button = find_element(self.driver, "//*[text()='Remove']")
            remove_button.click()
            time.sleep(2)

    def validate_the_table_list_contains_contributor(self, contributor):
        with allure.step(f'Verify the table list not contains contributor : {contributor}'):
            contributor = find_elements(self.driver, f"//td[text()='{contributor}']")
            assert len(contributor) == 1, "Contributor is not in the table list"
            return True

    def validate_the_table_list_is_empty(self):
        with allure.step('Verify the table list is empty'):
            contributor_list = find_elements(self.driver, "//table/tbody/tr")
            assert len(contributor_list) == 0, "Table list is not empty"
            return True

    def validate_ui_elements_in_remove_contributor_tab(self):
        with allure.step('Verify the presence of the text " Remove Contributor "'):
            text = get_text_by_xpath(self.driver, "//h3[text()='Remove Contributor']")
            assert text == 'Remove Contributor', "Text ' Remove Contributor ' has not been found"
        with allure.step('Verify the presence of the "Cancel" and "Remove" buttons'):
            cancel_button = find_elements(self.driver, "//a[contains(text(), 'Cancel')]")
            assert len(cancel_button) > 0, "Cancel button has not been found"
            confirm_button = find_elements(self.driver, "//a[text()= 'Confirm']")
            assert len(confirm_button) > 0, "Confirm button has not been found"
            return True

    def validate_ui_elements_in_assign_contributor_modal(self):
        with allure.step('Verify the presence of the text " All Contributors "'):
            text = get_text_by_xpath(self.driver, "//h3[text()='All Contributors']")
            assert text == 'All Contributors', "Text ' All Contributors ' has not been found"
        with allure.step('Verify the search box is visible'):
            ele = find_elements(self.driver, "//*[@role='document']//*[@name='search']")
            assert len(ele) == 1, "Search box is not in the assign contributor modal"
        with allure.step('Verify the list of contributors is visible'):
            ele = find_elements(self.driver, "//*[@role='document']//table/tbody")
            assert len(ele) == 1, "List of contributors is not in the assign contributor modal"
        with allure.step('Verify the pagination is visible'):
            ele = find_elements(self.driver, "//*[@data-test-id='select-pagination']")
            assert len(ele) == 1, "The pagination is not in the assign contributor modal"
        with allure.step('Verify Manage All Contributors link is visible'):
            ele = find_elements_by_css_selector(self.driver, "[role='document']+div+div a")
            assert len(ele) == 1, "Manage All Contributors link is not in the assign contributor modal"
        with allure.step('Verify Assign button is visible'):
            ele = find_elements(self.driver, "//*[text()='Assign']")
            assert len(ele) == 1, "Assign button is not in the assign contributor modal"
            return True

    def confirm_to_remove_contributor(self):
        with allure.step('Confirm to unassign contributor'):
            confirm_button = find_element(self.driver, "//a[text()= 'Confirm']")
            confirm_button.click()
            time.sleep(2)

    def close_assign_contributor_modal(self):
        with allure.step('Close Assign Contributor Modal'):
            close_icon = find_element(self.driver, "//*[@role='document']/parent::div/div[1]/a")
            close_icon.click()
            time.sleep(2)

    def validate_the_table_list_not_contains_contributor(self, contributor):
        with allure.step(f'Verify the table list not contains contributor : {contributor}'):
            contributor = find_elements(self.driver, f"//td[text()='{contributor}']")
            assert len(contributor) == 0, "Contributor is still in the table list"
            return True

    def upload_contributors_via_csv(self, file_name, wait_time=15):
        with allure.step('Upload data file'):
            el = find_elements_by_css_selector(self.app.driver, self._UPLOAD_CSV)
            if len(el) > 0:
                el[0].send_keys(file_name)
            else:
                print("Not able to upload data file")

            try:
                self.app.navigation.click_link("Proceed Anyway")
            except:
                print("no warning message")

            time.sleep(wait_time)

    def generate_contributors_csv(self):
        faker = Faker()
        email1, email2 = faker.email(), faker.email()
        name1, name2 = faker.name(), faker.name()

        filename = 'InternalContributorsCSV.csv'

        data = [
            {'email': email1, 'name': name1},
            {'email': email2, 'name': name2}
        ]
        df = pd.DataFrame(data)
        base_dir = os.getcwd()
        file_path = f"{base_dir}/{filename}"
        df.to_csv(file_path, index=False)
        print(f"CSV file '{filename}' created with new data.")
        return {
            'file_path': file_path,
            'file_name': filename,
            'email1': email1,
            'name1': name1,
            'email2': email2,
            'name2': name2,
        }


class QFJobMonitor:
    """
    deprecated
    """
    _MONITOR_INFO = "//h5[contains(text(),'{}')]/preceding-sibling::div[text()]"

    def __init__(self, job, app):
        self.job = job
        self.app = app
        self.driver = self.app.driver

    def get_total_jobs_count(self):
        with allure.step("Get Total Jobs count  from Monitor page"):
            return get_text_by_xpath(self.driver, self._MONITOR_INFO.format('Total Jobs'))

    def get_contributors_count(self):
        with allure.step("Get Contributors count  from Monitor page"):
            return get_text_by_xpath(self.driver, self._MONITOR_INFO.format('Contributors'))
