import argparse
import logging
from os import environ
from typing import NoReturn, Optional

import requests
from configobj import ConfigObj

from utils import dingtalk, serverchan, pushdeer, telegram, pushplus, smtp, feishu, cqhttp, webhook


def init_config() -> dict:
    environ['NO_PROXY'] = '*'  # 禁止代理

    args = get_args()

    init_logger(args.debug)  # 初始化日志系统

    # 获取配置
    config = (
        get_config_from_env()
        if args.action
        else ConfigObj('config.ini', encoding='UTF8')
    )

    if not config:
        logging.error('获取配置失败.')
        raise ValueError('获取配置失败.')
    else:
        return config


def get_args() -> argparse.Namespace:
    """
    获取命令行参数

    :return: 命令行参数
    """
    parser = argparse.ArgumentParser(description='签到')

    parser.add_argument('-a', '--action', help='由 GitHub Actions 调用', action='store_true', default=False)
    parser.add_argument('-d', '--debug', help='调试模式, 会输出更多调试数据', action='store_true', default=False)

    return parser.parse_args()


def init_logger(debug: Optional[bool] = False) -> NoReturn:
    """
    初始化日志系统

    :return:
    """
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log_format = logging.Formatter(
        '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s'
    )

    # Console
    ch = logging.StreamHandler()
    log.setLevel(logging.DEBUG if debug else logging.INFO)
    ch.setFormatter(log_format)
    log.addHandler(ch)

    # Log file
    log_name = 'signin.log'
    fh = logging.FileHandler(log_name, mode='a', encoding='utf-8')
    log.setLevel(logging.DEBUG if debug else logging.INFO)
    fh.setFormatter(log_format)
    log.addHandler(fh)


def get_config_from_env() -> Optional[dict]:
    """
    从环境变量获取配置

    :return: 配置字典, 配置缺失返回 None
    """
    try:
        return {
            # 阿里云盘
            'aliyundrive_refresh_tokens': environ['ALIYUNDRIVE_REFRESH_TOKENS'].split(','),
            'aliyundrive_do_not_reward': environ['ALIYUNDRIVE_DO_NOT_REWARD'],
            # 离线啦
            'lixianla_login_email': environ['LIXIANLA_LOGIN_EMAIL'],
            'lixianla_login_password': environ['LIXIANLA_LOGIN_PASSWORD'],
            # 消息推送
            'push_types': (environ['PUSH_TYPES'] or '').split(','),
            'serverchan_send_key': environ['SERVERCHAN_SEND_KEY'],
            'telegram_endpoint': 'https://api.telegram.org',
            'telegram_bot_token': environ['TELEGRAM_BOT_TOKEN'],
            'telegram_chat_id': environ['TELEGRAM_CHAT_ID'],
            'telegram_proxy': None,
            'pushplus_token': environ['PUSHPLUS_TOKEN'],
            'pushplus_topic': environ['PUSHPLUS_TOPIC'],
            'smtp_host': environ['SMTP_HOST'],
            'smtp_port': environ['SMTP_PORT'],
            'smtp_tls': environ['SMTP_TLS'],
            'smtp_user': environ['SMTP_USER'],
            'smtp_password': environ['SMTP_PASSWORD'],
            'smtp_sender': environ['SMTP_SENDER'],
            'smtp_receiver': environ['SMTP_RECEIVER'],
            'feishu_webhook': environ['FEISHU_WEBHOOK'],
            'webhook_url': environ['WEBHOOK_URL'],
            'cqhttp_endpoint': environ['CQHTTP_ENDPOINT'],
            'cqhttp_user_id': environ['CQHTTP_USER_ID'],
            'cqhttp_access_token': environ['CQHTTP_ACCESS_TOKEN'],
        }
    except KeyError as e:
        logging.error(f'环境变量 {e} 缺失.')
        return None


def push(
        config: ConfigObj | dict,
        content: str,
        content_html: str,
        title: Optional[str] = None,
) -> NoReturn:
    """
    推送签到结果

    :param config: 配置文件, ConfigObj 对象或字典
    :param content: 推送内容
    :param content_html: 推送内容, HTML 格式
    :param title: 推送标题

    :return:
    """
    configured_push_types = [
        i.lower().strip()
        for i in (
            [config['push_types']]
            if type(config['push_types']) == str
            else config['push_types']
        )
    ]

    for push_type, pusher in {
        'go-cqhttp': cqhttp,
        'dingtalk': dingtalk,
        'feishu': feishu,
        'pushdeer': pushdeer,
        'pushplus': pushplus,
        'serverchan': serverchan,
        'smtp': smtp,
        'telegram': telegram,
        'webhook': webhook,
    }.items():
        if push_type in configured_push_types:
            pusher.push(config, content, content_html, title)


def get_ip() -> str:
    try:
        resp = requests.get(url="https://gwgp-cekvddtwkob.n.bdcloudapi.com/ip/local/geo/v1/district")
        logging.info(resp.text)
        return resp.text
    except Exception as e:
        logging.error(e)
        return ''
