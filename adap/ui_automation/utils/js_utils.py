from adap.settings import Config


def element_to_the_middle(driver, element, center=False):
    """
    adjust screen position to show the element in the middle
    """
    current_screen_height = driver.get_window_size()['height']
    element_height = 0
    if center:
        element_height = element.size['height']
    element_y_axis_position = element.location['y']
    pxs = int(element_y_axis_position - current_screen_height / 2 + element_height / 2)

    driver.execute_script('document.body.scrollTop = document.documentElement.scrollTop = 0;')
    driver.execute_script("scroll(0, %s)" % pxs)


def mouse_click_element(driver, element):
    """
    JS implementation of mouse click event
    """
    java_script = "var evObj = document.createEvent('MouseEvents');\n" \
                  "evObj.initMouseEvent(\"click\",true, true, window," \
                  " 0, 0, 0, 80, 20, false, false, false, false, 0, null);\n" \
                  "arguments[0].dispatchEvent(evObj);"
    driver.execute_script(java_script, element)


def inner_scroll_to_element(driver, element, inside_element=None):
    """
    scroll within container
    """
    driver.execute_script("arguments[0].scrollTop = arguments[1];", element, inside_element)


def mouse_over_element(driver, element):
    """
    JS implementation of mouse over element event
    """
    java_script = "var evObj = document.createEvent('MouseEvents');\n" \
                  "evObj.initMouseEvent(\"mouseover\",true, false, window," \
                  " 0, 0, 0, 0, 0, false, false, false, false, 0, null);\n" \
                  "arguments[0].dispatchEvent(evObj);"
    driver.execute_script(java_script, element)


def scroll_to_page_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def scroll_to_page_top(driver):
    driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")


def scroll_to_element(driver, element):
    return driver.execute_script(
        "arguments[0].scrollIntoView();",
        element
    )


def get_text_excluding_children(driver, element):
    return driver.execute_script("""
    var parent = arguments[0];
    var child = parent.firstChild;
    var ret = "";
    while(child) {
        if (child.nodeType === Node.TEXT_NODE)
            ret += child.textContent;
        child = child.nextSibling;
    }
    return ret;
    """, element)


def drag_and_drop(driver, source, target):
    js_drag_drop = open(Config.PROJECT_ROOT + '/adap/ui_automation/utils/drag-drop.js', 'r').read()
    driver.execute_script(js_drag_drop, source, target, None, None, 101)


def enable_element_by(driver, element_id):
    """
        JS implementation of enabling element by id
    """
    java_script = "document.getElementById('" + element_id + "').style.display='block';"
    driver.execute_script(java_script, element_id)


def enable_element_by_type(driver, value):
    """
        JS implementation of enabling element by type
        """
    java_script = "document.querySelector('[type=\"" + value + "\"]').style.display='block';"
    driver.execute_script(java_script, value)


def open_new_tab(driver):
    driver.execute_script("window.open('');")


def open_url_in_new_tab(driver, url):
    driver.execute_script(f'''window.open("{url}","_blank");''')

def is_enabled_js(driver, element):
    java_script = "arguments[0].disabled;"
    return driver.execute_script(java_script, element)

def set_innerHTML(driver, element, value):
    return driver.execute_script("arguments[0].innerHTML = arguments[1]", element, value)
