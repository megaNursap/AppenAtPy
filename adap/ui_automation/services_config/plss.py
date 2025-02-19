import logging
import time
import pytest
import allure
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.utils.selenium_utils import find_elements, find_element
from adap.api_automation.utils.data_util import *
from selenium.webdriver import ActionChains
from adap.ui_automation.utils.js_utils import element_to_the_middle

LOGGER = logging.getLogger(__name__)


def create_plss_job(app, api_key, cml, user_name, password):
    job = JobAPI(api_key)
    job.create_job_with_cml(cml)
    job_id = job.job_id
    app.user.login_as_customer(user_name=user_name, password=password)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file("/plss/catdog.csv")
    app.job.data.upload_file(data_file)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Segmentation Ontology')

    ontology_file = get_data_file("/plss/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")
    time.sleep(3)

    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job.launch_job()
    time.sleep(10)
    job = JobAPI(api_key, job_id=job_id)

    job.wait_until_status('running', 80)
    res = job.get_json_job_status()
    assert res.json_response['state'] == 'running'
    res.assert_response_status(200)
    return job_id


class PlssUI(Annotation):
    buttons = {
        "annotate": {
            "id": 0,
            "name": "annotation"
        },
        "pan": {
            "id": 1,
            "name": "polygons annotation"
        },
        "zoom_in": {
            "id": 2,
            "name": "zoom_in"
        },
        "zoom_out": {
            "id": 3,
            "name": "zoom_out"
        },
        "reframe": {
            "id": 4,
            "name": "reframe"
        },
        "label": {
            "id": 5,
            "name": "label"
        },
        "image": {
            "id": 6,
            "name": "image"
        },
        "help": {
            "id": 7,
            "name": "help"
        },
        "full_screen": {
            "id": 8,
            "name": "Full screen"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def click_toolbar_button(self, btn_name):
        with allure.step('Click toolbar button %s' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[contains(@class,'b-ToolbarWrapper')]//button")
            buttons[index].click()
            time.sleep(3)

    def choose_annotate_tool(self, annotate_tool):
        with allure.step('Choose annotate tool %s' % annotate_tool):
            tool = self.driver.find_elements('xpath',"//div[@class='b-DropdownToolSelector__items' and text()='%s']" % annotate_tool)
            assert len(tool) > 0
            tool[0].click()
            time.sleep(3)

    def button_is_disable(self, btn_name):
        with allure.step('Check if button %s is disabled' % btn_name):
            index = self.buttons[btn_name]['id']
            buttons = self.driver.find_elements('xpath',"//div[contains(@class,'b-ToolbarWrapper')]//button")
            el_class = buttons[index].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def fill_image(self, x, y):
        with allure.step('Fill image'):
            ac = ActionChains(self.driver)
            ac.move_by_offset(x, y).click().perform()
            time.sleep(2)

    def draw_triangle(self, x0, y0, x1, y1, x2, y2):
        with allure.step('Draw triangle'):
            action = ActionChains(self.driver)
            action.move_by_offset(x0, y0)
            action.click()
            action.move_by_offset(x1, y1)
            action.click()
            action.move_by_offset(x2, y2)
            action.double_click()
            action.perform()
            time.sleep(2)

    def magic_wand(self, x, y):
        with allure.step('Add magic wand'):
            ac = ActionChains(self.driver)
            ac.move_by_offset(x, y).double_click().perform()
            time.sleep(2)

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
                msg = f'Max wait time reached, still no iframe, maybe image not loaded'
                raise Exception(msg)
            element_to_the_middle(self.driver, iframe[index], center=True)
            self.app.driver.switch_to.frame(iframe[index])

