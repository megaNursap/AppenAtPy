import time
import allure
from selenium.webdriver import ActionChains
from adap.ui_automation.utils.js_utils import element_to_the_middle, mouse_click_element
from adap.ui_automation.utils.selenium_utils import find_elements, find_element
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *


def create_peer_review_job(tmpdir, api_key, job_id, cml, units_per_page=None):
    # get test data
    payload = {
        'type': 'full',
        'key': api_key
    }

    if units_per_page:
        updated_payload = {
            'key': api_key,
            'job': {
                'title': "peer review job for annotation tool",
                'instructions': "Updated",
                'cml': cml,
                'project_number': 'PN000112',
                'units_per_assignment': units_per_page
            }
        }
    else:
        updated_payload = {
            'key': api_key,
            'job': {
                'title': "peer review job for annotation tool",
                'instructions': "Updated",
                'cml': cml,
                'project_number': 'PN000112'
            }
        }

    job = Builder(api_key)
    job.job_id = job_id

    # generate report
    resp1 = job.regenerate_report(payload=payload)
    resp1.assert_response_status(200)
    i = 1
    while i < 300:
        resp = job.generate_report(payload=payload)
        if resp.status_code == 200:
            open(tmpdir + '/full.zip', 'wb').write(resp.content)
            break
        i = i + 1

    # handle the zip file
    unzip_file(tmpdir + '/full.zip')

    data_peer_review = tmpdir + "/f%s.csv" % str(job.job_id)
    job = Builder(api_key)

    job.create_job_with_csv(data_peer_review)
    job.update_job(payload=updated_payload)
    return job.job_id


def create_annotation_tool_job(api_key, data_file, cml, job_title="Testing annotation tool please do not delete",
                               units_per_page=2):
    job = Builder(api_key)
    job.create_job_with_csv(data_file)
    updated_payload = {
        'key': api_key,
        'job': {
            'title': job_title,
            'instructions': "Updated",
            'cml': cml,
            'project_number': 'PN000112',
            'units_per_assignment': units_per_page
        }
    }
    job.update_job(payload=updated_payload)
    return job.job_id


class Annotation:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.ontology_attribute_annotate = OntologyAttributeAnnotate(self)

    def get_number_iframes_on_page(self):
        with allure.step('Get number of iframes on the page'):
          el = find_elements(self.driver, "//iframe")
          return len(el)

    def activate_iframe_by_index(self, index):
       with allure.step('Activate iframe by index'):
          iframe = find_elements(self.app.driver, "//iframe")
          total_frames = len(iframe)
          assert total_frames > 0 , 'No iframes found'
          print (f"Total iframes: {len(iframe)}")
          if 0 < index >= total_frames:
              index = total_frames - 1
          element_to_the_middle(self.driver, iframe[index])
          time.sleep(1)
          self.driver.switch_to.frame(iframe[index])
          time.sleep(3)

    def activate_iframe_by_name(self, name):
       with allure.step('Activate iframe by index'):
          iframe = find_elements(self.app.driver, "//iframe[@name='%s']" % name)
          element_to_the_middle(self.driver, iframe[0])
          time.sleep(1)
          self.driver.switch_to.frame(iframe[0])
          time.sleep(3)

    def activate_iframe_by_xpath(self, xpath):
       with allure.step('Activate iframe by xpath'):
          iframe = find_elements(self.app.driver, xpath)
          element_to_the_middle(self.driver, iframe[0])
          time.sleep(1)
          self.driver.switch_to.frame(iframe[0])
          time.sleep(3)

    def deactivate_iframe(self):
        with allure.step('Deactivate iframe'):
            self.driver.switch_to.default_content()
            time.sleep(2)

    def find_submit_button(self):
        with allure.step('Find submit button'):
            xpath = "//div[@class='form-actions']//input[@value='Submit & Continue']"
            submit_btn = find_elements(self.driver, xpath)
            return submit_btn

    def submit_page(self):
        with allure.step('Submit the page'):
            submit_btn = self.find_submit_button()
            element_to_the_middle(self.driver, submit_btn[0])
            submit_btn[0].click()
            time.sleep(2)

    def submit_continue(self):
        continue_btn = find_elements(self.driver, "//input[@type='submit' and @value='Continue']")
        assert len(continue_btn) > 0, "Continue button is not found"
        continue_btn[0].click()

    def find_test_validators(self):
        with allure.step('Find test validators button'):
            xpath = "//div[@class='form-actions']//input[@value='Test Validators']"
            test_validators_btn = find_elements(self.driver, xpath)
            return test_validators_btn

    def submit_test_validators(self):
        with allure.step('Submit test validators'):
            submit_btn = self.find_test_validators()
            element_to_the_middle(self.driver, submit_btn[0])
            submit_btn[0].click()
            time.sleep(2)

    def get_iframe_info(self):
        with allure.step('Get iframe info'):
            image_container = find_elements(self.driver, "//div[@class='canvas-container']")
            style = image_container[0].get_attribute('style')
            location = image_container[0].location
            size = image_container[0].size

            return {"style": style,
                    "location": location,
                    "size": size}

    def draw_box(self):
        with allure.step('Draw box'):
            image_info = self.get_iframe_info()
            x0, y0, size_x, size_y = self.get_random_box_param(image_info, 50)
            print("draw", x0, y0, size_x, size_y)
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            # canvas.click()
            mouse_click_element(self.driver, canvas)

            ActionChains(self.driver) \
                .move_to_element_with_offset(canvas, 1, 1) \
                .move_by_offset(x0, y0) \
                .click_and_hold() \
                .move_by_offset(size_x, size_y) \
                .release() \
                .perform()

            time.sleep(2)

    def draw_box_with_box_params(self, x0=250, y0=200, size_x=150, size_y=100):
        with allure.step('Draw box with box params'):
            print("draw", x0, y0, size_x, size_y)
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            canvas.click()

            ActionChains(self.driver) \
                .move_to_element_with_offset(canvas, 1, 1) \
                .move_by_offset(x0, y0) \
                .click_and_hold() \
                .move_by_offset(size_x, size_y) \
                .release() \
                .perform()

            time.sleep(2)

    def draw_box_for_tile_image(self):
        with allure.step('Draw box'):
            canvas = find_element(self.driver, "//div[@id='slippyMapContainerId']")
            canvas.click()

            action = ActionChains(self.driver)
            action.move_to_element_with_offset(canvas, 1, 1)
            action.move_by_offset(150, 150)
            action.click().perform()
            action.move_by_offset(100, 100)
            action.click().perform()

            time.sleep(2)
            
    def draw_line(self):
        with allure.step('Draw line'):
            image_info = self.get_iframe_info()
            x0, y0, x1, y1 = self.get_random_box_param(image_info, 50)
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            canvas.click()

            ActionChains(self.driver)\
                .move_to_element_with_offset(canvas, 1, 1)\
                .move_by_offset(x0, y0)\
                .click()\
                .move_by_offset(x1, y1)\
                .double_click()\
                .perform()

            time.sleep(2)

    def draw_triangle(self):
        with allure.step('Draw triangle'):
            image_info = self.get_iframe_info()
            x0, y0, x1, y1 = self.get_random_box_param(image_info, 50)
            x2 = 10
            y2 = 10
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            canvas.click()

            ActionChains(self.driver)\
                .move_to_element_with_offset(canvas, 1, 1)\
                .move_by_offset(x0, y0)\
                .click()\
                .move_by_offset(x1, y1)\
                .click() \
                .move_by_offset(x2, y2) \
                .double_click() \
                .perform()

            time.sleep(2)

    def draw_dot(self):
        with allure.step('Draw dot'):
            print("Draw dot")
            image_info = self.get_iframe_info()
            x0, y0 = self.get_random_dot_param(image_info, 50)
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            # canvas.click()

            ActionChains(self.driver)\
                .move_to_element_with_offset(canvas, x0, y0)\
                .perform()

            time.sleep(2)

    def draw_ellipse(self):
        with allure.step('Draw ellipse'):
            canvas = find_element(self.driver, "//canvas[contains(@class, 'upper-canvas')]")
            canvas.click()

            action = ActionChains(self.driver)
            action.move_to_element_with_offset(canvas, 1, 1)
            action.move_by_offset(150, 150)
            action.click().perform()
            # action.move_by_offset(100, 100)
            # action.click().perform()

            time.sleep(2)

    def draw_shape(self, shape='box'):
        with allure.step('Draw shape'):
            if shape == 'polygon':
                self.draw_triangle()
            if shape == 'line':
                self.draw_line()
            if shape == 'dot':
                self.draw_dot()
            if shape == 'ellipse':
                self.draw_ellipse()
            else:
                self.draw_box()

    def get_random_box_param(self, image_info, min_size):
        with allure.step('Get random box param for %s' % image_info):
            print('size',  image_info['size']['width'], image_info['size']['height'])
            x_limit, y_limit = image_info['size']['width'] - 100, image_info['size']['height'] - 100
            print("limit", x_limit, y_limit)
            x0 = random.randint(0, x_limit//2 - min_size)
            y0 = random.randint(0, y_limit//2 - min_size)
            print("new x0", x0, y0)
            # x0 = random.randint(0, x_limit - min_size)
            # y0 = random.randint(0, y_limit - min_size)
            # print("old x0", x0, y0)

            size_x = random.randint(min_size, min_size + 100)
            size_y = random.randint(min_size, min_size + 100)
            print("new final size", size_x, size_y)
            # size_x = random.randint(min_size, x_limit - x0)
            # size_y = random.randint(min_size, y_limit - y0)
            # print("old final size", size_x, size_y)
            # x0, y0, size_x, size_y = 195, 100, 260, 200
            return x0, y0, size_x, size_y

    def get_random_dot_param(self, image_info, min_size):
        with allure.step('Get random dot param for %s' % image_info):
            x_limit, y_limit = image_info['size']['width'] - 100, image_info['size']['height'] - 100
            x0 = random.randint(0, x_limit - min_size)
            y0 = random.randint(0, y_limit - min_size)
            return x0, y0

    def select_ontology_class(self, class_name):
        with allure.step('Select ontology class %s' % class_name):
            if class_name == 'random':
                el = find_elements(self.driver, "//div[@class='b-Sidebar__category-header']" )
                assert el, "No ontology"
                el[0].click()
            else:
                el = find_elements(self.driver, "//div[@class='b-Sidebar__category-header' and text()='%s']" % class_name)
                assert el, "Ontology class %s has not been found" % class_name
                el[0].click()

    def full_screen(self):
        with allure.step('Make full screen'):
            find_elements(self.driver, "//button[contains(@class, 'b-Button__fullscreen')]")[0].click()
            time.sleep(5)

    def close_help_menu(self):
        with allure.step('Close help menu'):
            self.driver.find_element('xpath',
                "//button[contains(@class, 'b-InformationBar__close_button')]//*[local-name() = 'svg']").click()

    def single_hotkey(self, key):
        with allure.step('Click hotkey %s' % key):
            ac = ActionChains(self.driver)
            ac.send_keys(key).perform()
            time.sleep(2)

    def combine_hotkey(self, keys, character):
        with allure.step('Combine hotkey'):
            ac = ActionChains(self.driver)
            for key in keys:
                ac.key_down(key)
            ac.send_keys(character)
            for key in keys:
                ac.key_up(key)
            ac.perform()
            time.sleep(3)

    def get_task_error_msg_by_index(self, index=0):
        with allure.step('Get error message for task'):
            tasks = find_elements(self.driver, "//div[@class='cml jsawesome']")
            msg = tasks[index].find_elements('xpath',".//div[contains(@class,'errorMessage')]//p")
            if len(msg)>0: return msg[0].text
            return None

    def click_image_rotation_button(self):
        with allure.step('Click image rotation button'):
            rotate_btn = self.driver.find_element('id', '_rotate_image_')
            # adjust a page view so that rotate button can be interactable
            self.driver\
                .execute_script("arguments[0].scrollIntoView(false);", rotate_btn)
            rotate_btn.click()
            time.sleep(1)

    def click_save_button(self):
        with allure.step('Click SAVE button'):
            save_button = self.driver.find_element('xpath',"//*[text()='SAVE']/..")
            save_button.click()
            time.sleep(1)

    def image_rotation_slider_bar_available(self, is_not=True):
        with allure.step('Check if image rotation slider bar is available'):
            slider = self.driver.find_elements('xpath',"//div[@class='b-RotationSlider']")
            if is_not:
                assert len(slider) > 0, "Image rotation slider bar should be displayed, but it is not"
            else:
                assert len(slider) == 0, "Image rotation slider bar should not be displayed, but it is"

    def get_image_rotation_degree(self):
        with allure.step('Get image rotation degree'):
            return self.driver.find_element('xpath',"//div[@class='b-RotationSlider']//span").text

    def close_image_rotation_bar(self):
        with allure.step('Close image rotation bar'):
            close_button = self.driver.find_elements('xpath',"//div[@class='b-RotationSlider__button']")
            close_button[0].click()
            time.sleep(1)

    def move_image_rotation_knob(self):
        with allure.step('Click image rotation knob'):
            slider = self.driver.find_element('xpath',"//div[@class='b-RotationSlider__container']")
            element_to_the_middle(self.driver, slider)
            slider.click()
            time.sleep(2)

    def search_ontology_class(self, text):
        with allure.step('Search ontology class'):
            search_input = find_elements(self.app.driver, "//input[@class='b-Sidebar-SearchInput__input']")
            assert len(search_input) > 0, "Search ontology class textbox is not found"
            search_input[0].clear()
            search_input[0].send_keys(text)
            time.sleep(1)

    def clear_search_ontology_result(self):
        with allure.step('Clear search result'):
            clear_search = find_elements(self.app.driver, "//button[@class='b-Sidebar-SearchInput__clear-button']//*[local-name() = 'svg']")
            assert len(clear_search) > 0, "Clear search ontology button not found"
            clear_search[0].click()
            time.sleep(1)


class OntologyAttributeAnnotate:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def select_value_for_checkbox_group(self, values):
        with allure.step('Select value for checkbox group'):
            for value in values:
                checkbox = find_elements(self.driver, "//label[text()='%s']/..//label" % value)
                checkbox[0].click()
                time.sleep(1)

    def save_ontology_attribute(self):
        with allure.step('Save ontology attribute'):
            save_button = self.driver.find_element('xpath',"//div[@class='b-ShapeForm__buttonText' or @class='b-CommonForm__buttonText']")
            save_button.click()
            time.sleep(1)

    def select_value_for_multiple_choice(self, choice):
        with allure.step('Select value for multiple choice'):
            self.driver.find_element('xpath',
                "//input[@type='radio' and @value='%s']" % choice).click()
            time.sleep(2)

    def select_value_for_pulldown_menu(self, index=0):
        with allure.step('Select value for pulldown menu'):
            dropdown = find_elements(self.driver, "//div[contains(@class,'b-FormDropdown')]//button[@type='button']//span")
            dropdown[0].click()
            menu_item = find_elements(self.driver,
                                        "//*[@class='b-PulldownMenu__menuItem']//*[@role='menuitem']")
            menu_item[index].click()
            time.sleep(1)

    def input_textbox_single_line(self, text):
        with allure.step('Input textbox single line'):
            textbox = find_elements(self.driver, "//input[contains(@class,'b-TextBox__textInputQuestion')]")
            assert len(textbox) > 0, "Textbox not found"
            textbox[0].clear()
            textbox[0].send_keys(text)
            time.sleep(1)

    def ontology_attribute_show_in_sidepanel(self):
        with allure.step('Check if ontology attribute show in side panel'):
            save_button = find_elements(self.app.driver, "//div[@class='b-ShapeForm__buttonText' or @class='b-CommonForm__buttonText']")
            if len(save_button) > 0:
                return True
            else:
                return False