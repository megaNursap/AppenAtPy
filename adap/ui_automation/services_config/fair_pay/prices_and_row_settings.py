import time

import allure

from adap.ui_automation.utils.selenium_utils import find_elements


class PricesAndRowSettings:
    def __init__(self, fair_pay):
        self.fair_pay = fair_pay
        self.app = self.fair_pay.app

    def get_price_slider_value(self):
        with allure.step("Get price slider value"):
            price_elements = find_elements(self.app.driver, "//input[@name='slider value']")
            assert price_elements, "Price in slider element has not been found"
            price_slider_value = float(price_elements[0].get_attribute('value')[1:])
            return price_slider_value

    def set_price_slider_value(self, price_value: str):
        with allure.step(f"Set price in slider to '{price_value}'"):
            price_elements = find_elements(self.app.driver, "//input[@name='slider value']")
            assert price_elements, "Price in slider element has not been found"
            price_elements[0].clear()
            price_elements[0].send_keys(price_value)
            time.sleep(2)

    def get_fair_pay_price(self):
        with allure.step("Get 'Fair Pay Price per Judgment' value"):
            time.sleep(2)
            fair_pay_prices = find_elements(
                self.app.driver,
                "//*[text()='Fair Pay Price per Judgment']/../span"
            )
            assert fair_pay_prices, "'Fair Pay Price per Judgment' value has not been found"
            fair_pay_price = float(fair_pay_prices[0].text[1:])
            return fair_pay_price

    def get_time_per_judgment(self):
        with allure.step("Get 'Estimated Time per Judgment' value"):
            time_per_judgment = find_elements(
                self.app.driver,
                "//*[contains(text(),'Time per Judgment')]//../div//input"
            )
            assert time_per_judgment, "'Estimated Time per Judgment' value has not been found"
            text = time_per_judgment[0].text

            if not text:
                return time_per_judgment[0].get_attribute('value')
            else:
                return text

    def set_new_time_per_judgment(self, time_per_judgment_value: str):
        with allure.step("Set 'Estimated Time per Judgment' value"):
            tpj_elements = find_elements(self.app.driver, "//input[@name='timePerJudgment']")
            assert tpj_elements, "'Estimated Time per Judgment' value has not been found"
            time.sleep(1)
            tpj_elements[0].clear()
            tpj_elements[0].send_keys(time_per_judgment_value)
            time.sleep(1)

    def set_tpj_seconds_minutes_hours(self, seconds_minutes_hours: str):
        with allure.step("Set 'Estimated Time per Judgment' seconds minutes hours value"):
            tpj_seconds_minutes_hours_els = find_elements(
                self.app.driver,
                "//*[text()='Seconds'] | //*[text()='Minutes'] | //*[text()='Hours']"
            )
            assert tpj_seconds_minutes_hours_els, \
                "'Estimated Time per Judgment' seconds minutes hours value has not been found"
            tpj_seconds_minutes_hours_els[0].click()
            tpj_s_m_h_els = find_elements(self.app.driver, f"//li[contains(text(),'{seconds_minutes_hours}')]")
            tpj_s_m_h_els[0].click()
            time.sleep(1)
