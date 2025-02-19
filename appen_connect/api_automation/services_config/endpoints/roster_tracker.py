

#ONBOARDING TRACKER endpoints

GET_ONBOARDING_TRACKER = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/onboarding"
EXPORT_ONBOARDING_TRACKER_PER_MARKET = "/services/metricGoalsSvc/api/v1/trackers/{projectId}/markets/{marketId}/onboarding/export"


#PRODUCTIVITY TRACKER endpoints

GET_TRACKER = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}"
METRICS = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/markets/{market}/metrics"
PRODUCTIVITY_METRICS = "/services/metricGoalsSvc/api/v1/trackers/{projectId}/productivityMetrics/{metricId}"
QUALITY_METRICS = "/services/metricGoalsSvc/api/v1/trackers/{projectId}/qualityMetrics/{metricId}"
MARKETS = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/markets"
MARKET = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/markets/{market}"
WORKERS = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/markets/{market}/workers"
WORKERS_EXPORT = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/markets/{market}/workers/export"
WORKERS_EXPORT_ALL = "/services/metricGoalsSvc/api/v1/trackers/{trackerId}/markets/{market}/workers/exportAll"

# Metrics & Goals

GOALS_HISTORY = "/services/metricGoalsSvc/api/v1/goals/history"
GOALS = "/services/metricGoalsSvc/api/v1/goals"
UPDATE_GOALS = "/services/metricGoalsSvc/api/v1/goals"


GET_METRICS = "/services/metricGoalsSvc/api/v1/metrics"
POST_METRICS = "/services/metricGoalsSvc/api/v1/metrics"
GET_METRIC_CHANGELOG ="/services/metricGoalsSvc/api/v1/metrics/{metricId}/changelogs"

GET_QUALITY_METRICS = "/services/metricGoalsSvc/api/v1/qualityMetrics"

def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp/api/v2',
        'stage': 'https://connect-stage.integration.cf3.us/qrp/api/v2',
        'integration': 'https://connect.integration.cf3.us/qrp/api/v2'
    }.get(env)