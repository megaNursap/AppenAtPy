import time

import allure

from adap.ui_automation.utils.selenium_utils import find_elements


class ReviewAndLaunch:
    def __init__(self, fair_pay):
        self.fair_pay = fair_pay
        self.app = self.fair_pay.app

    def set_rows_to_order(self, rows_to_order: str):
        with allure.step(f"Set rows to order - '{rows_to_order}'"):
            rows_elements = find_elements(self.app.driver, "//input[@name='rowsToOrder']")
            assert rows_elements, "Rows to order element has not been found"
            rows_elements[0].clear()
            rows_elements[0].send_keys(rows_to_order)
            time.sleep(2)

    def click_on_box(self, box_title):
        with allure.step(f"Click on box - '{box_title}'"):
            box_elements = find_elements(self.app.driver, f"//span[text()='{box_title}']")
            assert box_elements, f"Box element with box title - '{box_title}' has not been found"
            box_elements[0].click()
            time.sleep(2)

    def get_old_new_times_prices_per_judgment(self, time_or_price_per_judgment):
        with allure.step("Get Times or Prices Per Judgment"):
            times_prices_per_jud_elements = find_elements(
                self.app.driver, f"//p[text()='{time_or_price_per_judgment}']/..//span"
            )
            assert times_prices_per_jud_elements, f"{time_or_price_per_judgment} elements have not been found"
            return [time_price.text for time_price in times_prices_per_jud_elements]
