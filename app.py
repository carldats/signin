import logging
import os
from importlib import import_module

from modules import aliyundrive, lixianla
from utils.common import init_config


def dynamic_run(config):
    modules = os.listdir('modules')
    modules.sort()
    for file_name in modules:
        try:
            if not file_name.endswith('.py'):
                continue
            logging.info('######################## ' + file_name + ' ########################')
            file_name = file_name.replace('.py', '')
            import_module('modules.' + file_name).run(config)
        except Exception as e:
            logging.error(e)


def static_run(config):
    try:
        logging.info('######################## aliyundrive ########################')
        aliyundrive.run(config)
    except Exception as e:
        logging.error(e)
    try:
        logging.info('######################## lixianla ########################')
        lixianla.run(config)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    static_run(init_config())
