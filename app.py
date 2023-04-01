import threading

from modules import aliyundriver, lixianla
from utils.common import init_config

if __name__ == '__main__':
    config = init_config()
    threading.Thread(target=aliyundriver.main(config), name='阿里云盘').start()
    threading.Thread(target=lixianla.main(config), name='离线啦').start()
