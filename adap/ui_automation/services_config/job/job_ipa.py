import time

import allure
import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from adap.ui_automation.utils.js_utils import scroll_to_element
from adap.ui_automation.utils.selenium_utils import find_element, find_elements, get_text_by_xpath, \
    is_element, split_text
from adap.ui_automation.utils.page_element_utils import click_rebrand_popover


class IPA:

    def __init__(self, job):
        self.job = job
        self.app = job.app

    def clear_textarea(self, element, text):
        with allure.step("Clear text area"):
            ac = ActionChains(self.app.driver)
            ac.pause(2) \
                .move_to_element(element) \
                .click(element) \
                .send_keys(len(text) * Keys.BACKSPACE) \
                .pause(2) \
                .perform()

    def open_quality_audit_page(self, ipa_job):
        with allure.step(f"Open quality audit page for {ipa_job}"):
            ipa_url = "https://client.{env}.cf3.us/jobs/{job}/audit".format(env=pytest.env, job=ipa_job)
            self.app.navigation.open_page(ipa_url)
            click_rebrand_popover(self.app.driver)

    def open_quality_audit_with_endpoint(self, quality_audit_job_id, endpoint):
        with allure.step(f"Open quality audit page with endpoint {endpoint} for {quality_audit_job_id}"):
            quality_audit_url = f"https://client.{pytest.env}.cf3.us/jobs/{quality_audit_job_id}/audit/{endpoint}"
            self.app.navigation.open_page(quality_audit_url)
            click_rebrand_popover(self.app.driver)

    def customize_data_source(self, column_name, data_type, action=None):
        with allure.step('Customize data source: %s, %s' % (column_name, data_type)):
            field1 = find_elements(self.app.driver, "//input[@name='name_0']/..")[0]
            field1.click()
            el = field1.find_elements('xpath',".//li[text()='%s']" % column_name)
            assert len(el) > 0, "Column %s has not been found" % column_name
            el[0].click()

            field2 = find_elements(self.app.driver, "//input[@name='type_0']/..")[0]
            field2.click()
            time.sleep(1)
            el = field2.find_elements('xpath',".//li[text()='%s']" % data_type)
            assert len(el) > 0, "Data type %s has not been found" % data_type
            el[0].click()

            if action:
                self.app.navigation.click_link(action)

    def _find_units(self):
        return find_elements(self.app.driver, "//*[contains(text(),'Unit ID')]/../..")

    def get_all_units_on_page(self, unit_number=0, image_transcription=False):
        with allure.step('Get all units on the page'):
            all_el = self._find_units()
            result = []
            for _ in all_el:

                _data = _.find_element('xpath',".//h4").text
                _unit_id = _.find_element('xpath',".//*[contains(text(),'ID')]").get_attribute('title')
                _answer = _.find_elements('xpath',".//h4/following-sibling::div/div/div")
                _no_answer = _.find_elements('xpath',".//p[contains(text(), 'No answer')]")
                _answer_input = "No answer selected"
                if len(_no_answer) == 0 and not image_transcription :
                    _answer_input = _answer[unit_number].text
                elif image_transcription:
                    _answer_input = ""
                if len(_.find_elements('xpath',
                        ".//*[contains(text(), 'View Details')]/..//*[local-name() = 'svg']")) > 0:
                    _audited = True
                else:
                    _audited = False

                result.append({"data": _data,
                               "unit_id": _unit_id,
                               "answer": len(_answer),
                               "audited": _audited,
                               "answer_input": _answer_input,
                               "no_answer": len(_no_answer)
                               })
            print("---", result)
            return result

    def view_details_by_unit_id(self, unit_id):
        with allure.step('View details for unit: %s' % unit_id):
            el = find_elements(
                self.app.driver, f".//*[text()='{unit_id}']//..//..//div/a[text()='View Details']"
            )
            assert len(el) > 0, "Judgement with unit id: %s has not been found" % unit_id

            el[0].click()
            time.sleep(2)

    def click_carousel(self, type='next'):
        with allure.step(f"Click carousel with type {type}"):
            if type == 'next':
                el = find_elements(self.app.driver, "//a[.//span[contains(@class,'b-ModalNavigationButton__arrow "
                                                    "b-ModalNavigationButton__arrow--next')]]")
            else:
                el = find_elements(self.app.driver,
                                   "//a[.//span[contains(@class,'b-ModalNavigationButton__arrow')]]")
            assert len(el) > 0, "Button has not been found"
            el[0].click()

    def approve_question(self, question=0):
        with allure.step('Approve question'):
            el = find_elements(self.app.driver, "//div[@role='document']//div[@data-tooltip]")
            assert len(el), "Approve button has not been found"
            el[question].click()

    def reject_question(self, question=1):
        with allure.step('Reject question'):
            el = find_elements(self.app.driver, "//div[@role='document']//div[@data-tooltip]")
            assert len(el) > 1, "Incorrect button has not been found"
            el[question].click()

    def get_question_status(self, question='Question 1'):
        with allure.step('Get question status from Details page'):
            el = find_elements(self.app.driver, "//div[contains(@class, 'rebrand-Question__button--checked')]")
            assert len(el) > 0, f"Question {question} not found"
            _class = el[0].get_attribute('class')
            if ('rebrand-Question__button--incorrect' not in _class) and (
                    'rebrand-Question__button--correct' not in _class):
                return None
            elif 'rebrand-Question__button--correct' in _class:
                return "approved"
            elif "rebrand-Question__button--incorrect" in _class:
                return "rejected"

    def add_reason(self, reason=''):
        with allure.step('Add reason'):
            self.edit_reason()
            el = find_elements(self.app.driver, "//textarea")
            assert len(el) > 0, "Textarea has not been found"
            el[0].clear()
            el[0].send_keys(reason)

    def edit_reason(self):
        with allure.step('Edit reason'):
            el_reason = find_elements(self.app.driver, "//h2/span[contains(text(), 'Reason')]")
            if len(el_reason):
                find_element(self.app.driver, "//a[text()='Edit']").click()

    def clear_reason(self):
        with allure.step('Clear reason'):
            el = find_elements(self.app.driver, "//textarea")
            assert len(el) > 0, "Textarea has not been found"
            self.clear_textarea(el[0], el[0].text)

    def filter_questions_by_status(self, status):
        with allure.step(f"Filter questions by status {status}"):
            view = find_elements(self.app.driver, "//a[contains(@href,'/') and contains(text(), 'View')]")
            assert len(view) > 0, "Link contained string View not found"
            view[0].click()
            time.sleep(1)
            # for _ in ["Audited", "Unaudited"]:
            #     _input = find_element(self.app.driver, "//span[text()='%s']" % _)
            #     box = find_element(self.app.driver, "//span[text()='%s']/../..//input" % _)
            #     _checked = box.get_attribute('checked')
            #     # if _checked and (_ not in status) : _input.click()  # uncheck
            #     if not _checked and (_ in status): _input.click()

            _input = find_elements(self.app.driver, "//span[text()='%s']" % status)
            assert len(_input) > 0, f"Text with {status} not found"
            _input[0].click()
            # time.sleep(2)
            # find_element(self.app.driver,"//div[@class='b-AuditPage']").click()

    def customize_question(self):
        with allure.step('Customize_question'):
            self.app.navigation.click_link('Configure Tile')
            self.app.navigation.click_link('Customize Question')
            el = find_elements(self.app.driver, "//div[contains(text(), 'Select question to use as preview for "
                                                "audit. You can also filter rows by answers to the selected "
                                                "question')]")
            assert len(el) > 0, "Customize question box NOT opened"

    def get_question_by_index(self, index=0):
        with allure.step('Get name of first question in Customize question mode'):
            return get_text_by_xpath(self.app.driver, "//div[@tabindex='%d']/div" % index)

    def change_customize_question(self, text, save=False):
        with allure.step('Change question in Customize question box'):
            find_element(self.app.driver, "//div[@tabindex='0']/div").click()
            find_element(self.app.driver, "//ul/li[contains(text(),'%s')]" % text).click()
            if save:
                self.app.navigation.click_link("Save")

    def get_number_of_answer_in_customize_question(self):
        with allure.step("Verify if question answer display in customize question box"):
            len_of_att = len(find_elements(self.app.driver, "//label[contains(text(), 'Select Answers')]/../div//input[@type='checkbox']"))
            return len_of_att

    def get_number_of_question_in_view_details(self, cml_tag):
        with allure.step("Get number of question in view details"):
            return len(find_elements(self.app.driver, "//label[contains(text(), '%s')]" % cml_tag))

    def answer_in_view_details(self, question_name):
        with allure.step("Get number of shown answer in view detail for question"):
            return len(find_elements(self.app.driver,
                                     "//span[contains(text(), '%s')]/parent::h4/../../following-sibling::div/div" %
                                     question_name))

    def close_view_details(self):
        with allure.step('Close view details'):
            self.app.driver.switch_to.default_content()
            self.app.navigation.click_link('Save and Close') if self.app.verification.wait_untill_text_present_on_the_page('Save and '
                                                                                                           'Close', 2) \
                else self.app.navigation.click_link('Close')
            time.sleep(2)
            assert not is_element(self.app.driver, "//label[contains(text(), 'Question 1')]"), "View details box not " \
                                                                                               "closed "

    def select_correct_answer(self, correct_answer):
        with allure.step('Select correct answer after reject'):
            el = find_elements(self.app.driver, "//label[contains(@for, '%s')]" % correct_answer)
            assert len(el) > 0, f"The answer {correct_answer} NOT present on View Detail"
            choose_answer = el[0].find_element('xpath',"./../../div/label").click()
            checked_answer = el[0].find_element('xpath',"./../../div/input")
            return checked_answer.get_attribute("checked")

    def filter_by_label(self, symbol_of_answer, text=None, change_answer=False):
        with allure.step('Filter units by one of answer'):
            if change_answer:
                self.change_customize_question(text)
            answers = find_elements(self.app.driver, "//label[contains(text(), 'Select Answers')]/../div//div//label")
            assert len(answers) > 0, "The answer in customize question modal is absent"
            for index in range(symbol_of_answer[0], symbol_of_answer[1]):
                answers[index].click()
            self.app.navigation.click_link('Save')

    def click_add_answer(self):
        with allure.step('Click on Add answer btn'):
            el_add_answer = find_elements(self.app.driver, '//a[contains(text(), "Add Answer")]')
            assert len(el_add_answer) > 0, "The add answer option is missing"
            el_add_answer[0].click()

    def add_answer(self, correct_answer):
        with allure.step('Add answer after reject select question'):
            self.click_add_answer()
            el_input = find_elements(self.app.driver, '//input[@placeholder = "Add Answer"]')
            assert len(el_input) > 0, "The input for add text/textarea absent"
            el_input[0].clear()
            el_input[0].send_keys(correct_answer)


    def get_selected_value(self, name_of_value):
        with allure.step(f"Get values named as {name_of_value}"):
            el_value = find_elements(self.app.driver, "//input[contains(@name, '%s')]" % name_of_value )
            assert len(el_value) > 0, "The selected value not present"
            return el_value[0].get_attribute('value')

    def remove_selected_value(self, question_label='Color', select=False):
        with allure.step("Remove selected values"):
            el_remove = find_elements(self.app.driver, "//input[contains(@id, 'custom-answer')]/../../../../following-sibling::a")
            name_of_question = find_element(self.app.driver, "//h4[contains(text(), '%s')]" % question_label)
            scroll_to_element(self.app.driver, name_of_question)
            if select:
                assert el_remove, "The button for delete selected element not present on page"
                el_remove[0].click()
            else:
                el_remove_text = find_elements(self.app.driver, "//div[@data-test-id='answer-1']/a")
                assert el_remove_text, "The button for delete selected element not present on page"
                el_remove_text[0].click()

    def get_label_of_question_view_details(self, text):
        with allure.step("Get name of question in View Details"):
            labels = find_elements(self.app.driver, "//label[contains(text(), '%s')]/following-sibling::h4/span" % text)
            assert len(labels) > 0, "On View Details isn't rendered the label of questions"
            return labels[0].text

    def get_number_of_ontology_view_details(self):
        with allure.step("Verify incorrect if ontology rendered on View Details "):
            frame = find_elements(self.app.driver, "//div[contains(@id, 'ia-iframe-cml')]")
            assert len(frame) > 0
            iframe = self.app.driver.find_element(By.XPATH, "//div[contains(@id, 'ia-iframe-cml')]/iframe")
            time.sleep(3)
            self.app.driver.switch_to.frame(iframe)
            side_bar_categories = find_elements(self.app.driver, "//div[contains(@class, 'categories')]//div[contains(@class, 'category-header')]")
            return len(side_bar_categories)

    def open_judgment_dropdown(self, button_name):
        with allure.step("Verify if judgment rendered on Detail View"):
            self.app.navigation.click_btn(button_name)
            list_of_contributors = find_elements(self.app.driver, "//ul[contains(@class, 'Dropdown-SelectList')]/li")
            assert len(list_of_contributors) > 0, "The aggregation of units aren't rendered"
            return list_of_contributors

    def select_judgment_from_drop_down(self, index=0):
        with allure.step('Select judgment in drop down list on Detail View'):
            self.app.verification.wait_untill_text_present_on_the_page('Review Judgments', 5)
            judgment_list_btn = find_elements(self.app.driver, "//button[contains(@class, 'SelectList-ListItem__button')]")
            assert judgment_list_btn, "The drop down list with judgment empty"
            judgment_list_btn[index].click()

    def get_side_bar_information_finalized_units(self):
        with allure.step("Get information on Side bar about Total finalized units"):
            side_bar = find_elements(self.app.driver, "//span[text()='Audited']/../../div")
            information = []
            assert len(side_bar) > 0, "Side bar doesn't rendered"
            _row_bar = find_elements(self.app.driver, "//span[text()='Audited']/parent::div")
            assert _row_bar, "The information about Audited units not present on side bar"
            _job_accuracy = find_elements(self.app.driver, "//span[text()='Total Job Accuracy']/parent::div")
            assert _job_accuracy, "The information about Job accuracy not present on side bar"
            time.sleep(2)
            _total_of_units = find_elements(self.app.driver, "//span[text()='Total Finalized Units']/parent::div")
            assert _total_of_units, "The information about Total units not present on side bar"
            information.append({"audited": split_text(_row_bar[len(_row_bar)-1].text),
                               "job_accuracy": split_text(_job_accuracy[0].text),
                                "total of units": split_text(_total_of_units[0].text)
                               })
            return information

    def mark_all_that_apply(self, apply_text='Too many annotations', cml_name='shape_without_ontology'):
        with allure.step("Audit question as incorrect and mark the reason"):
            mark_lists = find_elements(self.app.driver, "//label[contains(text(), 'Mark all that apply')]")
            assert len(mark_lists) > 0, "The Mark all that apply doesnt present on page"
            list_of_mark_checkboxes = mark_lists[0].find_elements('xpath',"./parent::div//div/input")
            assert len(list_of_mark_checkboxes) > 4, "Incorrect number of marked checkboxes"
            mark_checkbox = find_element(self.app.driver, "//label[contains(text(), '%s')]" % apply_text)
            mark_checkbox.click()

    def filters(self):
        with allure.step("Filters by range of confidence score/audit/unaudited"):
            el_filters = find_elements(self.app.driver, "//div[text()='Filters']/../..")
            assert len(el_filters) > 0, "The element Filters doesn't present on Audit Page"
            el_filters[0].click()

    def filter_audit_status(self, view='All'):
        with allure.step("Filter units by audit/unaudited"):
            self.filters()
            view_by = find_elements(self.app.driver, "//div[text()='All' or text()='Audited']/..")
            assert len(view_by) > 0, "The View By filtering absent on audit page"
            view_by[0].click()
            filter_by = find_element(self.app.driver, "//li/a[text()='%s']" % view)
            filter_by.click()

    def filter_confidence_score(self, from_confidence=0, to_confidence=100):
        self.filters()
        el_from = find_elements(self.app.driver, "//input[@name='confidenceFrom']")
        assert len(el_from) > 0, "Input field for From confidence score doesn't present"
        el_to = find_elements(self.app.driver, "//input[@name='confidenceTo']")
        assert len(el_to) > 0, "Input field for To confidence score doesn't present"
        el_from[0].send_keys(from_confidence)
        el_to[0].send_keys(to_confidence)

    def apply_filters(self):
        el_apply_filters = find_elements(self.app.driver, "//a[text() = 'Apply Filters']")
        assert len(el_apply_filters) > 0, "The button Apply Filters absent"
        el_apply_filters[0].click()

    def remove_filters(self):
        el_remove_filters = find_elements(self.app.driver, "//span[contains(text(),'Filters')]/following-sibling::button")
        assert len(el_remove_filters) > 0, "The button Remove Filters absent"
        el_remove_filters[0].click()

    def sorting_by(self, sort='Descending order'):
        with allure.step(f"Sort units by {sort}"):
            el_sort_by = find_elements(self.app.driver, "//a[contains(text(),'Sort By') or contains(text(),'Sorting')]")
            assert len(el_sort_by) > 0, "The Sort By filtering absent on audit page"
            el_sort_by[0].click()
            sorted_by = find_element(self.app.driver, "//li/a[contains(text(), '%s')]" % sort)
            sorted_by.click()

    def get_type_question_grid_view(self):
        with allure.step("Gen type of questions that displays on grid view"):
            el_type_questions = find_elements(self.app.driver, "//label[contains(text(), 'Question')]")
            assert len(el_type_questions) > 0, "Any question don't displays on grid view"
            list_el_type_question = [el_type_question.text for el_type_question in el_type_questions]
            return list_el_type_question

    def get_sda_source_data(self, att='src', att_value='api'):
        with allure.step("SDA data rendering on Grid View "):
            list_el_sda_data = []
            el_sda_data = find_elements(self.app.driver, "//img[contains(@%s, '%s')]" % (att, att_value))
            assert len(el_sda_data) > 0, "SDA data not found on Grid View"
            list_el_sda_data = [el_sda_data[index].get_attribute('src') for index in range(0, len(el_sda_data))]
            return list_el_sda_data

    def title_present_in_modal_box(self, title, modal_box='Setup', h3_title=True):
        with allure.step(f"Title {title} present on modal box {modal_box}"):
            titles_list = []
            h3_els = find_elements(self.app.driver, "//h3")
            if len(h3_els) > 0 and h3_title:
                titles_list = [h3_el.text for h3_el in h3_els]

            h4_els = find_elements(self.app.driver, "//h4")
            if len(h4_els) > 0 and not h3_title:
                titles_list = [h4_el.text for h4_el in h4_els]

            assert title in titles_list, f"The {title} Not present on {modal_box} modal box"
            return titles_list

    def customize_sampling_units(self, sampling_unit_amount=100):
        with allure.step(f'Configure the Job with sampling amount = {sampling_unit_amount}'):
            input_sampling_unit_amounts = find_elements(self.app.driver, "//input[@name='randomSamplingSize']")
            assert len(input_sampling_unit_amounts) > 0, "The input for Sampling units amount ABSENT"
            input_sampling_unit_amounts[0].send_keys(sampling_unit_amount)

    def get_side_bar_unit_information(self, row_name):
        with allure.step("Get information about sampling units from side bar"):
            sampled_information = []
            sampled_units = find_elements(self.app.driver, "//span[text()='%s']" % row_name[0])
            sampled_units_accuracy = find_elements(self.app.driver, "//span[text()='%s']" % row_name[2])
            sampled_units_audited = find_elements(self.app.driver, "//span[text()='%s']" % row_name[1])
            assert len(sampled_units_audited) > 0, "The information about Audited units Absent "
            assert len(sampled_units) > 0, "The information about sampled units Absent "
            assert len(sampled_units_accuracy) > 0, "The information about Sample Job Accuracy Absent "
            sampled_units_info_el = sampled_units[0].find_element('xpath',".//parent::div").text
            sampled_units_info_audited = sampled_units_audited[0].find_element('xpath',".//parent::div").text
            sampled_units_info_accuracy = sampled_units_accuracy[0].find_element('xpath',".//parent::div").text
            sampled_information.append({"audited": split_text(sampled_units_info_audited),
                                "job_accuracy": split_text(sampled_units_info_accuracy),
                                row_name[0].lower(): split_text(sampled_units_info_el)
                                })
            return sampled_information

    def select_taxonomy_item(self, taxonomy_item):
        with allure.step("Select taxonomy item after reject unit"):
            self.click_add_answer()
            select_el = find_elements(self.app.driver, "//span[text()='Select ...']")
            assert select_el, "Item for select new taxonomy element not found"
            select_el[0].click()
            time.sleep(1)
            list_new_taxonomy_item = find_elements(self.app.driver, "//ul/li[text()='%s']" % taxonomy_item)
            assert list_new_taxonomy_item, f"The taxonomy item {taxonomy_item} not present in list of available items"
            list_new_taxonomy_item[4].click()
            new_value_el = find_elements(self.app.driver, "//input[contains(@id, 'select-1')]")
            assert new_value_el, f"The input for new element NOT present"
            value = self.app.driver.execute_script('return arguments[0].value;', new_value_el[0])
            return value

    def open_review_annotation(self):
        with allure.step("Open cml audio annotation on Detail View"):
            button_elem = find_elements(self.app.driver, "//button/div[text()='Review Annotation']")
            assert button_elem, "Review annotation button absent on Detail View"
            button_elem[0].click()

    def audio_annotation_info_on_detail_view(self):
        with allure.step("Get information about audio annotation on Detail View"):
            audio_annotation_info = []
            audio_ontology_el = find_elements(self.app.driver, "//div[@class='b-OntologyCategory']")
            audio_segments = find_elements(self.app.driver, "//div[contains(@class, 'b-AudioSegment')]")

            audio_annotation_info.append({"audio_ontology": len(audio_ontology_el),
                                          "audio_segments": len(audio_segments)})
            return audio_annotation_info


    def edit_annotation_tool(self, name, btn_name, index=0, audio_annotation=False):
        with allure.step("Edit %s tool" % name):
            self.app.driver.switch_to.default_content()
            self.app.navigation.click_btn('click here')
            if not audio_annotation:
                self.get_number_of_ontology_view_details()
                self.open_judgment_dropdown(btn_name)
                self.select_judgment_from_drop_down(index)
                self.app.driver.switch_to.default_content()
            self.app.navigation.click_btn('click here')
            if audio_annotation:
                self.get_number_of_ontology_view_details()


    def get_shape_annotation_count(self, ontology_names):
        with allure.step("Get information about count of annotation for shapes in Detail View"):
            dict_of_count = {}
            for ontology_name in ontology_names:
                category_el = find_elements(self.app.driver,
                                            "//div[@title='%s']//div[@class='b-CategoryShapesItem']" % ontology_name)
                dict_of_count[ontology_name] = len(category_el)
            return dict_of_count

    def delete_audio_active_annotate_segment(self):
        active_segment = find_elements(self.app.driver, "//div[contains(@class,'b-AudioLayer--active')]//div[contains(@class, 'colorize')]")
        assert active_segment, "Any segment on page NO active"
        active_segment[0].click()
        self.app.audio_annotation.single_hotkey(Keys.DELETE)

    def get_image_transcription_category_count(self, ontology_names):
        with allure.step("Get information about count of annotation for image transcription in Detail View"):
            dict_of_count = {}
            for ontology_name in ontology_names:
                category_el = find_elements(self.app.driver,
                                            "//div[text()='%s']//span[@class='b-InstanceLimits__counter']" % ontology_name)
                dict_of_count[ontology_name] = int(category_el[0].text)
            return dict_of_count













