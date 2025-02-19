import datetime
import re
import time


import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.ui_automation.services_config.job.job_data import Data
from adap.ui_automation.services_config.job.job_design import Design
from adap.ui_automation.services_config.job.job_ipa import IPA
from adap.ui_automation.services_config.job.job_judgements import Judgements
from adap.ui_automation.services_config.job.job_launch import Launch
from adap.ui_automation.services_config.job.job_monitor import Monitor
from adap.ui_automation.services_config.job.job_quality import Quality
from adap.ui_automation.services_config.job.job_results import Results
from adap.ui_automation.utils.js_utils import get_text_excluding_children
from adap.ui_automation.utils.page_element_utils import click_rebrand_popover
from adap.ui_automation.utils.selenium_utils import find_element, find_elements

class Job:

    def __init__(self, app):
        self.app = app
        self.data = Data(self)
        self.design = Design(self)
        self.launch = Launch(self)
        self.monitor = Monitor(self)
        self.quality = Quality(self)
        self.results = Results(self)
        self.judgements = Judgements(self)
        self.ipa = IPA(self)

    def search_jobs_by_id(self, job_id):
        with allure.step('Search job by id: %s' % job_id):
            # search_field = find_element(self.app.driver, "//input[@placeholder='Search Jobs']")
            search_field = find_element(self.app.driver, "//input[@name='query']")
            search_field.send_keys(job_id, Keys.RETURN)

    # update xpath to be contains to make it work on fed
    def pick_job_by_id(self, job_id):
        with allure.step('Pick job by id: %s' % job_id):
            job = find_elements(self.app.driver, "//a[contains(@href,'/jobs/%s')]" % job_id)
            assert len(job), "Job %s has not been found" % job_id
            job[0].click()
            time.sleep(2)

    def open_job_with_id(self, job_id):
        with allure.step('Open job with id: %s' % job_id):
            self.search_jobs_by_id(job_id)
            self.pick_job_by_id(job_id)
            self.app.driver.implicitly_wait(1)
            # modal_window = find_elements(self.app.driver, "//div[@class='rebrand-modal-content']//button[text()='Skip']")
            # if len(modal_window) > 0:
            #     modal_window[0].click()
            #
            # status_modal_window = find_elements(self.app.driver,
            #                                     "//div[@class='rebrand-popover-content']//*[local-name() = 'svg']")
            # if len(status_modal_window) > 0:
            #     status_modal_window[0].click()
            #     time.sleep(1)
            #
            # popup_alert = find_elements(self.app.driver,
            #                             "//a[contains(@class, 'rebrand-Popover__closeIcon')]//*[local-name() = 'svg']")
            # if len(popup_alert) > 0:
            #     popup_alert[0].click()

            click_rebrand_popover(self.app.driver)
            self.app.driver.implicitly_wait(5)
            time.sleep(2)

    def verify_job_id_is(self, job_id):
        with allure.step('Verify job id: %s'):
            self.app.verification.text_present_on_page("JOB ID %s" % job_id)

    def open_tab(self, tab_name):
        with allure.step(f'Open job tab {tab_name}'):
            adjust_tab_name=tab_name.lower()
            tab = find_elements(self.app.driver,
            f"//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{adjust_tab_name}') and contains(@href,'/jobs/')]")
            assert len(tab)>0, f"Tab {adjust_tab_name} has not found"
            tab[0].click()
            time.sleep(3)

            # rebrand_popover = self.app.driver.find_elements('xpath',
            #     "//*[text()='Status Icon' or text()='Home']/..//*[local-name() = 'svg']")
            # if len(rebrand_popover) > 0: rebrand_popover[0].click()
            self.app.user.close_guide()

            time.sleep(3)

    def open_action(self, action_name):
        with allure.step('Open job action: %s' % action_name):
            if 'Copy' not in action_name:
                # tab = find_elements(self.app.driver,
                #                     "//*[@id='js-job-action-links']//*[text()='%s']" % action_name)
                # if len(tab) == 0:
                tab = find_elements(self.app.driver, "//a[contains(@href, '%s')]" % action_name.lower())

                assert len(tab) > 0, "Tab %s has not found" % action_name
                tab[0].click()
                time.sleep(2)
            else:
                menu_items = action_name.split(',')
                if len(menu_items) == 2 and (
                        menu_items[1] in ("All Rows", "Test Questions Only", "No Rows", "Unfinalized Rows")):
                    sub_menu = menu_items[1]
                else:
                    assert False, "Please, provide correct menu item"

                # # open menu Copy
                # tab = find_elements(self.app.driver,
                #                     "//*[@id='js-job-action-links']//span[text()='Copy']")
                # # new UI
                # if len(tab) == 0:
                #     tab = find_elements(self.app.driver,
                #                         "//div[contains(@class,'rebrand-JobLocalNavActions')]//a[2]")
                tab = find_elements(self.app.driver, "//a[contains(@href, 'preview_redirect')]/following-sibling::a[1]")
                assert len(tab) > 0, "Link Copy has not been found"
                tab[0].click()
                time.sleep(2)

                # open submenu
                # https://appen.atlassian.net/browse/CW-7985
                el = find_elements(self.app.driver, "//label[@for='Options']/..//div[@tabindex]")
                el[0].click()
                time.sleep(2)
                # tab = find_elements(self.app.driver,
                #                     "//span[contains(@class,'rebrand-Select__option-value') and contains(.,'%s')]" % sub_menu)
                tab = find_elements(self.app.driver,
                                    "//span[contains(@class,'b-Select__option-value') and contains(.,'%s')]" % sub_menu)
                assert len(tab) > 0, "Menu %s has not found" % sub_menu
                tab[0].click()
            time.sleep(5)

    def open_settings_tab(self, tab_name):
        with allure.step('Open settings menu: %s' % tab_name):
            if 'Quality Control' not in tab_name:
                tab = find_elements(self.app.driver,
                                    "//a[contains(@href, '/settings') and text()='%s']" % tab_name)

                assert len(tab) > 0, "Tab %s has not found" % tab_name
                tab[0].click()
            else:
                menu_items = tab_name.split(',')

                if len(menu_items) == 2 and (
                        menu_items[1] in ("Test Questions", "Quality Control Settings", "Dynamic Judgments")):
                    sub_menu = menu_items[1]
                else:
                    assert False, "Please, provide correct menu item for Quality Control page"

                # open menu Quality control
                # tab = find_elements(self.app.driver,
                #                     "//button[.//span[text()='Quality Control']]|//a[normalize-space(text())='Quality Control']")
                tab = find_elements(self.app.driver,
                                    "//div[text()='Quality Control']//*[local-name()='svg']")
                assert len(tab) > 0, "Tab Quality Control has not found"
                tab[0].click()

                # open submenu
                tab = find_elements(self.app.driver,
                                    "//a[text()='%s']" % sub_menu)
                assert len(tab) > 0, "Tab %s has not been found" % sub_menu
                tab[0].click()
            time.sleep(1)

    def click_on_gear_for_job(self, job_id, sub_menu_action=None):
        with allure.step('Click on the gear for Job: %s' % job_id):
            job_xpath = "//tr[@data-test-id='job-%s']//td[@data-test-id='job-menu']" % job_id
            job_menu = find_elements(self.app.driver, job_xpath + "//a" )
            if len(job_menu) > 0:
                job_menu[0].click()
            else:
                assert False, f"Job {job_id} menu has not found"

            if sub_menu_action:
                job_menu_action = find_elements(self.app.driver, job_xpath + "//a[text()='%s']" % sub_menu_action)
                if len(job_menu_action) > 0:
                    job_menu_action[0].click()
                else:
                    assert False, f"Action {sub_menu_action} has not been found"


    def open_any_job(self, create_new=False, api_key=None):
        with allure.step('Open any existing job'):
            jobs = [x.get_attribute('data-id') for x in find_elements(self.app.driver, "//tr[@class='job-row']")]
            if len(jobs) == 0 and create_new == True and api_key is not None:
                resp = JobAPI(api_key).create_job()
                if resp.status_code == 200:
                    job_id = resp.json_response['id']
                    self.open_job_with_id(job_id)
            elif len(jobs) > 0:
                self.open_job_with_id(jobs[0])
            else:
                assert False, "No jobs have been found"

    def open_team_jobs(self, team):
        with allure.step(f'Open team jobs: {team}'):
            el = find_elements(self.app.driver, "//a[@href='/jobs'][.//div]")

            if len(el) > 0:
                el[0].click()
                team_link = find_elements(self.app.driver,
                                          f"//a[@href='/jobs' and text()='{team}'] | //a[@href='/' and text()='{team}']")
                if len(team_link) > 0:
                    team_link[0].click()
            else:
                assert False, "Team %s has not been found"
            time.sleep(2)

    def create_new_job_from_template(self, template_type, job_type):
        with allure.step('Create new job from template: %s - %s ' % (template_type, job_type)):
            if '/jobs' in self.app.driver.current_url:
                find_elements(self.app.driver, "//*[text()='Create Job']")[0].click()

            find_elements(self.app.driver, "//a[text()='%s' and @href]" % template_type)[0].click()
            time.sleep(2)
            find_elements(self.app.driver, "//div[text()='%s']" % job_type)[0].click()
            time.sleep(2)
            find_elements(self.app.driver,
                          "//a[text()='Use this template']")[0].click()
            time.sleep(2)

            status_modal_window = find_elements(self.app.driver,
                                                "//div[@class='popover-content']//*[local-name() = 'svg']")
            if len(status_modal_window) > 0:
                status_modal_window[0].click()
                time.sleep(1)

            rebrand_popover = self.app.driver.find_elements('xpath',
                "//*[text()='Status Icon']/..//*[local-name() = 'svg']")
            if len(rebrand_popover) > 0:
                rebrand_popover[0].click()

            time.sleep(1)

    def create_new_job_from_scratch(self):
        with allure.step('Create new job from scratch'):
            if '/jobs' in self.app.driver.current_url:
                find_elements(self.app.driver, "//*[text()='Create Job']")[0].click()
                time.sleep(1)
            find_elements(self.app.driver, "//*[text()='Start From Scratch']")[0].click()

    def grab_job_id(self):
        with allure.step('Grab job id'):
            time.sleep(1)
            job = find_elements(self.app.driver,
                                "//*[contains(text(),'job id') or contains(text(),'Job Id') or contains(text(),'JOB ID')]")
            if len(job) > 0:
                _job = job[0].text.lower()
                print("-----", _job)
                return re.findall(r'\b(\d+)\b', _job)[0]
            else:
                print("Job ID: None Provided")
                return None

    def get_available_hosted_channels(self):
        with allure.step('Get available hosted channel'):
            hosted_channel = []
            _channels = find_elements(self.app.driver, "//tr[@class='b-Table__row']")
            for ch in _channels:
                ch_name = ch.find_elements('xpath',".//td")[1]
                hosted_channel.append(ch_name.text)
            return hosted_channel

    def select_hosted_channel_by_name(self, name, save=False):
        with allure.step('Select hosted channel with name %s' % name):
            _channel = find_elements(self.app.driver, "//div[@class='b-ChannelsModal']//tbody//tr[.//td[contains(text(),'%s')]]/..//label[contains(@class, 'b-Checkbox__icon')]" % name)
            assert len(_channel) > 0, "Can not find the channel"
            _channel[0].click()
            time.sleep(1)
            if save:
                self.app.navigation.click_link('Ok')
                self.app.navigation.click_link('Save')
                time.sleep(1)

    def select_hosted_channel_by_index(self, save=False, index=1):
        with allure.step('Select first host channel'):
            _channel = find_elements(self.app.driver,"//label[contains(@class, 'b-Checkbox__icon')]")
            assert len(_channel) > 0, "Can not find the channel"
            _channel[index].click()
            time.sleep(1)
            if save:
                self.app.navigation.click_link('Ok')
                self.app.navigation.click_link('Save')
                time.sleep(1)

    def hosted_channel_is_selected(self, name):
        with allure.step('If hosted channel %s is selected' % name):
            el = find_elements(self.app.driver, "//div[@class='b-ChannelsModal']//tbody//tr[.//td[contains(text(),'%s')]]/..//input" % name)
            if len(el) > 0:
                return el[0].is_selected()
            else:
                assert False, "Checkbox with text - %s has not been found" % name


    def setting_select_contrib_channel(self,env, is_save=True):
        self.app.job.open_action("Settings")
        if env == 'fed':
            self.app.navigation.click_link("Select Contributor Channels")
            self.app.job.select_hosted_channel_by_index(save=is_save)

        else:
            external_chkbox = self.app.driver.find_elements('xpath',"//label[contains(text(),'External')]")
            general_opt = self.app.driver.find_elements('xpath',"//span[contains(text(),'General')]")
            if len(general_opt) == 0:
                assert len(external_chkbox) > 0, "Checkbox 'External' not found"
                external_chkbox[0].click()
                self.app.navigation.click_link('Save')

    # https://appen.atlassian.net/browse/CW-8013 filed to update xpath for it
    def get_user_jobs_ui(self):
        next_page = True
        _jobs = []
        while next_page:
            #jobs_on_page = find_elements(self.app.driver, "//tr[@class='b-Table__row']//span[@class='b-JobListingTableTitleCell__id']")

            jobs_on_page = find_elements(self.app.driver, "//tr//h5")
            if len(jobs_on_page) == 0:
                print("no jobs was found")
                return _jobs

            for j in jobs_on_page:
                # _jobs.append(int(j.get_attribute('data-id')))
                _jobs.append(int(j.text))


            next_page_link = find_elements(self.app.driver, "//span[text()='Page']/../..//a")
            if len(next_page_link) > 1:
                next_page_link[1].click()
                # sometimes, sleep 3 still stay on the same page cause duplicated id being added to list
                time.sleep(6)
            else:
                next_page = False

        return _jobs

    def get_job_status(self):
        with allure.step('Get job status (UI)'):
             # new UI
            nav_status = find_elements(self.app.driver, "//h5//div[@data-tooltip]")
            if len(nav_status) > 0:
                nav_status[0].click()
                time.sleep(1)
                # print(self.app.driver.page_source)
                status = find_elements(self.app.driver,
                                       "//div[contains(text(), 'Status:')]")
                if len(status) > 0:
                    current_status = status[0].get_attribute('innerHTML')
                    return current_status.split("Status: ")[1]

            assert False, "Job's status has not been found on the page"

    def get_job_messages(self):
        with allure.step('Get job messages'):
            msg = find_elements(self.app.driver, "//div[@id='message']//li")
            return [x.text for x in msg]

    def get_internal_link_for_job(self):
        with allure.step('Get internal link for job'):
            el = find_elements(self.app.driver, "//p[text()='Link to Share:']/..//a[contains(@href,'secret')]")
            if len(el) > 0:
                return el[0].get_attribute('href')
            assert False, "Internal link has not been found"

    def create_new_custom_channel(self):
        enable_custom_ch = find_element(self.app.driver, "//input[@id='customChannelsEnabled']")

        if not enable_custom_ch.get_attribute('value'):
            enable_custom_ch.click()

        self.app.navigation.click_link("Add Custom Channel")
        find_element(self.app.driver, "//*[text()='Automatically select contributors']").click()

        ch_name = "new_channel" + datetime.date.today().strftime("%m/%d/%Y")
        find_element(self.app.driver, "//input[@id='b-TextInput__input']").send_keys(ch_name)

    def get_all_custom_channels(self):
        enable_custom_ch = find_elements(self.app.driver, "//span[text()='Custom']")
        assert len(enable_custom_ch) > 0, "Option Custom not found"

        # if not enable_custom_ch.get_attribute('value'):
        enable_custom_ch[0].click()
        time.sleep(1)
        ch_info = []
        _channels = find_elements(self.app.driver, "//tbody//tr")
        for ch in _channels:
            ch_name = ch.find_elements('xpath',".//td")[1]
            ch_info.append(ch_name.text)

        return ch_info

    def set_up_job_owner(self, owner):
        with allure.step(f'Set up new job owner: {owner}'):
            el = find_elements(self.app.driver, "//input[@name='owner']")
            assert len(el), "Owner element has not been found"
            el[0].clear()
            el[0].send_keys(owner)

    def get_job_owner(self):
        with allure.step(f'Get job owner'):
            el = find_elements(self.app.driver, "//input[@name='owner']")
            assert len(el), "Owner element has not been found"

            return el[0].get_attribute('value')

    def select_custom_channel(self, name):
        _channel = find_elements(self.app.driver,
                                f"//tbody//tr[.//td[text()='{name}']]/td//label")
        assert len(_channel) > 0, f"Channel '{name}' not found in list"

        _channel[0].click()
        self.app.navigation.click_link("Save")

    def preview_job(self):
        with allure.step('Preview job'):
            el = find_elements(self.app.driver, "//a[contains(@href, '/preview_redirect')]")
            assert len(el), "Preview btn has not been found"
            el[0].click()
            window_after = self.app.driver.window_handles[1]
            self.app.navigation.switch_to_window(window_after)

    def add_job_to_project(self, job_id, project_name):
        with allure.step('Add job %s to the project %s' % (job_id, project_name)):
            time.sleep(3)
            job = find_elements(self.app.driver, "//tr[.//h5[text()='%s']]//td" % job_id)
            assert len(job), "Job %s has not been found" % job_id

            # job[0].find_element('xpath',"//td[@class='project']").click()
            job[-1].find_element('xpath',".//a[@href='/jobs' or @href='/']").click()
            time.sleep(1)
            # find_element(self.app.driver, "//div[@id='s2id_project-single-select']").click()

            find_element(self.app.driver,"//li[.//a[text()='Move To A Project']]").click()
            time.sleep(1)
            find_element(self.app.driver, "//span[text()='Select ...']").click()
            time.sleep(1)
            find_element(self.app.driver, "//input[@name='job-project']/..//li[text()='%s']" % project_name).click()
            time.sleep(1)

            self.app.navigation.click_link("Add")

    def get_wf_indicator_for_job(self, job_id):
        with allure.step(f'Get WF indicator for job id: {job_id}'):
            job = find_elements(self.app.driver, "//tr[.//a[@href='/jobs/%s/']]" % job_id)
            assert len(job) > 0, "Job %s has not been found on the page"  % job_id

            wf_link = job[0].find_elements('xpath',".//a[contains(@href,'workflows')]")

            if not len(wf_link): return None

            wf_name = job[0].find_element('xpath',".//a[contains(@href,'workflows')]/..")

            wf_id = wf_link[0].get_attribute('href')
            wf_id = wf_id.split('/')[-1]

            return {"wf_name": wf_name.text,
                    "wf_id": wf_id}

    def get_checkbox_status(self, name):
        with allure.step(f'Get checkbox status {name}'):
            el = find_elements(self.app.driver, "//label[text()='%s']/..//input" % name)
            assert len(el) > 0, "Checkbox %s has not been found on the page" % name

            return el[0].get_attribute('checked')

    def fill_out_ticket_summary_on_homepage(self, message):
        with allure.step(f'type message in ticket summary textbox {message}'):
            el = find_elements(self.app.driver, "//textarea[@id='ticket_summary' or contains(@class,'b-Textarea__input')]")
            assert len(el) > 0, "Ticket summary text box has not been found on the page"
            el[0].clear()
            el[0].send_keys(message)

    def verify_file_uploaded_homepage(self, filename):
        with allure.step(f'verify file uploaded on homepage {filename}'):
            el = find_elements(self.app.driver, "//div[@class='b-inline-uploader__file-name']")
            if len(el) == 0:
                # sandbox
                el = find_elements(self.app.driver, "//div[@class='b-FileUpload__file-selected-text']//div")

            assert len(el) > 0, f"uploaded file '{filename}' has not been found on the page"
            file_name_from_page = el[0].text
            if file_name_from_page == filename[1:]:
                print(f"file '{filename}' has been uploaded successfully.")
            else:
                assert False, ("\n '%s' file is shown on the page where as Expected is '%s'" % (
                    file_name_from_page, filename[1:]))

    # this function will verify the template name showing on recent tab
    def verify_recent_tab_template_homepage(self, template_name):
        with allure.step(f'verify recent tab template {template_name}'):

            el = find_elements(self.app.driver, "//div[@class='b-recent-template__name']")
            if len(el) == 0:
                el = find_elements(self.app.driver, "//div[@class='b-TemplateTypes__recentTemplate']//div")
            assert len(el) > 0, "Template name is not displayed on recent tab"
            template_name_from_recent_tab = get_text_excluding_children(self.app.driver, el[0])
            if template_name_from_recent_tab == template_name:
                print(f"'{template_name}' template is displayed on recent tab")
            else:
                assert False, ("\n '%s' template is displayed on recent tab where as Expected is '%s'" % (
                    template_name_from_recent_tab, template_name))

    def click_on_template_type(self, template_name):
        with allure.step('Click on template: %s' % template_name):
            # el = find_elements(self.app.driver,
            #                    "//div[@class='rebrand-template-thumbnail__title' or @class='rebrand-TemplateTypes__itemTitle' and contains(text(),'%s')]" % template_name)
            el = find_elements(self.app.driver,
                          "//a[text()='%s']" % template_name)
            assert len(el) > 0, "template '%s' not found" % template_name
            el[0].click()
            time.sleep(3)

    def delete_attached_file(self):
        with allure.step("Click on 'x' for deleting the file attached on homepage"):
            el = find_elements(self.app.driver,
                               "//div[@class='b-inline-uploader__preview-container']//i[@class='fa fa-times']")
            assert len(el) > 0, "'x' button has not been found"
            el[0].click()
            time.sleep(2)

    def verify_job_templates_present_on_welcomepage(self, template_list):
        with allure.step("verify '%s' template is present on home page" % template_list):
            for names in template_list:
                # el = find_elements(self.app.driver,
                #                    "//div[@class='rebrand-template-thumbnail__title' or @class='rebrand-TemplateTypes__itemTitle' and contains(text(),'%s')]" % names)
                el = find_elements(self.app.driver,
                              "//li/a[text()='%s']" % names)
                assert len(el) > 0, "'%s' template has not been found" % names

    def open_help_center_menu(self):
        with allure.step("click on questionMark welcomePage"):
            el = find_elements(self.app.driver, "//div[contains(@class,'rebrand-HelpCenterIcon')]//*[local-name()='svg']")
            assert len(el) > 0, "Question Mark link has not been found"
            el[0].click()

    def input_automatic_launch_row_period(self, time_period):
        with allure.step("Input auto launch period time"):
            el = find_elements(self.app.driver, "//input[@name='autoOrderTimeout']")
            assert len(el) > 0, "Time period input filed is not found"
            el[0].send_keys(time_period)
            self.app.navigation.click_link('Save')
            time.sleep(2)

    def verify_email_link(self, expected_email):
        with allure.step("verify email link from question mark on homepageis talking to '%s'" % expected_email):
            el = find_elements(self.app.driver, "//a[@class='b-HelpCenter__link']")
            email_page = el[0].get_attribute('href')
            if email_page == expected_email:
                print("\n email link is taking to '%s'" % expected_email)
            else:
                assert False, ("\n email is  taking to '%s', where as expected is '%s' " % (email_page, expected_email))

    # this function will get the header names from the table present on use case template page
    def verify_table_header_on_usecase_template_page(self, header_name):
        with allure.step("verify '%s' header name" % header_name):
            heads = self.app.driver.find_elements('xpath',
                "//table[contains(@class,'table b-templates-table')]//thead//tr//th")
            for i in range(len(header_name)):
                for j in range(len(heads)):
                    if i == j:
                        if header_name[i] == heads[j].text:
                            print("\n Header '%s' is displayed on the preview page" % header_name[i])
                        else:
                            assert False, (
                                    "\n Header '%s' is displayed on the preview page where as expected is '%s'" % (
                                heads[j].text, header_name[i]))


    def strip_sentence_FP(self, target_sentence):
        return ''.join(target_sentence.partition("increases")[:2])

    # this function will verify the sub options present for all the headings on fair pay settings page
    def verify_pay_settings_sub_options_FP(self, data):
        with allure.step(f'Verify "{data}" is present on the page'):
            for heading, value in data.items():
                if heading == "When the price per judgment falls below current PPJ:":
                    for sub_options in value:
                        element = find_elements(self.app.driver,"//div[contains(@class,'rebrand-FairPayFormSettings__title')][contains(text(),'%s')]"
                                                "/..//span[contains(text(),'%s')]" % (heading, sub_options))
                        assert (len(element) > 0), ("sub option '%s' has not been found", sub_options)
                else:
                    short_sentence = self.strip_sentence_FP(heading)
                    for sub_options in value:
                        element = find_elements(self.app.driver,
                                                "//*[text()[contains(.,'%s')]]/.."
                                                "/following-sibling::div//span[contains(text(),'%s')]" %(short_sentence, sub_options))
                        assert (len(element) > 0), ("sub option '%s' has not been found" %sub_options)

    # this function will check the default options selected for each heading
    def verify_default_selected_options_for_pay_settings_FP(self, data, is_not=True):
        with allure.step('Verify "%s" is default option for %s' % (data, is_not)):
            for key, value in data.items():
                if key == "When the price per judgment falls below current PPJ:":
                    element = find_elements(self.app.driver,
                                            "//div[contains(@class,'rebrand-FairPayFormSettings__title')][contains(text(),'%s')]"
                                            "/..//span[contains(text(),'%s')]/..//input" % (key, value))
                    assert (len(element) > 0), "sub option has not been found"
                    default_status = element[0].is_selected()
                else:
                    short_sentence = self.strip_sentence_FP(key)
                    element = find_elements(self.app.driver,
                                            "//div[contains(@class,'rebrand-FairPayFormSettings__title')]//*[text()[contains(.,'%s')]]/.."
                                            "/following-sibling::div//span[contains(text(),'%s')]/..//input" % (
                                                short_sentence, value))
                    assert (len(element) > 0), "sub option has not been found"
                    default_status = element[0].is_selected()

                if is_not:
                    if default_status:
                        print("\n '%s' have '%s' as default option selected" % (key, value))
                    else:
                        assert False, ("\n '%s' does not have '%s' as default option selected " % (key, value))
                if not is_not:
                    if not default_status:
                        print("\n '%s' does not have '%s' as default option selected (as expected!)" % (key, value))
                    else:
                        assert False, ("\n '%s' have '%s' as default option selected (but it must not!)" % (key, value))

    # this function will add text in the box and verify the same on the graph
    def verify_entered_percentage_is_shown_in_graph_FP(self, data, is_not=True):
        with allure.step('Verify "%s" is present= %s on the graph' % (data, is_not)):
            for key, value in data.items():
                short_sentence = self.strip_sentence_FP(key)
                element = find_elements(self.app.driver,
                                        "//*[text()[contains(.,'%s')]]/..//div//input" % (
                                            short_sentence))
                assert (len(element) > 0), "text box has not been found"
                element[0].clear()
                element[0].send_keys(value)

                # getting the %age text from the graph
                el = find_elements(self.app.driver,
                                   "//div[contains(text(), 'Up to')]")
                assert (len(el) > 0), "graph text has not been found"
                graph_text = el[0].text

                # getting the percentage from the text
                percentage = graph_text.split(" ")[2]
                if is_not:
                    if percentage == value:
                        print(f"\n '{value}' is shown in the graph")
                    else:
                        assert False, ("\n '%s' is  not shown in the graph. Expected is '%s'" % (value, graph_text))
                if not is_not:
                    if not percentage == value:
                        print(f"\n '{value}' is shown in the graph (as expected!)")
                    else:
                        assert False, f"\n '{value}' is shown in the graph (but it must not!)"

    # this function will select the radio button option and verify the same on the graph
    def verify_selected_option_is_shown_in_graph(self, data, is_not=True):
        with allure.step('Verify the text "%s" is present= %s on the graph' % (data, is_not)):
            for key, value in data.items():
                if key == "When the price per judgment falls below current PPJ:":
                    element = find_elements(self.app.driver,
                                            "//div[contains(@class,'rebrand-FairPayFormSettings__title')][contains(text(),'%s')]"
                                            "/..//span[contains(text(),'%s')]" % (key, value))
                    assert (len(element) > 0), "sub option has not been found"
                    element[0].click()
                    graph_text = find_elements(self.app.driver,
                                               "//div[contains(@class,'rebrand-ExplanationChart__block rebrand-ExplanationChart__block--main')]"
                                               "//div[contains(text(),'%s')]" % value)

                elif key == "When the price per judgment increases up to:":
                    short_sentence = self.strip_sentence_FP(key)
                    element = find_elements(self.app.driver,
                                            "//div[contains(@class,'rebrand-FairPayFormSettings__title')]//*[text()[contains(.,'%s')]]/.."
                                            "/following-sibling::div//span[contains(text(),'%s')]" % (
                                                short_sentence, value))
                    assert (len(element) > 0), "sub option has not been found"
                    element[0].click()
                    graph_text = find_elements(self.app.driver,
                                               "//div[contains(@class,'rebrand-ExplanationChart__block rebrand-ExplanationChart__block--mainCurrent')]"
                                               "//div[contains(@class,'rebrand-ExplanationChart__borderLabel--mainCurrent')]"
                                               "/preceding-sibling::div[contains(text(),'%s')]" % value)
                else:
                    short_sentence = self.strip_sentence_FP(key)
                    element = find_elements(self.app.driver,
                                            "//div[contains(@class,'rebrand-FairPayFormSettings__title')]//*[text()[contains(.,'%s')]]/.."
                                            "/following-sibling::div//span[contains(text(),'%s')]" % (
                                                short_sentence, value))
                    assert (len(element) > 0), "sub option has not been found"
                    element[0].click()
                    graph_text = find_elements(self.app.driver,
                                               "//div[contains(@class,'rebrand-ExplanationChart__block rebrand-ExplanationChart__block--main')]"
                                               "//div[contains(@class,'rebrand-ExplanationChart__borderLabel--main')]"
                                               "/preceding-sibling::div[contains(text(),'%s')]" % value)

                if is_not:
                    if len(graph_text) > 0:
                        print("\n The text %s is displayed on the graph" % value)
                    else:
                        assert False, ("\n The text %s is NOT displayed on the graph" % value)
                if not is_not:
                    if not len(graph_text) > 0:
                        print("\n The text %s is NOT displayed on the graph (as expected!)" % value)
                    else:
                        assert False, ("\n The text %s IS displayed on the graph (but it must not!)" % value)

    # on setting->quality control->quality control settings
    def set_minimum_time_per_page(self, seconds):
        with allure.step("set minimum time per page for '%s' second" % seconds):
            input_time = find_elements(self.app.driver, "//input[@name='minAssignmentDuration']")
            assert len(input_time) > 0, "input textbox for minimum time per page is not found"
            input_time[0].clear()
            input_time[0].send_keys(seconds)

    def get_minimum_time_per_page(self):
        with allure.step("get minimum time per page"):
            input_time = find_elements(self.app.driver, "//input[@name='minAssignmentDuration']")
            assert len(input_time) > 0, "input textbox for minimum time per page is not found"
            return input_time[0].get_attribute('value')

    def set_max_judgments_per_contributors(self, seconds):
        with allure.step("set max judgments time per contributor for '%s' second" % seconds):
            input_time = find_elements(self.app.driver, "//input[@name='maxJudgmentsPerWorker']")
            assert len(input_time) > 0, "input textbox for max judgments time per contributor is not found"
            input_time[0].clear()
            input_time[0].send_keys(seconds)

    def get_max_judgments_per_contributors(self):
        with allure.step("get max judgments time per contributor"):
            input_time = find_elements(self.app.driver, "//input[@name='maxJudgmentsPerWorker']")
            assert len(input_time) > 0, "input textbox for max judgments time per contributor is not found"
            return input_time[0].get_attribute('value')

    def get_activation_threshold(self):
        with allure.step("get activation threshold"):
            threshold = find_elements(self.app.driver, "//input[@name='judgmentDistributionActivationThreshold']")
            assert len(threshold) > 0, "threshold is not found"
            return threshold[0].get_attribute('value')

    def add_regular_expression(self, text):
        with allure.step("add regular expression"):
            regular_expression = find_elements(self.app.driver, "//input[@name='cmlRules.0.acceptableDistribution.0']")
            assert len(regular_expression) > 0, "regular expression is not found"
            regular_expression[0].clear()
            regular_expression[0].send_keys(text)

    def delete_regular_expression(self):
        with allure.step("delete regular expression"):
            delete = find_element(self.app.driver, "//span[text()='Regular Expression']/../../..//*[local-name() = 'svg']")
            delete.click()

    def click_edit_project_id(self):
        el = find_elements(self.app.driver, "//label[contains(text(),'Appen Connect Project ID')]/..//a[text()='Edit']")
        assert len(el) > 0, "Edit Project ID has not been found"
        el[0].click()

    def enter_job_id_delete_job_window(self, job_id):
        job_id_input = find_element(self.app.driver, "//input[@name='jobId']")
        job_id_input.send_keys(job_id)

    def click_on_delete_this_job(self):
        delete_job_button = find_element(self.app.driver,
                                         "//a[contains(@href, '/jobs') and text()='I understand the conditions, delete this job']")
        delete_job_button.click()

    def verify_job_action_not_in_dropdown_menu(self, job_id, sub_menu_action):
        with allure.step('Verify %s action job action not found' % sub_menu_action):
            job_xpath = "//tr[@data-test-id='job-%s']//td[@data-test-id='job-menu']" % job_id

            job_menu_actions = [element.text for element in find_elements(self.app.driver,
                                                                         job_xpath + "//li[contains(text(), 'Organize Project')]/following-sibling::li")]

            assert sub_menu_action not in job_menu_actions, "%s present in job menu actions"