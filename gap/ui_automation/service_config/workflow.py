import logging
import time

import allure

from adap.ui_automation.utils.selenium_utils import get_text_by_xpath, find_elements, send_keys_by_xpath, \
    click_element_by_xpath

log = logging.getLogger(__name__)


class GWorkflow:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.current_workflow = {}


    def gap_workflow_set_current_project(self, project_name, projectid, project_displayid):
        with allure.step("Set current workflow project params"):
            self.current_workflow['project_name'] = project_name
            self.current_workflow['project_display_id'] = projectid
            self.current_workflow['project_id'] = project_displayid


    def gap_workflow_generate_name(self, workflow_name=None):
        with allure.step("Generate current workflow name"):
            if not workflow_name:
                workflow_name = "auto_workflow_" + str(time.time())
            log.info(f"Current workflow name: {workflow_name}")
            self.current_workflow["workflow_name"] = workflow_name
            return self.current_workflow["workflow_name"]


    def gap_workflow_parse_id(self):
        with allure.step("Parse workflow id from url"):
            url_chunks = self.driver.current_url.split('/')
            assert len(url_chunks) > 0, "Problem to parse workflow id"
            self.current_workflow['workflow_id'] = url_chunks[4]
            log.info(f"Current workflow id: {self.current_workflow.get('workflow_id')}")


    def gap_workflow_parse_workflow_display_id(self):
        with allure.step("Parse workflow display id"):
            el = find_elements(self.driver, "//span[@class='ant-breadcrumb-link']")
            assert len(el) == 3, "Workflow display id not found"
            workflow_detail = el[2].text
            log.info(f"Workflow detail: {workflow_detail}")
            workflow_detail.replace("Workflow detail [", "")
            workflow_detail.replace("]'", "")
            log.info(f"Workflow display id: {workflow_detail}")
            self.current_workflow['workflow_display_id'] = workflow_detail
            log.info(f"Workflow display id: {self.current_workflow.get('workflow_display_id')}")


    def create_gap_workflow(self, template_name, workflow_name=None, button_title='OK'):
        with allure.step("Create new workflow"):
            buttons = ['OK', 'Cancel']
            self.app.g_nav.open_gap_project_tab("Workflow")

            self.app.g_nav.gap_click_btn("Create Workflow")

            self.gap_workflow_generate_name(workflow_name)

            # verify modal window Create Workflow open
            send_keys_by_xpath(self.driver, "//input[@id='flowName']", self.current_workflow.get('workflow_name'))
            # choose template
            click_element_by_xpath(self.driver, "//input[@id='templateIdType']")
            click_element_by_xpath(self.driver,
                                   f"//div[@class='rc-virtual-list-holder-inner']//div[contains(text(),'{template_name}')]")

            # select template
            # click_element_by_xpath(self.driver, f"//div[contains(text(),'{template_name}')]")
            time.sleep(1)
            if button_title in buttons:
                self.app.g_nav.gap_click_btn(f"{button_title}")

            if button_title == buttons[0]:
                self.current_workflow["template_name"] = template_name
                self.gap_workflow_parse_id()
                self.gap_workflow_parse_workflow_display_id()
                self.app.g_project.gap_project_add_workflow(self.current_workflow)
            else:
                click_element_by_xpath(self.driver, "//button/span[@class='ant-modal-close-x']")


    def gap_workflow_search(self, title=None, status=None, job_id=None, team=None, and_do=True):
        with allure.step(f"Search workflow {title}"):
            self.gap_workflow_search_reset()
            if title:
                # TODO SK fix xpath
                send_keys_by_xpath(self.driver, "//input[@placeholder='Please enter']", title)
            # if status:
            #     #//input[contains(@id,'rc_select')]
            # if job_id:
            #     send_keys_by_xpath(self.driver, "//input[@placeholder='Please enter'][2]", job_id)
            # if team:
            if and_do:
                self.app.g_nav.gap_click_btn("Search")
                total_items = get_text_by_xpath(self.driver, "//*[@class='ant-pagination-total-text']")
                log.info(f"Total workflows: {total_items}")
                return total_items


    def gap_workflow_search_reset(self):
        with allure.step("Reset workflow search"):
            self.app.g_nav.gap_click_btn("Reset")


    def gap_workflow_open_existing(self, workflow_name, project_display_id):
        with allure.step(f"Open gap workflow {workflow_name}"):
            if not self.app.g_verify.gap_verify_current_url_contain("workflow"):
                self.app.g_nav.gap_click_btn("Workflow")
                time.sleep(1)
            self.app.g_verify.text_present_on_page(workflow_name)
            # go to workflow details
            click_element_by_xpath(self.driver, f"//span[contains(text(),'{workflow_name}')]")
            self.app.g_verify.text_present_on_page(f"Workflow detail [{project_display_id}")


    # def open_workflow_details(self, workflow_name):
    #     with allure.step("Open gap workflow details"):
    #         expected_text = "Workflow List"
    #         assert self.app.g_verify.text_present_on_page(expected_text), f"Text {expected_text} not found"
    #         click_element_by_xpath(self.driver,
    #                                f"//div[@class='antd-pro-pages-project-workflow-components-workflow-card-title']//span[text()='{workflow_name}']")
    #         assert self.app.g_verify.text_present_on_page(workflow_name)

    def gap_workflow_search_by_name(self, name):
        with allure.step(f"Search workflow {name}"):
            self.app.g_nav.open_gap_project_tab("Workflow")
            assert self.app.g_verify.text_present_on_page("Workflow List")
            self.app.g_nav.gap_click_btn("Reset")
            send_keys_by_xpath(self.driver, "//input[@placeholder='Please enter']", name)
            self.app.g_nav.gap_click_btn("Search")
            el = find_elements(self.driver, "//li[contains(text(),'Total 1 items')]")
            assert len(el) > 0, "Workflow {name} not found"


    def gap_workflow_get_job_list(self, workflow_name):
        with allure.step(f"Get gap job list from workflow {workflow_name}"):
            self.app.g_nav.open_gap_project_tab("Workflow")
            self.gap_workflow_search_by_name(workflow_name)
            el = find_elements(self.driver, "//p[text()='Internal team']")
            assert len(el) > 0, "Not found internal team links"
            return el
