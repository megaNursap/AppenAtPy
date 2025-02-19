import time

import allure

from adap.ui_automation.utils.selenium_utils import find_elements


class Monitor:

    def __init__(self, job):
        self.job = job
        self.app = job.app

    def open_tab(self, tab_name):
        with allure.step('Open job tab %s' % tab_name):
            tab = find_elements(self.app.driver,
                                "//a[text()='%s' and contains(@href,'/jobs/')]"% tab_name)
            assert len(tab) > 0, "Tab %s has not found" % tab_name
            tab[0].click()
            time.sleep(3)

    def grab_info_from_dashboard(self, info_type):
        with allure.step('Grab info from dashboard %s' % info_type):
            el = find_elements(self.app.driver, "//label[text()='%s']/..//div[2]" %info_type)
            assert len(el) > 0, "Metrics %s has not been found" % info_type
            return el[0].text

    def get_internal_link_for_job_on_monitor_page(self):
        with allure.step('Get internal link for job'):
            el = find_elements(self.app.driver, "//a[contains(text(), 'https')]")
            if len(el) > 0:
                return el[0].get_attribute('href')
            assert False, "Internal link has not been found"

    def tab_present(self, tab_name):
        with allure.step('Verify tab present %s' % tab_name):
            tab = find_elements(self.app.driver,
                                "//a[text()='%s' and contains(@href,'/jobs/')]"% tab_name)
            assert len(tab) > 0, "Tab %s has not found" % tab_name

    def get_old_new_times_prices(self, section_name):
        with allure.step("Get Times or Prices Per Judgment"):
            times_prices_elements = find_elements(self.app.driver, f"//p[text()='{section_name}']/..//p")
            assert times_prices_elements, f"{section_name} elements have not been found"
            return times_prices_elements[0].text

    def change_times_prices_to_int_float(self, times_prices):
        with allure.step("Change Times or Prices Per Judgment to integer or float"):
            if "s" in times_prices:
                new_value = int(times_prices.replace("s", ""))
            else:
                new_value = float(times_prices.replace("$", ""))

            return new_value
