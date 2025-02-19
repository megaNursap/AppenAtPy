import allure

from adap.ui_automation.utils.selenium_utils import find_elements


class BasicInformation:
    BUSINESS_NAME = "//input[@name='businessName']"
    DEMOGRAPHIC_CONSENT = "//input[@name='demographic-consent-checkbox']/.."
    COMPLEXION = "//input[@id='complexion']"
    ETHNICITY = "//input[@id='ethnicity']"
    GENDER = "//input[@id='gender']"
    DISABILITY = "//input[@id='disability']"
    BIRTH = "//input[@id='birthDate']"


    elements = {
        "BUSINESS NAME":
            {"xpath": BUSINESS_NAME,
             "type": "input"
             },
        "DEMOGRAPHIC CONSENT":
            {"xpath": DEMOGRAPHIC_CONSENT,
             "type": "checkbox"
             },
        "COMPLEXION":
            {"xpath": COMPLEXION,
             "type": "dropdown"
             },
        "ETHNICITY":
            {"xpath": ETHNICITY,
             "type": "dropdown"
             },
        "GENDER YOU IDENTIFY WITH":
            {"xpath": GENDER,
             "type": "dropdown"
             },
        "ARE YOU CONSIDERED DISABLED?":
            {"xpath": DISABILITY,
             "type": "dropdown"
             },
        "COMPLEXION":
            {"xpath": COMPLEXION,
             "type": "dropdown"
             },
        "DATE OF BIRTH":
            {"xpath": BIRTH,
             "type": "calendar"
             },
    }
    def __init__(self, profile):
        self.profile = profile
        self.app = profile.app

    def fill_out_fields(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)

    def set_up_contract_type(self, contributor_type):
        with allure.step('Set up Contributor Type %s' % contributor_type):
            el = find_elements(self.app.driver, "//button/div[text()='%s']" % contributor_type)
            assert len(el)>0, "Contributor Type %s has not been found"
            el[0].click()

    def remove_data(self, data):
        self.app.ac_project.remove_data(data=data, elements=self.elements)