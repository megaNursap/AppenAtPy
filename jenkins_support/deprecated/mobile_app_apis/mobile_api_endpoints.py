# GET_THIRD_PARTY_SIGNATURE = "/api/v3/third-party-signatures?projectId=%s&userId=%s"
#
# POST_THIRD_PARTY_SIGNATURE = "/api/v3/third-party-signatures"
#
# GET_USER_SERVICE = "/api/v3/services/user-service/processes/%s/task?projectId=%s"
#
# GET_ALL_PROJECTS = "/api/v2/services/project-service/vendorProjectList/%s/all"
#
# APPLY_PROJECTS = "/api/v3/services/user-service/user-projects/registration"
#
# POST_INTELLIGENT_ATTRIBUTE = "/api/v3/services/user-service/processes/%s/task/intelligent-attributes"
#
# POST_SMART_PHONE = "/api/v3/services/user-service/processes/%s/task/smartphone-profile"
#
# POST_DOCUMENT_SIGNATURE = "/api/v3/services/user-service/processes/%s/task/document-signature"
#
#
# def URL(env):
#     return {
#         'qa': 'https://connect-qa.sandbox.cf3.us/qrp',
#         'stage': 'https://connect-stage.integration.cf3.us/qrp',
#         'integration': 'https://connect.integration.cf3.us/qrp'
#     }.get(env)