import random

from selenium.webdriver.support.select import Select


def collect_answers(_answers, answer_random):
    if not _answers.get(answer_random):
        _answers[answer_random] = 1
    else:
        _answers[answer_random] += 1


def mode_radio_buttons(data, _answers, element, text_message):
    answer_random = random.choice(data)
    answer = element.find_elements('xpath',".//input[@value='%s']" % answer_random)
    if len(answer) > 0:
        answer[0].click()
        print("click!!!!!")
        collect_answers(_answers, answer_random)


def mode_select_cml(data, _answers, element, text_message):
    answer_random = random.choice(data)
    select = Select(element.find_element('xpath',".//div[@class='select cml_field']//select"))
    select.select_by_value(answer_random)
    collect_answers(_answers, answer_random)


def mode_text_cml(data, _answers, element, text_message):
    answer_random = random.choice(data)
    random_num = random.randint(0, 2)
    answer = element.find_elements('xpath',".//input[contains(@class, '%s')]" % answer_random)
    if len(answer) > 0:
        answer[0].send_keys(text_message[random_num])
        print("send text!!!!!")
        collect_answers(_answers, answer_random)


def mode_textarea_cml(data, _answers, element, text_message):
    answer_random = random.choice(data)
    random_num = random.randint(0, 1)
    answer = element.find_elements('xpath',".//textarea[contains(@class, '%s')]" % answer_random)
    if len(answer) > 0:
        answer[0].send_keys(text_message[random_num])
        print("send text!!!!!")
        collect_answers(_answers, answer_random)


def mode_action(mode, data, _answers, element, text_message):
    mode_dict = {
        'radio_button': mode_radio_buttons,
        'cml_select': mode_select_cml,
        'cml_checkboxes': mode_radio_buttons,
        'cml_checkbox': mode_radio_buttons,
        'cml_text': mode_text_cml,
        'cml_textarea': mode_textarea_cml
    }
    return mode_dict[mode](data, _answers, element, text_message)
