import allure
import logging

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.ml_endpoints import *

LOGGER = logging.getLogger(__name__)


class MLAPI:

    def __init__(self, user_id, team_id=None, custom_url=None, payload=None, env=None, model_id=''):
        self.model_id = model_id
        self.user_id = user_id
        self.team_id = team_id
        self.payload = payload

        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL.format(env)

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_base_models(self, trainable):
        res = self.service.get(BASE_MODELS.format(trainable=trainable), ep_name=BASE_MODELS)
        return res

    @allure.step
    def get_user_models(self, user_id=None):
        if not user_id:
            user_id = self.user_id
        res = self.service.get(USER_MODELS.format(user_id=user_id), ep_name=USER_MODELS)
        return res

    def create_model(self, model_type, user_id=None, team_id=None, custom_name=None, payload=None):
        if not user_id:
            user_id = self.user_id

        if not team_id:
            team_id = self.team_id

        if not payload:
            if custom_name:
                payload = {
                    "base_model_id": model_type,
                    "user_id": user_id,
                    "team_id": team_id,
                    "name": custom_name
                }
            else:
                payload = {
                    "base_model_id": model_type,
                    "user_id": user_id,
                    "team_id": team_id
                }

        res = self.service.post(CREATE_MODEL, data=json.dumps(payload), ep_name=CREATE_MODEL)
        if os.environ.get("PYTEST_CURRENT_TEST", ""):
            if res.status_code == 201:
                self.model_id = res.json_response['id']
                pytest.data.models_collection[self.model_id] = self.user_id
        return res

    @allure.step
    def read_model(self, model_id):
        if not model_id:
            model_id = self.model_id

        res = self.service.get(MODEL.format(model_id=model_id), ep_name=MODEL)
        return res

    @allure.step
    def add_training_data(self, model_id, datafile):
        headers = {"Content-Type": "text/csv"}
        with open(datafile, buffering=1) as file:
            res = self.service.post(TRAINING_DATA.format(model_id=model_id), headers=headers, data=file, ep_name=TRAINING_DATA)
        return res

    @allure.step
    def get_training_data(self, model_id):
        res = self.service.get(TRAINING_DATA.format(model_id=model_id), ep_name=TRAINING_DATA)
        return res

    @allure.step
    def get_training_data_summary(self, model_id):
        res = self.service.get(TRAINING_DATA_SUMMARY.format(model_id=model_id), ep_name=TRAINING_DATA_SUMMARY)
        return res

    @allure.step
    def train_model(self, model_id):
        res = self.service.post(TRAIN_MODEL.format(model_id=model_id), ep_name=TRAIN_MODEL)
        return res

    @allure.step
    def evaluate_model(self, model_id):
        res = self.service.post(EVALUATE.format(model_id=model_id), ep_name=EVALUATE)
        return res

    @allure.step
    @allure.step
    def get_evaluation_summary(self, model_id):
        res = self.service.get(EVALUATION_SUMMARY.format(model_id=model_id), ep_name=EVALUATION_SUMMARY)
        return res

    @allure.step
    def get_training_results(self, model_id):
        res = self.service.get(TRAINING_RESULTS.format(model_id=model_id), ep_name=TRAINING_RESULTS)
        return res

    @allure.step
    def delete_model(self, model_id):
        res = self.service.delete(MODEL.format(model_id=model_id), ep_name=MODEL)
        return res

    @allure.step
    def get_names_of_model(self, model_id):
        model_names = []
        for i in range(len(model_id)):
            _ml = MLAPI(self.user_id)
            resp = _ml.read_model(model_id[i])
            model_names.append(resp.json_response.get('name'))
        return model_names
