

def gap_enable_element_by(driver, element_id):
    """
        JS implementation of enabling element
        """
    java_script = "document.getElementById('"+ element_id+"').style.display='block';"
    driver.execute_script(java_script, element_id)

def gap_enable_element_by_tag(driver,tag):
    """
        JS implementation of enabling element
        """
    java_script = "var el=document.getElementsByTagName('"+ tag+"');el.style.display='block';"
    driver.execute_script(java_script, tag)

def gap_enable_element_by_type(driver,value):
    """
        JS implementation of enabling element
        """
    java_script = "document.querySelector('[type=\""+ value+"\"]').style.display='block';"
    driver.execute_script(java_script, value)

#TODO SK not working, fix
###
# def enable_element_by_xpath(driver,xpath):
#     java_script = "var xpathResult=document.evaluate('"+xpath+"', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;xpathResult.style.display='block';"
#     driver.execute_script(java_script, xpath)
