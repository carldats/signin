import logging

import requests


def run(config):
    accounts = {
        'kt@kt.com': '4kA-neFoVzFMVx20Vp7p4HRGnwFoV_CTV3vPFHfquHq_nwFoF_1MV_YxV_YxLkFPFHLBuDMX2r1pJpA3zpFPFHLIWDMGnD7pJpAgnDFp5eA7s02pJpA_S0XGsg9XSkM02hTp5eA0n8AxsDRGF_IpVzWgLwFPFHldSH2pJpAsweAR',
    }
    for account in accounts:
        data = accounts[account]
        resp = requests.post(
            timeout=5,
            verify=False,
            url='http://104.233.162.120:81/signin',
            data=data
        )
        logging.info(account + resp.text)
        for _ in range(0, 5):
            resp = requests.post(
                timeout=5,
                verify=False,
                url='http://104.233.162.120:81/lucky',
                data=data
            )
            logging.info(account + resp.text)
