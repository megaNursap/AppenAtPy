import time
import re
from selenium.webdriver.common.keys import Keys
import allure
from selenium.webdriver import ActionChains

from adap.ui_automation.utils.js_utils import element_to_the_middle
from adap.ui_automation.utils.js_utils import mouse_over_element


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


class Lidar:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.toolbar = Toolbar(self)
        self.video_control = VideoControl(self)
        self.sidepanel = SidePanel(self)
        self.multiview = MultiView(self)
        self.iframe = ''

    def activate_iframe_by_index(self, index):
        with allure.step('Activate iframe: %s' % index):
            time.sleep(2)
            first_image = self.driver.find_elements('xpath',"//div[@class='cml jsawesome']")[index]
            element_to_the_middle(self.driver, first_image)
            iframe = first_image.find_element('xpath',".//iframe")
            self.iframe = iframe
            time.sleep(10)
            self.driver.switch_to.frame(iframe)

    def wait_until_video_load(self, interval, max_wait_time):
        with allure.step('Wait until video load'):
            _c = 0
            while _c < max_wait_time:
                create_button_disabled = self.toolbar.button_is_disable('create')
                if not create_button_disabled:
                    break
                else:
                    _c += interval
                    time.sleep(interval)
            else:
                msg = f'Max wait time reached, video still not fully loaded'
                raise Exception(msg)

    def click_coordinates(self, X, Y):
        with allure.step('Click coordinates %s and %s:' % (X, Y)):
            ac = ActionChains(self.driver)
            # move to the body...00
            ac.move_by_offset(X, Y).click().perform()
            time.sleep(2)
            # ac.move_by_offset(-X, -Y).perform()

    def single_hotkey(self, key):
        with allure.step('Hotkey space'):
            ac = ActionChains(self.driver)
            ac.send_keys(key).perform()
            time.sleep(2)

    def combine_hotkey(self, key, character):
        with allure.step('Hotkey character'):
            ac = ActionChains(self.driver)
            ac.key_down(key).send_keys(character).key_up(key).perform()
            time.sleep(3)

    def click_and_move(self, init_X, init_Y, res_X, res_Y):
        with allure.step('Click and move'):
            ac = ActionChains(self.driver)
            ac.move_by_offset(init_X, init_Y).click_and_hold().move_by_offset(res_X, res_Y).release().perform()

    def get_cuboids_counts(self):
        with allure.step('Get cuboids counts'):
            cuboids = self.find_cuboids()
            return len(cuboids)

    #  verification
    def find_cuboids(self):
        with allure.step('Find cuboids'):
            cuboids_el = self.driver.find_elements('xpath',"//div[.//span[contains(@style, 'display')] and contains(@style, 'transform')]")
            # assert len(cuboids_el) > 0, "Cuboids have not been found"
            if not cuboids_el: return {}

            cuboids = {}
            for c in cuboids_el:
                name = c.find_element('xpath',"./span").get_attribute('innerHTML')
                _style = {}
                for s in c.get_attribute('style').split(";"):
                    if s:
                        # print("find style:", s)
                        _s = s.split(':')
                        _style[_s[0].strip()] = _s[1].strip()
                        if _s[0].strip() == 'transform':
                            print(_s[1].strip().split('px'))
                            import re
                            _xy = re.findall(r"([0-9]+)+(\.?[0-9]+)(px|%)?", _s[1].split('translate')[-1])
                            X = ''.join(_xy[0][:-1])
                            Y = ''.join(_xy[1][:-1])
                            _style['coordinates'] = {"X": int(float(X)), "Y": int(float(Y))}
                cuboids[name] = _style
            return cuboids

    def get_cuboids_coordinate(self):
        with allure.step('Find cuboids coordination'):
            cuboids_el = self.driver.find_elements('xpath',"//div[@class='cube-label']")
            if not cuboids_el: return {}
            cuboids = {}
            for c in cuboids_el:
                _style = {}
                for s in c.get_attribute('style').split(";"):
                    if s:
                        print("find style:", s)
                        _s = s.split(':')
                        _style[_s[0].strip()] = _s[1].strip()
                        if _s[0].strip() == 'transform':
                            print(_s[1].strip().split('px'))
                            import re
                            _xy = re.findall(r"([0-9]+)+(\.[0-9]+)(px|%)?", _s[1])
                            X = _xy[0][0] + _xy[0][1]
                            Y = _xy[1][0] + _xy[1][1]
                            _style['coordinates'] = {"X": X, "Y": Y}
                cuboids[c.text] = _style
            return cuboids

    def move_cuboid(self, cuboid_name, hotkey):
        with allure.step('Move cuboid: %s' % cuboid_name):
            # self.sidepanel.select_shape_label(cuboid_name)
            self.single_hotkey('1')
            time.sleep(1)
            self.combine_hotkey(Keys.SHIFT, hotkey)
            move = self.find_cuboids()
            _xy = move[cuboid_name]['coordinates']
            return _xy

    def rotate_cuboid(self, cuboid_name, hotkey):
        with allure.step('Rotate cuboid: %s' % cuboid_name):
            self.sidepanel.select_shape_label()
            self.single_hotkey('2')
            time.sleep(1)
            self.combine_hotkey(Keys.SHIFT, hotkey)
            time.sleep(1)

    def get_background_color_for_cuboid(self, name):
        with allure.step('Get background color for cuboid: %s' % name):
            cuboid = self.find_cuboids().get(name)
            background_color = cuboid['background-color']
            rgb_tuple = tuple(map(int, re.findall(r'[0-9]+', background_color)))
            return rgb_to_hex(rgb_tuple).upper()


class Toolbar:
    buttons = {
        "mainview": {
            "id": 0,
            "name": "Create Cuboid"
        },
        "create": {
            "id": 1,
            "name": "Create Cuboid"
        },
        "move": {
            "id": 2,
            "name": "Move Cuboid"
        },
        "rotate": {
            "id": 3,
            "name": "Rotate Cuboid"
        },
        "resize": {
            "id": 4,
            "name": "Resize Cuboid"
        },
        "delete": {
            "id": 5,
            "name": "Remove Cuboid"
        },
        "undo": {
            "id": 6,
            "name": "UNDO"
        },
        "redo": {
            "id": 7,
            "name": "REDO"
        },
        "copy": {
            "id": 8,
            "name": "Copy Cuboid"
        },
        "paste": {
            "id": 9,
            "name": "Paste Cuboid"
        },
        "auto_adjust": {
            "id": 10,
            "name": "Auto Adjust Cuboid"
        },
        "interpolate": {
            "id": 11,
            "name": "Interpolate Cuboid"
        },
        "hide": {
            "id": 12,
            "name": "Hide unselected Cuboid"
        },
        "enable_auto_fit": {
            "id": 13,
            "name": "Enable auto fit"
        },
        "measure": {
            "id": 14,
            "name": "Measure"
        },
        "reset_view": {
            "id": 15,
            "name": "Reset View"
        },
        "label": {
            "id": 16,
            "name": "Labels"
        },
        "help": {
            "id": 17,
            "name": "Help"
        },
        "full_screen": {
            "id": 18,
            "name": "Full screen"
        },
        "save": {
            "id": 19,
            "name": "Full screen"
        }
    }

    def __init__(self, lidar):
        self.app = lidar.app
        self.driver = self.app.driver

    def find_buttons(self):
        with allure.step('Find button'):
            return self.driver.find_elements('xpath',"//div[@class='b-ToolbarWrapper']//button")

    def click_btn(self, btn_name):
        with allure.step('Click button'):
            index = self.buttons[btn_name]['id']
            self.find_buttons()[index].click()
            time.sleep(1)


    def button_is_disable(self, btn_name):
        with allure.step('Check button is disabled'):
            index = self.buttons[btn_name]['id']
            el_class = self.find_buttons()[index].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def close_help_menu(self):
        with allure.step('Close help menu'):
            self.driver.find_element('xpath',"//div[@class='b-InformationBar__header']//*[local-name() = 'svg']").click()

    def select_show_shape_labels_for(self, select_name):
        with allure.step('select show shape labels for'):
            self.driver.find_element('xpath',
                "//a[@class='b-DropdownButton__item' and text()='%s']" % select_name).click()
            time.sleep(2)


class VideoControl:

    control_btn = {
        "play": {
            "id": 0,
            "name": "Play/Pause"
        },
        "previous10": {
            "id": 1,
            "name": "Previous 10 Frames"
        },
        "previous": {
            "id": 2,
            "name": "Previous Frame"
        },
        "next": {
            "id": 3,
            "name": "Next Frame"
        },
        "next10": {
            "id": 4,
            "name": "Next 10 Frames"
        },
    }

    def __init__(self, lidar):
        self.app = lidar.app
        self.driver = self.app.driver

    def find_buttons(self):
        with allure.step('Find button'):
            return self.driver.find_elements('xpath',"//div[@class='b-VideoControl']//button")

    def click_btn(self, btn_name):
        with allure.step('Click button'):
            index = self.control_btn[btn_name]['id']
            self.find_buttons()[index].click()
            time.sleep(5)

    @property
    def __get_frames_numbers(self):
        text_num = self.driver.find_element('xpath',"//div[@class='b-VideoControl__numbers']").text
        return list(map(int, text_num.split('/')))

    def get_current_frame_number(self):
        with allure.step('Get current frame numbers'):
            return self.__get_frames_numbers[0]

    def get_total_frames_number(self):
        with allure.step('Get total frame numbers'):
            return self.__get_frames_numbers[1]

    def get_current_progress_bar_status(self):
        with allure.step('Get current progress bar status'):
            progressbar_style = self.driver.find_element('xpath',"//div[@class='b-ProgressBar__current']").get_attribute('style')
            return float(re.findall(r'\d*\.?\d+', progressbar_style)[0])


class SidePanel:
    def __init__(self, lidar):
        self.app = lidar.app
        self.driver = self.app.driver

    def search_ontology_class(self, search_name):
        with allure.step('Search ontology class for: %s' % search_name):
            search_input = self.driver.find_element('xpath',
                "//div[contains(@class,'b-Sidebar__search-input')]//input[@class='b-CommonSidebar-SearchInput__input']")
            search_input.send_keys(search_name)

    def clear_ontology_search(self):
        with allure.step('Clear ontoloty search'):
            self.driver.find_element('xpath',
                "//button[@class='b-CommonSidebar-SearchInput__clear-button']//*[local-name() = 'svg']").click()

    def no_search_result_found(self):
        with allure.step('Check no search result found'):
            no_result = self.driver.find_element('xpath',"//div[@class='b-Sidebar__no-results']").text
            print("text is:", no_result)
            if no_result == 'No Results':
                return True
            return False

    def get_ontology_instruction_title(self, ontology_name):
        with allure.step('Get ontology instruction title for: %s' % ontology_name):
            ontology_class = self.driver.find_element('xpath',
                "//div[contains(@class,'b-Sidebar__category-header') and text()='%s']" % ontology_name)
            mouse_over_element(self.driver, ontology_class)
            self.driver.find_element('xpath',
                ".//button[contains(@class,'b-Sidebar__category-info-icon')]//*[local-name() = 'svg']").click()
            time.sleep(2)
            instruction_title = self.driver.find_element('xpath',"//div[@class='b-CategoryInstructions__title']")
            print("title is:", instruction_title.text)
            return instruction_title.text

    def get_ontology_instruction_content(self):
        with allure.step('Get ontology instruction content'):
            instruction_content = self.driver.find_element('xpath',"//div[@class='b-CategoryInstructions__content']")
            return instruction_content.text

    def close_ontology_instruction(self):
        with allure.step('Close ontology instruction'):
            self.driver.find_element('xpath',
                "//button[contains(@class,'b-CategoryInstructions__close_button')]//*[local-name() = 'svg']").click()

    def ontology_class_is_displayed(self, ontology_name):
        with allure.step('Close ontology class is displayed'):
            el = self.driver.find_elements('xpath',
                "//div[contains(@class,'b-Sidebar__category-header') and text()='%s']" % ontology_name)
            if len(el) > 0:
                return True
            return False

    def get_ontology_class_color(self, ontology_name):
        with allure.step('Get ontology color for: %s' % ontology_name):
            el = self.driver.find_elements('xpath',
                "//div[@class='b-Sidebar__category-header' and text()='%s']/..//div["
                "@class='b-Sidebar__category-color']//*[local-name() = 'svg']" % ontology_name)
            if len(el) > 0:
                return el[0].get_attribute('fill').upper()
            return None

    def select_ontology(self, ontology_name):
        with allure.step('Select ontology: %s' % ontology_name):
            el = self.driver.find_elements('xpath',
                "//div[contains(@class,'b-Sidebar__category-header') and text()='%s']" % ontology_name)
            assert len(el) > 0, "Ontology class %s has not been found" % ontology_name
            el[0].click()

    def select_shape_label(self, name=None):
        with allure.step('Select shape label'):
            if name:
                index = name.split(' ')[-1]
                labels = self.driver.find_elements('xpath',
                    "//div[@class='b-ShapeLabel__value' and text()='%s']" % index)
            else:
                labels = self.driver.find_elements('xpath',
                    "//div[@class='b-ShapeLabel__value']")
            assert len(labels) > 0, "Shape label not found"
            labels[0].click()
            time.sleep(2)

    def get_shape_label_counts(self):
        with allure.step('Get shape label counts'):
            labels = self.driver.find_elements('xpath',
                "//div[@class='b-ShapeLabel__value']")
            return len(labels)


class MultiView:
    def __init__(self, lidar):
        self.app = lidar.app
        self.driver = self.app.driver

    def cuboid_displayed_on_front_view(self):
        with allure.step('Check cuboid front view'):
            front_view = self.driver.find_elements('xpath',"//div[@id='frontview']//div[@class='measure']")
            assert len(front_view) > 0, "front view not found"

    def cuboid_displayed_on_top_view(self):
        with allure.step('Check cuboid top view'):
            top_view = self.driver.find_elements('xpath',"//div[@id='topview']//div[@class='measure']")
            assert len(top_view) > 0, "top view not found"

    def cuboid_displayed_on_side_view(self):
        with allure.step('Check cuboid side view'):
            side_view = self.driver.find_elements('xpath',"//div[@id='sideview']//div[@class='measure']")
            assert len(side_view) > 0, "side view not found"