import logging
import re

import allure

from adap.ui_automation.services_config.verification import GeneralVerification
from adap.ui_automation.utils.selenium_utils import find_elements

log = logging.getLogger(__name__)


class GVerify(GeneralVerification):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.driver = self.app.driver


    def gap_verify_current_url_contain(self, chunk, do_assert=False):
        with allure.step(f'Verify current URL contains "{chunk}"'):
            current_url = self.driver.current_url
            log.debug(f"current:{current_url}, expected:{chunk}")
            result = chunk in current_url
            if not do_assert:
                return result
            assert result, f"{chunk} is not in {current_url}"


    def is_project_details_page(self, projectid):
        with allure.step(f"Verify project {projectid} open"):
            return self.gap_verify_current_url_contain(projectid)


    def gap_verify_modal_window(self, window_class_name='ant-modal-title', do_assert=True):
        with allure.step("Verify modal window present"):
            xpath = f"//*[@class='{window_class_name}']"
            el = find_elements(self.driver, xpath)
            result = len(el) > 0
            if not do_assert:
                return result
            assert result, "Modal window Create Project not exist"


    def gap_verify_logged_as(self, user_nick_name, do_assert=True):
        with allure.step(f"Verify user with nick name {user_nick_name} logged in"):
            el = find_elements(self.driver,
                               f"//div[@class='antd-pro-components-global-header-index-right']//span[text()='{user_nick_name}']")
            els = len(el)
            if not do_assert:
                return els > 0
            assert els > 0, f"User with nick name {user_nick_name} not logged in"


    def gap_verify_workflow_contain_job(self, do_assert=False):
        with allure.step("Verify any job exist"):
            existing_job_block_xpath = "//div[contains(text(),'Ready')]"
            existing_job_block = find_elements(self.driver, existing_job_block_xpath)
            result = False
            if len(existing_job_block) > 0:
                result = True
            if do_assert:
                assert result, "jobs in workflow not found"
            return result


    def gap_verify_template_exist(self, title, is_expected=True):
        with allure.step(f"Verify template {title} exist"):
            if title is None:
                return
            re.escape(title)
            row_xpath = f"//td[text()='{title}']"
            log.debug(f"Escaped title {title}")
            el = find_elements(self.driver, row_xpath)
            result = len(el)
            msg = f"Found template {title}: {result}"
            if is_expected:
                assert result > 0, msg
            else:
                assert result == 0, msg
