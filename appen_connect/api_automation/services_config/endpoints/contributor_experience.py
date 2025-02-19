POST_USER = "/users"

POST_VERIFY_EMAIL = "/users/verify-email"

GET_ONBOARDING = "/users/me/profile/documents/onboarding"

POST_SIGNATURE = "/users/me/profile/documents/bulk-signature"

GET_PROFILE = "/users/me/profile"
LOGIN = "/account-setup"

DELETE_USER = "/users/deleteme"


def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp',
        'stage': 'https://gateway-connect-stage.integration.cf3.us/ac-user-svc-keycloak',
        'integration': 'https://gateway-connect-stage.integration.cf3.us/ac-user-svc-keycloak'
    }.get(env)