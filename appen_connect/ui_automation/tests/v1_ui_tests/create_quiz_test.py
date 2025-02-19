"""
    Create new quiz
"""
import datetime

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.data_util import *
from faker import Faker

pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_ui_uat]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


@pytest.fixture(scope="function")
def login(app_test):
    app_test.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


def generate_quiz_name():
    faker = Faker()
    today = datetime.date.today().strftime("%m/%d/%Y")
    return [(faker.name() + today)]


def generate_quiz_instructions():
    faker = Faker()
    return [(faker.name())]


@pytest.mark.ac_old_ui_smoke
def test_create_quiz(app_test, login):
    app_test.navigation.click_link('Quality')
    app_test.navigation.click_link('Quizzes')
    app_test.navigation.click_link('Add')

    quiz_name = generate_quiz_name()
    quiz_instructions = generate_quiz_instructions()

    app_test.quizzes.quiz_title(quiz_name)
    app_test.quizzes.fill_out_fields(data={
        "Quiz Type": "Quiz",
        "Quiz Status": "Disabled"})
    app_test.quizzes.quiz_instructions(quiz_instructions)
    app_test.navigation_old_ui.click_input_btn("Save")

    app_test.quizzes.search_for_quiz_created(quiz_name)

    app_test.navigation_old_ui.click_input_btn("Go")
    app_test.verification.text_present_on_page(quiz_name[0])
