from adap.perf_platform.utils.logging import get_logger

LOGGER = get_logger(__name__)


def prepare_test_data(test_cases, props):
    LOGGER.info('Prepare test coveraqge data')
    adap_id, ac_id = 36, 37
    auto_status = {
        'Total': 0,
        'None': 0,
        'Done': 0,
        'Wont automate': 0,
        'In progress': 0,
        'TODO': 0
    }
    result = {'adap': {'features': {}, 'summary': dict(auto_status)},
              'appen connect': {'features': {}, 'summary': dict(auto_status)},
              'bad_data': {'Total': 0, 'ids': []}
              }

    adap_app = result['adap']
    ac_app = result['appen connect']

    # time: O(n) + O(1)
    for tc in test_cases:
        tc_prop = tc['CustomProperties']
        tc_status_id = tc_prop[4]['IntegerValue']
        tc_status = props[tc_status_id] if tc_status_id else 'None'
        app = ac_app if tc_prop[6]['IntegerValue'] == ac_id else adap_app
        app_feat = app['features']

        # mandatory field 'Automation feature'
        feat_id = tc_prop[7]['IntegerValue']
        if not feat_id:
            result['bad_data']['Total'] += 1
            # result['bad_data']['ids'].append(tc['TestCaseId'])
            continue

        feat_name = props[feat_id]

        if feat_name not in app_feat:
            app_feat[feat_name] = dict(auto_status)
        app_feat[feat_name][tc_status] += 1
        app_feat[feat_name]['Total'] += 1

        app['summary'][tc_status] += 1
        app['summary']['Total'] += 1

    return result


def prepare_test_case_properties(props):
    LOGGER.info('Prepare available test case properties')
    return {
        val['CustomPropertyValueId']: val['Name']
        for p in props
        if p['CustomList']
        for val in p['CustomList']['Values']
    }
