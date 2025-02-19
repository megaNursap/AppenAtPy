import time

from adap.ui_automation.utils.selenium_utils import find_elements


class Support:
    # XPATH
    USER_ROLE = "//span[text()='Select role']"
    USER = "//span[text()='Select user']"
    EDIT_USER = "//div[text()='Support (Ac)']"
    elements = {
        "Support User Role":
            {"xpath": USER_ROLE,
             "type": "dropdown"
             },
        "Member Name":
            {"xpath": USER,
             "type": "dropdown"
             },
        "Edit Member Name":
            {"xpath": EDIT_USER,
             "type": "dropdown"
             }
    }

    def __init__(self, project):
        self.project = project
        self.app = project.app

    def fill_out_fields(self, data, add_more_members=False):
        for field, value in data.items():
            if value:
                if self.elements[field]['type'] == 'dropdown':
                    el = find_elements(self.app.driver, self.elements[field]['xpath'])
                    assert len(el), "Field %s has not been found" % field
                    if add_more_members:
                        el[-1].click()
                    else:
                        el[0].click()
                    time.sleep(1)
                    option = find_elements(self.app.driver,
                                           "//div[contains(@id,'react-select')][.//div[contains(text(),'%s')]]" % value)
                    assert len(option), "Value %s has not been found" % value
                    option[0].click()
                    time.sleep(2)

    def verify_support_team_information_is_displayed(self, user_role, member_name, phone_number, email, is_not=True):
        support_team = find_elements(self.app.driver, "//tr[.//td[contains(.,'%s')]]"
                                               "[.//td[contains(.,'%s')]]"
                                               "[.//td[contains(.,'%s')]]"
                                               "[.//td[contains(.,'%s')]]" % (user_role, member_name, phone_number, email))
        if is_not:
            assert len(support_team) > 0, "Support team is not displayed on the page"
        else:
            assert len(support_team) == 0, "Support team is displayed on the page"

    def delete_support_team_member(self, index=-1):
        delete_icon = find_elements(self.app.driver, "//button[contains(@data-testid, 'project-setup--support-team--remove-user')]//*[local-name() = 'svg']")
        delete_icon[index].click()
        time.sleep(2)

