import logging
import os
import time
import random

import jsonlines

from adap.api_automation.utils.data_util import get_data_file, get_user_info, get_user_password
from adap.ui_automation.utils.selenium_utils import set_up_driver

LOGGER = logging.getLogger(__name__)


def create_screenshot(driver, name = None):
    filename = name + " " + time.strftime(
        "%d-%m-%Y %I-%M %p") + ".png"
    path = os.path.abspath("Failed_scenarios")

    if not os.path.exists(path):
        os.makedirs(path)
    fullpath = os.path.join(path, filename)

    driver.get_screenshot_as_png()
    driver.save_screenshot(fullpath)

def define_mode(driver):
    mode = driver.find_element('xpath',"//li[@class='worker-mode-gauge big-stat']/h4").text
    return mode.strip()


def login(driver, user, user_password):
    email = driver.find_element('xpath','//input[@id="username"]')
    email.send_keys(user)
    password = driver.find_element('xpath','//input[@id="password"]')
    password.send_keys(user_password)
    driver.find_element('xpath','//input[@type="submit"]').click()
    time.sleep(10)


def logout(driver):
    driver.find_element('xpath','//div[@class="b-DropdownButton b-AccountLinkNew__accountMenu"]').click()
    driver.find_element('xpath','//a[text()="Sign Out"]').click()


def click_submit_button(driver):
    driver.find_element('xpath',"//input[@type='submit']").click()

def update_answers(d1, d2):

    for k, v in d2.items():
        if d1.get(k) is not None:
            d1[k] += v
        else:
            d1[k] = v
    return d1


def complete_task(driver, tq_dict=None):
    """
    complete task and save answers
    """
    close_guide(driver)
    time.sleep(10)
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
        click_submit_button(driver)
    return saved_answers


def check_wrong_answer(driver):
    wrong_answer = driver.find_elements('xpath','//*[text()="Some of your answers weren\'t what we expected."]')
    if len(wrong_answer) > 0:
        driver.find_element('xpath',"//input[@value='Continue']").click()


def answer_questions_on_page(driver, tq_dict, mode='yes_no'):
    questions_on_page = driver.find_elements('xpath','//div[@class="cml jsawesome"]')
    _answers = {}
    for q in questions_on_page:
        time.sleep(1)
        if mode=='yes_no':
            answer_random = random.choice(['Yes', 'No'])
            answer = q.find_elements('xpath',".//input[@value='%s']" % answer_random)
            if len(answer)> 0:
                answer[0].click()
                if not _answers.get(answer_random):
                   _answers[answer_random] = 1
                else:
                    _answers[answer_random] += 1


        # text = q.find_element('xpath',".//input[@value='s']").text
        # if tq_dict.get(text) is not None:
        #     answer = q.find_element('xpath',
        #         ".//div[@class='radios cml_field']//input[@value='%s']" % tq_dict[text])
        # else:
        #     answer = q.find_element('xpath',".//div[@class='radios cml_field']//input[@value]")
        # answer.click()
    time.sleep(2)
    return _answers


def pass_quiz(driver, tq_dict):
    close_guide(driver)
    answer_questions_on_page(driver, tq_dict)
    click_submit_button(driver)
    check_wrong_answer(driver)


def wait_until_job_available(driver, link, max_attempts=10):
    error_msg = driver.find_elements('xpath','//h1[text()="There is no work currently available in this task."]')
    running_time = 0
    while len(error_msg) > 0 and running_time<max_attempts:
        time.sleep(10)
        driver.get(link)
        error_msg = driver.find_elements('xpath','//h1[text()="There is no work currently available in this task."]')
        running_time += 1


def open_job_link(link, user):
    driver = set_up_driver()
    driver.get(link)
    time.sleep(3)
    create_screenshot(driver, "get")
    # login
    user_name = get_user_info(user)['email']
    user_password = get_user_password(user)
    login(driver, user_name, user_password)
    time.sleep(3)
    wait_until_job_available(driver, link)
    return driver


def define_tq_for_job():
    tq_dict = {}
    tq_sample_file = get_data_file('/simple_job/simple_data__tq_ex.json', env="qa")
    with jsonlines.open(tq_sample_file) as reader:
        for obj in reader:
            if obj['_golden'] == 'true':
                tq_dict[obj['text']] = obj['is_this_funny_or_not_gold']
    return tq_dict


def close_guide(driver):
    time.sleep(1)

    guider = driver.find_elements('xpath',"//div[@class='guider'][not(contains(@style,'display: none'))]")
    while len(guider) > 0:
        close = guider[0].find_elements('xpath',".//a[text()='Close']")
        if len(close) > 0:
            close[0].click()
            time.sleep(2)
        else:
            next = guider[0].find_elements('xpath',".//a[text()='Next']")
            if len(next) > 0:
                next[0].click()
                time.sleep(2)
            else:
                print('something wrong with guide')
        guider = driver.find_elements('xpath',"//div[@class='guider'][not(contains(@style,'display: none'))]")


def get_judgment_for_job(link=None, users=None, tq_mode=False):
    for user in users:
        driver = open_job_link(link, user)
        tq_dict = None

        if tq_mode:
            # generate TQs for job
            tq_dict = define_tq_for_job()

            # if this is Quize mode
            if define_mode(driver) == "Quiz mode":
                pass_quiz(driver, tq_dict)

        # start Work mode
        if define_mode(driver) == "Work mode":
            saved_answers = complete_task(driver, tq_dict)

        time.sleep(3)
        driver.close()

    return  saved_answers