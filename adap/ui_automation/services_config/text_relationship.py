import time
import allure
import pytest
import logging
from lorem_text import lorem
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import unzip_file
from adap.ui_automation.utils.js_utils import element_to_the_middle, mouse_over_element
from adap.ui_automation.utils.pandas_utils import (
    collect_data_from_file,
    replace_column_in_csv,
)
from adap.ui_automation.utils.selenium_utils import find_elements

log = logging.getLogger(__name__)

CML = (
    '<cml:text_relationships label="Your annotation:" validates="required" source-data="{{my_annotations}}" '
    'name="text relationship"/>'
)
LONG_SPAN_CML = (
    '<cml:text_relationships label="Your annotation:" validates="required" source-data="{{annotations}}" '
    'name="text relationship"/>'
)


def change_text_column(file_name):
    paragraph_length = 5
    long_text = lorem.paragraphs(paragraph_length)

    file_data = collect_data_from_file(file_name)

    new_text = ["test{}".format(i) for i in range(file_data.shape[0] - 1)]
    new_text.append(long_text)
    replace_column_in_csv(file_name, "text", new_text)


def create_text_relationship_job(
    tmpdir, api_key, predifined_jobs, change_text=False, job_id=False
):
    # get test data
    payload = {"type": "full", "key": api_key}
    if not job_id:
        job_id = predifined_jobs["text_annotation"].get(pytest.env)["text_relationship"]
        updated_payload = {
            "key": api_key,
            "job": {
                "title": "Text Relationship",
                "instructions": "Updated",
                "cml": CML,
                "project_number": "PN000112",
            },
        }
    else:
        updated_payload = {
            "key": api_key,
            "job": {
                "title": "Test Long Span Text Relationship",
                "instructions": "Updated",
                "cml": LONG_SPAN_CML,
                "project_number": "PN000112",
            },
        }

    job = Builder(api_key)
    job.job_id = job_id

    # generate report
    resp1 = job.regenerate_report(payload=payload)
    resp1.assert_response_status(200)
    i = 1
    while i < 300:
        resp = job.generate_report(payload=payload)
        if resp.status_code == 200:
            open(tmpdir + "/full.zip", "wb").write(resp.content)
            break
        i = i + 1

    # handle the zip file
    unzip_file(tmpdir + "/full.zip")

    data_text_annotation = tmpdir + "/f%s.csv" % str(job.job_id)

    if change_text:
        change_text_column(str(data_text_annotation))

    job = Builder(api_key)

    job.create_job_with_csv(data_text_annotation)
    job.update_job(payload=updated_payload)
    return job.job_id


class TextRelationship:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def get_number_iframes_on_page(self):
        with allure.step("Get number of iframes on the page"):
            iframe = find_elements(
                self.app.driver, "//iframe[contains(@src, 'TextRelationships')]"
            )
            return len(iframe)

    def activate_iframe_by_index(self, index):
        with allure.step("Activate iframe by index"):
            time.sleep(3)
            els = find_elements(self.driver, "//div[@class='cml jsawesome']")
            total_elements = len(els)
            log.info(f"Total image elements: {total_elements}")
            assert total_elements > index, f"Images not found or image with index {index} not exist"
            first_image = els[index]
            element_to_the_middle(self.driver, first_image)
            iframe = first_image.find_element('xpath',".//iframe")
            self.iframe = iframe
            self.driver.switch_to.frame(iframe)
            time.sleep(2)

    def full_screen(self):
        with allure.step("Full screen"):
            find_elements(
                self.driver, "//button[contains(@class, 'b-Button__fullscreen')]"
            )[0].click()
            time.sleep(2)

    def find_word_with_label(self, value, label, word_index=0):
        with allure.step("Find word with label %s" % label):
            els = find_elements(
                self.driver,
                "//div[contains(@class, 'b-TextGridSpan b-SpansCanvas-RootSpan')]"
                "[.//div[@class='b-TextGridSpan-TextSpan__label' and text()='%s']]"
                "//div[contains(@class,'b-TextGridSpan__textToken') and text()='%s']/.."
                % (label, value),
            )

            assert len(els) > 0, "Word %s, label= %s has not been found" % (
                value,
                label,
            )

            if word_index:
                assert (
                    len(els) >= word_index + 1
                ), "Word %s, label= %s, index %s has not been found" % (
                    value,
                    label,
                    word_index,
                )

            return els[word_index]

    def find_all_words_with_label(self, label):
        with allure.step("Find all words with label %s" % label):
            els = find_elements(
                self.driver,
                "//div[contains(@class, 'b-TextGridSpan')][.//div["
                "@class='b-TextGridSpan-TextSpan__label' and text()='%s']]//div[contains("
                "@class,'b-TextGridSpan-TextToken')]" % label,
            )
            words = [e.text for e in els]
            return words

    def click_word(self, value, label, word_index=0):
        with allure.step("Click word %s" % value):
            el = self.find_word_with_label(value, label, word_index)
            el.click()
            time.sleep(2)

    def word_is_blocked(self, value, label, word_index=0):
        with allure.step("Word %s is blocked" % value):
            el = self.find_word_with_label(value, label, word_index)
            if len(
                el.find_elements('xpath',
                    ".//div[contains(@class, 'b-TextGridSpan-TextSpan__background')]"
                )
            ):
                return True
            return False

    def get_active_options(self):
        pass

    def select_relationship_type(self, name):
        with allure.step("Select relationship type for %s" % name):
            els = find_elements(
                self.app.driver,
                "//button[contains(@class, 'b-RelationshipTypesList-ListItem') and text()='%s']"
                % name.lower(),
            )
            assert len(els) > 0, "Relationship: %s has not been found" % name
            els[0].click()
            time.sleep(4)

    def get_available_relationships(self):
        pass

    def get_list_of_relationships(self):
        with allure.step("Get list of relationship"):
            rows = find_elements(
                self.driver, "//div[@class='b-RelationshipsList-Relationship']"
            )
            res = []
            for e in rows:
                value_from = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__fromSpanName']//span"
                ).text
                value_relation = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__relationshipTypeName']//span"
                ).text
                value_to = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__toSpanName']//span"
                ).text
                res.append(
                    {
                        "from": value_from,
                        "relation": value_relation.lower(),
                        "to": value_to,
                    }
                )
            return res

    def long_span_truncate(self, from_span, to_span):
        with allure.step("Long span truncate"):
            rows = find_elements(
                self.driver, "//div[@class='b-RelationshipsList-Relationship']"
            )
            for e in rows:
                value_from = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__fromSpanName']//span"
                )
                value_relation = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__relationshipTypeName']//span"
                )
                value_to = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__toSpanName']//span"
                )
                if value_from.text == from_span and value_to.text == to_span:
                    assert (
                        value_from.value_of_css_property("text-overflow") == "ellipsis"
                    )
                    assert (
                        value_relation.value_of_css_property("text-overflow")
                        == "ellipsis"
                    )
                    assert value_to.value_of_css_property("text-overflow") == "ellipsis"

    def get_headers(self, left, center, right):
        with allure.step("Get headers"):
            left_header = find_elements(
                self.driver,
                "//div[contains(@class, 'b-RelationshipsListHeader__header--left') and text() = '%s']"
                % left.lower(),
            )
            center_header = find_elements(
                self.driver,
                "//div[contains(@class, 'b-RelationshipsListHeader__header--center') and text() = '%s']"
                % center.lower(),
            )
            right_header = find_elements(
                self.driver,
                "//div[contains(@class, 'b-RelationshipsListHeader__header--right') and text() = '%s']"
                % right.lower(),
            )
            assert len(left_header) > 0, "left header %s not found" % left
            assert len(center_header) > 0, "center header %s not found" % center
            assert len(right_header) > 0, "right header %s not found" % right

    def search_text_relationship(self, from_span, to_span):
        with allure.step(
            "Search text relationship between %s and %s" % (from_span, to_span)
        ):
            rows = find_elements(
                self.driver, "//div[@class='b-RelationshipsList-Relationship']"
            )
            for e in rows:
                value_from = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__fromSpanName']//span"
                ).text
                value_to = e.find_element('xpath',
                    ".//div[@class='b-RelationshipsList-Relationship__toSpanName']//span"
                ).text
                if value_from == from_span and value_to == to_span:
                    print("we found span")
                    return e

    def edit_text_relationship(self, from_span, to_span, new_relationship_type):
        with allure.step(
            "Edit text relationship between %s and %s" % (from_span, to_span)
        ):
            el_relationship = self.search_text_relationship(from_span, to_span)
            mouse_over_element(self.driver, el_relationship)
            edit_btn = el_relationship.find_element('xpath',
                "//button[contains(@class, 'b-RelationshipActions__edit')]"
            )
            edit_btn.click()
            time.sleep(1)
            self.select_relationship_type(new_relationship_type)

    def delete_text_relationship(self, from_span, to_span):
        with allure.step(
            "Delete text relationship between %s and %s" % (from_span, to_span)
        ):
            el_relationship = self.search_text_relationship(from_span, to_span)
            mouse_over_element(self.driver, el_relationship)
            delete_btn = el_relationship.find_element('xpath',
                "//button[contains(@class, 'b-RelationshipActions__delete')]"
            )
            delete_btn.click()

    def add_text_relationship(self, first_word, second_word, relation_type):
        with allure.step(
            "Add text relationship for %s and %s" % (first_word, second_word)
        ):
            self.click_word(first_word["word"], first_word["label"])
            time.sleep(2)
            self.click_word(second_word["word"], second_word["label"])
            time.sleep(2)
            self.select_relationship_type(relation_type)
            time.sleep(2)

    def context_btn_is_displayed(self):
        with allure.step("Check context button is displayed"):
            btn = find_elements(
                self.driver, "//button[contains(@class,'b-ButtonContext')]"
            )
            if len(btn) > 0:
                return True
            return False

    def click_context_btn(self):
        with allure.step("Click context button"):
            btn = find_elements(
                self.driver, "//button[contains(@class,'b-ButtonContext')]"
            )
            assert len(btn), "Context btn is not displayed"
            btn[0].click()
            time.sleep(1)

    def context_btn_is_active(self):
        with allure.step("Check context button is active"):
            btn = find_elements(
                self.driver, "//button[contains(@class,'b-ButtonContext')]"
            )
            assert len(btn), "Context btn is not displayed"
            current_class = btn[0].get_attribute("class")
            if "b-Button--active" in current_class:
                return True
            return False

    def get_current_context(self):
        with allure.step("Get current context"):
            context = find_elements(
                self.driver, "//span[@class='b-Context__annotatedText']"
            )
            if len(context) == 0:
                context = find_elements(self.driver, "//p[@class='b-Context__text']")
            if len(context) == 0:
                return ""
            return context[0].text

    def context_scrollbar_is_visible(self):
        with allure.step("Check context scrollbar is visible"):
            el = self.driver.find_element('xpath',"//p[@class='b-Context__text']/..")
            return self.app.verification.scrollbar_is_visible(el)
