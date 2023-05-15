# import logging
# import os
# from importlib import import_module
from modules import aliyundrive, kutogroup, lixianla
from utils.common import init_config

if __name__ == '__main__':
    config = init_config()
    # for file_name in os.listdir('modules'):
    #     if not file_name.endswith('.py'):
    #         continue
    #     logging.info('#################################### ' + file_name + ' ####################################')
    #     file_name = file_name.replace('.py', '')
    #     import_module('modules.' + file_name).run(config)
    aliyundrive.run(config)
    kutogroup.run(config)
    lixianla.run(config)
