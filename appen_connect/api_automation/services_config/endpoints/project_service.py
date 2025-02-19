def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp/api/v3/services/',
        'stage': 'https://connect-stage.integration.cf3.us/qrp/api/v3/',
        'integration': 'https://connect.integration.cf3.us/qrp/api/v3/'
    }.get(env)


VENDOR_PROJECT_LIST = "/services/project-service/vendorProjectList/{userId}/all/"
COUNTRIES_LIST = "/countries?excludeWildcard=true&language={languageCode}"