import time
import pytest
import allure
from selenium.webdriver import ActionChains

from adap.ui_automation.utils.js_utils import mouse_over_element
from adap.ui_automation.utils.selenium_utils import find_element, find_elements
from adap.ui_automation.services_config.annotation import Annotation


class ImageTranscription(Annotation):
    buttons = {
        "delete": {
            "id": 0,
            "name": "delete annotation"
        },
        "undo": {
            "id": 1,
            "name": "undo"
        },
        "redo": {
            "id": 2,
            "name": "redo"
        },
        "pan": {
            "id": 3,
            "name": "pan"
        },
        "zoom_in": {
            "id": 4,
            "name": "zoom in"
        },
        "zoom_out": {
            "id": 5,
            "name": "zoom out"
        },
        "reframe": {
            "id": 6,
            "name": "reframe"
        },
        "crosshair": {
            "id": 7,
            "name": "crosshair"
        },
        "focus_mode": {
            "id": 8,
            "name": "focus mode"
        },
        "hide_mode": {
            "id": 9,
            "name": "hide mode"
        },
        "shape_opacity": {
            "id": 10,
            "name": "shape opacity"
        },
        "show_label": {
            "id": 11,
            "name": "show label"
        },
        "auto_enhance": {
            "id": 12,
            "name": "auto enhance"
        },
        "help": {
            "id": 13,
            "name": "help"
        },
        "full_screen": {
            "id": 14,
            "name": "Full screen"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def save_prediction(self):
        with allure.step('Click prediction button'):
            time.sleep(3)
            predictions = self.driver.find_elements('xpath',"//button[contains(@class, 'b-Prediction--fetched')]")
            assert len(predictions) > 0, "prediction is not found"
            predictions[0].click()
            time.sleep(3)
            self.driver.find_elements('xpath',"//button[contains(@class, 'b-Metadata__doneButton')]")[0].click()
            time.sleep(2)

    def edit_transcription_text(self, category_header, index, new_text):
        with allure.step('edit text to label the job'):
            shape_items = self.get_shape_items_for_category(category_header)
            shape_items[index].click()
            text_area = self.driver.find_elements('xpath',"//textarea[@class='b-TextMetadata__input']")
            assert len(text_area) > 0, "Text area is not found"
            text_area[0].clear()
            text_area[0].send_keys(new_text)
            time.sleep(1)
            self.driver.find_elements('xpath',"//button[contains(@class, 'b-Metadata__doneButton')]")[0].click()
            time.sleep(2)

    def input_transcription_text(self, text):
        with allure.step('Input text to label the job'):
            text_area = self.driver.find_elements('xpath',"//textarea[@class='b-TextMetadata__input']")
            assert len(text_area) > 0, "Text area is not found"
            text_area[0].send_keys(text)
            time.sleep(1)
            self.driver.find_elements('xpath',"//button[contains(@class, 'b-Metadata__doneButton')]")[0].click()
            time.sleep(2)

    def get_transcription_text(self, category_header, index):
        with allure.step('Get transcription text'):
            shape_items = self.get_shape_items_for_category(category_header)
            shape_items[index].click()
            text_area = self.driver.find_elements('xpath',"//textarea[@class='b-TextMetadata__input']")
            assert len(text_area) > 0, "Text area is not found"
            res = text_area[0].text
            try:
                self.app.navigation.click_btn('Done')
            except:
                print('No Done button')
            return res

    def delete_transcription(self, category_header, index):
        with allure.step('Delete transcription'):
            shape_items = self.get_shape_items_for_category(category_header)
            shape_items[index].click()
            self.click_toolbar_button('delete')
            time.sleep(1)

    def get_shape_items_for_category(self, category_header):
        with allure.step('Get shape items from sidebar for category header %s' % category_header ):
            shape_items = find_elements(self.driver,"//div[contains(@class,'b-InstancesHeader')][.//span[contains(@class, 'b-InstancesHeader__className') and text()='%s']]/..//div[@class='b-InstanceItem__instance']/.." % category_header)
            assert len(shape_items) > 0, "Shapes have not been found"

            return shape_items

    def get_shape_count_for_category(self, category_header):
        with allure.step('Get number of shapefrom sidebar for category header %s' % category_header ):
            items = find_elements(self.driver,"//div[@class='b-Sidebar__category-header' and text()='%s']//span[@class='b-InstanceLimits__counter']" % category_header)
            assert len(items) > 0, "Shapes have not been found"
            return items[0].text

    def expand_category(self, category_header):
        with allure.step('Expand category %s' % category_header):
            time.sleep(1)
            expand_button = find_elements(self.driver,
                                          "//div[contains(@class,'b-Sidebar__category-header') and contains(.,'%s')]//button" % category_header)
            assert len(expand_button) > 0, "Expand btn has not been found"
            expand_button[0].click()
            time.sleep(1)

    def collapse_open_category(self):
        with allure.step('collapse category'):
            # close category

            sidebar = find_elements(self.driver,
                                "//div[@class='b-Sidebar']")
            assert len(sidebar) > 0
            sidebar[0].click()

            btn = find_elements(self.driver, "//div[contains(@class,'b-InstancesHeader__button')]//*[local-name() = 'svg']")
            assert len(btn) > 0

            time.sleep(1)
            btn[0].click()

    def draw_box_with_coordination(self, x0, y0, x1, y1, absolute_offset=False):
        with allure.step('Draw box with coordination'):
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            canvas.click()
            time.sleep(1)
            if absolute_offset:
                ActionChains(self.driver) \
                    .move_by_offset(x0, y0) \
                    .click_and_hold() \
                    .move_by_offset(x1, y1) \
                    .release() \
                    .perform()
            else:
                ActionChains(self.driver)\
                    .move_to_element_with_offset(canvas, 1, 1)\
                    .move_by_offset(x0, y0)\
                    .click_and_hold()\
                    .move_by_offset(x1, y1)\
                    .release()\
                    .perform()
            time.sleep(2)

    def find_labethisjob_floatingwrapper(self):
        with allure.step('find labe this job floating wrapper'):
            floating_wrapper = self.driver.find_elements('xpath',"//div[contains(@class, 'b-ShapeMetadata__floatingWrapper')]")
            return (False, True)[len(floating_wrapper) > 0]

    def click_toolbar_button(self, btn_name):
        with allure.step('Click toolbar button %s' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[@class='b-ToolbarWrapper']//button")
            buttons[index].click()
            time.sleep(5)

    def button_is_disable(self, btn_name):
        with allure.step('Check if button %s is disabled' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[@class='b-ToolbarWrapper']//button")
            el_class = buttons[index].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def get_instance_limits_sidebar(self, column_name):
        with allure.step('Get the Instance Limits Text in Sidebar on Image'):
            text_area = self.driver.find_element('xpath',
                f"//div[@class='b-Sidebar__category-header'][text()='{column_name}']//span[@class='b-InstanceLimits__limits']").text
            return text_area