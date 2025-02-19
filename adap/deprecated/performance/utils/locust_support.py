from locust import constant, constant_pacing, between


def setup_wait_time(wait_config_type, wait_time_param):

    if wait_config_type == 'constant':
        wait_time = constant(int(wait_time_param))
    elif wait_config_type == 'constant_pacing':
        wait_time = constant_pacing(int(wait_time_param))
    elif wait_config_type == 'between':
        wait_time_min = int(wait_time_param.split('-')[0])
        wait_time_max = int(wait_time_param.split('-')[1])
        wait_time = between(wait_time_min, wait_time_max)

    return  wait_time

