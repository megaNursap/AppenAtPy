import logging
import time

import allure

from adap.api_automation.utils.data_util import get_data_file
from adap.ui_automation.utils.js_utils import enable_element_by_type
from adap.ui_automation.utils.selenium_utils import find_elements

log = logging.getLogger(__name__)


def gap_upload_file(driver, file_path=None, modal_window_xpath=None, close_modal_window=False, wait_time=10):
    with allure.step('Upload file: %s' % file_path):

        file_to_upload = get_data_file(file_path)
        el = find_elements(driver, "//input[@type='file']")

        if len(el) > 0:
            enable_element_by_type(driver, 'file')
            el[0].send_keys(file_to_upload)
        else:
            log.info("Not able to upload data file")
        time.sleep(wait_time)
        # if modal window "upload data" is still present - close it
        if close_modal_window:
            if not modal_window_xpath:
                modal_window_xpath = "//div[contains(@class, 'ant-modal')]//*[local-name()='span']"
            el = find_elements(driver,
                               modal_window_xpath)
            if len(el) > 0:
                el[0].click()
