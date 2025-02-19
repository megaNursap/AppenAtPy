REPORTS = "/v2/services/svc/dpr/reports"

PROGRAMS = "/v2/services/svc/dpr/programs"

METRICS = "/v2/services/svc/dpr/metrics"

WBR_METRIC_MAPPINGS = "/v2/services/svc/dpr/metrics/wbr-metrics-mapping"

def URL(env):
    return {
        'qa': 'https://connect-qa.sandbox.cf3.us/qrp',
        'stage': 'https://connect-stage.integration.cf3.us/qrp',
        'integration': 'https://connect.integration.cf3.us/qrp'
    }.get(env)