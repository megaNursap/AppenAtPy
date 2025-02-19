import allure

from adap.ui_automation.utils.selenium_utils import find_elements


class Tickets:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.navigation = self.app.navigation

    PROJECT = "//select[@id='projects']"
    TICKET_TYPE = "//select[@id='ticket-type']"
    TEMPLATE = "//select[@id='templates']"
    RECIPIENTS = "//textarea[@name='emailList']"
    TITLE = "//fieldset[@class='standard-form']//input[@id='title']"
    MAIL_MERGE = "//input[@name='mailMerge']"

    elements_ticket = {
        "Project":
            {
                "xpath": PROJECT,
                "type": "dropdown"
            },
        "Type":
            {
                "xpath": TICKET_TYPE,
                "type": "dropdown"
            },
        "Template":
            {
                "xpath": TEMPLATE,
                "type": "dropdown"
            },
        "Recipients":
            {
                "xpath": RECIPIENTS,
                "type": "textarea"
            },
        "Title":
            {
                "xpath": TITLE,
                "type": "textarea"
            },
        "Mail_Merge":
            {
                "xpath": MAIL_MERGE,
                "type": "radio"

            }

    }

    def fill_out_fields(self, data={}):
        with allure.step('Fill out fields. to create your Ticket. %s' % data):
            self.app.navigation_old_ui.enter_data_v1(data, self.elements_ticket)

    def fill_ticket_body(self,ticket_body):
       with allure.step('Fill out field Ticket body %s' % ticket_body):
           self.driver.switch_to.frame(0)
           el = find_elements(self.driver, "//p[contains(text(),'Dear Search Engine Evaluator,')]")
           assert len(el), "Element is not found"
           if len(el)>0:
              el[0].send_keys(ticket_body)
           self.driver.switch_to.default_content()


