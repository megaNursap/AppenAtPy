import time

import allure
from selenium.webdriver.common.keys import Keys
from adap.ui_automation.utils.selenium_utils import find_elements, send_keys_by_xpath, find_element


class Overview():
    # XPATH
    PROJECT_TITLE = "//input[@name='projectTitle']"
    PROJECT_NAME = "//input[@name='projectName']"
    PROJECT_ALIAS = "//input[@name='projectAlias']"
    PROJECT_DESCRIPTION = "//textarea[@name='projectDescription'] | //div[@aria-label='rdw-editor']"
    PROJECT_CUSTOMER = "//input[@name='customer']"
    PROJECT_TYPE = "//input[@name='projectType']"
    PROJECT_TASK_TYPE = "//input[@name='taskType']"
    PROJECT_TASK_VOLUME = "//input[@name='taskVolume']"

    elements = {
        "Project Title":
            {"xpath": PROJECT_TITLE,
             "type": "input"
             },
        "Project Name":
            {"xpath":PROJECT_NAME,
             "type": "input"
            },
        "Project Alias":
            {"xpath": PROJECT_ALIAS,
             "type": "input"
            },
        "Project Description":
            {"xpath": PROJECT_DESCRIPTION,
             "type": "input"
            },
        "Customer":
            {"xpath": PROJECT_CUSTOMER,
             "type": "dropdown"
             },
        "Project Type":
            {"xpath": PROJECT_TYPE,
             "type": "dropdown"
             },
        "Task Type":
            {"xpath": PROJECT_TASK_TYPE,
             "type": "dropdown"
             },
        "Task Volume":
            {"xpath": PROJECT_TASK_VOLUME,
             "type": "dropdown"
             }
    }

    def __init__(self, project):
        self.overview = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.overview.enter_data(data=data, elements=self.elements)

    def remove_data_from_fields(self, data):
        self.overview.remove_data(data, self.elements)

    def load_project(self, data):
        self.overview.load_project(data=data, elements=self.elements)



