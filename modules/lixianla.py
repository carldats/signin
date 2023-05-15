import base64
import logging
import random
import re
import time

import ddddocr
import requests

from utils.common import push


def getVcode(codeHeaders) -> str:
    vcode = ''
    while not re.match('[0-9]{5}', vcode):
        codeResp = requests.get(
            verify=False,
            url="https://lixianla.com/vcode.htm?" + str(random.random()),
            headers=codeHeaders
        )
        codeResp.close()
        codeBase64 = base64.b64encode(codeResp.content).decode('utf-8')
        ocr = ddddocr.DdddOcr(show_ad=False)
        vcode = ocr.classification(codeBase64)
        logging.info('验证码：' + vcode)
    return vcode


def getSignUrl(codeHearders) -> str:
    indexResp = requests.post(
        timeout=5,
        verify=False,
        url='https://lixianla.com',
        headers=codeHearders
    )
    content = str(indexResp.content)
    indexStart = content.find('sg_sign-lx-')
    temp = ''
    indexEnd = 0
    while temp != '"':
        indexEnd = indexEnd + 1
        temp = content[indexStart + indexEnd]

    return content[indexStart: indexStart + indexEnd]


def run(config):
    email = config['lixianla_login_email']
    password = config['lixianla_login_password']
    serverIp = config['server_ip']

    retryMaxCount = 20

    codeHeaders = {
        'authority': 'lixianla.com',
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.7',
        'cookie': 'bbs_sid=qb5mkagm92j924563thcpjam9r',
        'dnt': '1',
        'referer': 'https://lixianla.com/user-login.htm',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }

    count = 1
    while True:
        logging.info('==========第' + str(count) + '次登陆==========')
        vcode = getVcode(codeHeaders)
        loginResp = requests.post(
            timeout=5,
            verify=False,
            url="https://lixianla.com/user-login.htm?email=" + email + "&password=" + password + "&vcode=" + vcode,
            headers=codeHeaders
        )
        loginResp.close()
        if email in loginResp.text:
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
            timeout=5,
            verify=False,
            url="https://lixianla.com/" + getSignUrl(codeHeaders) + "?vcode=" + getVcode(codeHeaders),
            headers=codeHeaders
        )
        rewardResp.close()
        resultResp = requests.get(
            timeout=5,
            verify=False,
            url="https://lixianla.com/sg_sign.htm",
            headers=codeHeaders
        )
        resultResp.close()
        result = resultResp.text
        if '已签' in result:
            keyword = 'var s3 = '
            indexStart = result.find(keyword) + len(keyword)
            indexStart = indexStart + 1
            indexEnd = indexStart + 6
            logging.info('√离线啦签到成功：' + result[indexStart: indexEnd])
            # push(config, result + '\n\n' + serverIp, '', '√离线啦签到成功')
            return
        elif count > retryMaxCount:
            push(config, result + '\n\n' + serverIp, '', '×离线啦签到失败')
            return
        else:
            count = count + 1
            time.sleep(1)
