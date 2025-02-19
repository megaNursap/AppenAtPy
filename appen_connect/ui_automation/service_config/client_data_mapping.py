import time
import allure
from selenium.webdriver.common.keys import Keys

from adap.ui_automation.utils.js_utils import inner_scroll_to_element, scroll_to_element
from adap.ui_automation.utils.selenium_utils import find_elements, find_element


class ClientDataMapping:
    MAPPING_TYPE = "//input[@id='filterByMapping']"
    CLIENT = "//input[@id='filterByClient']"
    UPLOAD_FILE_INPUT = "//div[@data-baseweb='file-uploader']//input[@type='file']"
    TOOL_NAME = "//div[contains(text(),'Select...')]"

    elements = {
        "Mapping Type":
            {"xpath": MAPPING_TYPE,
             "type": "dropdown"
             },
        "Client":
            {"xpath": CLIENT,
             "type": "dropdown"
             },
        "Tool Name":
            {"xpath": TOOL_NAME,
             "type": "dropdown"
             },

        "Upload File":
            {"xpath": UPLOAD_FILE_INPUT,
             "type": "file"
             }
    }

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    def enter_data(self, data):
        self.app.ac_project.enter_data(data=data, elements=self.elements)
        time.sleep(4)

    def get_accepted_rows(self):
        element = self.app.driver.find_element('xpath',
            "(//div[contains(text(),'accepted rows')]/preceding-sibling::div)[1]")
        accepted_rows = element.get_attribute("innerText")
        return accepted_rows

    def get_rejected_rows(self):
        element = self.app.driver.find_element('xpath',
            "(//div[contains(text(),'rejected rows')]/preceding-sibling::div)[1]")
        rejected_rows = element.get_attribute("innerText")
        return rejected_rows

    def setup_filter(self, index, value):
        # el = find_elements(self.app.driver, '//div[contains(@class,"override_filter__control")]')
        with allure.step('Set up: show %s items on the page at the index %s' % (value,index)):
            el = find_elements(self.app.driver, '//div[@data-baseweb="select"]')

            assert len(el), "Field Filter by %s  has not been found" % value
            el[index].click()
            time.sleep(1)
            option = find_elements(self.app.driver, "//li//div[contains(text(),'%s')]" % value)
            assert len(option), "Value %s has not been found" % value
            option[0].click()
            time.sleep(2)

    def _search_mapping_on_client_mapping_list(self, search_field='index', value=0):
        with allure.step('Search mapping in client mapping list by %s=%s' % (search_field, value)):
            try:
                if search_field == 'id':
                    report = find_elements(self.driver, "//div[contains(text(),'%s')]/" % value)[0]
                if search_field == 'index':
                    report = find_elements(self.driver, "//div[@role='rowgroup']//div[@role='row']")[int(value)]
                return report
            except:
                return None

    def get_client_mapping_info_by(self, client=None, mapping_type=None):
        with allure.step('Get client info by mapping type or client'):
            if mapping_type:
                self.setup_filter(index=0, value=mapping_type)
            if client:
                self.setup_filter(index=1, value=client)
            time.sleep(2)

    def count_mapping_list(self):
        with allure.step('Count number of mappings on page'):
            return len(find_elements(self.driver, "//div[@role='rowgroup']//div[@role='row']"))

    def get_user_client_mapping_data(self, search_field='id', value=None):
        with allure.step('Get mapping info by %s = %s' % (search_field, value)):
            mapping = self._search_mapping_on_client_mapping_list(search_field, value)
            if mapping:
                mapping_columns = mapping.find_elements('xpath',".//div[@role='gridcell']")
                _id = mapping_columns[1].text

                # try:
                #     _report_type = report_columns[1].find_element('xpath',".//span").text
                # except:
                #     _report_type = ""
                _client_name = mapping_columns[2].text
                # print ("REPORT_TYPE",_report_type)
                # print("TEMPLATE",report.find_element('xpath',".//div[@role='gridcell'][3]").text)

                # try:
                #     _name = report_columns[2].find_element('xpath',".//span").text
                # except:
                #     _name = ""
                _tool_name = mapping_columns[3].text

                _client_id = mapping_columns[4].text

                _ac_user_id = mapping_columns[5].text

                creation = mapping_columns[6].find_elements('xpath',".//div[@data-baseweb='block']//div[text()]")
                _date = creation[0].text
                _author = creation[1].text

                return {"id": _id,
                        "client_name": _client_name,
                        "tool_name": _tool_name,
                        "client_id": _client_id,
                        "ac_user_id": _ac_user_id,
                        "create_date": _date,
                        "create_author": _author,
                        }
            else:
                assert False, "Mapping has not been found"

    def get_project_client_mapping_data(self, search_field='id', value=None):
        with allure.step('Get mapping info by %s = %s' % (search_field, value)):
            mapping = self._search_mapping_on_client_mapping_list(search_field, value)
            if mapping:
                mapping_columns = mapping.find_elements('xpath',".//div[@role='gridcell']")
                _id = mapping_columns[1].text
                _client_name = mapping_columns[2].text

                _client_id = mapping_columns[3].text

                _ac_id = mapping_columns[4].text

                _market = mapping_columns[5].text

                creation = mapping_columns[6].find_elements('xpath',".//div[@data-baseweb='block']//div[text()]")
                _date = creation[0].text
                _author = creation[1].text

                return {"id": _id,
                        "client_name": _client_name,
                        "client_id": _client_id,
                        "ac_id": _ac_id,
                        "market": _market,
                        "create_date": _date,
                        "create_author": _author,
                        }
            else:
                assert False, "Mapping has not been found"

    def find_client_mappings(self, project_id=None, user_id=None, client=None, mapping_type=None, owner=None):
        with allure.step('Find user by id: user_id = %s' % user_id):
            if (user_id is not None) or (project_id is not None):
                el = find_elements(self.app.driver, "//input[@name='filterByText']")
                assert len(el), "Field Search by user ID or client ID has not been found"
                current_value = el[0].get_attribute('value')
                for i in range(len(current_value)):
                    el[0].send_keys(Keys.BACK_SPACE)
                if user_id:
                    el[0].send_keys(user_id)
                elif project_id:
                    el[0].send_keys(project_id)
            time.sleep(1)

            if mapping_type:
                self.setup_filter(index=0, value=mapping_type)

            if client:
                self.setup_filter(index=1, value=client)
            time.sleep(2)

    def get_all_client_mappings_list(self):
        with allure.step('Get all client mapping list on the page'):
            num_mappings = self.count_mapping_list()
            _mappings = []
            for index in range(num_mappings):
                print(index)
                mapping_info = self.get_project_client_mapping_data('index',index)
                _mappings.append(mapping_info)
            return _mappings
