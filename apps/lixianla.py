import argparse
import base64
import logging
import random
import re
import time
from os import environ
from sys import argv
from typing import Optional, NoReturn

import ddddocr
import requests
from configobj import ConfigObj

from modules import dingtalk, serverchan, pushdeer, telegram, pushplus, smtp, feishu


def get_config_from_env() -> Optional[dict]:
    try:

        push_types = environ['PUSH_TYPES'] or ''

        return {
            'push_types': push_types.split(','),
            'li_xian_la_login_email': environ['LI_XIAN_LA_LOGIN_EMAIL'],
            'li_xian_la_login_password': environ['LI_XIAN_LA_LOGIN_PASSWORD'],
            'serverchan_send_key': environ['SERVERCHAN_SEND_KEY'],
            'telegram_endpoint': 'https://api.telegram.org',
            'telegram_bot_token': environ['TELEGRAM_BOT_TOKEN'],
            'telegram_chat_id': environ['TELEGRAM_CHAT_ID'],
            'telegram_proxy': None,
            'pushplus_token': environ['PUSHPLUS_TOKEN'],
            'smtp_host': environ['SMTP_HOST'],
            'smtp_port': environ['SMTP_PORT'],
            'smtp_tls': environ['SMTP_TLS'],
            'smtp_user': environ['SMTP_USER'],
            'smtp_password': environ['SMTP_PASSWORD'],
            'smtp_sender': environ['SMTP_SENDER'],
            'smtp_receiver': environ['SMTP_RECEIVER'],
            'feishu_webhook': environ['FEISHU_WEBHOOK'],
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
    configured_push_types = [
        i.lower().strip()
        for i in (
            [config['push_types']]
            if type(config['push_types']) == str
            else config['push_types']
        )
    ]

    for push_type, pusher in {
        'dingtalk': dingtalk,
        'serverchan': serverchan,
        'pushdeer': pushdeer,
        'telegram': telegram,
        'pushplus': pushplus,
        'smtp': smtp,
        'feishu': feishu,
    }.items():
        if push_type in configured_push_types:
            pusher.push(config, content, content_html, title)


def get_args() -> argparse.Namespace:
    """
    获取命令行参数

    :return: 命令行参数
    """
    parser = argparse.ArgumentParser(description='离线啦自动签到')

    parser.add_argument('--action', '-a', help='由 GitHub Actions 调用', action='store_true', default=False)
    parser.add_argument('--debug', '-d', help='调试模式', action='store_true', default=False)

    return parser.parse_args()


class lixianla():
    if 'action' in argv:
        by_action = True
        debug = False
    else:
        args = get_args()
        by_action = args.action
        debug = args.debug

    # 获取配置
    config = (
        get_config_from_env()
        if by_action
        else ConfigObj('config.ini', encoding='UTF8')
    )

    email = config['li_xian_la_login_email']
    password = config['li_xian_la_login_password']
    retryMaxCount = 10

    codeHeaders = {
        'accept': 'text/plain, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://lixianla.com',
        'referer': 'https://lixianla.com/user-login.htm',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    loginResp = requests.post(
        url='https://lixianla.com/user-login.htm',
        headers=codeHeaders
    )

    flag = False
    while not flag:
        time.sleep(1)
        codeResp = requests.post(url="https://lixianla.com/vcode.htm?" + str(random.random()), headers=codeHeaders)
        codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
        ocr = ddddocr.DdddOcr()
        vcode = ocr.classification(codeBase64)
        print('登陆验证码：' + vcode)
        flag = re.match('[0-9]{5}', vcode)
        if not flag:
            continue
        if 'set-cookie' not in codeResp.headers:
            continue
        codeHeaders['cookie'] = codeResp.headers['set-cookie']
        loginResp = requests.post(
            url="https://lixianla.com/user-login.htm?email=" + email + "&password=" + password + "&vcode=" + vcode,
            headers=codeHeaders
        )
        result = str(loginResp.text)
        print(result)
        flag = '登录成功' in result
        if not flag:
            continue
        flag = 'vcode' not in result
        if not flag:
            continue

    count = 0
    flag = False
    result = ''
    while not flag and count < retryMaxCount:
        count = count + 1
        print('==========第' + str(count) + '次签到==========')
        vcode = ''
        while not re.match('[0-9]{5}', vcode):
            codeResp = requests.post(url="https://lixianla.com/vcode.htm?" + str(random.random()), headers=codeHeaders)
            codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
            ocr = ddddocr.DdddOcr()
            vcode = ocr.classification(codeBase64)
            print('签到验证码：' + vcode)

        # 获取签到地址
        indexResp = requests.post(
            url='https://lixianla.com',
            headers=codeHeaders
        )
        content = str(indexResp.content)
        indexStart = content.find('sg_sign-lx-')
        findChar = ''
        indexEnd = 0
        while findChar != '"':
            indexEnd = indexEnd + 1
            findChar = content[indexStart + indexEnd]
        url = content[indexStart: indexStart + indexEnd]
        print(url)

        rewardResp = requests.post(
            url="https://lixianla.com/" + url + "?vcode=" + vcode,
            headers=codeHeaders
        )
        result = rewardResp.text
        print(result)
        flag = '成功' in result or '今天已经签过啦' in result
        if not flag:
            time.sleep(2)

    if flag:
        push(config, result, '', '√离线啦签到成功1')
    else:
        push(config, result, '', '×离线啦签到失败1')
