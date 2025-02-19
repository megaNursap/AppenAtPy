import time

import allure
import pytest

from adap.ui_automation.utils.page_element_utils import click_rebrand_popover
from adap.ui_automation.utils.selenium_utils import find_elements, click_by_action, move_to_element

TAXONOMY_ACTION = {
    "Edit": 0,
    "Delete": 1,
    "Upload": 2
}


class Taxonomy:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def open_taxonomy_page(self, taxonomy_job):
        with allure.step(f"Open quality audit page for {taxonomy_job}"):
            ipa_url = "https://client.{env}.cf3.us/jobs/{job}/taxonomy".format(env=pytest.env, job=taxonomy_job)
            self.app.navigation.open_page(ipa_url)
            click_rebrand_popover(self.app.driver)

    def get_taxonomy_nodes_name(self):
        with allure.step("Get taxonomy first category"):
            list_nodes = []
            nodes = find_elements(self.app.driver,
                                  "//div[contains(@class, 'Taxonomy__tool')]//div[contains(@class, 'title')]")
            assert len(nodes) > 0, 'The taxonomy nodes does not loaded'
            for node in nodes:
                list_nodes.append(node.text)
            return list_nodes

    def get_taxonomy_children_nodes_name(self, nodes_index=1):
        with allure.step("Get list of children taxonomy names"):
            list_names_of_node = []
            children_nodes = find_elements(self.app.driver,
                                           "//div[contains(@class, 'Taxonomy__tool')]//div[@class='b-column__container']")
            assert len(children_nodes) > 0, 'The taxonomy children nodes does not loaded'
            names_of_nodes = children_nodes[nodes_index].find_elements('xpath',".//div[contains(@class, 'title')]")
            for name in names_of_nodes:
                list_names_of_node.append(name.text)
            return list_names_of_node

    def get_error_msg(self):
        with allure.step('Find error message'):
            error_msg_list = []
            error_messages = find_elements(self.app.driver,
                                           "//div[@type='error']//div")
            for error_message in error_messages:
                strong_text = error_message.find_element('xpath',"./strong")
                error_msg_list.append(error_message.text)
                error_msg_list.append(strong_text.text)
            return ''.join(error_msg_list)

    def select_taxonomy_item(self, items=None, index_of_select=0, index_of_select_list=0):
        with allure.step('Select the taxonomy item'):
            for item in items:
                taxonomy_item = find_elements(self.app.driver, '//div[text()="%s"]' % item)
                assert len(taxonomy_item) > 0, f'The item {item} does not present'
                click_by_action(self.app.driver, taxonomy_item[0], 'b_title')
            self.app.verification.wait_untill_text_present_on_the_page('Select this category', 20)
            select_category = find_elements(self.app.driver, "//div[contains(text(), 'Select this category')]")
            select_category[index_of_select].click()
            select_list = find_elements(self.app.driver, "//span[contains(@class, 'SelectionsList')]")
            assert len(select_list) > 0, 'List of items not selected'
            return select_list[index_of_select_list].text

    def add_taxonomy(self):
        with allure.step("Add Taxonomy"):
            self.app.verification.wait_untill_text_present_on_the_page('Add Taxonomy', 10)
            el_add = find_elements(self.app.driver, '//a[text() = "Add Taxonomy"]')
            el_add[0].click()

    def input_name_of_taxonomy(self, name):
        with allure.step(f'Input name: {name} for taxonomy file'):
            self.app.verification.wait_untill_text_present_on_the_page('Edit Taxonomy', 10)
            el_input = find_elements(self.app.driver, '//input[@name="taxonomyTitle"]')

            assert len(el_input) > 0, "The input field dor Taxonomy name not found"
            el_input[0].send_keys(name)
            time.sleep(1)

    def upload_taxonomy(self, taxonomy_data):
        with allure.step("Upload Taxonomy file and save its"):
            self.app.job.data.upload_file(taxonomy_data)
            self.app.navigation.click_link("Save")
            self.app.verification.wait_until_text_disappear_on_the_page("Edit Taxonomy", 10)

    def action_taxonomy(self, name_of_taxonomy, action_name):
        with allure.step(f"Delete taxonomy file {name_of_taxonomy} "):
            el_taxonomy = find_elements(self.app.driver, "//div[contains(text(), '%s' )]" % name_of_taxonomy)
            assert len(el_taxonomy), f"{name_of_taxonomy} taxonomy not present on page"
            el_taxonomy[0].click()
            el_icons = el_taxonomy[0].find_elements('xpath',"./../following-sibling::div/a")
            assert len(el_icons) > 0, "The button for delete, edit and download absent"
            move_to_element(self.app.driver,el_icons[TAXONOMY_ACTION[action_name]] )
            # el_icons[TAXONOMY_ACTION[action_name]].click()

    def deselect_taxonomy_item(self):
        with allure.step('Deselect the taxonomy item'):
            deselect_category = find_elements(self.app.driver, "//div[contains(text(), 'Deselect this category')]")
            assert len(deselect_category) > 0, "Impossible DESELECT the selected category"
            deselect_category[0].click()

    def get_description_of_column(self):
        with allure.step('Retrieve the description of colum'):
            el_description = find_elements(self.app.driver, "//div[contains(@class, 'Taxonomy__tool')]//div[contains(@class, 'description')]")
            assert len(el_description) > 0, "The description doesn't present on the column"
            return el_description[0].text

    def taxonomy_title(self, title_num=0):
        el_title = find_elements(self.app.driver, "//h2[@class='category_name']")
        assert len(el_title) > 0, "Taxonomy title not present on page"
        return el_title[title_num].text

    def get_taxonomy_selected_list(self):
        with allure.step('Get list of selected taxonomy items'):
            list_of_taxonomy_items=[]
            selected_els = find_elements(self.app.driver, "//div[@class='b-SelectionsList']/div")
            if len(selected_els) > 0:
                for selected_el in selected_els:
                    list_of_taxonomy_items.append(selected_el.find_element('xpath',".//span").text)
            return list_of_taxonomy_items

    def taxonomy_answers(self, unit):
        with allure.step("Taxonomy answer for units on unit page"):
            list_of_answer = []
            answers_el = find_elements(self.app.driver, "//div[contains(@class, 'answer-value')]")
            assert len(answers_el) > 0, f"The answer on unit page for unit {unit} Not present"
            for answer_el in answers_el:
                list_of_answer.append(answer_el.text)
            return list_of_answer

    def delete_submission(self, delete=True):
        with allure.step("Submit that Taxonomy should be delete"):
            delete_title = find_elements(self.app.driver, "//h3[text()='Delete Taxonomy']")
            assert delete_title, 'Delete box with submission of delete taxonomy fail absent'
            if delete:
                self.app.navigation.click_link('Delete')
            else:
                self.app.navigation.click_link('Cancel')
