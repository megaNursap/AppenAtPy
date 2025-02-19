
class Phone:
    PRIMARY_PHONE = "//input[@id='primaryPhone']"
    SECONDARY_PHONE = "//input[@id='secondaryPhone']"

    elements = {
        "Mobile Phone Number":
            {"xpath": PRIMARY_PHONE,
             "type": "input"
            },
        "Secondary Phone Number":
            {"xpath": SECONDARY_PHONE,
             "type": "input"
             }
        }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)

    def verify_data(self, data):
        self.app.ac_project.load_project(data=data, elements=self.elements)

    def remove_data(self, data):
        self.app.ac_project.remove_data(data=data, elements=self.elements)
