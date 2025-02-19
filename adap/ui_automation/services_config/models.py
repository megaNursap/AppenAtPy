import allure
import time
from adap.ui_automation.utils.selenium_utils import find_elements, find_element


class Models:
    def __init__(self, app):
        self.app = app
        self.driver = app.driver

    def choose_model_template_by_name(self, model_name):
        with allure.step('choose model template by name: %s' % model_name):
            model = find_elements(self.driver, "//div[contains(@class,'rebrand-CatalogPageLayoutCard__name') and text()='%s']" % model_name)
            assert len(model) > 0, "Model with name: %s is not found" % model_name
            model[0].click()
            time.sleep(2)

    def wait_until_data_load(self, interval, max_wait_time):
        with allure.step('Wait until image load'):
            _c = 0
            while _c < max_wait_time:
                el = find_elements(self.driver, "//div[contains(@id, 'iframe-container')]")
                if len(el) > 0:
                    break
                else:
                    _c += interval
                    time.sleep(interval)
            else:
                msg = f'Max wait time reached, image still not loaded, something maybe wrong'
                raise Exception(msg)

    def get_number_iframes_on_page(self):
        el = find_elements(self.driver, "//div[contains(@id, 'iframe-container')]")
        return len(el)

    def open_menu(self, menu_name, sub_menu=None):
        with allure.step('Open menu on Models page %s' % menu_name):
            el_menu = find_elements(self.driver, "//li[.//*[.='%s']]" % menu_name)
            assert len(el_menu) > 0, "Menu %s has not been found" % menu_name
            el_menu[0].click()
            time.sleep(2)
            if menu_name == "Datatypes":
                _sub_menu = sub_menu.split(',')
                for _menu in _sub_menu:

                    el = find_elements(self.driver, "//li[text()='%s']" % _menu)
                    if len(el) == 0:
                        el = find_elements(self.driver, "//a[text()='%s']" % _menu)
                    assert len(el) > 0, "Submenu %s has not been found" % _menu
                    el[0].click()
                    time.sleep(1)

    def get_templates_on_page(self):
        with allure.step('Get all templates on the page'):
            templates = find_elements(self.driver, "//div[contains(@class,'rebrand-CatalogPageLayout__cards')]/child::div")
            result = []
            for t in templates:
                name = t.find_element('xpath',".//div[contains(@class,'rebrand-CatalogPageLayoutCard__name')]").text
                description = t.find_element('xpath',".//div[contains(@class,'rebrand-CatalogPageLayoutCard__description')]").text
                type = t.find_element('xpath',".//div[contains(@class,'rebrand-CatalogPageLayoutCard__badge')]").text

                result.append({
                    "name": name,
                    "description": description,
                    "type": type
                })
            return result
