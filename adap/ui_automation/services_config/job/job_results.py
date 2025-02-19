import time
from adap.ui_automation.utils.selenium_utils import find_element

class Results:

    def __init__(self, job):
        self.job = job
        self.app = job.app
        self.driver = self.job.app.driver

    def download_report(self, report_type, job_id):
        # xpath = "//li[.//h2[text()='%s']]//a[text()='Download Report']" % report_type
        xpath = "//*[text()='%s']/../..//a[text()='Download Report']" % report_type
        find_element(self.driver, xpath).click()
        # progress bar feature changed.
        # progressbar = find_element(self.driver,"//div[@id='progressbar']")
        # time_to_wait = 1000
        # progress = 0
        # current_time = 0
        # while progress != '100' and current_time < time_to_wait:
        #     progress = progressbar.get_attribute('aria-valuenow')
        #     time.sleep(1)
        #     current_time += 1
        time.sleep(15)
        tmp_files_dir = self.job.app.temp_path_file
        file_name = self.get_file_report_name(job_id, report_type)
        time.sleep(10)
        self.app.verification.verify_file_present_in_dir(file_name, tmp_files_dir)

    def get_file_report_name(self, job_id, report_type):
        if report_type == "Full":
            file_name = "f%s.csv.zip" % job_id
        elif report_type == "Aggregated":
            file_name = "a%s.csv.zip" % job_id
        elif report_type == "Source":
            file_name = "source%s.csv.zip" % job_id
        elif report_type == "Test Questions":
            file_name = "job_%s_gold_report.csv.zip" % job_id
        elif report_type == "Contributors":
            file_name = "workset%s.csv.zip" % job_id
        elif report_type == "Json":
            file_name = "job_%s.json.zip" % job_id
        else:
            assert False, "Unknown report type!"
        return file_name
