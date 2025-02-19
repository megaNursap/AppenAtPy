import allure

from adap.ui_automation.services_config.fair_pay.crowd_settings import CrowdSettings
from adap.ui_automation.services_config.fair_pay.prices_and_row_settings import PricesAndRowSettings
from adap.ui_automation.services_config.fair_pay.review_and_launch import ReviewAndLaunch
from adap.ui_automation.utils.selenium_utils import find_elements


class FairPay:
    def __init__(self, app):
        self.app = app
        self.crowd_settings = CrowdSettings(self)
        self.price_and_row_settings = PricesAndRowSettings(self)
        self.review_and_launch = ReviewAndLaunch(self)

    def change_team_roles_by_names(self, role_names: list, select: bool = True):
        with allure.step(f"Change team roles by role names list: '{role_names}'"):
            for role_name in role_names:
                self.app.user.update_role_for_team(role=role_name, value=select)

    def select_radio_button_by_name(self, radio_button_name: str):
        with allure.step(f"Select radio button by name: {radio_button_name}"):
            radio_buttons = find_elements(self.app.driver, f"//*[(text()='{radio_button_name}')]/..//input/..")
            assert radio_buttons, f"Radio button with name - '{radio_button_name}' has not been found"

            if radio_buttons[0].is_selected():
                return
            else:
                radio_buttons[0].click()
