import os

from configparser import ConfigParser


def get_config(filename='../settings.ini', section='spira'):
    parser = ConfigParser()
    parser.read(os.path.join(os.path.dirname(__file__), filename))

    # get config section
    section_cfg = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            section_cfg[param[0]] = param[1]
    else:
        raise Exception('Section "{0}" not found in the {1} file'.format(section, filename))

    return section_cfg
