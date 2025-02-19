BASE_MODELS = '/base_models?trainable={trainable}'
CREATE_MODEL = '/models'
MODEL = '/models/{model_id}'
USER_MODELS = '/models?user_id={user_id}'
TRAINING_DATA = '/models/{model_id}/training_data'
TRAINING_DATA_SUMMARY = '/models/{model_id}/training_data_summary'
TRAIN_MODEL = '/models/{model_id}/train'
TRAINING_RESULTS = '/models/{model_id}/training_results'
STATE = '/models/{model_id}/v/latest'
EVALUATE = '/models/{model_id}/evaluate'
EVALUATION_SUMMARY = '/models/{model_id}/evaluation_summary'

URL = "https://ml-api.internal.{}.cf3.us"
