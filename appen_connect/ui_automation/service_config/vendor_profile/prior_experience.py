
class PriorExperience:

    EXPERIENCE_TRANSCRIPTION = "//input[@name='experienceTranscription']/.."
    EXPERIENCE_PROOF_READING = "//input[@name='experienceProofReading']/.."
    SEARCH_ENGINE_EVALUATOR = "//input[@name='workAsSearchEngineEvaluator']/.."

    elements = {
        "EXPERIENCE TRANSCRIPTION":
            {"xpath": EXPERIENCE_TRANSCRIPTION,
             "type": "checkbox"
             },
        "EXPERIENCE PROOF READING":
            {"xpath": EXPERIENCE_PROOF_READING,
             "type": "checkbox"
             },
        "SEARCH ENGINE EVALUATOR":
            {"xpath": SEARCH_ENGINE_EVALUATOR,
             "type": "checkbox"
             }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)

    def verify_data(self, data):
        self.app.ac_project.load_project(data=data, elements=self.elements)
