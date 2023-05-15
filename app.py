import logging
import os
from importlib import import_module

from utils.common import init_config

if __name__ == '__main__':
    config = init_config()
    modules = os.listdir('modules')
    modules.sort()
    for file_name in modules:
        try:
            if not file_name.endswith('.py'):
                continue
            logging.info('#################################### ' + file_name + ' ####################################')
            file_name = file_name.replace('.py', '')
            import_module('modules.' + file_name).run(config)
        except Exception as e:
            logging.error(e)
