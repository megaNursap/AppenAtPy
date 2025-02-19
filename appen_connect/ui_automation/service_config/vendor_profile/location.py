from adap.ui_automation.utils.selenium_utils import find_elements


class Location:
    STREET_ADDRESS = "//textarea[@name='address']"
    CITY = "//input[@name='city']"
    ZIP = "//input[@name='zip']"
    YEARS = "//label[text()='YEARS']/..//input[contains(@id,'react-select')]"
    RESIDENCY_HISTORY = "//input[@aria-label='Select a date.']"

    elements = {
        "Street Address":
            {"xpath": STREET_ADDRESS,
             "type": "textarea"
             },
        "CITY":
            {"xpath": CITY,
             "type": "input"
             },
        "ZIP CODE":
            {"xpath": ZIP,
             "type": "input"
             },
        "YEARS":
            {"xpath": YEARS,
             "type": "dropdown"
             },
        "Residency History":
            {"xpath": RESIDENCY_HISTORY,
             "type": "calendar"
             }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app
        self.driver = self.app.driver

    def fill_out_fields(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)

    def verify_data(self, data):
        self.app.ac_project.load_project(data=data, elements=self.elements)

    def remove_data(self, data):
        self.app.ac_project.remove_data(data=data, elements=self.elements)

    def residence_history_of_worker(self, value):
        residence_history = find_elements(self.app.driver,
                                          "//label[text()='YEARS']/..//div[contains(@class,'control') and @data-testid='residency-years-select']")
        assert len(residence_history), "Field country of residence has not been found"
        residence_history[0].click()
        option = find_elements(self.driver,
                                   "//div[contains(@id,'react-select')][.//div[text()='%s']]" % value)
        #if len(option)==0:
            #option = find_elements(self.driver,
                                  # "//div[contains(@id,'react-select')][.//div[text()='%s']]" % value)
        assert len(option), "Value %s has not been found" % value
        option[0].click()
