import allure

from adap.ui_automation.utils.js_utils import get_text_excluding_children, element_to_the_middle
from adap.ui_automation.utils.selenium_utils import *


class QualityFlowProjectDashboard:
    _TAB = "//nav//a[contains(text(),'{}')]"
    _DOWNLOAD_BUTTON = "//table[@role='table']/tbody/tr[1]/td[9]"
    _CLOSE_BATCH_JOB_POPUP = "//*[text()='Processes Running In Background']/following-sibling::*"

    def __init__(self, project, app):
        self.app = app
        self.driver = self.app.driver
        self.project_quality = QualityFlowDashboardProjectQuality(self, app)
        self.project_productivity = QualityFlowDashboardProjectProductivity(self, app)
        self.project_reports = QualityFlowDashboardReports(self, app)

    def open_tab(self, name):
        with allure.step(f'Open tab {name}'):
            click_element_by_xpath(self.driver, self._TAB.format(name))
            time.sleep(2)


class QualityFlowDashboardProjectQuality:
    _STATISTICS_DATA = "//span[text()='{data_type}']/../../..//label[.='{unit_type}']//preceding-sibling::span"

    def __init__(self, project, app):
        self.app = app
        self.driver = self.app.driver
        self.project = project

    def _get_statistics_data(self, data_type, units):
        result = {}
        for unit_type in units:
            _ = get_text_by_xpath(self.driver, self._STATISTICS_DATA.format(data_type=data_type, unit_type=unit_type))
            result[unit_type] = int(_)

        return result

    def get_quality_flow_summary(self):
        with allure.step(f'Get Quality Flow Summary'):
            units = ['ACCEPTED', 'MODIFIED', 'REJECTED', 'TOTAL UNITS SUBMITTED', 'TOTAL QAED UNITS']
            result = self._get_statistics_data(data_type='Review Jobs Statistics', units=units)
            return result

    def get_leading_job_statistics(self):
        with allure.step(f'Get Leading Jobs Statistics'):
            units = ['TOTAL UNITS SUBMITTED', 'TOTAL QAED UNITS', 'ACCEPTED', 'MODIFIED', 'REJECTED']
            result = self._get_statistics_data(data_type='Leading Jobs Statistics', units=units)
            return result


class QualityFlowDashboardProjectProductivity:
    _PROGRESS_SECTION = "//span[text()='Progress']/../.."
    _THROUGHPUT_SECTION = "//span[text()='Throughput']/../.."
    _SECTION = "//span[text()='{name}']/../.."
    _PROGRESS_JOBS = "//span[text()='Progress']/../../..//a[contains(@href, 'jobs')]/../.."
    _FILTER = "//span[text()='{filter_type}']/../..//a[.//span[text()='Filters']]"
    _DATE_START = "//input[@name='startDate-date-picker']"
    _DATE_END = "//input[@name='endDate-date-picker']"
    _TIME_SLOT = "//input[@name='time-slot-selector']/.."


    def __init__(self, project, app):
        self.app = app
        self.driver = self.app.driver
        self.project = project

    def get_progress_details(self):
        with allure.step(f'Get Progress details'):
            result = {}
            jobs = find_elements(self.driver, self._PROGRESS_JOBS)
            for job in jobs:
                job_name = job.find_element('xpath','.//div[.//a]')
                job_name = get_text_excluding_children(self.driver, job_name)

                completed = job.find_element('xpath','.//div[./span[text()="completed"]]')
                completed = get_text_excluding_children(self.driver, completed)

                total_units = job.find_element('xpath','.//div[./span[text()="total units"]]')
                total_units = get_text_excluding_children(self.driver, total_units)

                not_started = job.find_element('xpath','.//div[./span[text()="Not Started"]]')
                not_started = get_text_excluding_children(self.driver, not_started)

                working = job.find_element('xpath','.//div[./span[text()="Working"]]')
                working = get_text_excluding_children(self.driver, working)

                submitted = job.find_element('xpath','.//div[./span[text()="Submitted"]]')
                submitted = get_text_excluding_children(self.driver, submitted)

                resolving = job.find_element('xpath','.//div[./span[text()="Resolving"]]')
                resolving = get_text_excluding_children(self.driver, resolving)

                result[job_name] = {
                    "completed": completed,
                    "total_units": int(total_units),
                    "not_started": int(not_started),
                    "working": int(working),
                    "submitted": int(submitted),
                    "resolving": int(resolving)
                }

            return result

    # TODO
    def _progress_select_jobs(self):
        pass

    # TODO
    def _get_throughput_details(self):
        with allure.step(f'Get Throughput details'):
            # TODO
            pass

    def _open_filter_for(self, filter_type):
        click_element_by_xpath(self.driver, self._FILTER.format(filter_type=filter_type))

    def _set_filter_for_section(self, section_name, job_type=None, time_slot=None, date_start=None, date_end=None, action=None):
        if job_type:  # TODO
            pass

        if date_start:
            start_date_xpath = self._SECTION.format(name=section_name) + self._DATE_START
            el = find_elements(self.driver, start_date_xpath)
            input_value = el[0].get_attribute('value')
            for i in range(len(input_value)):
                el[0].send_keys(Keys.BACK_SPACE)

            for i in range(len('Invalid date')):
                el[0].send_keys(Keys.BACK_SPACE)

            send_keys_by_xpath(self.driver, start_date_xpath, date_start)
            time.sleep(1)
            click_element_by_xpath(self.driver, start_date_xpath)

        time.sleep(5)

        if date_end:
            end_date_xpath = self._SECTION.format(name=section_name) + self._DATE_END

            el = find_elements(self.driver, end_date_xpath)
            input_value = el[0].get_attribute('value')

            for i in range(len(input_value)):
                el[0].send_keys(Keys.BACK_SPACE)

            for i in range(len('Invalid date')):
                el[0].send_keys(Keys.BACK_SPACE)


            send_keys_by_xpath(self.driver, end_date_xpath, date_end, clear_current=True)
            time.sleep(1)
            click_element_by_xpath(self.driver, end_date_xpath)

        # click_element_by_xpath(self.driver, "//div[text()='Filters']")

        if time_slot:
            click_element_by_xpath(self.driver, self._TIME_SLOT)
            click_element_by_xpath(self.driver, f"//li[text()='{time_slot}']")
            time.sleep(2)

        if action:
            click_element_by_xpath(self.driver, self._SECTION.format(name=section_name)+f"//a[text()='{action}']")

    def set_throughput_filter(self, job_type=None, time_slot=None, date_start=None, date_end=None, action=None):
        with allure.step(f'Set up Throughput filter'):
            _section_name = 'Throughput'
            self._open_filter_for(_section_name)
            self._set_filter_for_section(section_name=_section_name,
                                         job_type=job_type,
                                         time_slot=time_slot,
                                         date_start=date_start,
                                         date_end=date_end,
                                         action=action)

            time.sleep(5)

    def set_progress_filter(self, job_type=None, time_slot=None, date_start=None, date_end=None, action=None):
        with allure.step(f'Set up Progress filter'):
            _section_name = 'Progress'
            self._open_filter_for(_section_name)
            self._set_filter_for_section(section_name=_section_name,
                                         job_type=job_type,
                                         time_slot=time_slot,
                                         date_start=date_start,
                                         date_end=date_end,
                                         action=action)

    def get_throughput_judgements_screenshot(self, temp_dir, file_name):
        with allure.step(f'Get screenshot of Judgements completed graph'):
            full_path = temp_dir + file_name
            el = find_elements(self.driver, "//label[text()='judgements completed']/..")
            assert len(el), "Graph Judgements completed has not been found"
            create_screenshot_for_element(self.driver, el[0], full_path)
            return full_path




class QualityFlowDashboardReports:
    _DOWNLOAD_REPORT = "//tr[.//td[text()='{report_type}']]//a"

    def __init__(self, project, app):
        self.app = app
        self.driver = self.app.driver
        self.project = project

    def download_report(self, report_type):
        with allure.step(f'Download report by type:{report_type}'):
            click_element_by_xpath(self.driver, self._DOWNLOAD_REPORT.format(report_type=report_type))

