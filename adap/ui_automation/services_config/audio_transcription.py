import time

import allure
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import re
from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.utils.js_utils import *
from adap.ui_automation.utils.selenium_utils import find_elements, find_element, click_by_action, move_to_element, \
    scroll_to_element_by_action


class AudioTranscriptionUI(Annotation):

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
        self.toolbar = Toolbar(self)
        self.span = Span(self)
        self.event = Event(self)
        self.group_labels = GroupLabels(self)
        self.data_unit = DataUnit(self)

    def btn_is_displayed(self, btn_name):
        with allure.step('Button %s is displayed' % btn_name):
            # print(self.driver.page_source)
            btn = find_elements(self.driver, "//*[.//*[text()='%s'] or text()='%s']" % (btn_name, btn_name))
            if len(btn) > 0: return True
            return False

    def get_audio_layers(self):
        with allure.step('Get all current audio layers'):
            layers = find_elements(self.driver,
                                   "//div[contains(@class,'b-AudioLayers')]//div[@class='b-AudioLayer']//div[@class='b-AudioSegment']")

            _ = []
            for l in layers:
                color = l.value_of_css_property('background-color')
                _.append(color)
            return _

    def get_audio_layers_with_segments(self):
        with allure.step('Get all current audio layers'):
            layers = find_elements(self.driver,
                                   "//div[@class='b-ToolBody__layers']//div[@class='b-AudioLayer']")
            layers_info = {}
            for l in layers:
                el = l.find_elements('xpath',".//div[@class='b-AudioSegment']")
                for s in el:
                    style = s.get_attribute('style')
                    color = style.split('--active-segment-color:')[1][:-1]
                    top = style.split('; ')[0][5:]
                    height = style.split('; ')[1][8:]
                    inactive_color = style.split('; ')[2][25:-2]
                    segments = {'color': color,
                                'inactive_color': inactive_color,
                                'top': top,
                                'height': height}

                    if layers_info.get(color, False):
                        _segments = layers_info[color]
                        _segments.append(segments)
                        layers_info[color] = _segments
                    else:
                        layers_info[color] = [segments]

            return layers_info

    def get_bubbles_list(self):
        with allure.step('Get current bubbles list'):
            bubbles = find_elements(self.driver, "//div[@class='b-SegmentsArea']//div[@class='b-Segment__header']")
            _bubbles_info = []
            for b in bubbles:
                name = b.find_element('xpath',".//div[@class='b-Segment__segmentTitle']").text
                _bubbles_info.append({'name': name})
            return _bubbles_info

    def get_bubbles_name(self):
        with allure.step('Get current bubbles name'):
            bubbles = self.get_bubbles_list()
            _bubbles_name = []
            for bubble in bubbles:
                _bubbles_name.append(bubble['name'])
            return _bubbles_name

    def close_at_tool_without_saving(self):
        with allure.step('Close audio transcription tool w/o saving'):
            try:
                self.driver.minimize_window()
            except:
                print("Error!")

    def _find_bubble_by_name(self, name, index=0, default_name='Segment 1'):
        bubble = find_elements(self.driver,
                               "//div[@class='b-Segment__headerArea'][.//div[@class='b-Segment__segmentTitle' and "
                               "text()='%s']]/.." % name)
        if not bubble:
            bubble = find_elements(self.driver,
                                   "//div[@class='b-Segment__headerArea'][.//div[@class='b-Segment__segmentTitle' and "
                                   "text()='%s']]/.." % default_name)
        assert len(bubble), "Bubble %s has not been found" % name
        assert len(bubble) >= index + 1, "Bubble %s has not been found; index - %s" % (name, index)
        return bubble[index]

    def select_bubble_by_name(self, name, index=0, default_name='Segment 1'):
        with allure.step('Select bubble by name and index'):
            bubble = self._find_bubble_by_name(name, index, default_name)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

    def select_bubble_by_index(self, index=0):
        with allure.step('Select bubble by Segment %s index ' % index):
            bubble_index = find_elements(self.driver, "//div[@class='b-Segment__segmentTitle']")
            assert len(bubble_index) > 0, "Bubble Segment %s has not been found" % index
            mouse_click_element(self.driver, bubble_index[index])
            bubble_index[index].click()

    def scroll_and_select_bubble(self, index=0):
        bubble_index = find_elements(self.driver, "//div[@class='b-Segment__segmentTitle']")
        assert len(bubble_index) > 0, "Bubble Segment %s has not been found" % index
        scroll_to_element(self.driver, bubble_index[index])
        mouse_click_element(self.driver, bubble_index[index])

    def get_active_layer(self):
        with allure.step('Get active layer'):
            layer = find_elements(self.driver, "//div[contains(@class, 'b-AudioSegment--active')]")
            assert len(layer), "Active layer has not been found"

            style = layer[0].get_attribute('style')
            color = style.split('; ')[2].split(":")[1][:7]
            return color

    def get_active_layer_number(self):
        with allure.step('Get active layer number'):
            layer = find_elements(self.driver, "//div[contains(@class, 'b-AudioSegment--active')]")
            return len(layer)

    def add_text_to_bubble(self, name, value, index=0):
        with allure.step('Add text to the bubble'):
            bubble = self._find_bubble_by_name(name, index)
            try:
                bubble.click()
                # b1 = bubble.find_element('xpath',".//div[@class='b-Segment__transcriptionArea']")
                # b1.click()
            except:
                move_to_element(self.driver, bubble)
                time.sleep(2)
                # b1 = bubble.find_element('xpath',".//div[@class='b-Segment__transcriptionArea']")
                # b1.click()

            el = bubble.find_element('xpath',".//div[@class='DraftEditor-editorContainer']//span[@data-offset-key]")
            el.send_keys(value)
            time.sleep(3)

    def get_text_from_bubble(self, name, index=0, events=False, default_name='Segment 1'):
        with allure.step('Add text to the bubble'):
            bubble = self._find_bubble_by_name(name, index, default_name)
            if events:
                return "".join(
                    [x.text for x in bubble.find_elements('xpath',".//div[@class='DraftEditor-editorContainer"
                                                                   "']//span[@data-text='true']")])

            current_text = "".join([x.text for x in bubble.find_elements('xpath',".//div[@class='DraftEditor-editorContainer"
                                                                         "']//span[not(@class='b-Event')]//span[@data-text='true']")])

            if current_text: return current_text
            nothing_to_transcribe = find_elements(self.driver, "//div[@class='b-Segment__transcriptionArea']//div")
            if len(nothing_to_transcribe) > 0: return nothing_to_transcribe[0].text
            return ''

    def edit_text_from_bubble(self, name, value, index=0):
        with allure.step('Edit text from the bubble'):
            self.delete_text_from_bubble(name, index)
            self.add_text_to_bubble(name, value, index)

    def delete_text_from_bubble(self, name, index=0):
        with allure.step('Delete text from the bubble'):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el = bubble.find_element('xpath',".//div[@class='DraftEditor-editorContainer']//span[@data-text]")
            try:
                while len(el.text) > 0:
                    el.send_keys(Keys.BACK_SPACE)
                    el = bubble.find_element('xpath',".//div[@class='DraftEditor-editorContainer']//span[@data-text]")
                    time.sleep(1)
            except:
                print("Error")

    def click_nothing_to_transcribe_for_bubble(self, name, index=0):
        with allure.step('Click nothing to transcribe for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el = bubble.find_elements('xpath',
                ".//button[contains(@class, 'b-ButtonNothingToTranscribe')]//*[local-name() = 'svg']")
            assert len(el) > 0, "Btn 'Nothing to transcribe' has not been found"
            el[0].click()
            time.sleep(2)

    def click_review_for_bubble_by_name(self, name, index=0):
        with allure.step('Click review for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el = bubble.find_elements('xpath',
                ".//button[contains(@class, 'b-ButtonReviewed')]//*[local-name() = 'svg']")
            assert len(el) > 0, "Btn 'review' has not been found"
            el[0].click()
            time.sleep(2)

    def click_review_for_bubble(self, index=0):
        with allure.step('Click review for bubble %s' % index):
            el = find_elements(self.app.driver,
                               "//button[contains(@class, 'b-ButtonReviewed')]")
            assert len(el) > 0, "Btn 'review' has not been found"
            move_to_element(self.app.driver, el[index])

    def review_btn_is_disable_for_bubble(self, name, index=0):
        with allure.step('Review button is disable for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            btn = bubble.find_elements('xpath',".//button[contains(@class,'ButtonReviewed')]")
            assert len(btn) > 0, "Button has not been found"
            style = btn[0].get_attribute('class')
            if 'disabled' in style: return True
            return False

    def review_button_is_displayed(self, name, index=0):
        with allure.step('Review button is displayed %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el = bubble.find_elements('xpath',
                ".//button[contains(@class, 'b-ButtonReviewed')]//*[local-name() = 'svg']")
            if len(el) > 0: return True
            return False

    def reviewed_icon_is_displayed(self, name, index=0):
        with allure.step('Reviewed icon displayed for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el = bubble.find_elements('xpath',
                ".//*[contains(@class, 'b-Segment__reviewedIcon')]")
            if len(el) > 0: return True
            return False

    def review_all_segments(self):
        with allure.step('Review all segment'):
            list_of_bubble_name = self.get_bubbles_name()
            for i in range(0, len(list_of_bubble_name)):
                self.click_review_for_bubble(i)

    def click_play_segment_for_bubble(self, name, index=0):
        with allure.step('Click nothing to transcribe for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el = bubble.find_elements('xpath',
                ".//button[contains(@class, 'b-Button')]//*[local-name() = 'svg']")
            assert len(el) > 0, "Btn 'Play segment' has not been found"
            el[0].click()
            time.sleep(2)

    def get_audio_cursor_transform_info(self):
        with allure.step('Get information about where audio cursor stopped'):
            el_cursor = find_elements(self.driver,
                                      "//div[contains(@class, 'b-Segment--active')]//div[contains(@class, 'SegmentAudioCanvas__cursor')]")
            assert len(el_cursor) > 0, "Element cursor on audio NOT present"
            style = el_cursor[0].get_attribute('style')
            time.sleep(2)
            return style

    def get_nothing_to_transcribe_status_for_bubble(self, name, index=0):
        with allure.step('Get Nothing to transcribe status for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            el = bubble.find_elements('xpath',
                ".//div[@class='b-Segment__transcriptionArea']//*[text()='Nothing to Transcribe']")
            if len(el) > 0: return True
            return False

    def nothing_to_transcribe_btn_is_disable_for_bubble(self, name, index=0):
        with allure.step('Nothing to transcribe button is disable for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            btn = bubble.find_elements('xpath',".//button[contains(@class,'ButtonNothingToTranscribe')]")
            assert len(btn) > 0, "Button has not been found"
            style = btn[0].get_attribute('class')
            if 'disabled' in style: return True
            return False

    def click_nothing_to_transcribe_for_task(self):
        with allure.step('Select Nothing to transcribe for task'):
            el = find_elements(self.driver, "//div[@class='b-NothingToTranscribe__action']//input")
            assert len(el) > 0, "Checkbox Nothing to transcribe has not been found"
            el[0].click()

    def info_icon_is_displayed_on_bubble(self, name, index=0):
        with allure.step('Class info icon is displayed for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            icon = bubble.find_elements('xpath',".//div[contains(@class,'b-SegmentInfo')]//*[local-name() = 'svg']")
            if len(icon) > 0: return True
            return False

    def click_info_icon_on_bubble(self, name, index=0):
        with allure.step('Click info icon for bubble %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            icon = bubble.find_elements('xpath',".//div[contains(@class,'b-SegmentInfo')]//*[local-name() = 'svg']")
            assert len(icon) > 0, "Icon has not been found"
            icon[0].click()

    def get_audio_lengtn(self):
        el = find_elements(self.driver, "//div[@class='b-AudioTranscriptionPreview__length']")
        assert len(el) > 0, "Audio info has not been found"
        return float(el[0].text.split(' ')[0])

    def get_num_segments_to_transcribe(self):
        el = find_elements(self.driver, "//div[@class='b-AudioTranscriptionPreview__segments']")
        assert len(el) > 0, "Audio info has not been found"
        print(el[0].text)
        num_s = re.findall(r"([0-9]+)(/[0-9]+)", el[0].text)
        return int(num_s[0][1][1:])

    def get_active_bubble(self):
        with allure.step('Get active bubble'):
            _bubble = find_elements(self.driver, "//div[@class='b-Segment b-Segment--active']")
            if len(_bubble) == 0: return None
            _color = _bubble[0].find_element('xpath',".//div[@class='b-Segment__color']") \
                         .get_attribute('style').split("--color:")[1][:-1]
            _name = _bubble[0].find_element('xpath',".//div[@class='b-Segment__title']").text
            return {'name': _name,
                    "color": _color}

    def nothing_to_transcribe_checkbox_is_displayed(self):
        with allure.step('Checkbox "Nothing to transcribe" is displayed'):
            _checkbox = find_elements(self.driver, "//div[@class='b-NothingToTranscribe__action']")
            if len(_checkbox) > 0: return True
            return False

    def open_label_panel_by_name(self, name, index=0):
        with allure.step('Open label panel for %s' % name):
            bubble = self._find_bubble_by_name(name, index)
            bubble.click()
            el_label_panel = bubble.find_elements('xpath',
                ".//button[contains(@class, 'b-ButtonReviewed')]//*[local-name() = 'svg']")
            assert len(el_label_panel) > 0, "Btn 'labelPanel' has not been found"
            el_label_panel[0].click()
            time.sleep(2)

    def open_label_panel(self, index=0):
        with allure.step('Open label panel for '):
            el_label_panel = find_elements(self.driver,
                ".//button[contains(@class, 'b-ButtonLabelsPanel')]")
            assert len(el_label_panel) > 0, "Btn 'labelPanel' has not been found"
            if not self.group_labels.active_label_panel():
                move_to_element(self.app.driver, el_label_panel[index])
                time.sleep(2)

    def open_label_panel_disabled(self):
        with allure.step('Open label panel for '):
            el_label_panel = find_elements(self.driver,
                "//button[contains(@class, 'b-ButtonLabelsPanel')]")
            if len(el_label_panel) > 0:
                return False
            return True

    def add_feedback(self, feedback_msg):
        with allure.step('Add feedback to segments'):
            feedback_el = find_elements(self.driver, "//textarea[contains(@class,'b-Comment__input')]")
            assert len(feedback_el) > 0, "The textarea for feedback absent on page"
            feedback_el[0].send_keys(feedback_msg)

    def nothing_to_trinscribe(self, index=0):
        with allure.step('Validate if the segments with some transcription message'):
            nothing_to_transcribe = find_elements(self.driver, "//div[contains(@class,'transcriptionArea')]/div")
            if nothing_to_transcribe[index].text == 'Nothing to Transcribe':
                return True
            return False

    def active_segment(self):
        with allure.step('Find active segment'):
            active_segment = find_elements(self.driver, "//div[contains(@class,'b-Segment--active')]")
            assert len(active_segment) > 0, 'Non of the segment active'
            return active_segment[0]

    def get_reviewed_info(self, event=False):
        with allure.step('Get data from correction judgment'):
            review_el = self.active_segment().find_elements('xpath',
                ".//div[contains(@class, 'reviewedArea')]//div[@class='b-TranscriptionViewer']")
            assert len(review_el) > 0, 'The review Area for correction judgment Not present'
            if event:
                return "".join(
                    [x.text for x in review_el[0].find_elements('xpath',".//div[@class='DraftEditor-editorContainer"
                                                                         "']//span[@data-text='true']")])

            current_text = "".join(
                [x.text for x in review_el[0].find_elements('xpath',".//div[@class='DraftEditor-editorContainer"
                                                                     "']//span[not(@style='rgba(101, "
                                                               "0, 211, 0.2)')]//span[@data-text='true']")])
            if current_text: return current_text
            nothing_to_transcribe = review_el[0].text
            if len(nothing_to_transcribe) > 1: return nothing_to_transcribe

    def get_reviewed_comment(self):
        with allure.step('Get comment from correction judgment'):
            review_comment_el = self.active_segment().find_elements('xpath',
                ".//div[@class='b-Comment__readonly-comment']")
            assert len(review_comment_el) > 0, 'The review comment NOT present or render'
            return review_comment_el[0].text

    def dispute_the_feedback(self, bubble_name):
        with allure.step('Dispute the feedback for bubble %s' % bubble_name):
            # comment_area = find_element(self.driver, "//div[text()='Reply To Feedback']")
            dispute_els = find_elements(self.driver, "//input[@id='dispute']")
            assert dispute_els, "The Dispute radio btn ABSENT for active segment"
            scroll_to_element(self.driver, dispute_els[0])
            # scroll_to_element_by_action(self.driver, comment_area)
            dispute_els[0].click()

    def acknowledge_the_feedback(self, bubble_name):
        with allure.step('Dispute the feedback for bubble %s' % bubble_name):
            ack_els = find_elements(self.driver, "//input[@id='acknowledge']")
            assert len(ack_els) > 0, "The Acknowledge radio btn ABSENT for active segment"
            scroll_to_element_by_action(self.driver, ack_els[0])
            ack_els[0].click()

    def acknowledge_feedback_check(self):
        with allure.step('Acknowledge feedback checked automatically'):
            acknowledge_feedback_el = find_elements(self.driver, "//input[@id='acknowledge']")
            assert len(acknowledge_feedback_el) > 0, "The Acknowledge radio btn ABSENT for active segment"
            if acknowledge_feedback_el[0].get_attribute('checked'):
                return True
            else:
                return False

    def get_acknowledge_feedback(self):
        with allure.step("Get feedback from acknowledge judgment"):
            acknowledge_feedbacks = find_elements(self.app.driver,
                                                  "//div[@class = 'b-Comment__readonly-comment empty']")
            assert acknowledge_feedbacks, "Acknowledge Feedback not present on Page"
            return acknowledge_feedbacks[0].text

    def arbitration_of_feedback(self, action='Revert'):
        with allure.step('Decide approve feedback or revert'):
            action_require_title = find_elements(self.driver, "//div[text()='Reply To Feedback']")
            assert action_require_title, "The box with arbitration option NOT present"
            scroll_to_element(self.driver, action_require_title[0])
            arbitration_els = find_elements(self.driver, "//div[@class='b-ArbitrationPanel__group']/div")
            assert arbitration_els, "The option for Revert/Approve feedback ABSENT"
            if action == 'Revert':
                revert_radio_btn = find_elements(self.driver,
                                                 "//div[@class='b-ArbitrationPanel__group']/div//input[@value='revert']")
                assert revert_radio_btn, "The button for Revert Feedback not present"
                time.sleep(5)
                revert_radio_btn[0].click()
            else:
                radio_btn = find_element(self.driver, "//input[contains(@id, 'Revert')]")
                scroll_to_element(self.driver, radio_btn)
                approve_radio_btn = find_elements(self.driver,
                                                  "//div[@class='b-ArbitrationPanel__group']/div//input[@value='approve']")
                assert approve_radio_btn, "The button for Approve Feedback not present"
                time.sleep(5)
                approve_radio_btn[0].click()

    def get_span_event(self, bubble_name, index=0, default_name='Segment 1'):
        with allure.step("Get span/event info from transcription test"):
            bubble = self._find_bubble_by_name(bubble_name, index, default_name)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            text_content = bubble.find_elements('xpath',
                ".//..//div[contains(@class,'transcriptionArea')]//span[@contenteditable='false']")
            current_tag = {'event_name': [], 'span_name': []}
            for el in text_content:
                _span_event_text = el.find_element('xpath',".//span[@data-text='true']").text
                if re.search('<[^/>]+/>', _span_event_text) != None:
                    current_tag['event_name'].append(_span_event_text)
                else:
                    current_tag['span_name'].append(_span_event_text)
            return current_tag


class Toolbar:
    buttons = {
        "play": {
            "id": 0,
            "name": "Play/Pause"
        },
        "pause": {
            "id": 0,
            "name": "Play/Pause"
        },
        "back": {
            "id": 1,
            "name": "Nudge back"
        },
        "forward": {
            "id": 2,
            "name": "Nudge forward"
        },
        "empty_segments": {
            "id": 3,
            "name": "emtpy_segments"
        },
        "play_speed": {
            "id": 4,
            "name": "x_button"
        },
        "help": {
            "id": 5,
            "name": "help"
        },
        "save": {
            "id": 6,
            "name": "Save & Close"
        },
        "full_screen": {
            "id": 6,
            "name": "Save & Close"
        }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def find_buttons(self):
        with allure.step('Find button'):
            return self.driver.find_elements('xpath',
                "//div[@class='b-ToolbarWrapper' or @class='b-Toolbar' or @class='b-Toolbar b-Toolbar--fullscreen-mode' or @class='b-ToolbarWrapper b-ToolbarWrapper--fullscreen-mode']//button")

    def click_btn(self, btn_name, index=0):
        with allure.step(f'Click button {btn_name}'):
            left_buttons = find_elements(self.driver, "//div[@class='b-Toolbar__left']/button")
            assert left_buttons, "Buttons for play/back/forward not present on page"
            left_buttons[index].click()
            time.sleep(3)

    def click_btn_right_panel(self, btn_name, index=0):
        with allure.step(f'Click button {btn_name} on right panel'):
            right_buttons = find_elements(self.driver, "//button[contains(@class, '%s')]" % btn_name)
            assert right_buttons, "Buttons on right panel not present"
            right_buttons[index].click()
            time.sleep(3)

    def save_annotation(self):
        with allure.step('Save annotation'):
            save_button = find_elements(self.driver, "//button[contains(@class, 'b-ButtonSaveClose')]")
            assert len(save_button) > 0, "Save button has not been found"
            save_button[0].click()
            time.sleep(1)

    def button_is_disable(self, btn_name):
        with allure.step('Check button is disabled'):
            index = self.buttons[btn_name]['id']
            el_class = self.find_buttons()[index].get_attribute('class')
            return (True, False)[el_class.find('disabled') == -1]

    def close_info_panel(self):
        with allure.step('Close info help panel'):
            el = find_elements(self.driver,
                               "//button[contains(@class, 'b-InformationBar__close_button')]//*[local-name() = 'svg']")
            assert len(el) > 0, "Element has not been found"
            el[0].click()

    def get_tooltip_for_btn(self, btn_name, btn_index=0):
        with allure.step('Get tooltip for button %s: ' % btn_name):
            index = self.buttons[btn_name]['id']
            btn = self.find_buttons()
            mouse_over_element(self.driver, btn[index])
            time.sleep(2)
            tooltip = find_elements(self.driver, "//div[contains(@class,'b-Tooltip-placement-bottom')]"
                                                 "//div[@class='b-Tooltip-inner']")
            assert len(tooltip), "Tooltip for btn %s has not been found" % btn_name

            return tooltip[btn_index].text

    def get_play_speed(self):
        with allure.step('Get current play speed'):
            play_speed = find_elements(self.driver, "//button[contains(@class, 'b-DropdownButton__button')]//div")
            return play_speed[0].text

    def select_play_speed(self, speed):
        with allure.step('Select play speed'):
            play_speed = find_elements(self.driver, "//div[@class='b-DropdownButton__item']")
            for i in range(len(play_speed)):
                if play_speed[i].text == speed:
                    play_speed[i].click()
                    time.sleep(1)

    def get_displayed_time(self):
        with allure.step('Get displayed time'):
            display_time = find_elements(self.driver, "//div[@class='b-Timecode']//span[@class='b-Timecode__displayedTime']")
            return display_time[0].text

    def get_total_time(self):
        with allure.step('Get total time'):
            total_time = find_elements(self.driver, "//div[@class='b-Timecode']//span[@class='b-Timecode__totalTime']")
            return total_time[0].text

    def audio_cursor_is_displayed(self):
        with allure.step('Audio cursor is displayed'):
            el = find_elements(self.driver, "//div[@class='b-AudioLayers__container']")
            if len(el) > 0: return True
            return False

    def get_audio_cursor_position(self):
        with allure.step('Get audio cursor position'):
            cursor = find_elements(self.driver, "//div[@class='b-AudioCursor b-Cursor']")
            assert len(cursor) > 0, "Audio has not been found"
            style = cursor[0].get_attribute('style')
            style = re.findall(r"([0-9]+)(px|%)?", style)
            return style[0][0]


class Span:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def highlight_text_in_bubble(self, span_text, bubble_name, index=0):
        with allure.step('Select word %s in bubble %s' % (span_text, bubble_name)):
            bubble = self.app._find_bubble_by_name(bubble_name, index)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            bubble_text = self.app.get_text_from_bubble(bubble_name, index)
            start_index = bubble_text.find(span_text)
            # bubble_text_with_events = self.app.get_text_from_bubble(bubble_name, index, events=True)
            # start_index_with_events = bubble_text_with_events.find(span_text)
            # adjustment = (start_index_with_events - start_index) *2
            b1 = bubble.find_element('xpath',".//div[@class='DraftEditor-editorContainer']//span[@data-offset-key]")

            b1.send_keys('')
            action = ActionChains(self.driver)

            for i in range(len(bubble_text)):
                action.send_keys(Keys.ARROW_LEFT)
            action.perform()

            for i in range(start_index):
                action.send_keys(Keys.ARROW_RIGHT)
            action.perform()

            action.key_down(Keys.SHIFT)
            for i in range(start_index, start_index + len(span_text)):
                action.send_keys(Keys.ARROW_RIGHT)
            action.key_up(Keys.SHIFT).perform()
            time.sleep(1)

    def add_span(self, span_name):
        with allure.step('Add span %s' % span_name):
            span = find_elements(self.driver,
                                 "//div[@class='b-SpansList']//div[@class='b-SpansList__name' and text()='%s']" % span_name)
            assert len(span) > 0
            span[0].click()
            time.sleep(1)

    def get_popup_list(self, details=False):
        with allure.step('Get span list popup'):
            spans = [x.text for x in
                     find_elements(self.driver, "//div[@class='b-SpansList']//div[@class='b-SpansList__name']")]
            eraser_btn = True if find_elements(self.driver, "//div[@class='b-SpansList__eraseButton']") else False

            _span_details = []
            if details:
                for s in find_elements(self.driver, "//div[@class='b-SpansList']//div[@class='b-List__Entity']"):
                    _color = s.find_element('xpath',".//div[@class='b-SpansList__color']") \
                                 .get_attribute('style') \
                                 .split('--span-color:')[1][:-1]
                    _key = s.find_elements('xpath',".//div[@class='b-SpansList__keyWrapper']")
                    _name = s.find_element('xpath',".//div[@class='b-SpansList__name']").text

                    _span_details.append({
                        "name": _name,
                        "key": "+".join([key.text for key in _key]),
                        "color": _color
                    })

            return {'spans': spans,
                    'eraser': eraser_btn,
                    'details': _span_details}

    def delete_span(self):
        with allure.step('Delete span'):
            btn = find_elements(self.driver, "//div[@class='b-SpansList__eraseButton']//*[local-name() = 'svg']")
            assert len(btn) > 0, "Eraser has not been found"
            btn[0].click()
            time.sleep(1)

    def delete_audio_tx_span(self, spans_info=['span_name', 'span_text']):
        with allure.step('Delete span'):
            b1 = find_elements(self.driver, "//span[contains(text(),'%s')]/../span" % spans_info[1])

            b1[0].send_keys(Keys.DELETE)
            action = ActionChains(self.driver)
            action.send_keys(Keys.ARROW_RIGHT).send_keys(Keys.BACK_SPACE).perform()
            time.sleep(1)

    def filter_span(self, value):
        with allure.step('Filter spans'):
            filter_field = find_element(self.driver,
                                        "//div[@class='b-List__SearchInput']//input[@class='b-List__input']")
            filter_field.clear()
            filter_field.send_keys(value)

    def close_popup_list(self):
        with allure.step('Close popup list'):
            btn = find_element(self.driver, "//div[@class='b-List__SearchInput']//*[local-name() = 'svg']")
            btn.click()

    def open_span_info_bar(self, name):
        with allure.step('Open span info'):
            info_icon = find_element(self.driver, "//div[@class='b-SpansList__item'][.//div["
                                                  "@class='b-SpansList__name' and text()='%s']]/.." % name)
            # mouse_over_element(self.driver, info_icon)
            action = ActionChains(self.driver)
            action.move_to_element(info_icon).pause(2).perform()
            time.sleep(2)
            _icon = find_element(self.driver, "//div[@class='b-SpansList__item']//div[@class='b-SpanInfo']")
            _icon.click()

    def grab_span_info(self):
        with allure.step('Open span info'):
            _name = find_element(self.driver, "//div[@class='b-InformationBar__title']").text
            hot_key = " ".join([x.text for x in find_elements(self.driver,
                                                              "//div[@class='b-InformationBar__hotKeyWrapper']//*[text()]")])
            description = find_element(self.driver, "//div[@class='b-InformationBar__content']").text
            return {"name": _name, "hot_keys": hot_key, "description": description}

    def close_span_info_bar(self):
        with allure.step('Close span info'):
            btn = find_elements(self.driver,
                                "//button[contains(@class, 'b-Button b-InformationBar__close_button')]//*[local-name() = 'svg']")
            assert len(btn) > 0, "Close button has not been found"
            btn[0].click()
            time.sleep(1)

    def get_text_with_spans(self, bubble_name, index=0, default_name='Segment 1'):
        with allure.step('Get text with labels from bubble'):
            bubble = self.app._find_bubble_by_name(bubble_name, index, default_name)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            text_content = bubble.find_elements('xpath',
                ".//..//div[contains(@class,'transcriptionArea')]//span[@contenteditable='false' and contains(@style,'rgba(255, 170, 0, 0.2)')]")
            _current_spans = []
            for el in text_content:
                # _span_color = el.get_attribute('style').split('--name-color:')[1][:7]
                try:
                    _span_name = el.find_element('xpath',".//span[@data-text='true']").text
                    _span_text = el.find_element('xpath',"./following-sibling::span/span[@data-text='true']").text
                except:
                    _span_name = ''
                    _span_text = ''

                _current_spans.append({
                    "span_name": _span_name,
                    "text": _span_text,
                    "span_color": 'light orange'
                })
            return _current_spans

    def span_modal_is_displayed(self):
        with allure.step('Span modal is displayed'):
            span_el = find_elements(self.driver, "//div[@class='b-SpansList__item']")
            if len(span_el) > 0: return True
            return False

    def get_review_text_span(self):
        with allure.step('Get reviewed text  from active bubble'):
            text_content = self.app.active_segment().find_elements('xpath',
                ".//div[@class='b-CorrectedAnnotation']//span[@contenteditable='false' and contains(@style,'rgba(255, 170, 0, 0.2)')]")
            _current_spans = []
            for el in text_content:
                try:
                    _span_name = el.find_element('xpath',".//span[@data-text='true']").text
                except:
                    _span_name = ''
                _span_text = el.find_element('xpath',"./following-sibling::span/span[@data-text='true']").text

                _current_spans.append({
                    "span_name": _span_name,
                    "text": _span_text
                })
            return _current_spans


class Event:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def add_event(self, event_name):
        with allure.step('Add span %s' % event_name):
            event = find_elements(self.driver,
                                  "//div[@class='b-EventsList']//div[@class='b-EventsList__name' and text()='%s']" % event_name)
            assert len(event) > 0
            event[0].click()
            time.sleep(1)

    def event_btn_is_disable(self, bubble_name, index=0):
        with allure.step('Event button is disable'):
            bubble = self.app._find_bubble_by_name(bubble_name, index)
            element_to_the_middle(self.driver, bubble)
            bubble.click()
            btn = bubble.find_elements('xpath',".//button[contains(@class,'b-ButtonEventMarker')]")
            if len(btn) > 0: return False
            return True

    def move_cursor_to_text_in_bubble(self, span_text, bubble_name, index=0):
        with allure.step('Move mouse to the word %s in bubble %s' % (span_text, bubble_name)):
            bubble = self.app._find_bubble_by_name(bubble_name, index)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            bubble_text = self.app.get_text_from_bubble(bubble_name, index, events=True)
            bubble_text_no_events = self.app.get_text_from_bubble(bubble_name, index, events=False)

            start_index = bubble_text.find(span_text)
            start_index_no_events = bubble_text_no_events.find(span_text)
            adjustment = (start_index - start_index_no_events) * 2

            b1 = bubble.find_element('xpath',".//div[@class='DraftEditor-editorContainer']//span[@data-offset-key]")

            b1.send_keys('')
            action = ActionChains(self.driver)

            for i in range(len(bubble_text)):
                action.send_keys(Keys.ARROW_LEFT)
            action.perform()

            for i in range(start_index):
                action.send_keys(Keys.ARROW_RIGHT)
            action.perform()

            for i in range(adjustment):
                action.send_keys(Keys.ARROW_RIGHT)
            action.perform()

    def move_cursor_to_the_end_of_text_in_bubble(self, bubble_name, index=0, additional_space=False):
        with allure.step('Move mouse to the end of text in bubble %s' % (bubble_name)):
            bubble = self.app._find_bubble_by_name(bubble_name, index)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            bubble_text = self.app.get_text_from_bubble(bubble_name, index, events=True)
            bubble_text_no_events = self.app.get_text_from_bubble(bubble_name, index, events=False)

            start_index = len(bubble_text)
            start_index_no_events = len(bubble_text_no_events)
            adjustment = (start_index - start_index_no_events) * 2

            b1 = bubble.find_element('xpath',".//div[@class='DraftEditor-editorContainer']//span[@data-offset-key]")

            b1.send_keys('')
            action = ActionChains(self.driver)

            for i in range(len(bubble_text)):
                action.send_keys(Keys.ARROW_RIGHT)
            action.perform()

            for i in range(adjustment):
                action.send_keys(Keys.ARROW_RIGHT)
            action.perform()

            if additional_space:
                action.send_keys(Keys.SPACE)
                action.perform()

    def click_event_marker(self, bubble_name, index=0):
        with allure.step('Click event marker'):
            bubble = self.app._find_bubble_by_name(bubble_name, index)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            btn = bubble.find_elements('xpath',".//button[contains(@class,'b-ButtonEventMarker')]")
            assert len(btn) > 0, "Event marker has not been found"
            btn[0].click()

    def get_popup_list(self, details=False):
        with allure.step('Get event list popup'):
            events = [x.text for x in
                      find_elements(self.driver, "//div[@class='b-EventsList']//div[@class='b-EventsList__name']")]
            filter_field = True if find_elements(self.driver, "//div[@class='b-List__SearchInput']") else False

            _event_details = []
            if details:
                for s in find_elements(self.driver, "//div[@class='b-EventsList']//div[@class='b-List__Entity']"):
                    _color = s.find_element('xpath',".//div[@class='b-EventsList__colorWrapper']//*[local-name() = "
                                                     "'svg']").get_attribute('fill')

                    _key = s.find_elements('xpath',".//div[@class='b-EventsList__keyWrapper']")
                    _name = s.find_element('xpath',".//div[@class='b-EventsList__name']").text

                    _event_details.append({
                        "name": _name,
                        "key": "+".join([key.text for key in _key]),
                        "color": _color
                    })

            return {'events': events,
                    'filter': filter_field,
                    'details': _event_details}

    def filter_events(self, value):
        with allure.step('Filter events'):
            filter_field = find_element(self.driver,
                                        "//div[@class='b-EventsList']//input[@class='b-List__input']")
            filter_field.clear()
            filter_field.send_keys(value)

    def open_info_bar(self, name):
        with allure.step('Open event info'):
            time.sleep(3)
            info_icon = find_element(self.driver, "//div[@class='b-EventsList__item'][.//div["
                                                  "@class='b-EventsList__name' and text()='%s']]" % name)
            # mouse_over_element(self.driver, info_icon)
            action = ActionChains(self.driver)
            action.move_to_element(info_icon).pause(1).perform()
            time.sleep(4)
            _icon = find_element(self.driver, "//div[@class='b-EventsList__item'][.//div[@class='b-EventsList__name' "
                                              "and text()='%s']]//div[@class='b-SpanInfo']" % name)
            _icon.click()

    def grab_info(self):
        with allure.step('Open event info'):
            _name = find_element(self.driver, "//div[@class='b-InformationBar__title']").text
            hot_key = " ".join([x.text for x in find_elements(self.driver,
                                                              "//div[@class='b-InformationBar__hotKeyWrapper']//*[text()]")])
            description = find_element(self.driver, "//div[@class='b-InformationBar__content']").text
            return {"name": _name, "hot_keys": hot_key, "description": description}

    def get_events_from_bubble(self, bubble_name, index=0, default_name='Segment 1'):
        with allure.step('Get all events from bubble'):
            bubble = self.app._find_bubble_by_name(bubble_name, index, default_name)
            element_to_the_middle(self.driver, bubble)
            bubble.click()

            events = bubble.find_elements('xpath',".//span[@contenteditable='false' and contains(@style,'rgba(101, "
                                                   "0, 211, 0.2)')]//span[@data-text='true']")
            events_names = [e.text for e in events]
            return events_names

    def get_events_from_reviewed_bubble(self):
        with allure.step('Get all events from active bubble in review box'):
            events = [e.text for e in self.app.active_segment().find_elements('xpath',
                ".//div[@class='b-CorrectedAnnotation']//span[@contenteditable='false' and contains(@style,"
                "'rgba(101, 0, 211, 0.2)')]//span[@data-text='true']")]
            return events

    def delete_event(self, key='delete'):
        action = ActionChains(self.driver)
        if key == 'delete':
            action.send_keys(Keys.ARROW_LEFT).send_keys(Keys.DELETE)
        elif key == 'backspace':
            action.send_keys(Keys.BACK_SPACE)
        action.perform()

    def get_all_btn_event(self):
        with allure.step('Get all event from unit'):
            btn_events = find_elements(self.driver,
                                       "//button[contains(@class,'b-ButtonEventMarker') and not(contains(@class, 'b-Button--disabled'))]")
            return len(btn_events)


class GroupLabels:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def active_label_panel(self):
        with allure.step("The Label panel opened"):
            el_labels_panel = find_elements(self.driver, "//div[@class='b-LabelsPanel']")
            if len(el_labels_panel) > 0:
                return True
            else:
                return False

    def choose_labels_by_name(self, name_labels, multi_select=False, index=0):
        with allure.step('Select %s label' % name_labels):
            el_label_names = find_elements(self.driver, "//div[@class = 'b-LabelsPanel__group']")
            if multi_select:
                el_label_names[index].find_element('xpath',
                    ".//div[contains(@class, 'b-Radio')]//input[@value='%s']" % name_labels).click()
            else:
                el_label_names[index].find_element('xpath',
                    ".//div[contains(@class, 'b-Checkbox')]/label[text()='%s']" % name_labels).click()

    def close_label_panel(self):
        with allure.step('Close label panel'):
            if self.active_label_panel():
                close_button = find_elements(self.driver, "//h3[text()='Choose Labels']/following-sibling::button")
                assert len(close_button) > 0, "Close btn for label panel not found"
                close_button[0].click()

    def the_list_of_transcribe_labels(self):
        with allure.step('Return the list of transcribe layer'):
            group_label_transcribe_list = []
            choose_transcribe_layers = find_elements(self.driver, "//span[contains(@class,'group-title')]")
            group_label_transcribe_list = [group_title_name.text for group_title_name in choose_transcribe_layers]
            return group_label_transcribe_list

    def get_selected_labels(self):
        label_list = []
        label_els = self.app.active_segment().find_elements('xpath',
            "./div[@class='b-LabelsList']//div[@class='b-LabelsList__tag']//span")
        if len(label_els) > 0:
            label_list = [label_el.text for label_el in label_els]
        return label_list

    def delete_label_button_disabled(self):
        with allure.step('Delete label button disabled'):
            button_delete_label = find_elements(self.driver,
                                                "//div[@class='b-Segment__selectedLabelsTag']//button[@class='b-Button']")
            if button_delete_label:
                return False
            return True

    def get_reviewed_label(self):
        with allure.step('Get labels from correction judgment'):
            review_label_els = self.app.active_segment().find_elements('xpath',
                ".//div[@class='b-CorrectedAnnotation']//div[@class='b-LabelsList__tag']/span")
            list_of_selected_reviewed_label = [review_label_el.text for review_label_el in review_label_els]
            return list_of_selected_reviewed_label


class DataUnit:

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def activate_iframe_on_unit_page(self):
        with allure.step('Activate iframe on unit page'):
            iframe = find_elements(self.app.driver, "//iframe[contains(@name, 'unit_page')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)
            iframe = find_elements(self.app.driver, ".//iframe[contains(@src, 'AudioTranscription')]")
            element_to_the_middle(self.app.driver, iframe[0])
            time.sleep(1)
            self.app.driver.switch_to.frame(iframe[0])
            time.sleep(2)

    def worker_id_dropdown_button_is_displayed(self, is_not=True):
        with allure.step("Check if dropdown is displayed on toolbar"):
            btn = find_elements(self.app.driver,
                                "//div[@class='b-DropdownButton']//button[contains(@class, 'b-DropdownButton__button')]//*[local-name() = 'svg']")
            if is_not:
                assert len(btn) > 0, "Dropdown is not displayed on the page"
            else:
                assert len(btn) == 0, "Link %s is displayed on the page"

    def click_worker_id_dropdown_button(self):
        with allure.step("Click dropdown on toolbar"):
            btn = find_elements(self.app.driver,
                                "//div[@class='b-DropdownButton']//button[contains(@class, 'b-DropdownButton__button')]//*[local-name() = 'svg']")
            assert len(btn) > 0, "Dropdown button is not found"
            btn[0].click()
            time.sleep(2)

    def click_worker_id_from_dropdown_list(self, worker_id):
        with allure.step("Click worker id %s from dropdown" % worker_id):
            item = find_elements(self.app.driver,
                                 "//div[@class='b-DropdownButton__content']//div[contains(@class,'b-JudgmentsSwitcher__item') and text()='%s']" % worker_id)
            assert len(item) > 0, "Dropdown list item is not found"
            item[0].click()
            time.sleep(2)

    def get_number_of_contributors_from_dropdown_list(self):
        with allure.step("Get number of contributors from dropdown list"):
            item = find_elements(self.app.driver,
                                 "//div[@class='b-DropdownButton__content']//div[contains(@class,'b-JudgmentsSwitcher__item')]")
            return len(item)
