import logging
import time
import pytest
import allure
from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.utils.selenium_utils import find_elements, find_element
from selenium.webdriver import ActionChains


LOGGER = logging.getLogger(__name__)


class AudioAnnotationUI(Annotation):
    buttons = {
        "zoom_in": {
            "id": 0,
            "name": "zoom_in"
        },
        "zoom_out": {
            "id": 1,
            "name": "zoom_out"
        },
        "reframe": {
            "id": 2,
            "name": "reframe"
        },
        "previous": {
            "id": 3,
            "name": "previous"
        },
        "play_pause": {
            "id": 4,
            "name": "play_pause"
        },
        "snap_mode": {
            "id": 5,
            "name": "snap_mode"
        },
        "help": {
            "id": 6,
            "name": "help"
        },
        "volume": {
            "id": 7,
            "name": "volume"
        },
        "save_close": {
            "id": 8,
            "name": "save_close"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def click_toolbar_button(self, btn_name):
        with allure.step('Click toolbar button %s' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',
                "//div[@class='b-ToolbarWrapper b-AudioAnnotationApp__toolbar']//button")
            buttons[index].click()
            time.sleep(2)

    def begin_annotate(self, index):
        with allure.step('Begin annotate'):
            annotate = self.driver.find_elements('xpath',
                "//div[contains(@class, 'b-AudioAnnotationPreview__fullscreenText--begin')]")
            assert annotate, "Begin Annotate button is not found"
            annotate[index].click()
            time.sleep(3)

    def edit_annotate(self, index):
        with allure.step('Edit annotate'):
            edit = self.driver.find_elements('xpath',
                "//div[contains(@class, 'b-AudioAnnotationPreview__fullscreenText--edit')]")
            assert edit, "Edit Annotate button is not found"
            edit[index].click()
            time.sleep(2)

    def get_segment_count(self):
        with allure.step('Get segment count'):
            segment = self.driver.find_elements('xpath',
                "//div[contains(@class, 'b-AudioSegment')]")
            return len(segment)

    def select_ontology_class(self, class_name):
        with allure.step('Select ontology class %s' % class_name):
            el = find_elements(self.driver, "//div[@class='b-AudioLayer__title' and text()='%s']" % class_name)
            assert el, "Ontology class %s has not been found" % class_name
            el[0].click()
            time.sleep(1)

    # Todo, click work for audio annotation, hold does not work
    def annotate_audio(self):
        with allure.step('Annotate audio'):
            action = ActionChains(self.driver)
            canvas = find_element(self.driver, "//div[@class='b-AudioCanvas__waveCanvas']")
            action.move_to_element_with_offset(canvas, 0, 0)
            action.move_by_offset(100, 100)
            time.sleep(3)
            action.click_and_hold()
            time.sleep(3)
            action.move_by_offset(200, 0)
            time.sleep(3)
            action.release().perform()

    def button_is_disable(self, btn_name):
        with allure.step('Check if button %s is disabled' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',
                "//div[@class='b-ToolbarWrapper b-AudioAnnotationApp__toolbar']//button")
            el_class = buttons[index].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def get_current_cursor(self):
        with allure.step('Get current cursor'):
            cursor = find_elements(self.driver,
                                   "//div[@class='b-AudioCursor b-Cursor b-AudioAnnotationApp__playback-cursor']")
            _c = cursor[0].get_attribute('style').split(":")
            return str(_c[1].strip())[:-3]

    def mini_map_visible(self):
        with allure.step('Check if mini map visible'):
            mini_map = find_elements(self.driver, "//div[@class='b-Minimap b-Minimap__visible']")
            if len(mini_map) > 0:
                return True
            else:
                return False

    def save_for_nothing_annotate(self):
        with allure.step('Save for nothing to annotate'):
            button = find_elements(self.driver, "//button[contains(@class, 'b-ReopenForAnnotating__save-and-close')]")
            assert button, "Save and close button is not found"
            button[0].click()
            time.sleep(3)




