
import time
from adap.ui_automation.utils.selenium_utils import find_elements
from adap.ui_automation.services_config.annotation import Annotation
from adap.perf_platform.utils.logging import get_logger
from adap.ui_automation.utils.js_utils import *
import json
import allure

log = get_logger(__name__)


class ImageAnnotationUI(Annotation):
    # this index is only for the case when you enable boxes,ellipses,polygons, lines and dots, if you do not enable some of them, index will be different
    buttons = {
        "boxes": {
            "id": 0,
            "name": "boxes annotation"
        },
        "ellipses": {
            "id": 1,
            "name": "ellipses annotation"
        },
        "polygons": {
            "id": 2,
            "name": "polygons annotation"
        },
        "lines": {
            "id": 3,
            "name": "lines annotation"
        },
        "dots": {
            "id": 4,
            "name": "dots annotation"
        },
        "delete": {
            "id": 5,
            "name": "delete annotation"
        },
        "undo": {
            "id": 6,
            "name": "undo"
        },
        "redo": {
            "id": 7,
            "name": "redo"
        },
        "pan": {
            "id": 8,
            "name": "pan"
        },
        "zoomin": {
            "id": 9,
            "name": "zoom in"
        },
        "zoomout": {
            "id": 10,
            "name": "zoom out"
        },
        "reframe": {
            "id": 11,
            "name": "reframe"
        },
        "crosshair": {
            "id": 12,
            "name": "crosshair"
        },
        "focus_mode": {
            "id": 13,
            "name": "focus mode"
        },
        "hide_mode": {
            "id": 14,
            "name": "hide mode"
        },
        "shape_opacity": {
            "id": 15,
            "name": "shape opacity"
        },
        "show_label": {
            "id": 16,
            "name": "show label"
        },
        "auto_enhance": {
            "id": 17,
            "name": "auto enhance"
        },
        "help": {
            "id": 18,
            "name": "help"
        },
        "full_screen": {
            "id": 19,
            "name": "Full screen"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.data_unit = DataUnit(self)

    def activate_iframe_on_unit_page(self):
        with allure.step('Activate iframe on unit page'):
            iframe = find_elements(self.app.driver, "//iframe[contains(@name, 'unit_page')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)
            iframe = find_elements(self.app.driver, ".//iframe[contains(@src, 'image-annotation')]")
            if len(iframe) == 0:
                iframe = find_elements(self.app.driver, ".//iframe[contains(@src, 'Shapes')]")
            assert len(iframe) > 0, "iframe on unit page not found"
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)

    def annotate_image(self, mode, value, annotate_shape='box'):
        with allure.step('Annotate image'):
            if mode == 'random':
                for n in range(value):
                    try:
                        self.draw_shape(annotate_shape)
                    except Exception as e:
                        log.error({
                            'message': 'Annotation failure',
                            'exception': e.__repr__(),
                            'user_id': self.app.user.user_id
                            })

            if mode == 'ontology':
                for ontology_class, num_box in value.items():
                    self.select_ontology_class(ontology_class)
                    time.sleep(2)
                    for n in range(num_box):
                        try:
                            self.draw_shape(annotate_shape)
                        except Exception as e:
                            log.error({
                                'message': 'Annotation failure',
                                'exception': e.__repr__(),
                                'user_id': self.app.user.user_id
                                })

    def hide_mode(self):
        with allure.step('Hide mode'):
            find_elements(self.driver, "//div[@class='b-ToolbarWrapper']//span[.//button[contains(@class, 'b-Button')]]")[9].click()
            time.sleep(2)

    def get_annotation_value(self, index=0):
        with allure.step('Get annotation value'):
            annotations = self.driver.find_elements('xpath',"//input[contains(@name, 'annotation')]")
            value = annotations[index].get_attribute('value')
            if len(value) > 0:
                json_value = json.loads(value)
                return json_value
            return value

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

    def annotate_with_ontology_attribute(self, mode, value, max_annotate):
        with allure.step('Annotate until ontology attribute load'):
            _c = 0
            while _c < max_annotate:
                self.annotate_image(mode, value)
                time.sleep(6)
                save_button = find_elements(self.app.driver, "//div[@class='b-CommonForm__buttonText']")
                if len(save_button) > 0:
                    break
                else:
                    _c += 1
            else:
                msg = f'Not able to annotate image'
                raise Exception(msg)

    def go_to_object_panel(self):
        with allure.step('Go to object panel'):
            object = find_elements(self.driver, "//div[text()='OBJECTS']")
            object[0].click()
            object_class = find_elements(self.driver, "//div[@class='b-ListItem__itemEnd']")
            mouse_over_element(self.driver, object_class[0])

            time.sleep(1)
            object_class[0].click()
            time.sleep(2)


class DataUnit:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def activate_iframe_on_unit_page(self):
        with allure.step('Activate iframe on unit page'):
            iframe = find_elements(self.app.driver, "//iframe[contains(@name, 'unit_page')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)
            iframe = find_elements(self.app.driver, ".//iframe[contains(@src, 'Shapes')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(5)

    def find_a_judgment_dropdown_button_is_displayed(self, is_not=True):
        with allure.step("Check if dropdown is displayed on toolbar"):
            btn = find_elements(self.app.driver,
                                 "//button[@class='b-Judgments-Dropdown-DropdownButton__text-button']")
            if is_not:
                assert len(btn) > 0, "Drop down is not displayed on the page"
            else:
                assert len(btn) == 0, "Drop down displayed on the page"

    def click_find_a_judgment_dropdown_button(self):
        with allure.step("Click dropdown on toolbar"):
            btn = find_elements(self.app.driver,
                                "//button[@class='b-Judgments-Dropdown-DropdownButton__text-button']")
            assert len(btn) > 0, "Dropdown button is not found"
            btn[0].click()
            time.sleep(2)

    def click_worker_id_from_dropdown_list(self, worker_id):
        with allure.step("Click worker id %s from dropdown" % worker_id):
            item = find_elements(self.app.driver,
                                 "//button[@class='b-Judgments-Dropdown-SelectList-ListItem__button' and text()='%s']" % worker_id)
            assert len(item) > 0, "Dropdown list item is not found"
            item[0].click()
            time.sleep(2)

