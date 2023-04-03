import base64
import logging
import random
import re
import time

import ddddocr
import requests

from utils.common import push


def main(config):
    email = config['lixianla_login_email']
    password = config['lixianla_login_password']
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

    flag = False
    while not flag:
        time.sleep(1)
        codeResp = requests.post(url="https://lixianla.com/vcode.htm?" + str(random.random()), headers=codeHeaders)
        codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
        ocr = ddddocr.DdddOcr()
        vcode = ocr.classification(codeBase64)
        logging.info('登陆验证码：' + vcode)
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
        logging.info(result)
        flag = '登录成功' in result or 'vcode' not in result
        if not flag:
            continue

    count = 0
    flag = False
    result = ''
    while not flag and count < retryMaxCount:
        count = count + 1
        logging.info('==========第' + str(count) + '次签到==========')
        vcode = ''
        while not re.match('[0-9]{5}', vcode):
            codeResp = requests.post(url="https://lixianla.com/vcode.htm?" + str(random.random()), headers=codeHeaders)
            codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
            ocr = ddddocr.DdddOcr()
            vcode = ocr.classification(codeBase64)
            logging.info('签到验证码：' + vcode)

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

        rewardResp = requests.post(
            url="https://lixianla.com/" + url + "?vcode=" + vcode,
            headers=codeHeaders
        )
        result = rewardResp.text
        logging.info(result)
        flag = '成功' in result or '今天已经签过啦' in result
        if not flag:
            time.sleep(2)

    if flag:
        push(config, result, '', '√离线啦签到成功')
    else:
        push(config, result, '', '×离线啦签到失败')
