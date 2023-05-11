import base64
import logging
import random
import re
import time

import ddddocr
import requests

from utils.common import push, get_ip


def getVcode(codeHeaders) -> str:
    vcode = ''
    while not re.match('[0-9]{5}', vcode):
        codeResp = requests.post(url="https://lixianla.com/vcode.htm?" + str(random.random()), headers=codeHeaders)
        codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
        ocr = ddddocr.DdddOcr(show_ad=False)
        vcode = ocr.classification(codeBase64)
        # logging.info('验证码：' + vcode)
    return vcode


def getSignUrl(codeHearders) -> str:
    indexResp = requests.post(
        url='https://lixianla.com',
        headers=codeHearders
    )
    content = str(indexResp.content)
    indexStart = content.find('sg_sign-lx-')
    findChar = ''
    indexEnd = 0
    while findChar != '"':
        indexEnd = indexEnd + 1
        findChar = content[indexStart + indexEnd]

    return content[indexStart: indexStart + indexEnd]


def run(config):
    ipInfo = get_ip()

    email = config['lixianla_login_email']
    password = config['lixianla_login_password']
    retryMaxCount = 20

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

    count = 1
    while True:
        codeResp = requests.post(url="https://lixianla.com/vcode.htm?" + str(random.random()), headers=codeHeaders)
        codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
        ocr = ddddocr.DdddOcr(show_ad=False)
        vcode = ocr.classification(codeBase64)
        # logging.info('登陆验证码：' + vcode)
        if (not re.match('[0-9]{5}', vcode)) or ('set-cookie' not in codeResp.headers):
            continue
        codeHeaders['cookie'] = codeResp.headers['set-cookie']
        logging.info('==========第' + str(count) + '次登陆==========')
        loginResp = requests.post(
            url="https://lixianla.com/user-login.htm?email=" + email + "&password=" + password + "&vcode=" + vcode,
            headers=codeHeaders
        )
        result = str(loginResp.text).replace('\n', '')
        logging.info(result)
        if '登录成功' in result:
            break
        elif count > retryMaxCount:
            return
        else:
            count = count + 1
            time.sleep(1)

    count = 1
    while True:
        logging.info('==========第' + str(count) + '次签到==========')
        rewardResp = requests.post(
            url="https://lixianla.com/" + getSignUrl(codeHeaders) + "?vcode=" + getVcode(codeHeaders),
            headers=codeHeaders
        )
        result = str(rewardResp.text).replace('\n', '')
        logging.info(result)
        if '成功' in result or '今天已经签过啦' in result:
            # push(config, result + '\n\n' + ipInfo, '', '√离线啦签到成功')
            return
        elif count > retryMaxCount:
            push(config, result + '\n\n' + ipInfo, '', '×离线啦签到失败')
            return
        else:
            count = count + 1
            time.sleep(1)
