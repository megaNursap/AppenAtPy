import pytest
import allure
import logging
import time

from adap.api_automation.services_config.mlapi import MLAPI
from adap.api_automation.utils.data_util import get_akon_id, get_user_team_id, get_data_file, count_row_in_file

pytestmark = pytest.mark.regression_core

LOGGER = logging.getLogger(__name__)
MODEL = pytest.data.predefined_data
try:
    PRETRAINED_WATSON_MODEL_FOOTWEAR_ID = MODEL["pretrained_model"][pytest.env]
except ValueError:
    PRETRAINED_WATSON_MODEL_FOOTWEAR_ID = ''

USER_ID = get_akon_id('test_account')
USER_TEAM_ID = get_user_team_id('test_account')
SUMMARY_KEYS = ["test_split", "training_split", "validation_split"]


@pytest.fixture(scope="module")
def new_model(request):
    ml = MLAPI(USER_ID)
    resp = ml.create_model('face-blur-model', USER_ID, USER_TEAM_ID)
    ml.model_id = resp.json_response['id']
    return ml.model_id


@allure.parent_suite('/base_models?trainable={trainable}:post')
@pytest.mark.ml_api
@pytest.mark.parametrize('scenario, trainable',
                         [("trainable models", "true"),
                          ("pre-trained models", "false")])
def test_get_model_catalog(scenario, trainable):
    _ml = MLAPI(USER_ID)

    resp = _ml.get_base_models(trainable)
    resp.assert_response_status(200)


@allure.parent_suite('/models/{model_id}/user_id={user_id}:get')
@pytest.mark.ml_api
def test_get_users_models():
    _ml = MLAPI(USER_ID)

    resp = _ml.get_user_models()
    resp.assert_response_status(200)
    assert resp.json_response['models']


@allure.parent_suite('/models:post')
@pytest.mark.ml_api
def test_create_model():
    _ml = MLAPI(USER_ID)
    model_type = 'f8-coherence-detection'
    custom_name = 'API_GENERATED_MODEL'

    resp = _ml.create_model(model_type, _ml.user_id, USER_TEAM_ID, custom_name)

    resp.assert_response_status(201)
    _ml.model_id = resp.json_response.get('id')
    assert _ml.model_id, "model id was not generated"
    assert resp.json_response['user_id'] == USER_ID
    assert resp.json_response['team_id'] == USER_TEAM_ID
    assert resp.json_response['name'] == custom_name

    LOGGER.info(_ml.model_id)


@allure.parent_suite('/models/{model_id}:get')
@pytest.mark.ml_api
def test_read_model(new_model):
    _ml = MLAPI(USER_ID)
    resp = _ml.read_model(_ml.model_id)
    assert resp.json_response['name']


@allure.parent_suite('/models:post')
@pytest.mark.ml_api
@allure.issue("https://appen.atlassian.net/browse/ADAP-2921", "BUG on Integration/Staging ADAP-2921")
def test_create_model_invalid():
    _ml = MLAPI(USER_ID)

    resp = _ml.create_model('non-existent', _ml.user_id, USER_TEAM_ID)
    resp.assert_response_status(422)
    resp.assert_error_message_v2("Couldn't find the base model to create the model from.")


@allure.parent_suite('/models/{model_id}:get')
@pytest.mark.ml_api
def test_read_model(new_model):
    _ml = MLAPI(USER_ID)
    _ml.model_id = new_model

    _resp = _ml.read_model(_ml.model_id)
    _resp.assert_response_status(200)

    assert _resp.json_response['id'] == _ml.model_id


# @allure.parent_suite('/models/{model_id}/training_data:post')
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_add_training_data_csv_to_model(new_model):
#     _ml = MLAPI(USER_ID)
#
#     file = get_data_file('/catdog_training.csv')
#
#     _resp = _ml.add_training_data(new_model, file)
#     _resp.assert_response_status(200)
#     num_rows = count_row_in_file(file)
#     assert _resp.json_response['provided'] == num_rows
#     assert _resp.json_response['added'] == num_rows
#
#
# @allure.parent_suite('/models/{model_id}/training_data:get')
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_get_training_data(new_model):
#     _ml = MLAPI(USER_ID)
#
#     _resp = _ml.get_training_data(new_model)
#     _resp.assert_response_status(200)
#
#
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_get_training_data_summary_trained_model():
#     _ml = MLAPI(USER_ID)
#
#     _resp = _ml.get_training_data_summary(PRETRAINED_WATSON_MODEL_FOOTWEAR_ID)
#     _resp.assert_response_status(200)
#
#     assert _resp.json_response["test_split"]
#     assert _resp.json_response["training_split"]
#     assert _resp.json_response["validation_split"]
#
#
# @allure.parent_suite('/models/{model_id}/training_data_summary:get')
# @pytest.mark.ml_api
# @pytest.mark.skip
# # @allure.issue('https://appen.atlassian.net/browse/CW-4499', 'Bug')
# def test_get_training_data_summary_no_data():
#     _ml = MLAPI(USER_ID, USER_TEAM_ID)
#     _resp = _ml.create_model('f8-coherence-detection')
#     _resp.assert_response_status(201)
#
#     resp = _ml.get_training_data_summary(_ml.model_id)
#     resp.assert_response_status(404)
#     resp.assert_error_message_v2('No data found')
#
#
# @allure.parent_suite('/models/{model_id}/train:post')
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_train_model(new_model):
#     _ml = MLAPI(USER_ID)
#
#     _resp = _ml.train_model(new_model)
#     _resp.assert_response_status(200)
#     assert _resp.json_response['task_id'], "A task id was not generated"
#
#
# @allure.parent_suite('/models/{model_id}/training_results:get')
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_get_training_results():
#     _ml = MLAPI(USER_ID)
#
#     _resp = _ml.get_training_results(PRETRAINED_WATSON_MODEL_FOOTWEAR_ID)
#     _resp.assert_response_status(200)
#
#
# @allure.parent_suite('/models/{model_id}/evaluate:post')
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_evaluate_model():
#     _ml = MLAPI(USER_ID)
#
#     _resp = _ml.evaluate_model(PRETRAINED_WATSON_MODEL_FOOTWEAR_ID)
#     assert _resp.json_response['task_id']
#     _resp.assert_response_status(200)
#
#
# @allure.parent_suite('/models/{model_id}/evaluation_summary:get')
# @pytest.mark.ml_api
# @pytest.mark.skip
# def test_get_evaluate_summary():
#     _ml = MLAPI(USER_ID)
#
#     resp = _ml.get_evaluation_summary(PRETRAINED_WATSON_MODEL_FOOTWEAR_ID)
#     resp.assert_response_status(200)
#
#     assert resp.json_response['f8_model_id'] == PRETRAINED_WATSON_MODEL_FOOTWEAR_ID
#
#     tries = 0
#     time.sleep(2)
#
#     while resp.json_response['progress_evaluated_of'] != resp.json_response['progress_evaluated_rows'] and tries < 40:
#         resp = _ml.get_evaluation_summary(PRETRAINED_WATSON_MODEL_FOOTWEAR_ID)
#         time.sleep(5)
#         tries += 1
#         LOGGER.info("number of tries: %s" % tries)
#
#     assert resp.json_response['progress_evaluated_of'] == resp.json_response['progress_evaluated_rows'] == \
#         resp.json_response['progress_evaluated_total'] == resp.json_response['summary']['total_rows']
