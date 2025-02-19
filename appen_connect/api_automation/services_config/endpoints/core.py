def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp/core',
        'stage': 'https://connect-stage.integration.cf3.us/qrp/core',
        'integration': 'https://connect.integration.cf3.us/qrp/core'
    }.get(env)


LOGIN = "/login"
LOGOUT = "/login/logout"
TICKETS = "/tickets"
IMPERSONATE = "/impersonate/change/{user_id}"
VENDOR_VIEW = "/vendor/view/{user_id}"
VENDOR_PROJECTS = "/vendors/projects"
VENDOR_TASK_VIEW = "/vendors/task/view/{project_id}"
ACAN_TIMESHEETS = "/vendors/acan_timesheets"
