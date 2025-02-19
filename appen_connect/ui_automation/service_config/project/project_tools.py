import time

from adap.ui_automation.utils.selenium_utils import find_elements


class Tools:
    # XPATH
    EXTERNAL_SYSTEM = "//input[@name='hasExternalSystem']/../span[@class='overlay']"
    EXTERNAL_SYSTEM_OPTIONS = "//input[@name='externalSystem']"
    AVAILABLE_PRODUCTIVE_DATA = "//input[@name='hasProductivityData']/../span[@class='overlay']"
    SECURE_IP_ACCESS = "//input[@name='hasIPRestrictions']/../span[@class='overlay']"
    ALLOWED_IP = "//input[@name='ipAddress0']"
    SWFH_URL = "//input[@placeholder='Input SWFH url']"

    elements_tools = {
        "External System checkbox":
            {"xpath": EXTERNAL_SYSTEM,
             "type": "checkbox"
             },
        "External System":
            {"xpath": EXTERNAL_SYSTEM_OPTIONS,
             "type": "dropdown"
             },
        "Secure IP Access":
            {"xpath": SECURE_IP_ACCESS,
             "type": "checkbox"
             },
        "Allowed IPs":
            {"xpath": ALLOWED_IP,
             "type": "input"
             },
        "SWFH URL":
            {"xpath": SWFH_URL,
             "type": "input"
             }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data):
        self.project.enter_data(data=data, elements=self.elements_tools)

    def add_allowed_ip(self, ip):
        self.app.navigation.click_btn('Add Other IP')
        el = find_elements(self.app.driver, "//input[contains(@name, 'ipAddress')]")
        el[-1].send_keys(ip)
        time.sleep(1)

    def remove_allowed_ip(self, ip):
        el = find_elements(self.app.driver, "//input[@value='%s']/../../../button" % ip)
        el[0].click()
        time.sleep(1)

    def load_project(self, data):
        self.project.load_project(data=data, elements=self.elements_tools)

    def remove_data_from_fields(self, data):
        self.project.remove_data(data, self.elements_tools)

    def get_current_user_groups(self):
        groups = find_elements(self.app.driver, "//input[contains(@name,'userGroup')]//..//div[contains(@class, 'singleValue')]")
        return [x.text for x in groups]

    def add_user_group(self, group):
        new_group = find_elements(self.app.driver, "//span[text()='Select user group']")
        if len(new_group) == 0:
            self.app.navigation.click_btn("Add Other User Group")

        new_group_input = find_elements(self.app.driver, "//span[text()='Select user group']")
        assert len(new_group_input) > 0, "Input field Select user Group has not been found"

        new_group_input[0].click()
        option = find_elements(self.app.driver,
                               "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % group)

        assert len(option), "Value %s has not been found" % group
        option[0].click()
        time.sleep(1)

    def edit_user_group(self, current_group, new_group):
        old_group = find_elements(self.app.driver,
                                  "//div[contains(@class, 'singleValue') and text()='%s']" % current_group)
        assert len(old_group) > 0, "Group %s has not been found" % current_group

        old_group[0].click()
        option = find_elements(self.app.driver,
                               "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % new_group)

        assert len(option), "Value %s has not been found" % new_group
        option[0].click()
        time.sleep(1)

    def delete_user_group(self, group):
        _group = find_elements(self.app.driver,
                                  "//div[contains(@class,'container')][.//div[text()='%s']]/../.." % group)
        assert len(_group) > 0, "Group %s has not been found" % group

        del_btn = _group[0].find_element('xpath',".//button[contains(@data-testid, 'delete')]")
        del_btn.click()
        self.app.navigation.click_btn("Proceed")

    def get_current_user_groups_view(self):
        groups = find_elements(self.app.driver, "//table[.//label[text()='User Group']]//tr//td")
        return [x.text for x in groups]
# TODO create new tool, not omplemented yet