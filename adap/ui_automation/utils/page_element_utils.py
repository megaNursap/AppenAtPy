from adap.ui_automation.utils.selenium_utils import find_elements


def click_rebrand_popover(driver):
    rebrand_popover = find_elements(driver,
                                    "//a[contains(@class, 'rebrand-Popover__closeIcon')]//*[local-name() = 'svg']")
    if len(rebrand_popover) > 0: rebrand_popover[0].click()

    rebrand_popover = find_elements(driver,
                                    "//*[text()='Status Icon']/..//*[local-name() = 'svg']")
    if len(rebrand_popover) > 0: rebrand_popover[0].click()

