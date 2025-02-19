import logging
from datetime import datetime

import allure

from adap.ui_automation.services_config.navigation import Navigation
from adap.ui_automation.utils.selenium_utils import set_up_driver
from gap.ui_automation.service_config.data import GData
from gap.ui_automation.service_config.job import GJob
from gap.ui_automation.service_config.navigation import GNavigation
from gap.ui_automation.service_config.project import GProject
from gap.ui_automation.service_config.template import GTemplate
from gap.ui_automation.service_config.user import GUser
from gap.ui_automation.service_config.verification import GVerify
from gap.ui_automation.service_config.workflow import GWorkflow

log = logging.getLogger(__name__)


class Gap:
    def __init__(self, env=None, temp_path_file=None, driver=None):
        self.uniq_mark = None
        if env is None:
            env = 'gap'

        self.env = env
        self.gap_generate_test_uniq_mark()

        if driver:
            self.driver = driver
        else:
            self.driver = set_up_driver(temp_path_file)

        self.temp_path_file = temp_path_file
        self.g_verify = GVerify(self)
        self.g_nav = GNavigation(self)
        self.navigation = Navigation(self)
        self.g_job = GJob(self)
        self.g_user = GUser(self)
        self.g_project = GProject(self)
        self.g_workflow = GWorkflow(self)
        self.g_template = GTemplate(self)
        self.g_data = GData(self)

    def gap_generate_test_uniq_mark(self):
        with allure.step("Generate test unique mark"):
            if self.uniq_mark is None:
                now = datetime.now()

                self.uniq_mark = now.strftime("_%d%m%Y_%H%M%S")
            log.info(f"Test unique mark: {self.uniq_mark}")
            return self.uniq_mark
