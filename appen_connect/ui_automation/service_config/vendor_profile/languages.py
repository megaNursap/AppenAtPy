
class Languages:

    # PRIMARY_LANGUAGE ="//label[text()='YOUR PRIMARY LANGUAGE']/..//input[contains(@id,'react-select')]"
    PRIMARY_LANGUAGE ="//label[text()='YOUR PRIMARY LANGUAGE']/..//div[text() and contains(@class, 'singleValue')]"
    LANGUAGE_REGION = "//label[text()='YOUR LANGUAGE REGION']/..//div[text() and contains(@class, 'singleValue')]"
    ADDITIONAL_LANGUAGES = "//input[@name='additionalLanguages']/.."
    TRANSLATION_EXPERIENCE = "//input[@name='translationExperiences']/.."

    LOCALE_LANGUAGE = ""

    elements = {
        "YOUR PRIMARY LANGUAGE":
            {"xpath": PRIMARY_LANGUAGE,
             "type": "dropdown"
             },
        "YOUR LANGUAGE REGION":
            {"xpath": LANGUAGE_REGION,
             "type": "dropdown"
             },
        "Additional languages":
            {"xpath": ADDITIONAL_LANGUAGES,
             "type": "checkbox"
             },
        "Translation experience":
            {"xpath": TRANSLATION_EXPERIENCE,
             "type": "checkbox"
             },
        "LOCALE LANGUAGE":
            {"xpath": "",
             "type": "dropdown"
             },
        "LANGUAGE REGION":
            {"xpath": "",
             "type": "dropdown"
             },
        "SPOKEN FLUENCY":
            {"xpath": "",
             "type": "dropdown"
             },
        "WRITTEN FLUENCY":
            {"xpath": "",
             "type": "dropdown"
             },
        "FROM":
            {"xpath": "",
             "type": "dropdown"
             },
        "TO":
            {"xpath": "",
             "type": "dropdown"
             }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)

    def verify_data(self, data):
        self.app.ac_project.load_project(data=data, elements=self.elements)

    def add_additional_language(self, data, action=None):
        self.app.ac_project.enter_data(data=data, elements=self.elements)
        if action:
            self.app.navigation.click_btn(action)

    def add_translation_experience(self, data, action=None):
        self.app.ac_project.enter_data(data=data, elements=self.elements)
        if action:
            self.app.navigation.click_btn(action)






