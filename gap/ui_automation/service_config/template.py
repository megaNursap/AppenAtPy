import logging
import time

import allure

from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
from adap.ui_automation.utils.selenium_utils import find_element, get_text_by_xpath, find_elements, send_keys_by_xpath, \
    click_element_by_xpath

log = logging.getLogger(__name__)


class GTemplate:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver


    def gap_template_create(self, title=None, category='LiDAR', template_type='cuboid'):
        with allure.step(f"Create template category {category} {template_type} "):
            self.app.g_nav.open_gap_project_tab("Template Center")
            self.app.g_nav.gap_click_btn('Create template')
            self.app.g_nav.open_gap_template_tab(category)

            thumbs_xpath = "//div[@class='antd-pro-pages-project-template-center-components-styles-template-list']"
            els = find_elements(self.driver, thumbs_xpath)
            assert len(els) > 0, 'Template category not found'

            log.debug(f"Select template {template_type}")
            gif_chunk = '.e8d9b223' if 'cuboid' in template_type else '-sse.173e75eb'
            thumb_xpath = f"//div[contains(@style,'lidar{gif_chunk}.png')]"
            click_element_by_xpath(self.driver, thumb_xpath)

            title_lbl_xpath = "//label[contains(text(),'Template title')]"
            lbl = find_elements(self.driver, title_lbl_xpath)
            if not len(lbl) > 0:
                button_xpath = f"//div[contains(@style,'{gif_chunk}')]//*[contains(text(),'template')]"
                click_element_by_xpath(self.driver, button_xpath)
            get_text_by_xpath(self.driver, title_lbl_xpath)

            log.debug("Populate new template form title field")
            fld_title_xpath = "//input[@id='title']"
            if title is not None:
                send_keys_by_xpath(self.driver, fld_title_xpath, title)
            el = find_element(self.driver, fld_title_xpath)
            current_title = el.get_attribute("value")
            # if title:
            #     fld = find_element(self.driver, fld_title_xpath)
            #     fld.clear()
            #     send_keys_by_xpath(self.driver, fld_title_xpath,title)
            # else:
            #     title = get_text_by_xpath(self.driver,fld_title_xpath)

            log.debug("Populate new template form description text area")
            click_element_by_xpath(self.driver, "//span[contains(text(),'Insert')]")
            click_element_by_xpath(self.driver, "//div[contains(text(),'Horizontal line')]")
            click_element_by_xpath(self.driver, "//span[contains(text(),'Next')]")
            click_element_by_xpath(self.driver, "//span[contains(text(),'Save')]")
            time.sleep(1)
            scroll_to_page_bottom(self.driver)

            click_element_by_xpath(self.driver, "//span[contains(text(),'Complete')]")
            return current_title
