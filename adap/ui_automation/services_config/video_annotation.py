
import logging
import time
import pytest
import allure
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.utils.selenium_utils import find_elements
from adap.api_automation.utils.data_util import *
from selenium.webdriver import ActionChains
from adap.ui_automation.utils.js_utils import element_to_the_middle
from adap.ui_automation.utils.js_utils import mouse_over_element

LOGGER = logging.getLogger(__name__)


def create_video_annotation_job(app, api_key, cml, user_name, password, data_file):
    job = JobAPI(api_key)
    job.create_job_with_cml(cml)
    job_id = job.job_id
    app.user.login_as_customer(user_name=user_name, password=password)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')

    ontology_file = get_data_file("/video_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    # app.verification.text_present_on_page("2/1000 Classes Created")
    time.sleep(3)

    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job.launch_job()

    job = JobAPI(api_key, job_id=job_id)

    job.wait_until_status('running', 80)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    return job_id


class VideoAnnotationUI(Annotation):
    # this index is only for the case when you enable 'box','polygon','dot','line', 'point-box' for linear_interpolation, if you do not enable some of them, index will be different
    buttons = {
        "boxes": {
            "id": 0,
            "name": "boxes annotation"
        },
        "polygons": {
            "id": 1,
            "name": "polygons annotation"
        },
        "lines": {
            "id": 2,
            "name": "lines annotation"
        },
        "dots": {
            "id": 3,
            "name": "dots annotation"
        },
        "point_box": {
            "id": 4,
            "name": "point_box annotation"
        },
        "merging": {
            "id": 5,
            "name": "merging"
        },
        "switch_ids": {
            "id": 6,
            "name": "switch_ids"
        },
        "pan": {
            "id": 7,
            "name": "pan"
        },
        "zoom_in": {
            "id": 8,
            "name": "zoom_in"
        },
        "zoom_out": {
            "id": 9,
            "name": "zoom_out"
        },
        "reframe": {
            "id": 10,
            "name": "reframe"
        },
        "cross_hair": {
            "id": 11,
            "name": "cross_hair"
        },
        "focus_mode": {
            "id": 12,
            "name": "focus_mode"
        },
        "hide_mode": {
            "id": 13,
            "name": "hide_mode"
        },
        "shape_opacity": {
            "id": 14,
            "name": "shape_opacity"
        },
        "map": {
            "id": 15,
            "name": "map"
        },
        "show_label": {
            "id": 16,
            "name": "show_label"
        },
        "auto_enhance": {
            "id": 17,
            "name": "auto_enhance"
        },
        "error_log": {
            "id": 18,
            "name": "error_log"
        },
        "help": {
            "id": 19,
            "name": "help"
        },
        "full_screen": {
            "id": 20,
            "name": "Full screen"
        }
    }

    # this index is only for the case when you enable 'box','ellipse', 'polygon','dot','line', 'point-box' for linear_interpolation, if you do not enable some of them, index will be different
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
        "point_box": {
            "id": 5,
            "name": "point_box annotation"
        },
        "merging": {
            "id": 6,
            "name": "merging"
        },
        "switch_ids": {
            "id": 7,
            "name": "switch_ids"
        },
        "pan": {
            "id": 8,
            "name": "pan"
        },
        "zoom_in": {
            "id": 9,
            "name": "zoom_in"
        },
        "zoom_out": {
            "id": 10,
            "name": "zoom_out"
        },
        "reframe": {
            "id": 11,
            "name": "reframe"
        },
        "cross_hair": {
            "id": 12,
            "name": "cross_hair"
        },
        "focus_mode": {
            "id": 13,
            "name": "focus_mode"
        },
        "hide_mode": {
            "id": 14,
            "name": "hide_mode"
        },
        "shape_opacity": {
            "id": 15,
            "name": "shape_opacity"
        },
        "map": {
            "id": 16,
            "name": "map"
        },
        "show_label": {
            "id": 17,
            "name": "show_label"
        },
        "auto_enhance": {
            "id": 18,
            "name": "auto_enhance"
        },
        "error_log": {
            "id": 19,
            "name": "error_log"
        },
        "help": {
            "id": 20,
            "name": "help"
        },
        "full_screen": {
            "id": 21,
            "name": "Full screen"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def get_video_info(self):
        with allure.step('Get video info'):
            info = find_elements(self.driver, "//div[@class='b-VideoControl__numbers']")
            time_to_wait = 10
            current_time = 0
            while current_time < time_to_wait:
                if len(info) > 0:
                    break
                else:
                    current_time += 1
                    time.sleep(1)
            else:
                msg = f'Max wait time reached, still no video info, something went wrong'
                raise Exception(msg)
            assert info, "Video info has not been found"
            return info[0].text

    def get_num_of_frames_for_video(self):
        with allure.step('Get num of frames for video'):
            _text = self.get_video_info()
            return int(_text.split('/')[1].strip())

    def get_num_of_current_frame(self):
        with allure.step('Get num of current frame'):
            _text = self.get_video_info()
            return int(_text.split('/')[0].strip())

    def next_frame(self):
        with allure.step('Get next frame'):
            btns = find_elements(self.driver, "//div[@class='b-VideoControl']//button")
            btns[2].click()
            time.sleep(3)

    def previous_frame(self):
        with allure.step('Get previous frame'):
            btns = find_elements(self.driver, "//div[@class='b-VideoControl']//button")
            btns[1].click()
            time.sleep(3)

    def play_pause(self):
        with allure.step('Pay and pause'):
            btns = find_elements(self.driver, "//div[@class='b-VideoControl']//button")
            btns[0].click()
            time.sleep(3)

    def wait_until_user_views_all_frames(self, num_frames=None, wait=10, max_time=300):
        with allure.step('Wait until user view all frames'):
            if not num_frames:
                num_frames = self.get_num_of_frames_for_video()

            running_time = 0
            current_frame = self.get_num_of_current_frame()
            while (current_frame < num_frames) and (running_time < max_time):
                current_frame = self.get_num_of_current_frame()
                print("current frame...", current_frame)
                running_time += wait
                time.sleep(wait)

    def hide_all_boxes_on_frame(self):
        with allure.step('Hide all boxes on frame'):
            boxes = find_elements(self.driver,
                                  "//div[@class='b-Sidebar__category-body']//div[@class ='b-ShapeLabel' or @class='b-ShapeLabel b-ShapeLabel--selected']")
            initial_num = len(boxes)
            while boxes and initial_num>0:
                boxes[0].click()
                time.sleep(1)
                boxes[0].find_element('xpath',".//div[@class='b-ShapeLabel__menu-toggle']").click()
                # time.sleep(1)
                el = find_elements(self.driver, "//div[@class='b-ShapeMenu b-ShapeMenu--visible']//a[text()='Mark as hidden']")
                assert len(el), "Mark as hidden option has not been found"
                el[0].click()
                initial_num -= 1
                # time.sleep(2)
                boxes = find_elements(self.driver,
                                      "//div[@class='b-Sidebar__category-body']//div[@class ='b-ShapeLabel' or @class='b-ShapeLabel b-ShapeLabel--selected']")


    def annotate_frame(self, mode, value, hide_box=False, annotate_shape='box'):
        with allure.step('Annotate frame'):
            if mode == 'random':
                self.select_ontology_class('random')
                for n in range(value):
                    try:
                        self.draw_shape(annotate_shape)
                        if hide_box: self.hide_all_boxes_on_frame()
                        time.sleep(1)
                    except:
                        print("Something went wrong!")
                        LOGGER.error("Something went wrong!")

            elif mode == 'ontology':
                for ontology_class, num_box in value.items():
                    self.select_ontology_class(ontology_class)
                    time.sleep(5)
                    for n in range(num_box):
                        try:
                            self.draw_shape(annotate_shape)
                            if hide_box: self.hide_all_boxes_on_frame()
                            time.sleep(1)
                        except Exception as e:
                            LOGGER.error("Something went wrong!- ", e)
            time.sleep(2)

    def click_toolbar_button(self, btn_name):
        with allure.step('Click toolbar button %s' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[@class='b-ToolbarWrapper']//button")
            buttons[index].click()
            time.sleep(5)

    def button_is_disable(self, btn_name):
        with allure.step('Check see if button %s disabled' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[@class='b-ToolbarWrapper']//button")
            el_class = buttons[index].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def get_sidepanel_shapelabel_count(self):
        with allure.step('Get sidepanel shapelabel count'):
            shapelabel_count = self.driver.find_elements('xpath',"//div[@class='b-ListItem__title']")
            return len(shapelabel_count)

    def press_combine_hotkey(self, key, character):
        with allure.step('Press combine hotkey'):
            ac = ActionChains(self.driver)
            ac.key_down(key).send_keys(character).key_up(key).perform()
            time.sleep(3)

    def activate_iframe_by_index(self, index):
        with allure.step('Activate iframe by index'):
            iframe = find_elements(self.app.driver, "//form[@id='job_units']//iframe")
            time_to_wait = 30
            current_time = 0
            while current_time < time_to_wait:
                if len(iframe) > 0:
                    break
                else:
                    current_time += 1
                    time.sleep(1)
            else:
                msg = f'Max wait time reached, still no iframe, maybe video not loaded'
                raise Exception(msg)
            element_to_the_middle(self.driver, iframe[index], center=True)
            self.app.driver.switch_to.frame(iframe[index])

    def click_classes_or_objects_tab(self, tab_name):
        with allure.step('Click tab'):
            tabs = find_elements(self.driver, "//div[text()= '%s']" % tab_name)
            tabs[0].click()
            time.sleep(1)

    def click_ontology_item(self, item_name):
        with allure.step('Click ontology item'):
            items = find_elements(self.driver,
                                  "//div[contains(@class,'b-ListItem__name--video') and text()= '%s']/../..//div[contains(@class,'b-ListItem__itemEnd')]" % item_name)
            mouse_over_element(self.driver, items[0])
            items[0].click()
            time.sleep(1)

    def error_icon_is_displayed(self, item_name, displayed=True):
        with allure.step('Click tab'):
            items = find_elements(self.driver, "//div[contains(@class,'b-ListItem__name--video') and text()= '%s']/../..//div[contains(@class,'b-ListItem__itemEnd')]" % item_name)
            mouse_over_element(self.driver, items[0])
            icons = find_elements(self.driver, "//div[@class='b-ListItem__icons']//*[local-name() = 'svg']")
            if displayed:
                assert len(icons) == 6
            else:
                assert len(icons) == 4

    def eclipse_is_displayed(self, item_name, displayed=True):
        with allure.step('Click tab'):
            items = find_elements(self.driver, "//div[contains(@class,'b-ListItem__name--video') and text()= '%s']/../..//div[contains(@class,'b-ListItem__itemEnd')]" % item_name)
            mouse_over_element(self.driver, items[0])
            icons = find_elements(self.driver, "//div[@class='b-ListItem__icons']//div[@class='b-Sidebar__ellipse']")
            if displayed:
                assert len(icons) > 0
            else:
                assert len(icons) == 0

    def click_x_go_back_to_panel(self):
        with allure.step('Go back to panel'):
            el = find_elements(self.driver, "//div[contains(@class, 'b-CommonForm__item')]//*[local-name() = 'svg']")
            el[0].click()
            time.sleep(1)

    def click_error_log_panel(self):
        with allure.step('Click error log'):
            el = find_elements(self.driver, "//div[contains(@class, 'b-ToolbarWrapper__right')]//button[contains(@class,'b-Button')]//*[local-name() = 'svg']")
            el[0].click()
            time.sleep(1)

    def get_error_log_items(self):
        with allure.step('Get error log items'):
            el = find_elements(self.driver, "//div[contains(@class, 'b-ErrorLog__content')]//div[@class ='b-ErrorLogItem']")
            return len(el)

    def get_error_log_item_title(self):
        with allure.step('Get error log item title'):
            el = find_elements(self.driver, "//div[contains(@class, 'b-ErrorLogItem__title')]")
            return el[0].text

    def get_error_log_item_frame(self):
        with allure.step('Get error log item frame'):
            el = find_elements(self.driver, "//div[contains(@class, 'b-ErrorLogItem__frames')]")
            return el[0].text

    def get_error_log_item_footer(self):
        with allure.step('Get error log item footer'):
            el = find_elements(self.driver, "//div[contains(@class, 'b-ErrorLogItem__footer')]")
            return el[0].text

    def get_frame_info_on_form_panel(self):
        with allure.step('Get frame info'):
            el = find_elements(self.driver, "//div[@class='b-CommonForm__frameInfo']")
            return el[0].text

    def get_frame_info_on_object_panel(self):
        with allure.step('Get frame info'):
            el = find_elements(self.driver, "//div[@class='b-ShapesList__frameInfo']")
            return el[0].text

    def click_eclipse_menu_on_form_panel_to_delete_or_hidden_object(self, item_name, delete=False, hidden=False, visible=False):
        with allure.step('Click eclipse on form panel'):
            el = find_elements(self.driver, "//div[@class='b-CommonForm__name' and text()='%s']/..//div[@class='b-EllipsesMenu']//*[local-name() = 'svg']" % item_name)
            el[0].click()
            time.sleep(1)
            if delete:
                el = find_elements(self.driver,
                                   "//div[@class='b-EllipsesMenu__ellipsesMenu']//div[@class='b-EllipsesMenu__item' and text()='Delete from all frames']")
                el[0].click()
            if hidden:
                el = find_elements(self.driver,
                                   "//div[@class='b-EllipsesMenu__ellipsesMenu']//div[@class='b-EllipsesMenu__item' and text()='Mark as hidden']")
                el[0].click()
            if visible:
                el = find_elements(self.driver,
                                   "//div[@class='b-EllipsesMenu__ellipsesMenu']//div[@class='b-EllipsesMenu__item' and text()='Mark as visible']")
                el[0].click()
            time.sleep(1)

    def object_is_hidden(self, is_not=True):
        with allure.step('Object is hidden'):
            el = find_elements(self.driver, "//div[@class='b-CommonForm__hidden']")
            if is_not:
                if len(el) > 0 and el[0].text == 'OBJECT HIDDEN':
                    print("The object is hidden")
                    return True
                else:
                    assert False, ("The object is not hidden while it should")
            if not is_not:
                if len(el) == 0:
                    print("The object is not hidden as expected")
                    return True
                else:
                    assert False, ("The text is displayed on the page (but it must not!)")

    def no_object_yet(self):
        with allure.step('Verify no object'):
            el = find_elements(self.driver, "//div[@class='b-ShapesList__text']")
            return el[0].text

    def click_eclipse_menu_on_object_panel_to_delete_or_hidden_object(self, item_name, delete=False, hidden=False, visible=False):
        with allure.step('Click tab'):
            items = find_elements(self.driver, "//div[contains(@class,'b-ListItem__name--video') and text()= '%s']/../..//div[contains(@class,'b-ListItem__itemEnd')]" % item_name)
            mouse_over_element(self.driver, items[0])
            icons = find_elements(self.driver, "//div[@class='b-ListItem__icons']//div[@class='b-Sidebar__ellipse']//div[@class='b-EllipsesMenu']//*[local-name() = 'svg']")
            icons[0].click()
            if delete:
                el = find_elements(self.driver, "//*[text()='Delete from all frames']")
                el[0].click()
            if hidden:
                el = find_elements(self.driver, "//*[text()='Mark as hidden']")
                el[0].click()
            if visible:
                el = find_elements(self.driver, "//*[text()='Mark as visible']")
                el[0].click()
            time.sleep(1)

