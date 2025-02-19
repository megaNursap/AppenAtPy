def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp/api/v2/services/user-service',
        'stage': 'https://connect-stage.integration.cf3.us/qrp/api/v2/services/user-service',
        'adap_ac': 'https://connect-stage.integration.cf3.us/qrp/api/v2/services/user-service',
        'integration': 'https://connect.integration.cf3.us/qrp/api/v2/services/user-service'
    }.get(env)


PROD = ""


DEMOGRAPHICS_COMPLEXIONS = '/demographics/complexions'
DEMOGRAPHICS_DISABILITY_TYPES = '/demographics/disability-types'
DEMOGRAPHICS_ETHNICITIES = '/demographics/ethnicities'
DEMOGRAPHICS_GENDERS = '/demographics/genders'


EDUCATION_LEVELS = '/education-levels'

LINGUISTICS_QUALIFICATION = '/linguistics-qualification'

USER_PROFILE = '/users/{id}/profile'

NEW_USER = '/users'
VERIFY_EMAIL = '/users/verify-email'

FALSE_POSITIVE = '/falsePositives'
FALSE_POSITIVE_USER = '/falsePositives?userId={user_id}'

USER_IP_MASK = '/user-ip-mask'
USER_IP_MASK_CHECK = '/user-ip-mask/check'
