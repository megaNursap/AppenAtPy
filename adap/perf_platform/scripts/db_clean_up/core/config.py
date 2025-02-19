import os

from configparser import ConfigParser
from scripts.one_offs.perf_platform_dbase_pwds import get_qa_perf_db_pwd


def get_config(filename='../settings.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(os.path.join(os.path.dirname(__file__), filename))

    section_cfg = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            section_cfg[param[0]] = param[1]

        if len(section_cfg) > 0 :
            section_cfg['password'] = get_qa_perf_db_pwd()
    else:
        raise Exception('Section "{0}" not found in the {1} file'.format(section, filename))

    return section_cfg
