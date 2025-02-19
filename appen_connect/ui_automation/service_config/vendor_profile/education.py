
class Education:
    HIGHEST_LEVEL_OF_EDUCATION = "//label[text()='HIGHEST LEVEL OF EDUCATION']/..//div[ contains(@data-baseweb, 'select')]"
    LINGUISTICS_QUALIFICATION = ("//label[text()='LINGUISTICS QUALIFICATION']/../..//div[ contains(@data-baseweb, "
                                 "'select')]")

    elements = {
        "HIGHEST LEVEL OF EDUCATION":
            {"xpath": HIGHEST_LEVEL_OF_EDUCATION,
             "type": "dropdown"
             },
        "LINGUISTICS QUALIFICATION":
            {"xpath": LINGUISTICS_QUALIFICATION,
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