import time
import pytest
import allure
from selenium.webdriver import ActionChains
from adap.ui_automation.services_config.annotation import Annotation
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import find_elements
from adap.api_automation.services_config.requestor_proxy import RP
from adap.data.video_transcription import data
from adap.ui_automation.utils.js_utils import element_to_the_middle
from selenium.webdriver.common.keys import Keys


def create_video_transcription_job(api_key, data_file, cml, jwt_token=None, username=None, password=None):
    job = Builder(api_key)
    job.create_job_with_csv(data_file)
    updated_payload = {
        'key': api_key,
        'job': {
            'title': "Testing video transcription",
            'instructions': "Updated",
            'cml': cml,
            'project_number': 'PN000112',
            'units_per_assignment': 3
        }
    }
    job.update_job(payload=updated_payload)
    rp = RP()
    rp.get_valid_sid(username, password)

    resp = rp.update_ontology(job.job_id, data.ontology)
    assert resp.status_code == 200, f"Actual status code: {resp.status_code}, content {resp.text}"
    return job.job_id


class VideoTranscriptionUI(Annotation):
    buttons = {
        "back": {
            "id": 0,
            "name": "back"
        },
        "play": {
            "id": 1,
            "name": "play video"
        },
        "pause": {
            "id": 1,
            "name": "play video"
        },
        "forward": {
            "id": 2,
            "name": "forward"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

        # Todo, click work for audio annotation, hold does not work
    def create_segment(self):
        with allure.step('Create segment for video'):
            action = ActionChains(self.driver)
            wave = find_elements(self.driver, "//div[@id='wave']//wave")
            action.move_to_element_with_offset(wave[0], 0, 0)
            action.move_by_offset(500, 100)
            time.sleep(3)
            action.click_and_hold()
            action.perform()
            action.move_by_offset(200, 0)
            action.perform()
            action.release().perform()
            time.sleep(2)

    def get_number_iframes_on_page(self):
        with allure.step('Get number of iframes on the page'):
          iframe = find_elements(self.app.driver, "//iframe[contains(@src, 'VideoTranscription')]")
          return len(iframe)

    def click_toolbar_button(self, btn_name):
        with allure.step('Click toolbar button %s' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[@class='video-segment3-btn-group']//button")
            buttons[index].click()
            time.sleep(2)

    def get_number_of_segment(self):
        with allure.step('Get number of segments video'):
            segments = find_elements(self.driver, "//region[contains(@class, 'wavesurfer-region')]")
            return len(segments)

    def get_segment_coordination(self, index=0):
        with allure.step('Get segment coordination'):
            segments = find_elements(self.driver, "//region[contains(@class, 'wavesurfer-region')]")
            assert len(segments) > index, "segments not found"
            style = segments[index].get_attribute('style').split(";")
            _segment_position = {}
            left_position = 0
            width = 0
            for s in style:
                if s:
                    _s = s.split(':')
                    if _s[0].strip() == 'left':
                        left_position = _s[1].strip().split('px')[0]
                    if _s[0].strip() == 'width':
                        width = _s[1].strip().split('px')[0]
            _segment_position['left'] = int(left_position)
            _segment_position['right'] = int(left_position) + int(width)
            return _segment_position

    def click_to_select_segment(self, index=0):
        with allure.step('Click to select segment'):
            position = self.get_segment_coordination(index)
            click_position = random.randint(position['left'], position['right'])
            action = ActionChains(self.driver)
            wave = find_elements(self.driver, "//div[@id='wave']//wave")
            action.move_to_element_with_offset(wave[0], 0, 0)
            action.move_by_offset(click_position, 100)
            time.sleep(1)
            action.click().perform()
            time.sleep(2)

    def turn_id_is_displayed(self):
        with allure.step('Check if turn id is displayed'):
            turn_id = find_elements(self.driver, "//span[@title='default']")
            return (False, True)[turn_id[0].text == 'default']

    def create_segment_while_playing(self, start_time, end_time):
        with allure.step('Create segment by hotkey while playing'):
            self.click_toolbar_button('play')
            time.sleep(start_time)
            self.single_hotkey('s')
            time.sleep(end_time)
            self.single_hotkey('e')
            self.click_toolbar_button('pause')
            time.sleep(1)

    def get_ontology_displayed_under_category(self):
        with allure.step('Get ontology displayed under category'):
            ontologys = []
            el = find_elements(self.driver, "//label[text()='Category']/..//div")
            if len(el) > 0:
                for i in range(len(el)):
                    ontologys.append(el[i].text)
            return ontologys

    def click_to_select_ontology_under_category(self, ontology_name):
        with allure.step('Click to select ontology %s' % ontology_name):
            el = find_elements(self.driver, "//label[text()='Category']/..//div[text()='%s']" % ontology_name)
            assert len(el) > 0, "Ontology with name %s is not found" % ontology_name
            el[0].click()
            time.sleep(1)

    def input_transcription_in_textbox(self, transcription_text):
        with allure.step('Input transcription with text %s' % transcription_text):
            el = find_elements(self.driver, "//label[text()='Transcription']/..//textarea")
            assert len(el) > 0, "Text area is not found"
            el[0].clear()
            el[0].send_keys(transcription_text)
            time.sleep(1)

    def click_dropdown_to_select_turn_id(self):
        with allure.step('Select turn id'):
            el = find_elements(self.driver, "//div[@class='ant-select-selector']//span[@class='ant-select-selection-item']")
            assert len(el) > 0, "Text area is not found"
            el[0].click()

    def input_turn_id(self, turn_id):
        with allure.step('Input turn id %s' % turn_id):
            el = find_elements(self.driver, "//div[contains(@class, 'ant-select-dropdown')]//input")
            assert len(el) > 0, "Input textbox is not found"
            el[0].send_keys(turn_id)
            time.sleep(1)

    def select_turn_id_from_list(self, turn_id):
        with allure.step('Select turn id %s' % turn_id):
            el = find_elements(self.driver, "//div[@class='ant-select-item-option-content' and text()='%s']" % turn_id)
            assert len(el) > 0, "Turn id not found"
            el[0].click()
            time.sleep(1)

    def create_turn_id_and_select_it(self, turn_id):
        with allure.step('Create turn id %s' % turn_id):
            self.click_dropdown_to_select_turn_id()
            self.input_turn_id(turn_id)
            self.app.navigation.click_link('New Turn')
            self.select_turn_id_from_list(turn_id)
            time.sleep(1)

    def activate_iframe_on_unit_page(self):
        with allure.step('Activate iframe on unit page'):
            iframe = find_elements(self.app.driver, "//iframe[contains(@name, 'unit_page')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)
            iframe = find_elements(self.app.driver, ".//iframe[contains(@src, 'VideoTranscription')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)