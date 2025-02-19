from adap.ui_automation.services_config.application import Application
from adap.ui_automation.utils.selenium_utils import set_up_driver
from appen_connect.ui_automation.service_config.application import AC


class ADAP_AC:
    def __init__(self, temp_path_file=None, driver=None):

        if driver:
            self.driver = driver
        else:
            self.driver = set_up_driver(temp_path_file)

        self.adap = Application(env='integration', driver=self.driver)
        self.ac = AC(env='stage', driver=self.driver)
