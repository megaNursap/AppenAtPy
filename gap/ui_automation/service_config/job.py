import logging
import time

import allure

from adap.ui_automation.utils.js_utils import scroll_to_page_bottom, scroll_to_element
from adap.ui_automation.utils.selenium_utils import find_element, find_elements, send_keys_by_xpath, \
    click_element_by_xpath, get_text_by_xpath
from gap.ui_automation.utils.gap_workarounds import gap_upload_file

log = logging.getLogger(__name__)


class GJob:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.default_rate = "0.01"
        self.current_job = None
        self.current_workflow = None
        self.current_job_name = None
        self.job_description = None


    def gap_job_delete(self, job_name):
        with allure.step(f"Delete job {job_name}"):
            # TODO SK add body
            pass


    def gap_job_invite_workers_to_job_list(self, job_lst, workers_file):
        with allure.step(f"Invite workers to job via upload csv"):
            num_of_jobs = len(job_lst)
            assert num_of_jobs > 0, "No jobs found"
            job_lst[0].click()
            # via upload csv
            # click on job envelope
            click_element_by_xpath(self.driver, "//div[@class='ant-drawer-wrapper-body']")
            click_element_by_xpath(self.driver, "//div[@role='tab' and contains(text(),'Worker Management')]")
            click_element_by_xpath(self.driver,
                                   "//*[contains(@class,'anticon anticon-plus-circle ant-dropdown-trigger')]")

            opt_text = "Upload internal workers from csv"
            click_element_by_xpath(self.driver, f"//span[contains(text(),'{opt_text}')]")
            time.sleep(2)

            gap_upload_file(driver=self.driver, file_path=workers_file, wait_time=5)

            total = get_text_by_xpath(self.driver, "//li[@class='ant-pagination-total-text']")
            assert "0" not in total, f"{total}"
            self.app.g_nav.refresh_page()

    # TODO SK not completed yet: finish
    def gap_job_invite_workers_from_internal_pool(self, job, worker_email):
        with allure.step(f"Invite worker to gap job via internal pool"):
            job.click()
            click_element_by_xpath(self.driver, "//div[@class='ant-drawer-wrapper-body']")  # click on job envelope
            click_element_by_xpath(self.driver, "//div[@role='tab' and contains(text(),'Worker Management')]")

            click_element_by_xpath(self.driver,
                                   "//*[contains(@class,'anticon anticon-plus-circle ant-dropdown-trigger')]")
            opt_text = "Select from internal workers pool"
            click_element_by_xpath(self.driver, f"//span[contains(text(),'{opt_text}')]")

            modal_win_footer = find_elements(self.driver, "//div[@class='antd-pro-components-material-modal-buttons']")
            if len(modal_win_footer) > 0:
                scroll_to_element(self.driver, modal_win_footer[0])
            total = get_text_by_xpath(self.driver,
                                      "//div[@class='ant-modal-body']//li[@class='ant-pagination-total-text']")
            assert "0" not in total, f"{total}"
            row = find_elements(self.driver, "//tr[@data-row-key]")
            time.sleep(1)
            assert len(row) > 0, "No workers in list"

            check_box = find_elements(self.driver,
                                      "//tbody//tr[contains(@class,'ant-table-row-level-')]//*[@class='ant-checkbox']")
            if len(check_box) > 1:
                check_box[1].click()

            current_worker_email = get_text_by_xpath(self.driver,
                                                     "//tr[contains(@class,'ant-table-row-level-')]//td//span[contains(@style,'color')]")
            logging.info(f"Current worker email: {current_worker_email}")
            # TODO SK fix below

            # if worker_email is not None:
            #     assert worker_email == listed_worker, "expected worker email not in the list"
            scroll_to_page_bottom(self.driver)
            click_element_by_xpath(self.driver,
                                   "//div[@class='antd-pro-components-material-modal-buttons']//span[text()='Ok']")
            total = get_text_by_xpath(self.driver, "//li[@class='ant-pagination-total-text']")
            assert "0" not in total, f"{total}"
            self.app.g_nav.refresh_page()


    def gap_job_publish_and_start(self, job, do_publish=True, do_start=True):
        with allure.step("Job publish and start"):
            job.click()
            click_element_by_xpath(self.driver, "//div[@class='ant-drawer-wrapper-body']")  # click on job envelope


    def gap_job_create(self, contact_email, job_name=None, skill_type=None, rate=None, description=None, timeout=60,
                       strict_timing=False, enforce_same_worker_rework=True):
        with allure.step("Create job"):
            # verify location
            # invoke create job form
            click_element_by_xpath(self.driver, "//span[@aria-label='plus']")
            assert self.app.g_verify.text_present_on_page("Internal Job"), "Button 'Internal Job' not displayed"
            self.app.g_nav.gap_click_btn("Internal job")
            time.sleep(1)
            is_any_job_exist = self.app.g_verify.gap_verify_workflow_contain_job()
            # options for not QA job
            if is_any_job_exist:
                tmp = 'NO (rework job available to all workers)'
                click_element_by_xpath(self.driver, "//input[@class='ant-radio-input' and @value='yes']")
                assert self.app.g_verify.text_present_on_page("Enforce the same worker once turned back"), \
                    "Text 'Enforce the same worker once turned back' not present"

                if enforce_same_worker_rework:
                    tmp = "Yes (rework job only available to the original same worker)"
                click_element_by_xpath(self.driver, f"//span[contains(text(),'{tmp}')]")
                self.app.g_nav.gap_click_btn("Confirm")

            # job name
            job_name_xpath = "//input[@id='jobName']"
            if job_name:
                send_keys_by_xpath(self.driver, job_name_xpath, job_name)
            job_name = find_element(self.driver, job_name_xpath).get_attribute('value')
            logging.debug(f"Job name {job_name}")
            # strict timing
            if strict_timing:
                click_element_by_xpath(self.driver, "//*[@id='strictTiming']//span[contains(text(),'Yes')]")
            # skill type
            if skill_type:
                click_element_by_xpath(self.driver, "//span[contains(text(),'Please select')]")
                click_element_by_xpath(self.driver,
                                       f"//*[@class='ant-select-item ant-select-item-option' and @title='{skill_type}']")
                logging.debug(f"Skill type {skill_type}")
            # rate
            if not rate:
                rate = str(self.default_rate)
                logging.debug(f"Rate {rate}")
            send_keys_by_xpath(self.driver, "//input[@id='rate']", rate)
            # timeout
            if timeout:
                send_keys_by_xpath(self.driver, "//input[@id='timeout']", str(timeout))

            logging.debug(f"Contact_email: {contact_email}")
            send_keys_by_xpath(self.driver, "//input[@id='contactEmail']", contact_email)

            if not is_any_job_exist:
                if not description:
                    description = "test"
                # description temp workaround
                click_element_by_xpath(self.driver, "//span[contains(text(),'Insert')]")
                click_element_by_xpath(self.driver, "//div[contains(text(),'Horizontal line')]")

                assert rate and timeout and contact_email and description, "Required value(s) not set"
            scroll_to_page_bottom(self.driver)
            self.app.g_nav.gap_click_btn("Submit", timeout=3)
            return job_name
