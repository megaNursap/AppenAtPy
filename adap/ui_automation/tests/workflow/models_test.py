"""
Workflow Models tests
"""
import time

from adap.api_automation.services_config.mlapi import MLAPI
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
USER_ID = get_akon_id('test_ui_account')
USER_TEAM_ID = get_user_team_id('test_ui_account')


def create_new_model(user_id, user_team_id, model_name, base_model):
    _ml = MLAPI(user_id)
    resp = _ml.create_model(model_type=base_model, custom_name=model_name, user_id=user_id, team_id=user_team_id)
    resp.assert_response_status(201)
    return resp.json_response['id']


def get_ml_models(user_id, user_team_id):
    # find ML model, if there is no existing model - create new
    _ml = MLAPI(user_id)
    resp = _ml.get_user_models()
    resp.assert_response_status(200)

    models_trained = []
    models_not_trained = []
    current_models = resp.json_response['models']

    for m in current_models:
        if not m['deleted']:
            model_name = m['name']
            if m['latest_version']['state'] == 'ready':
                models_trained.append({'id': m['id'], 'name': model_name})
            else:
                models_not_trained.append({'id': m['id'], 'name': model_name})

    model_name = generate_random_string(length=6)
    if len(models_trained) == 0:
        model_id = create_new_model(user_id, user_team_id, model_name, 'ibm-watson-explicit-image-detection')
        models_trained.append({'id': model_id, 'name': model_name})

    # if len(models_not_trained) == 0:
    #     model_name = "not ready" + model_name
    #     model_id = create_new_model(user_id, user_team_id, model_name, 'ibm-watson-visual-recognition')
    #     models_not_trained.append({'id': model_id, 'name': model_name})

    return {'trained': models_trained, 'not_trained': []}


@pytest.fixture(scope="module")
def login_and_create_wf(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.workflows_page()

    app.navigation.click_link("Create Workflow")
    wf_name = generate_random_wf_name()

    app.workflow.fill_up_wf_name(wf_name)
    models = get_ml_models(USER_ID, USER_TEAM_ID)

    return models


def test_no_models_access(app_test):
    """
    As a customer without  models enabled, I should not have access to Models in workflows
    """
    user_no_mmodels = get_user_email('no_models')
    password_no_models = get_user_password('no_models')

    app_test.user.login_as_customer(user_name=user_no_mmodels, password=password_no_models)
    app_test.mainMenu.workflows_page()
    app_test.navigation.click_link("Create Workflow")

    wf_name = generate_random_wf_name()
    app_test.workflow.fill_up_wf_name(wf_name)

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Canvas")

    app_test.verification.text_present_on_page("Add Operator")
    app_test.verification.text_present_on_page("Models", is_not=False)


@pytest.mark.dependency()
def test_models_access(app, login_and_create_wf):
    """
    As a customer with models enabled, I should have access to Models in workflows
    As a customer, I can go to my models page from the "Add Operator" panel
    """
    models = login_and_create_wf

    sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")
    app.job.data.upload_file(sample_file)

    app.verification.text_present_on_page("customer_01_sample_22.csv")
    app.navigation.click_link("Canvas")

    app.verification.text_present_on_page("Add Operator")
    app.verification.text_present_on_page("Models")

    app.navigation.click_link("Models")
    app.verification.text_present_on_page(models['trained'][0]['name'])


@pytest.mark.dependency(depends=["test_models_access"])
def test_access_models_page(app, login_and_create_wf):
    wf_window = app.driver.window_handles[0]

    app.navigation.click_link('models listings page')

    models_window = app.driver.window_handles[1]
    app.navigation.switch_to_window(models_window)

    app.verification.current_url_contains('/models')
    app.verification.text_present_on_page('Create Model')

    app.driver.close()
    app.navigation.switch_to_window(wf_window)


# @pytest.mark.skip(reason="feature is deprecated")
# @pytest.mark.dependency(depends=["test_access_models_page"])
# def test_not_able_to_add_not_trained_model(app, login_and_create_wf):
#     not_trained_model = login_and_create_wf['not_trained'][0]['name']
#
#     app.workflow.select_operator.search_job_into_side_bar(not_trained_model)
#     app.workflow.select_operator.verify_job_status_on_the_list(not_trained_model, "Not trained")
#     time.sleep(2)
#
#
#
@pytest.mark.dependency(depends=["test_access_models_page"])
def test_add_trained_model(app, login_and_create_wf):
    trained_model = login_and_create_wf['trained'][0]

    app.workflow.select_operator.search_job_into_side_bar(trained_model['name'])
    # app.workflow.select_operator.verify_job_status_on_the_list(trained_model['name'], "Trained")

    app.workflow.select_operator.connect_job_to_wf(trained_model['name'], 580, 370)

    app.navigation.click_link("Launch")
    linked_models = app.workflow.get_all_operators_on_launch_page()

    assert len(linked_models) == 1
    assert linked_models.get(str(trained_model['id']), False)
    assert linked_models[str(trained_model['id'])]['name'] == trained_model['name']
