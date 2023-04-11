import requests


def main(config):
    accounts = {
        'kt@kt.com': '4kA-neFoVzFMVx20Vp7p4HRGnwFoV_CTV3vPFHfquHq_nwFoF_1MV_YxV_YxLkFPFHLBuDMX2r1pJpA3zpFPFHLIWDMGnD7pJpAgnDFp5eA7s02pJpA_S0XGsg9XSkM02hTp5eA0n8AxsDRGF_IpVzWgLwFPFHldSH2pJpAsweAR',

    }
    for account in accounts:
        data = accounts[account]
        resp = requests.post('http://104.233.162.120:81/signin', data=data)
        print(account + resp.text)
        for _ in range(0, 5):
            resp = requests.post('http://104.233.162.120:81/lucky', data=data)
            print(account + resp.text)


if __name__ == '__main__':
    main('')
