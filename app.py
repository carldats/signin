import logging
import os
import threading
from importlib import import_module

from utils.common import init_config

if __name__ == '__main__':
    config = init_config()
    for file_name in os.listdir('modules'):
        logging.info('开始执行---' + file_name)
        file_name = file_name.replace('.py', '')
        obj = import_module('modules.' + file_name)
        threading.Thread(target=obj.main(config), name=file_name).start()
