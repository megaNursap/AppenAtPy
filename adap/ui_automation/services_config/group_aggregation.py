import logging
import time
import allure
from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.utils.selenium_utils import find_elements

LOGGER = logging.getLogger(__name__)


class GroupAggregation(Annotation):

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def add_another_by_index(self, index):
        with allure.step('Add another by index %s' % index):
            add_another = find_elements(self.driver, "//div[@class='multiple_add']")
            assert add_another, "Add another link not found"
            add_another[index].click()
            time.sleep(2)

    def get_input_text_field(self, name):
        with allure.step('Get input text field for %s' % name):
            text_field = find_elements(self.driver, "//input[contains(@name,'%s')]" % name)
            assert text_field, "text_field not found"
            return text_field
