import logging

import pytest
from faker import Faker

from appen_connect.ui_automation.service_config.administration_page import AdministrationPage
from appen_connect.ui_automation.service_config.file_upload import FileUpload
from appen_connect.ui_automation.service_config.client_data_mapping import ClientDataMapping
from appen_connect.ui_automation.service_config.invoices_page import InvoicesPage
from appen_connect.ui_automation.service_config.mfa_profile.mfa_profile import MfaProfile
from appen_connect.ui_automation.service_config.old_ui.internal_home_page import InternalHome
from appen_connect.ui_automation.service_config.old_ui.navigation_old_ui import NavigationAcUi

from appen_connect.ui_automation.service_config.old_ui.partner_home import PartnerHome
from appen_connect.ui_automation.service_config.old_ui.project import ProjectOldUI
from appen_connect.ui_automation.service_config.old_ui.tickets import Tickets
from appen_connect.ui_automation.service_config.old_ui.vendor_pages import VendorPages
from appen_connect.ui_automation.service_config.user_screening import UserScreeningPage

from appen_connect.ui_automation.service_config.project.project import Project
from appen_connect.ui_automation.service_config.dpr import Dpr

from appen_connect.ui_automation.service_config.project_list import ProjectList
from appen_connect.ui_automation.service_config.user import User
from adap.ui_automation.services_config.navigation import Navigation
from adap.ui_automation.services_config.verification import GeneralVerification
from adap.ui_automation.utils.selenium_utils import set_up_driver
from appen_connect.ui_automation.service_config.old_ui.quizzes import Quizzes
from appen_connect.ui_automation.service_config.vendor_profile.profile import VendorProfile
from appen_connect.ui_automation.service_config.web_mobile.account_setup import ContributorExperienceAccountSetup
from appen_connect.ui_automation.service_config.web_mobile.sign_up_page import SignUpPage, SignUpWebMobile
from appen_connect.ui_automation.service_config.web_mobile.user_profile import ContributorExperienceProfile

LOGGER = logging.getLogger(__name__)


class AC:
    def __init__(self, env=None, temp_path_file=None, driver=None):
        if env is None: env = pytest.env

        self.env = env

        if driver:
            self.driver = driver
        else:
            self.driver = set_up_driver(temp_path_file)

        self.temp_path_file = temp_path_file

        self.ac_user = User(self)
        self.ac_project = Project(self)
        self.project_list = ProjectList(self)
        self.dpr = Dpr(self)
        self.file_upload = FileUpload(self)
        self.client_data_mapping = ClientDataMapping(self)

        self.vendor_profile = VendorProfile(self)

        self.mfa_profile = MfaProfile(self)

        self.navigation = Navigation(self)
        self.verification = GeneralVerification(self)

        self.quizzes = Quizzes(self)
        self.navigation_old_ui = NavigationAcUi(self)
        self.project_old_ui = ProjectOldUI(self)

        self.partner_home = PartnerHome(self)
        self.vendor_pages = VendorPages(self)
        self.internal_home_pages = InternalHome(self)
        self.tickets = Tickets(self)
        self.faker = Faker()

        self.user_screening = UserScreeningPage(self)
        self.administration = AdministrationPage(self)


        self.invoices = InvoicesPage(self)

        # ContributorExperienceP
        self.sign_up_web_mobile = SignUpWebMobile(self)
        self.ce_account_setup = ContributorExperienceAccountSetup(self)
        self.ce_profile = ContributorExperienceProfile(self)
