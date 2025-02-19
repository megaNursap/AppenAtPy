import random
import time
import pytest
import allure
from selenium.webdriver import ActionChains

from adap.ui_automation.utils.js_utils import mouse_over_element, scroll_to_page_bottom
from adap.ui_automation.utils.selenium_utils import find_element, find_elements, LOGGER, move_to_element


class Ontology:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.ontology_attribute = OntologyAttribute(self)

    def add_class(self, title, color=None, save=True):
        with allure.step(f"Add class [title:{title}, color:{color}]"):
            self.app.navigation.click_link("Add Class")
            find_element(self.driver, "//input[@name='classTitle']").send_keys(title)

            if color:
                self.select_color(color)
            self.app.navigation.click_link("Done")

            if save:
                self.app.navigation.click_link("Save")

    def select_color(self, color):
        with allure.step(f"Select color {color}"):
            find_element(
                self.driver, "//label[text()='Color']/following-sibling::div//div"
            ).click()
            time.sleep(1)
            el = find_elements(self.driver, "//div[@title='%s']" % color)
            assert len(el) > 0, f"Color {color} has not been found"
            el[0].click()
            time.sleep(1)

    # def get_class_dovuniq_attrribute_xpath(self,is_AT=False):
    #     xpath = "//div[@data-react-beautiful-dnd-draggable=0]"
    #     if is_AT:
    #         xpath = "//div[@data-rbd-drag-handle-draggable-id]"
    #     return xpath

    def expand_nested_ontology_by_name(self, class_name):
        el = find_elements(self.driver, "//div[text()='%s']/../.. " % class_name)

        assert len(el), f"Element '{class_name}' not found"
        expand_icon = el[0].find_element('xpath',".//*[local-name() = 'svg']")
        expand_icon.click()
        time.sleep(1)

    def manage_class_buttons(self, class_name, button_type="all", mode=None):
        # Button_type options selection: (-1) all; (0) button "edit"; (1) button "delete"
        button_id = -1
        if "edit" in button_type:
            button_id = 0
        elif "delete" in button_type:
            button_id = 1
        step = f"For class {class_name} select {button_type} button(s) "
        with allure.step(step):
            el_class = self.find_class_by_name(class_name, True, mode)
            el_class.click()
            buttons = el_class.find_elements('xpath',".//a//*[local-name() = 'svg']")
            if button_id < 0:
                return buttons
            return buttons[button_id]

    def delete_class(self, class_name, save=True, mode=None):
        with allure.step(f"{class_name}: click on button Delete"):
            del_button = self.manage_class_buttons(class_name, "delete", mode)
            del_button.click()
            time.sleep(1)
            if save:
                self.app.navigation.click_link("Save")

    def delete_class_icon_is_displayed(self, class_name):
        with allure.step(f"{class_name}: verify Delete icon is visible"):
            el_class = self.search_class_by_name(class_name)
            el_class.click()
            del_btn = el_class.find_elements('xpath',
                ".//div[contains(@class,'rebrand-OntologyTreeItem__delete')]//*[local-name() = 'svg']"
            )
            if len(del_btn):
                return True
            return False

    def click_edit_class(self, class_name, mode=None):
        with allure.step(f"{class_name} class: click on Edit button"):
            button = self.manage_class_buttons(class_name, "edit", mode)
            button.click()
            time.sleep(1)

    def edit_class(
        self, class_name, new_title=None, new_color=None, save=True, mode=None
    ):
        with allure.step(
            f"For {class_name} class: set new title {new_title} and color {new_color}"
        ):
            self.click_edit_class(class_name, mode)
            if new_color:
                self.select_color(new_color)
            if new_title:
                time.sleep(1)
                title_input = find_element(self.driver, "//input[@name='classTitle']")
                # add wait time to make clear work, found case it is not working as expected to clear the text
                time.sleep(1)
                title_input.clear()
                time.sleep(1)
                title_input.send_keys(new_title)
                time.sleep(1)
            self.app.navigation.click_link("Done")

            if save:
                self.app.navigation.click_link("Save")

    def search_class_by_name(self, class_name, found=True):
        with allure.step(f"Search class by name={class_name}"):

            class_el = find_elements(
                self.driver,
                f"//div[@data-react-beautiful-dnd-draggable][.//*[text()='{class_name}']]",
            )

            if found:
                assert len(class_el) > 0, f"Class {class_name} has not been found"
                return class_el[0]
            else:
                assert (
                    len(class_el) == 0
                ), f"Class {class_name} is found, it is not expected"

    def find_class_by_name(self, class_name, found=True, mode=None):
        with allure.step(f"Find ontology class {class_name} with mode {mode}"):
            xpath = (
                "//div[@data-react-beautiful-dnd-draggable][.//*[contains(text(),'%s')]]"
                % class_name
            )
            if mode == "AT":
                xpath = (
                    "//div[@data-rbd-drag-handle-draggable-id][.//*[contains(text(),'%s')]]"
                    % class_name
                )
            print(xpath)
            class_el = find_elements(self.driver, xpath)
            lng = len(class_el)
            print(f"DEBUG !!! {lng}")
            if found:
                assert lng > 0, f"Class {class_name} has not been found"
                return class_el[0]
            else:
                assert lng == 0, f"Class {class_name} is found, it is not expected"

    def open_class(self, class_name, mode=None):
        with allure.step(f"Open ontology class {class_name} with mode {mode}"):
            assert len(class_name) > 0, "Requested class name is empty"
            el_class = self.find_class_by_name(class_name, True, mode)
            el_class.click()
            print(f"Verify class {el_class} opened")
            buttons = self.manage_class_buttons(class_name, "all", mode)
            assert len(buttons) > 0, "Class buttons not found"
            count = 0
            while not self.is_class_open() and count < 2:
                self.click_edit_class(class_name, mode)
                time.sleep(1)
                count += 1

            return self.is_class_open()

    def is_class_open(self):
        with allure.step("Verify modal window Edit Class is open"):
            xpath = "//h3[contains(text(),'Edit Class')]"
            el = find_elements(self.driver, xpath)
            if len(el) == 0:
                LOGGER.info("Edit Class modal window is not open")
                return False
            return True

    def open_random_ontology_class(self, mode=None):
        with allure.step("Open random ontology class"):
            all_classes = self.get_all_group_labels(mode=mode)
            if len(all_classes) > 1:
                _class = random.choice(all_classes)
            else:
                _class = all_classes[0]
            self.open_class(_class, mode)
            return _class

    def upload_ontology(self, file_name, rebrand=True, verify_upload=True):
        with allure.step(f"Upload ontology {file_name}"):
            if rebrand:
                ontology_upload = find_elements(
                    self.driver, "//a[contains(., 'Upload')]//*[local-name() = 'svg']"
                )
                error_text = find_elements(self.app.driver, "//div[@type='error']//div")
                error_text_result = error_text[0].text if len(error_text) > 0 else 'unknown'
                assert len(ontology_upload) > 0, f"Upload file '{file_name}' failed with error: '{error_text_result}'"
                ontology_upload[0].click()
            else:
                self.app.navigation.click_link("Upload")
            self.app.job.data.upload_file(
                file_name, close_modal_window=False, wait_time=5
            )
            if verify_upload:
                errors = find_elements(self.app.driver, "//div[@type='error']//div")
                assert len(errors) == 0 , f"Unexpected error {errors[0]} displayed"

    def btn_add_relationship_click(self):
        btn_add_relationship_title = "Add Relationship"
        with allure.step(f"Click button {btn_add_relationship_title}"):
            btn_add_relationship_xpath = "//a[text()='%s']" % btn_add_relationship_title

            scroll_to_page_bottom(self.driver)
            btn = find_element(self.driver, btn_add_relationship_xpath)
            time.sleep(1)
            assert (
                btn.is_displayed()
            ), f"Button {btn_add_relationship_title} is not visible"
            btn.click()
            LOGGER.info(f"Click on button {btn_add_relationship_title}")
            return True

    def get_relationship_by_order(self, number):
        with allure.step(f"Select relationship by order: {number}"):
            relationship_blk_xpath = (
                "//a[text()='Add Relationship']//parent::div/../div/div"
                + "[%d]" % number
                if number > 0
                else ""
            )
            relationship_blk = find_element(self.driver, relationship_blk_xpath)
            assert relationship_blk.is_displayed(), "new relationship block not exist"
            return relationship_blk

    def set_relationship_name(self, current_relationship_blk, name, do_validate=False):
        with allure.step(
            f"Set relationship name {name} and " + "do"
            if do_validate
            else "do not " + "valiate"
        ):
            relationship_name_xpath = ".//input[@name='relationshipTypeName']"
            fld_name = current_relationship_blk.find_element('xpath',
                relationship_name_xpath
            )
            assert (
                fld_name.is_displayed() and fld_name.is_enabled()
            ), "field Relationship Name not exist"
            fld_name.send_keys(name)
            if do_validate:
                current_value = current_relationship_blk.find_element('xpath',
                    relationship_name_xpath
                ).get_attribute("value")
                LOGGER.debug(f"Current fld value is {current_value}")
                assert current_value == name, f"Relationship name '{name}' not set"

    def set_relationship_connect_to(
        self, current_relationship_blk, connect_to, do_validate=False
    ):
        with allure.step(f"Set relatinship connect to: {connect_to}"):
            btn_select_connect_to_title = "Select Class"
            btn_select_connect_to_xpath = (
                f".//span[text()='{btn_select_connect_to_title}']"
            )
            lst_outer_xpath = (
                f".//*[text()='{connect_to}']/../../following-sibling::div"
            )
            target_option_xpath = f".//*[text()='{connect_to}']"

            btn_connect_to = current_relationship_blk.find_element('xpath',
                btn_select_connect_to_xpath
            )
            assert (
                btn_connect_to.is_displayed()
            ), f"button {btn_select_connect_to_title} not exist"
            scroll_to_page_bottom(self.driver)
            btn_connect_to.click()
            LOGGER.info(f"Select option {connect_to} from list")
            lst_outer = current_relationship_blk.find_element('xpath',lst_outer_xpath)
            action = ActionChains(self.driver)
            action.move_to_element(lst_outer).pause(6).perform()
            req_sel = current_relationship_blk.find_element('xpath',
                target_option_xpath
            )
            req_sel.click()

            if do_validate:
                current_connect_to = current_relationship_blk.find_element('xpath',
                    ".//input[@name='relationshipTypeToClassName']/.././div[1]//div[1]"
                )
                current_value = current_connect_to.get_attribute(
                    "innerHTML"
                ).splitlines()[0]
                assert (
                    current_value == connect_to
                ), f"Relationship not set to {connect_to}"

    def add_relationship(self, name, connect_to, save=True):
        with allure.step(
            f"Add relationship with name:'{name}' connected to:'{connect_to}'"
        ):
            relationship_blk_xpath = (
                "//a[text()='Add Relationship']//parent::div/../div/div"
            )
            LOGGER.info("Collect existing relationship blocks")
            old_relation_blks = find_elements(self.driver, relationship_blk_xpath)
            old_relation_blks_total = len(old_relation_blks)
            LOGGER.info(f"Total existing relationship blocks:{old_relation_blks_total}")

            if self.btn_add_relationship_click():
                current_relat_blks = find_elements(self.driver, relationship_blk_xpath)
                total = len(current_relat_blks)
                assert (
                    total - old_relation_blks_total == 1
                ), "new relationship block does not appear"
                current_block = current_relat_blks[total - 1]
                self.set_relationship_name(current_block, name, True)
                self.set_relationship_connect_to(current_block, connect_to, True)
                time.sleep(1)

            self.app.navigation.click_link("Done")
            if save:
                self.app.navigation.click_link("Save")

    def get_relationship_by_name(self, name, do_validate=False):
        with allure.step(f"Get relationship by name='{name}'"):
            relationship_blk_xpath = (
                "//a[text()='Add Relationship']//parent::div/../div/div"
            )
            time.sleep(2)
            relationships = find_elements(
                self.driver,
                f"{relationship_blk_xpath}[.//input[@name='relationshipTypeName' and @value='{name}']]",
            )
            num = len(relationships)
            if do_validate:
                assert num, f"Not found relationship with name='{name}'"
            if num:
                return relationships[0]
            return False

    def find_relationship_by_name(self, name):
        with allure.step(f"Find existing relationship by name='{name}'"):
            relationship = self.get_relationship_by_name(name)
            if not relationship:
                return {"name": "Not Found"}

            connect = relationship.find_element('xpath',
                ".//input[@name='relationshipTypeToClassName']"
            )
            connect_name = connect.get_attribute("value")
            LOGGER.debug(f"Current connect_name: {connect_name}")
            return {"name": name, "connect_to": connect_name}

    def edit_relationship(self, name, update_name, update_connect, save=True):
        with allure.step(
            f"Edit relationship with name='{name}' to update_name='{update_name}'"
        ):
            # edit name
            name = find_elements(
                self.driver,
                "//input[@name='relationshipTypeName' and @value='%s']" % name,
            )
            LOGGER.info("ke fo is: %d" % len(name))
            assert len(name), f"Relationship {name} has not been found"
            name[0].clear()
            name[0].send_keys(update_name)
            # validate name
            relationship = self.get_relationship_by_name(update_name, True)
            new_connect_btn = relationship.find_element('xpath',
                "//input[@name='relationshipTypeToClassName']/.././div[1]"
            )
            new_connect_btn.click()
            # edit connect_to
            lst_outer = relationship.find_element('xpath',
                "//input[@name='relationshipTypeToClassName']/.././div[2]"
            )
            action = ActionChains(self.driver)
            action.move_to_element(lst_outer).pause(6).perform()
            target_option_xpath = f".//li[text()='{update_connect}']"
            req_sel = relationship.find_element('xpath',target_option_xpath)
            req_sel.click()
            # validate connect_to
            current_connect_to = (
                relationship.find_element('xpath',
                    ".//input[@name='relationshipTypeToClassName']/.././div[1]//div[1]"
                )
                .get_attribute("innerHTML")
                .splitlines()[0]
            )
            assert (
                current_connect_to == update_connect
            ), f"Relationship not set to {update_connect}"

            self.app.navigation.click_link("Done")

            if save:
                self.app.navigation.click_link("Save")

    def delete_relationship(self, name, save=True, do_validate=False):
        with allure.step(f"Delete relationship name='{name}'"):
            del_button_xpath = f"//*[@data-test-id='rte-list']//div[.//input[@value='{name}']]/a"
            del_btn = find_elements(self.driver, del_button_xpath)
            assert len(del_btn) > 0, "Delete button not found"
            del_btn[0].click()

            if do_validate:
                assert not self.get_relationship_by_name(
                    name
                ), f"Relationship name='{name}' not deleted"
            # # selenium.common.exceptions.ElementNotInteractable Exception
            self.app.navigation.click_link("Done")

            if save:
                self.app.navigation.click_link("Save")

    def find_all_relationships_for_class(self, class_name):
        with allure.step("Find all relatinships for class"):
            pass

    def get_all_group_labels(self, mode=None):
        with allure.step("Select all group labels"):
            xpath = "//a[text()='Design']/../../../..//div[@data-react-beautiful-dnd-droppable='0']/div/div/div[4]/div"

            el = find_elements(self.driver, xpath)
            total_classes = len(el)
            assert total_classes > 0, f"found {total_classes}"

            class_name = [e.text for e in el]
            LOGGER.debug("Print list of classes")
            for c in class_name:
                LOGGER.debug(f"Class name: {c}")
            return class_name

    def get_all_group_audio_tx_labels(self):
        with allure.step("Select all group labels"):
            xpath = "//span[@data-test-id='labelGroups-count']"

            total_classes = find_elements(self.driver, xpath)
            assert total_classes, f"found {total_classes}"

            return total_classes[0].text

    def update_class_description(self, value):
        with allure.step(f"Update class description with {value}"):
            el = self.driver.find_element('xpath',"//div[@role='textbox']")
            el.send_keys(value)

    def get_class_description(self, value):
        with allure.step(f"Get class description {value}"):
            el = self.driver.find_element('xpath',
                "//div[@role='textbox']//span[text()]"
            )
            return el.text

    #     class events
    def get_current_class_events(self):
        with allure.step("Get current class events"):
            _list_of_events = []
            events = find_elements(
                self.driver,
                "//h4[text()='Events']/../..//div[contains(@style, 'background-color')]"
            )
            if len(events) == 0:
                return _list_of_events
            assert (
                len(events) > 0
            ), "no events blocks found or event block locator is invalid"
            LOGGER.info(events)
            for e in events:
                _name = e.find_element('xpath',"../following-sibling::div/div").text
                _description = e.find_element('xpath',"../following-sibling::div[2]/div").text
                _list_of_events.append({"name": _name, "description": _description})
            time.sleep(3)
            return _list_of_events

    def add_event(self, name, description=None, action=None):
        with allure.step(
            f"Add event {name}, description {description}, action {action}"
        ):
            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            self.app.navigation.click_link("Add Event")
            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            new_name = find_elements(
                self.driver, "//label[text()='Events']/..//input[@name='name']"
            )
            assert len(new_name) > 0, "Event Input field name not found"
            new_name[-1].send_keys(name)

            if description:
                new_description = find_elements(
                    self.driver,
                    "//label[text()='Events']/..//input[@name='description']",
                )
                assert (
                    len(new_description) > 0
                ), "Event Input field Description not found"
                new_description[-1].send_keys(description)

            if action:
                self.app.navigation.click_link(action)

    def find_class_event_by_name(self, name):
        with allure.step(f"Find class event {name}"):
            time.sleep(4)
            event = find_elements(
                self.driver,
                "//div[text()='%s']" % name
            )
            return event

    def edit_class_event(
        self, name, update_name=None, update_description=None, action=None
    ):
        with allure.step(
            f"Update class event: {name} with name {update_name} and description {update_description}"
        ):
            # find event by name
            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            event = self.find_class_event_by_name(name)
            assert len(event) > 0, f"Event {name} has not been found"
            edit_button = event[0].find_elements('xpath',"./../../..//a[contains(@href, 'ontology_manager')]")
            assert len(edit_button) > 0, f"Edit bth not found for event {name} "
            move_to_element(self.driver, edit_button[0])

            if update_name:
                _name = find_element(self.driver, "//input[@name='entityTitle']")
                _name.clear()
                _name.send_keys(update_name)

            if update_description:
                _name = find_elements(self.driver, "//div[@class='DraftEditor-editorContainer']//span/span")
                _name_des = find_elements(
                    self.driver,
                    "//div[@class='DraftEditor-editorContainer']//span",
                )
                if len(_name) > 0:
                    _name_des[0].clear()

                _name_des[-1].send_keys(update_name)

            if action:
                self.app.navigation.click_link(action)

    def delete_event_by_name(self, name, action=None):
        with allure.step(f"Delete event by name: {name}"):
            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            event = self.find_class_event_by_name(name)
            assert len(event) > 0, f"Event {name} has not been found"

            mouse_over_element(self.driver, event[0])
            time.sleep(2)
            del_btn = event[0].find_elements('xpath',"./../../..//a[contains(@href, 'ontology_manager')]")
            assert len(del_btn) > 0, f"Delete bth not found for event {name} "
            del_btn[1].click()
            time.sleep(3)

            if action:
                self.app.navigation.click_link(action)

    # TODO method is not working - fix later
    # def drag_and_drop_event(self, first_event, second_event):
    #
    #     time.sleep(2)
    #     scroll_to_page_bottom(self.driver)
    #     time.sleep(4)
    #     event1 = self.find_class_event_by_name(first_event)[0].find_element('xpath',
    #         "./..//div[@class='b-EntitiesList__dragButton']"
    #     )
    #     event2 = self.find_class_event_by_name(second_event)[0]
    #
    #     add_btn = find_element(self.driver, "//button[text()='Add Event']")
    #     # mouse_over_element(self.driver, add_event_btn)
    #     # time.sleep(2)
    #
    #     scroll_to_page_bottom(self.driver)
    #     # self.driver.execute_script("scrollIntoView();", add_event_btn)
    #
    #     time.sleep(4)
    #
    #     action = ActionChains(self.driver)
    #     # action.click_and_hold(event1).pause(2).move_to_element(event2).release().perform()
    #     # action.drag_and_drop(event1, event2).release().perform()
    #     action.move_to_element(event1).click_and_hold(event1).pause(4).move_to_element(add_btn).release(
    #         add_btn
    #     ).perform()
    #     # time.sleep(4)
    #     #
    #     event1 = self.find_class_event_by_name(first_event)[0].find_element('xpath',
    #         "./..//div[@class='b-EntitiesList__dragButton']"
    #     )
    #     #
    #     action.move_to_element(event1).click_and_hold(event1).pause(4).move_to_element(event2).release(event2).perform()
    #
    #     # action.click_and_hold(event1).pause(4).move_to_element_with_offset(event2, 50,
    #     #                                                                   100).release().perform()
    #     time.sleep(3)

    def add_span(self, name, description=None, action=None):
        with allure.step(f"Add span with {name} and description {description}"):
            popup_alert = self.driver.find_elements('xpath',
                "//div[contains(@class, 'rebrand-FlashAlert')]//*[local-name() = 'svg']"
            )
            if len(popup_alert) > 0:
                popup_alert[0].click()
            time.sleep(2)

            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            self.app.navigation.click_btn("Add Span")
            # scroll_to_page_bottom(self.driver)
            time.sleep(1)
            new_name = find_elements(
                self.driver, "//input[@name='entityTitle']"
            )
            assert len(new_name) > 0, "Span input field not found"
            new_name[-1].send_keys(name)
            if description:
                new_description = find_elements(
                    self.driver,
                    "//div[@class='DraftEditor-editorContainer']//span",
                )
                assert (
                    len(new_description) > 0
                ), "Span Description input field not found"
                new_description[-1].send_keys(description)
            if action:
                self.app.navigation.click_link(action)

    def get_current_class_spans(self):
        with allure.step("Get current class spans"):
            _list_of_spans = []
            spans = find_elements(
                self.driver,
                "//h4[text()='Spans']/../..//div[contains(@style, 'background-color')]"
            )
            if len(spans) == 0:
                return _list_of_spans
            assert (
                    len(spans) > 0
            ), "no events blocks found or event block locator is invalid"
            LOGGER.info(spans)
            for s in spans:
                _name = s.find_element('xpath',"../following-sibling::div/div").text
                _description = s.find_element('xpath',"../following-sibling::div[2]/div").text
                _list_of_spans.append({"name": _name, "description": _description})
            time.sleep(3)
            return _list_of_spans

    def find_class_span_by_name(self, name):
        with allure.step(f"Find class span by name {name}"):
            time.sleep(4)
            span = find_elements(
                self.driver,
                "//div[text()='%s']" % name
            )
            return span

    def edit_class_span(
        self, name, update_name=None, update_description=None, action=None
    ):
        with allure.step(f"Edit event by name: {name}"):
            # find span by name
            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            event = self.find_class_span_by_name(name)
            assert len(event) > 0, f"Span {name} has not been found"
            edit_button = event[0].find_elements('xpath',"./../../..//a[contains(@href, 'ontology_manager')]")
            assert len(edit_button) > 0, f"Edit bth not found for span {name} "
            move_to_element(self.driver, edit_button[0])

            if update_name:
                _name = find_element(self.driver, "//input[@name='entityTitle']")
                _name.clear()
                _name.send_keys(update_name)

            if update_description:
                _name = find_elements(self.driver, "//div[@class='DraftEditor-editorContainer']//span/span")
                _name_des = find_elements(
                    self.driver,
                    "//div[@class='DraftEditor-editorContainer']//span",
                )
                if len(_name) > 0:
                    _name_des[0].clear()

                _name_des[-1].send_keys(update_name)

            if action:
                self.app.navigation.click_link(action)

    def delete_span_by_name(self, name, action=None):
        with allure.step(f"Delete span by name: {name}"):
            scroll_to_page_bottom(self.driver)
            time.sleep(1)
            span = self.find_class_span_by_name(name)
            assert len(span) > 0, f"Span {name} has not been found"

            mouse_over_element(self.driver, span[0])
            time.sleep(2)
            del_btn = span[0].find_elements('xpath',"./../../..//a[contains(@href, 'ontology_manager')]")
            assert len(del_btn) > 0, f"Delete bth not found for span {name} "
            del_btn[1].click()
            time.sleep(3)

            if action:
                self.app.navigation.click_link(action)

    def add_tag(self, tag_name, name, description=None, action='Done'):
        with allure.step(f"Add {tag_name} tag for ontology"):
            self.app.navigation.click_btn(f"Add {tag_name}")
            time.sleep(1)
            new_name = find_elements(
                self.driver, "//input[@name='entityTitle']"
            )
            assert len(new_name) > 0, f"{tag_name} input field not found"
            new_name[-1].send_keys(name)
            if description:
                new_description = find_elements(
                    self.driver,
                    "//div[@class='DraftEditor-editorContainer']//span",
                )
                assert (
                        len(new_description) > 0
                ), f"{tag_name} Description input field not found"
                new_description[-1].send_keys(description)
            if action:
                self.app.navigation.click_link(action)


class OntologyAttribute:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def select_question_type_from_dropdown(self, question_type):
        with allure.step("Choose question type from drop down"):
            drop_down_button = find_elements(self.driver, "//*[text()='Add Questions']")
            assert len(drop_down_button) > 0, "Dropdown button not found"
            drop_down_button[0].click()
            item = find_elements(
                self.app.driver, "//ul//li[text()='%s']" % question_type
            )
            assert len(item) > 0, f"Question with type {question_type} not found"
            item[0].click()
            time.sleep(2)

    def manage_single_checkbox_or_textbox_question(self, question_type, question_text):
        with allure.step("Add single checkbox or text box question"):
            if pytest.env == "fed":
                el = find_elements(
                    self.driver,
                    f"//a[(normalize-space(text())='{question_type}')]/../../..",
                )
            else:
                el = find_elements(
                    self.driver,
                    f"//span[(normalize-space(text())='{question_type}')]/../..",
                )
            LOGGER.debug(f"single len is: {len(el)}", )
            textbox = el[0].find_element('xpath',".//input[@name='Question Text']")
            textbox.clear()
            time.sleep(1)
            textbox.send_keys(question_text)

    def copy_question(self, question_type):
        with allure.step("Copy question"):
            el = find_elements(self.driver, f"//span[text()='{question_type}']/../..")
            copy_icon = el[0].find_elements('xpath',".//a")
            copy_icon[0].click()
            time.sleep(1)

    def delete_question(self, question_type):
        with allure.step(f"Delete question for question type {question_type}"):
            el = find_elements(self.driver, f"//span[text()='{question_type}']/../..")
            delete_icon = el[0].find_elements('xpath',".//a")
            delete_icon[1].click()
            time.sleep(1)

    def delete_all_questions(self):
        with allure.step("Delete all questions"):
            el = find_elements(
                self.driver,
                "//div[contains(@class, 'rebrand-Accordion__body')]//a[contains(@class, 'rebrand-Button--leftMargin')]",
            )
            for i in range(0, len(el)):
                el[i].click()
            time.sleep(1)

    def get_number_of_questions(self, question_type):
        with allure.step("Get number of question for question type %s" % question_type):
            el = find_elements(
                self.driver,
                "//h2[.//span[text()='%s']]" % question_type,
            )
            return len(el)

    def add_checkbox_group_or_multiple_choice_or_pulldown_menu_question(
        self, question_type, question_text, label0, label1, value0=None, value1=None
    ):
        with allure.step(
            "Add checkbox group or multiple choice or pulldown menu question"
        ):
            if pytest.env == "fed":
                el = find_elements(
                    self.driver,
                    "//a[(normalize-space(text())='%s')]/../../.." % question_type,
                )
                labels = find_elements(
                    self.driver,
                    "//a[(normalize-space(text())='%s')]/../../..//input[@name='Label']"
                    % question_type,
                )
                values = find_elements(
                    self.driver,
                    "//a[(normalize-space(text())='%s')]/../../..//input[@name='Value']"
                    % question_type,
                )
            else:
                el = find_elements(
                    self.driver,
                    "//span[(normalize-space(text())='%s')]/../.." % question_type,
                )
                labels = find_elements(
                    self.driver,
                    "//span[(normalize-space(text())='%s')]/../..//input[@name='Label']"
                    % question_type,
                )
                values = find_elements(
                    self.driver,
                    "//span[(normalize-space(text())='%s')]/../..//input[@name='Value']"
                    % question_type,
                )
            textbox = el[0].find_element('xpath',".//input[@name='Question Text']")
            textbox.send_keys(question_text)
            labels[0].send_keys(label0)
            if value0:
                values[0].clear()
                values[0].send_keys(value0)
            labels[1].send_keys(label1)
            if value1:
                values[1].clear()
                values[1].send_keys(value1)

    def add_option(self, question_type, more_label, more_value=None):
        with allure.step("Add more options"):
            if pytest.env == "fed":
                more_option_button = find_elements(
                    self.driver,
                    "//a[text()='%s']/../../..//a[text()='Add Option']" % question_type,
                )
                more_option_button[0].click()
                labels = find_elements(
                    self.driver,
                    "//a[text()='%s']/../../..//input[@name='Label']" % question_type,
                )
                values = find_elements(
                    self.driver,
                    "//a[text()='%s']/../../..//input[@name='Value']" % question_type,
                )
            else:
                more_option_button = find_elements(
                    self.driver,
                    "//span[text()='%s']/../..//a[text()='Add Option']" % question_type,
                )
                more_option_button[0].click()
                labels = find_elements(
                    self.driver,
                    "//span[text()='%s']/../..//input[@name='Label']" % question_type,
                )
                values = find_elements(
                    self.driver,
                    "//span[text()='%s']/../..//input[@name='Value']" % question_type,
                )
            labels[-1].send_keys(more_label)
            if more_value:
                values[-1].clear()
                values[-1].send_keys(more_value)

    def add_tips_and_hints_in_additional_options(
        self, question_type, tips, results_header=None
    ):
        with allure.step("Add tips and hints"):
            if pytest.env == "fed":
                el = find_elements(
                    self.driver, "//a[text()='%s']/../../.." % question_type
                )
            else:
                el = find_elements(
                    self.driver, "//span[text()='%s']/../.." % question_type
                )
            additional_option_link = el[0].find_element('xpath',
                ".//span[text()='Additional Options']"
            )
            additional_option_link.click()
            tips_textbox = el[0].find_element('xpath',".//input[@name='Tips/Hints']")
            tips_textbox.send_keys(tips)
            if results_header:
                result_header_textbox = el[0].find_element('xpath',
                    ".//input[@name='Results Header']"
                )
                result_header_textbox.clear()
                result_header_textbox.send_keys(results_header)

    def click_edit_ontology_attribute(self):
        with allure.step("Click edit ontology attribute"):
            edit = find_elements(
                self.app.driver,
                "//span[text()='Ontology Attributes']/..//a[text()='Edit']",
            )
            assert len(edit) > 0, "Edit ontology attributes has not been found"
            edit[0].click()

