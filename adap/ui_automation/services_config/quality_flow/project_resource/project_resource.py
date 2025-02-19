import time

import allure

from adap.ui_automation.services_config.quality_flow.project_resource.project_resource_internal_contributor import \
    Project_Resource_Internal_Contributor, Project_Resource_Internal_Contributor_Group


class Project_Resource():

    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

        self.icm = Project_Resource_Internal_Contributor(app)
        self.contributor = Project_Resource_Internal_Contributor(app)
        self.contributor_group = Project_Resource_Internal_Contributor_Group(app)

    def navigate_to_project_resource(self):
        with allure.step('Navigate to project resource page'):
            self.app.navigation.click_link_by_href('/project-resources/contributors/list')
            time.sleep(3)

    def is_project_management_page(self):
        with allure.step('Verify project resource page'):
            return self.app.verification.text_present_on_page('Project Resources')
