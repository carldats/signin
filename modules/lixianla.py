import base64
import logging
import random
import re
import time

import ddddocr
import requests

from utils.common import push


def get_vcode(headers) -> str:
    vcode = ''
    while not re.match('[0-9]{5}', vcode):
        resp = requests.get(
            timeout=5,
            verify=False,
            url="https://lixianla.com/vcode.htm?" + str(random.random()),
            headers=headers
        )
        resp.close()
        codeBase64 = base64.b64encode(resp.content).decode('utf-8')
        ocr = ddddocr.DdddOcr(show_ad=False)
        vcode = ocr.classification(codeBase64)
        logging.info('验证码：' + vcode)
    return vcode


def get_sign_url(headers) -> str:
    resp = requests.post(
        timeout=5,
        verify=False,
        url='https://lixianla.com',
        headers=headers
    )
    content = str(resp.content)
    index_start = content.find('sg_sign-lx-')
    temp = ''
    index_end = 0
    while temp != '"':
        index_end = index_end + 1
        temp = content[index_start + index_end]

    return content[index_start: index_start + index_end]


def run(config):
    email = config['lixianla_login_email']
    password = config['lixianla_login_password']
    serverIp = config['server_ip']
    retry_max_count = 20

    headers = {
        'authority': 'lixianla.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    login_flag = False
    count = 1
    while not login_flag:
        try:
            logging.info('==========第' + str(count) + '次登陆==========')
            # 打开主页
            resp = requests.get(
                timeout=5,
                verify=False,
                url="https://lixianla.com",
                headers=headers
            )
            resp.close()
            try:
                cookie = resp.headers['set-cookie']
                headers['cookie'] = cookie
            except Exception as e:
                continue

            vcode = get_vcode(headers)
            headers = {
                'authority': 'lixianla.com',
                'accept': 'text/plain, */*; q=0.01',
                'accept-language': 'zh-CN,zh;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://lixianla.com',
                'referer': 'https://lixianla.com/user-login.htm',
                'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                'cookie': cookie
            }
            resp = requests.post(
                timeout=5,
                verify=False,
                url="https://lixianla.com/user-login.htm?email=" + email + "&password=" + password + "&vcode=" + vcode,
                headers=headers
            )
            resp.close()
            if '成功' in resp.text:
                login_flag = True
            elif count >= retry_max_count:
                break
            else:
                logging.warning(resp.text.replace('\n', '').replace(' ', ''))
        except Exception as e:
            logging.error(e)
        finally:
            count = count + 1
            time.sleep(1)

    count = 1
    while login_flag:
        try:
            logging.info('==========第' + str(count) + '次签到==========')
            requests.post(
                timeout=5,
                verify=False,
                url="https://lixianla.com/" + get_sign_url(headers) + "?vcode=" + get_vcode(headers),
                headers=headers
            ).close()
            resp = requests.get(
                timeout=5,
                verify=False,
                url="https://lixianla.com/sg_sign.htm",
                headers=headers
            )
            resp.close()
            result = resp.text
            if '已签' in result:
                keyword = 'var s3 = '
                indexStart = result.find(keyword) + len(keyword)
                indexStart = indexStart + 1
                indexEnd = indexStart + 6
                logging.info('√离线啦签到成功：' + result[indexStart: indexEnd])
                # push(config, result + '\n\n' + serverIp, '', '√离线啦签到成功')

                # 登出
                requests.get(
                    timeout=5,
                    verify=False,
                    url="https://lixianla.com/user-logout.htm",
                    headers=headers
                ).close()

                return
            elif count >= retry_max_count:
                break
        except Exception as e:
            logging.error(e)
        finally:
            count = count + 1
            time.sleep(1)

    push(config, serverIp, '', '×离线啦签到失败')
