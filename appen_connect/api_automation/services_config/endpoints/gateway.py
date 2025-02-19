def URL(env):
    return {
        'qa': 'https://gateway-connect-qa.sandbox.cf3.us/project-profile-builder/api',
        'stage': 'https://gateway-connect-stage.integration.cf3.us/project-profile-builder/api'
    }.get(env)


MASTER_PROFILE_QUESTIONS = "/master-profile/questions"
MASTER_PROFILE_QUESTIONS_ID = "/master-profile/questions/{id}"
QUESTION_CATEGORIES = "/question-categories"
CREATE_PROFILE_TARGETS = "/profile-targets"
GET_PROFILE_TARGETS = "/profile-targets/{target_id}"
QUESTION_TYPES = "/question-types"
USER_MATCH_PROJECT = "/global-profile-target-user-match?userId={user_id}&projectId={project_id}"
