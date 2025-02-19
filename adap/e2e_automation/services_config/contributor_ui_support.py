import random
import time

from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.e2e_automation.services_config.job_mode_support import mode_radio_buttons, mode_action

from adap.ui_automation.services_config.application import Application
from adap.ui_automation.utils.selenium_utils import go_to_page

CONTRIBUTOR_PASSWORD = ""


def update_answers(d1, d2):
    for k, v in d2.items():
        if d1.get(k) is not None:
            d1[k] += v
        else:
            d1[k] = v
    return d1


def answer_questions_on_page(driver, tq_dict, mode='radio_button', values=['yes', 'no'],
                             text_for_textarea_text=['Blue', 'Red']):
    questions_on_page = driver.find_elements('xpath', '//div[@class="cml jsawesome" or @class="cml"]')
    _answers = {}
    for q in questions_on_page:
        time.sleep(1)
        mode_action(mode, values, _answers, q, text_for_textarea_text)
    time.sleep(2)
    return _answers


def check_wrong_answer(driver):
    wrong_answer = driver.find_elements('xpath', '//*[text()="Some of your answers weren\'t what we expected."]')
    if len(wrong_answer) > 0:
        driver.find_element('xpath', "//input[@value='Continue']").click()


def complete_task(driver, tq_dict=None, all_units=True):
    """
    complete task and save answers
    """
    # close_guide(driver)
    time.sleep(1)
    saved_answers = {}
    job_completed = driver.find_elements('xpath',
                                         "//h1[text()='You have done the maximum amount of work on this job.']")
    while len(job_completed) == 0:
        time.sleep(2)
        check_wrong_answer(driver)
        _answers = answer_questions_on_page(driver, tq_dict, mode='radio_button')

        update_answers(saved_answers, _answers)

        job_completed = driver.find_elements('xpath',
                                             "//h1[text()='You have done the maximum amount of work on this job.' "
                                             "or text()='Thanks for giving us your feedback.' "
                                             "or text()='Your accuracy is too low.']")
        if len(job_completed) > 0:
            print("JOB is COMPLETE !!!!!!!!!!!")
            return saved_answers
        time.sleep(20)
        driver.find_element('xpath', "//input[@type='submit']").click()
        if all_units == False:
            print("STOP JOB")
            return saved_answers

    return saved_answers


def define_mode(driver):
    mode = driver.find_elements('xpath', "//li[@class='worker-mode-gauge big-stat']/h4")
    if len(mode) > 0: return mode[0].text.strip()
    return None


def generate_judgments_for_job(env, job_link, contributor, contributor_password, all_units=True):
    app = Application(env)
    go_to_page(app.driver, job_link)
    app.user.task.login(contributor, contributor_password)
    app.user.task.wait_until_job_available_for_contributor(job_link)

    current_mode = define_mode(app.driver)

    if current_mode == "Quiz mode":
        # pass quize or fail it
        pass

    if current_mode == "Work mode":
        saved_ques = complete_task(app.driver, all_units=all_units)
        assert len(saved_ques) > 0


def get_judgments(job_id, config):
    api_key = config['user']['api_key']
    contributors = config['judgments']['contributors']

    job_link = generate_job_link(job_id, api_key, config['env'])

    if job_link == '':
        raise Exception("Job link has not been found")

    for contributor, contributor_password in contributors.items():
        generate_judgments_for_job(config['env'], job_link, contributor, contributor_password)
