import re
import time

import allure
from selenium.webdriver import ActionChains, Keys

from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.utils.js_utils import scroll_to_element
from adap.ui_automation.utils.selenium_utils import find_elements, move_to_element, double_click_on_element, \
    double_click_element_by_xpath


class AudioTranscriptionBetaElement:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def get_segment_list(self):
        with allure.step("Get all segment list"):
            segment_el = find_elements(self.driver,
                                       "//div[@class='b-SegmentsList__listWrapperInner']/div")
            assert segment_el, "Segment list NOT present for unit"
            return segment_el

    def get_work_area(self):
        with allure.step("Find work area"):
            work_area_el = find_elements(self.app.driver, "//div[@class='b-WorkArea']")
            assert work_area_el, "Work area NOT opened or absent"
            return work_area_el

    def text_area(self):
        with allure.step("Find the text area of segment"):
            text_area_els = find_elements(self.driver,
                                                   "//div[@class='DraftEditor-editorContainer']")
            return text_area_els
    def text_area_of_segment(self):
        with allure.step("Find text area of segment"):
            text_area_el = text_el = find_elements(self.driver,
                                                   "//div[@class='DraftEditor-editorContainer']//span[@data-offset-key]")
            assert text_el, "Area for input text absent"
            return text_area_el

    def listen_to_block(self):
        with allure.step("Find listen-to block"):
            listen_to_block_el = find_elements(self.driver, "//div[@class='b-ListenToBlock__main']")
            assert listen_to_block_el, "Listen to blocks ABSENT on page"
            return listen_to_block_el

    def get_work_panel(self):
        with allure.step("Find work panel with label"):
            work_panel_el = find_elements(self.driver, "//div[@class='b-WorkPanel']")
            return work_panel_el

    def get_label_list_element(self):
        label_list_els = find_elements(self.driver, "//div[contains(@class,'b-ActiveSegment__labelsList')]")
        return label_list_els

    def get_waveform_el(self):
        with allure.step("Find waveform element"):
            waveform_els = find_elements(self.driver, "//div[@class='b-SegmentAudioCanvas__container']")
            assert waveform_els, "Waveform Not present for unit"
            return waveform_els

    def get_transcription_area(self):
        with allure.step("Find transcription area element"):
            transcription_area_els = find_elements(self.driver,"//div[contains(@class, 'b-ActiveSegment__transcription')]")
            assert transcription_area_els, "Transcription area Not present for units"
            return transcription_area_els

    def get_interval_lines(self):
        with allure.step("Find interval lines ob waveform"):
            interval_lines = find_elements(self.driver, "//div[@class='b-IntervalLines']/canvas")
            assert interval_lines, "The element interval lines Absent"
            return interval_lines

    def get_big_waveform(self):
        with allure.step("Find big waveform element"):
            big_waveforms = find_elements(self.driver, "//div[@class='b-Layout__waveform']")
            assert big_waveforms, "Big waveform NOT rendering on page"
            return big_waveforms

class AudioTranscriptionBETA(Annotation):
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.audio_transcription_beta_element = AudioTranscriptionBetaElement(self)
        self.action = ActionChains(self.driver)

    def move_to_word(self, word_in_text, index=0):
        with allure.step(f"Place cursor after word {word_in_text}"):
            segment_text = self.grab_text_from_text_area()
            start_index = segment_text.find(word_in_text)
            b1 = self.audio_transcription_beta_element.text_area_of_segment()[index]

            b1.send_keys('')

            self.action.send_keys(Keys.ARROW_RIGHT).send_keys(Keys.ARROW_DOWN).perform()
            for i in range(0, len(segment_text) - start_index):
                self.action.send_keys(Keys.ARROW_LEFT).perform()

    def get_segment_info(self):
        with allure.step("Grab info from segments"):
            segment_dict = {}
            for segment_el in self.audio_transcription_beta_element.get_segment_list():
                segment_index = segment_el.find_element('xpath',"./div[@class='b-SegmentsList__listItemIndex']")
                segment_time = segment_el.find_element('xpath',"./div[@class='b-SegmentsList__listItemTime']")
                segment_dict[segment_index.text] = segment_time.text
            return segment_dict

    def click_on_segment(self, index=0, transcribe_all_segment=False):
        with allure.step(f"Choose segment by index {index + 1}"):
            specific_segment_el = self.audio_transcription_beta_element.get_segment_list()[
                index].find_element('xpath',
                ".//div[@class='b-SegmentsList__listItemTime']")
            if transcribe_all_segment:
                double_click_on_element(self.driver, specific_segment_el)
            else:
                specific_segment_el.click()

    def get_work_area_listen_to(self, index=0):
        with allure.step("Get listen to work area"):
            listen_to_area_info = []
            listen_to_area = self.audio_transcription_beta_element.get_work_area()[index].find_elements('xpath',
                ".//div[@class='b-ListenToBlock']")
            assert listen_to_area, "Listen to panel on work area absent"
            for _listen_to_area in listen_to_area:
                listen_to_time = _listen_to_area.find_elements('xpath',".//div[@class='b-ListenToBlock__main']/div")
                listen_to_progress = _listen_to_area.find_elements('xpath',
                    ".//span[contains(@class,'not-listened-enough')]")
                listen_to_area_info.append({
                    "listen_to_time": listen_to_time[0].text,
                    "listen_to_progress": listen_to_progress[0].text
                })
            return listen_to_area_info

    def get_header_waveform_info(self, transcription=True):
        with allure.step("Get information from header for active segment"):
            header_info_dict = {}
            header_els = find_elements(self.driver, "//div[@class='b-ActiveSegment__header']")
            assert header_els, "Waveform header absent"
            for header_el in header_els:
                _segment_name = header_el.find_element('xpath',"./div[@class='b-ActiveSegment__title']")
                _segment_actions = header_el.find_elements('xpath',"./div[@class='b-ActiveSegment__actions']/button")
                _segment_event = header_el.find_elements('xpath',"./div[@class='b-ActiveSegment__actions']/div/button")
                header_info_dict['segment_name'] = _segment_name.text
                header_info_dict['segment_action'] = [segment_btn.get_attribute('class').replace('b-Button', '') for
                                                      segment_btn in _segment_actions]
                if transcription:
                    header_info_dict['segment_event'] = _segment_event[0].get_attribute('class').replace('b-Button',
                                                                                                         '').split(" ")
                else:
                    header_info_dict['segment_event'] = _segment_event
            return header_info_dict

    def get_waveform_info(self):
        with allure.step("Grab info from baby waveform"):
            waveform_info_dict = {}
            waveform_els = self.audio_transcription_beta_element.get_waveform_el()
            for waveform_el in waveform_els:
                cursor = waveform_el.find_element('xpath',".//div[contains(@class,'b-PlaybackCursor')]")
                audio_cursor_position = waveform_el.find_element('xpath',
                    ".//div[@class='b-PlaybackCursor__duration']")
                audio_duration = waveform_el.find_element('xpath',".//div[@class='b-AudioWaveform__duration']")
                waveform_info_dict['cursor'] = cursor.size
                waveform_info_dict['audio_duration'] = audio_duration.text
                waveform_info_dict['audio_cursor_position'] = audio_cursor_position.text

            return waveform_info_dict

    def get_big_waveform_info(self):
        with allure.step("Grab info from big waveform"):
            big_waveform_info_dict = {}
            big_waveform_el = self.audio_transcription_beta_element.get_big_waveform()[0]
            audio_region = big_waveform_el.find_elements('xpath',".//region[contains(@class, 'wavesurfer-region')]")
            cursor = big_waveform_el.find_element('xpath',".//div[contains(@class,'b-PlaybackCursor')]")
            audio_duration = big_waveform_el.find_element('xpath',".//div[@class='b-AudioWaveform__duration']")
            audio_cursor_position = big_waveform_el.find_element('xpath',
                ".//div[@class='b-PlaybackCursor__duration']")
            big_waveform_info_dict['region'] = len(audio_region)
            big_waveform_info_dict['cursor'] = cursor.size
            big_waveform_info_dict['audio_duration'] = audio_duration.text
            big_waveform_info_dict['audio_cursor_position'] = audio_cursor_position.text
            return big_waveform_info_dict

    def get_active_region_from_waveform(self):
        big_waveform_el = self.audio_transcription_beta_element.get_big_waveform()[0]
        active_audio_region = big_waveform_el.find_elements('xpath',".//region[@class='wavesurfer-region' and "
                                                                     "contains(@style, 'background-color: rgba(0, "
                                                                     "161, 179, 0.5);')]")
        assert active_audio_region, "Active region absent on for selected Unit"
        return active_audio_region[0].get_attribute('title')

    def choose_region_on_waveform(self, index=0):
        big_waveform_el = self.audio_transcription_beta_element.get_big_waveform()[0]
        audio_region = big_waveform_el.find_elements('xpath',".//region[@class='wavesurfer-region']")
        assert audio_region, "On waveform not present region"
        audio_region[index].click()

    def click_on_waveform(self):
        self.audio_transcription_beta_element.get_waveform_el()[0].click()

    def get_error_message(self, index=0):
        with allure.step(f"Collect all error message from segment {index}"):
            error_message_list = []
            error_message_ul_els = find_elements(self.driver,
                                                 "//div[contains(@class,'b-Tooltip-placement-right')]//ul")
            for error_message_ul_el in error_message_ul_els:
                error_message_li_els = error_message_ul_el.find_elements('xpath',"./li")
                error_message_list = [error_message_li_el.text for error_message_li_el in error_message_li_els]
            return error_message_list

    def get_error_icon_info(self):
        with allure.step("Get count of error icon and error message provide by this icon"):
            error_icon_info = {}
            error_icon_els = find_elements(self.driver, "//span[@class='b-SegmentsList__statusIconTooltip']")

            for segment in range(0, len(self.audio_transcription_beta_element.get_segment_list())):
                self.action.pause(2).move_to_element(error_icon_els[segment]).perform()
                error_icon_info[segment + 1] = self.get_error_message()
            return error_icon_info

    def add_text_to_segment(self, value):
        with allure.step("Add text to segment"):
            self.audio_transcription_beta_element.text_area_of_segment()[0].send_keys(value)
            self.app.verification.wait_untill_text_present_on_the_page(value, 25)

    def grab_text_from_text_area(self):
        with allure.step("Grab text from text area"):
            transcription_text_el = [text_area.find_element('xpath',
                "./span[@data-text='true']") for text_area in self.audio_transcription_beta_element.text_area_of_segment()]
            current_text = "".join(
                [x.text for x in transcription_text_el])
            return current_text

    def clear_text_area(self):
        with allure.step("Clear the transcription area"):
            self.audio_transcription_beta_element.text_area()[0].click()
            self.app.navigation.combine_hotkey(Keys.COMMAND, "a")
            self.action.send_keys(Keys.BACKSPACE).perform()
            time.sleep(1)

    def highlight_text_in_segments(self, text_for_highlight):
        with allure.step(f"Highlight {text_for_highlight}"):
            self.move_to_word(text_for_highlight)
            self.action.key_down(Keys.SHIFT)
            for i in range(0, len(text_for_highlight)):
                self.action.send_keys(Keys.ARROW_RIGHT)
            self.action.key_up(Keys.SHIFT).perform()
            time.sleep(1)
            return self.action

    def highlight_words_in_segments(self, word_for_highlight):
        self.move_to_word(word_in_text=word_for_highlight)
        self.action.key_down(Keys.SHIFT).send_keys(Keys.ARROW_DOWN).key_up(Keys.SHIFT).perform()
        time.sleep(1)

    def delete_highlight_text_in_segments(self, delete_text):
        self.highlight_text_in_segments(delete_text).send_keys(Keys.DELETE).perform()

    def delete_word_in_segment(self, delete_word):
        self.move_to_word(delete_word)
        for i in range(0, len(delete_word)):
            self.action.send_keys(Keys.ARROW_RIGHT)
        self.action.perform()
        for i in range(0, len(delete_word)):
            self.action.send_keys(Keys.BACKSPACE).perform()

    def click_event_marker(self, text_for_event, index=0):
        with allure.step('Click event marker'):
            self.move_to_word(text_for_event, index)
            self.click_on_action_button('ButtonEventMarker')

    def delete_tag(self, tag_name, index=0):
        with allure.step(f"Delete tag {tag_name}"):
            list_of_tag = self.grab_all_tags()
            segment_text = self.grab_text_from_text_area()
            len_of_transcription_text = len(segment_text)
            start_index = segment_text.find(tag_name)
            b1 = self.audio_transcription_beta_element.text_area_of_segment()[index]

            b1.send_keys('')

            self.action.send_keys(Keys.ARROW_RIGHT).send_keys(Keys.ARROW_DOWN).perform()

            len_of_tag = 0
            count = -1
            for index in range(0, len(list_of_tag)):
                if list_of_tag.index(tag_name) <= index:
                    len_of_tag += len(list_of_tag[index])
                    count += 1
            new_tag_len = len_of_tag - count

            for i in range(0, len_of_transcription_text - start_index - new_tag_len):
                self.action.send_keys(Keys.ARROW_LEFT).perform()
            self.action.send_keys(Keys.BACK_SPACE).perform()

    def grab_all_tags(self):
        with allure.step("Collect all tags"):
            tags_els = self.audio_transcription_beta_element.text_area()[0].find_elements('xpath',".//span[@contenteditable='false']//span[@data-text='true']")
            tag_list = [tag_el.text for tag_el in tags_els]
            return tag_list

    def click_on_listen_to_block(self, time_value, index=0):
        with allure.step("Click on listen to block to play the audio"):
            self.audio_transcription_beta_element.listen_to_block()[index].click()
            count_of_listen_portion = len(self.audio_transcription_beta_element.listen_to_block())
            time.sleep(time_value)
            return count_of_listen_portion

    def listening_required(self):
        with allure.step("Verify if listening required for a audio"):
            listen_to_hover_msg = []
            index = 0
            for _listen_to_block in self.audio_transcription_beta_element.listen_to_block():
                self.action.pause(1).move_to_element(_listen_to_block).perform()
                listen_to_tooltip = find_elements(self.driver, "//div[@class='b-Tooltip-inner']")
                listen_to_hover_msg.append(listen_to_tooltip[index].text)
                index += 1
            return listen_to_hover_msg

    def stop_play_audio_by_tab(self):
        with allure.step("Play/stop audio by tab"):
            self.action.send_keys(Keys.TAB).perform()

    def get_selected_labels(self):
        with allure.step("Get selected label from segment"):
            label_list = []
            if self.audio_transcription_beta_element.get_label_list_element():
                label_els = self.audio_transcription_beta_element.get_label_list_element()[0].find_elements('xpath',
                    ".//span")
                label_list = [label_el.text for label_el in label_els]
                return label_list
            return label_list

    def delete_label_by_button(self, index=0):
        with allure.step("Delete label by button"):
            delete_btn = self.audio_transcription_beta_element.get_label_list_element()[0].find_elements('xpath',
                ".//button")
            assert delete_btn, "Delete button NOT present for label"
            delete_btn[index].click()

    def verify_checked_label(self, label_name, button_type='radio'):
        checked_label = find_elements(self.driver, "//label[text()='%s']/input" % label_name) if button_type == 'radio' \
            else find_elements(self.driver, "//label[text()='%s']/../input" % label_name)
        assert checked_label, f'Label with name {label_name} NOT present for segment'
        return checked_label[0].get_attribute('checked')

    def clear_choice_label(self, index=0):
        with allure.step("Clear selected label by button clear choice"):
            clear_choice_el = find_elements(self.driver,
                                            "//button[contains(@class,'b-LabelsPanel__group-clear-choices')]")
            assert clear_choice_el, "The clear choice btn not present for group label"
            move_to_element(self.driver, clear_choice_el[index])

    def click_on_action_button(self, action, index=0):
        with allure.step(f'Chose action {action}'):
            action_btn_els = find_elements(self.driver, "//button[contains(@class, '%s')]" % action)
            assert action_btn_els, f"Button for action {action} NOT present on work panel"
            action_btn_els[index].click()

    def click_nothing_to_annotate(self):
        nothing_annotate_btn_els = "//button[contains(@class, 'ButtonNothingToTranscrib')]"
        double_click_element_by_xpath(self.driver, nothing_annotate_btn_els)

    def get_interval_lines_height(self, min_height, max_height):
        with allure.step("Find interval lines for big waveform or baby"):
            waveform = filter(lambda interval_line: min_height < int(interval_line.get_attribute('height')) < max_height,
                              self.audio_transcription_beta_element.get_interval_lines())
            width = list(waveform)[0].get_attribute('width')
            return width

    def nothing_to_transcribe(self, index=0):
        with allure.step('Validate if the segments with some transcription message'):
            nothing_to_transcribe = self.audio_transcription_beta_element.get_transcription_area()
            if nothing_to_transcribe[index].text == 'Nothing to Transcribe':
                return True
            return False

    def get_tags_info(self, tag, index=0):
        with allure.step("Get span/event info from transcription test"):
            style = {
                "event": 'rgba(101, 0, 211, 0.2)',
                "span": 'rgba(255, 170, 0, 0.2)',
                'timestamp': 'rgba(0, 208, 255, 0.2)'
            }

            b1 = self.audio_transcription_beta_element.text_area_of_segment()[index]
            b1.click()
            text_content = b1.find_elements('xpath',
                "./..//span[@contenteditable='false' and contains(@style,'%s')]//span[@data-text='true']" % style[tag])
            current_tag = {tag: []}
            for el in text_content:
                    current_tag[tag].append(el.text)
            return current_tag

    def chose_seed_of_audio(self, speed):
        speed_list = find_elements(self.driver, "//div[@class='b-DropdownButton__content']/div[text()='%s']" % speed)
        assert speed_list, "Dropdown with with speed option NOT opened"
        speed_list[0].click()

    def speed_specific_audio(self, speed_time):
        audio_time_on_listen_block = self.get_work_area_listen_to()[0]['listen_to_time'].split('/')
        audio_time = re.findall("\d+\.\d+", audio_time_on_listen_block[1])
        speed_audio_time = 20
        audio_time_digit = float(audio_time[0])
        if audio_time_digit > 19:
            self.click_on_action_button("b-DropdownButton__button")
            self.chose_seed_of_audio(speed=speed_time)
            speed_audio_time = audio_time_digit / 6
        self.click_on_action_button("PlayPauseButton")
        time.sleep(int(speed_audio_time)+2)
        return audio_time_digit

    def scroll_to_label(self, label_name):
        label_title_els = find_elements(self.driver, "//span[@class='b-LabelsPanel__group-title' and text()='%s']" % label_name)
        assert label_title_els, f"Label with title {label_name} Not present for segment"
        scroll_to_element(self.driver, label_title_els[0])

    def nothing_to_segment(self):
        nothing_seg_els = find_elements(self.driver, "//button[contains(@class,'b-ButtonNothingToAnnotate')]")
        assert nothing_seg_els, "Button nothing to segment NOT present on page"
        nothing_seg_els[0].click()
