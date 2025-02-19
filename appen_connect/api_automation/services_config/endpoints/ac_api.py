AUTH = "/auth/session"
AUTH_ME = "/auth/me"
PROJECT_STATUS = "/project-status"
BUSINESS_UNITS = "/business-units"
COUNTRIES = "/countries"
EXTERNAL_SYSTEMS = "/external-systems"
GROUPS = "/groups"
STATES = "/countries/{country_id}/states?includeTerritories={include_territories}"

HIRING_TARGET = "/hiring-tagets"

PROJECTS = "/projects"
PROJECT_FULL = "/projects/full"

PAY_RATES = "/payrates"
RATE_TYPES = "/rate-types"

TASK_VOLUMES = "/task-volumes"

LOCALE_TENANTS = "/locale-tenants"

LANGUAGES = "/languages"

PROJECT_PAGES = "/project-pages"

LANGUAGE_FLUENCY_LEVEL = "/language-fluency-levels"

TASK_TYPES = "/task-types"
TEAM_TYPES = "/team-types"
TENANTS = "/tenants"
USERS = "/users"
WORK_TYPES = "/work-types"

BPM_QUALIFICATION_STEPS = "/qualification-processes/steps"
BPM_REGISTRATION_STEPS = "/registration-processes/steps"

QUALIFICATION_PROCESS = "/qualification-processes"
QUALIFICATION_PROCESS_TYPES = "/qualification-processes/types"
QUALIFICATION_PROCESS_PROJECTS = "/qualification-processes/{id}/projects"

REGISTRATION_PROCESS = "/registration-processes"
REGISTRATION_PROCESS_TYPES = "/registration-processes/types"
REGISTRATION_PROCESS_PROJECTS = "/registration-processes/{id}/projects"


DEMOGRAPHICS_REQUIREMENTS = "/demographics-requirements"
DEMOGRAPHICS_METRICS = "/demographics-requirements/metrics?generalMetrics={}"
DEMOGRAPHICS_PARAMETERS = "/demographics-requirements/parameters"

STATUS = "/projects/{id}/status"
INVOICE_CONFIGURATION ="/projects/{id}/invoice-configuration"

EXPERIMENTS = "/experiments"
EXPERIMENT = "/experiments/{id}"
EXPERIMENT_GROUPS = "/experiments/{id}/groups"
EXPERIMENT_STATUS = "/experiments/status"

RESOURCE_MAPPINGS = "/projects/{id}/resource-mappings"
RESOURCE_MAPPINGS_EDIT = "/projects/{id}/resource-mappings/{resourceid}?"

QUIZZES = "/quizzes?quizType=quiz"
SURVEY = "/quizzes?quizType=survey"
DOCUMENTS = "/documents"
ACADEMIES = "/academies"

DC_CONSENT_FORMS = "/data-collection-consent-forms?projectId={projectId}"
DC_VERSION = "/data-collection-consent-forms/{dc_id}/version"
PII_DATA = "/pii-data"
APPEN_ENTITIES = "/appen-entities"


def URL_BASE(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us',
        'stage': 'https://connect-stage.integration.cf3.us',
        'integration': 'https://connect.integration.cf3.us'
    }.get(env)


def URL(env):
    url_base = URL_BASE(env=env)
    return {
        'qa': '%s/qrp/api/{version}' % url_base,
        'stage': '%s/qrp/api/{version}' % url_base,
        'integration': '%s/qrp/core/api/{version}' % url_base
    }.get(env)



"""
TODO

client-controller
Client Controller

markets-info-controller
Markets Info Controller

project-info-controller
Project Info Controller

user-info-controller
User Info Controller
"""