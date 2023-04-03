import logging
import os
import threading

from utils.common import init_config

if __name__ == '__main__':
    config = init_config()
    for file_name in os.listdir('modules'):
        file_name = file_name.replace('.py', '')
        logging.info('开始执行---' + file_name)
        threading.Thread(target=eval(file_name + '.main(config)'), name=file_name).start()
