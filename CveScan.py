"""

"""
import argparse
import importlib
import os
import sys
import requests
from urllib3.exceptions import InsecureRequestWarning
from importlib.util import module_from_spec
import importlib.util
from colorama import Fore, Style  # 打印彩色文本
from colorama import init  # 颜色库初始化
from concurrent.futures import ThreadPoolExecutor, as_completed  # 线程池
import threading
import pyfiglet  # 艺术字
# logo使用的库
from colorama import Fore, Back, Style
from termcolor import colored
import time
import signal  # 处理POSIX信号,处理ctrl+c

# 禁用不安全的连接警告(处理https)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
# 创建一个Event对象,作为停止得标志
stop_flag = threading.Event()


def load_poc_modules(poc_dir="pocs") -> object:
    poc_modules = {}
    for root, dirs, files in os.walk(poc_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]  # 使用文件名，而不是路径
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                poc_modules[module_name] = module
    return poc_modules


def poc_scanner(target_url, poc_modules, found_vulnerabilities, found_vulnerabilities_lock, output_lock, stop_flag):
    # 使用加载的poc模块,对指定目标url进行漏洞检测的函数
    # 加载所有的poc模块
    # poc_modules = load_poc_modules()
    # print(poc_modules)
    poc_modules = poc_modules
    # print_green("[*]开始扫描目标:{}".format(target_url))
    # print("开始漏洞扫描..................")
    # print(poc_modules)
    for module_name, module in poc_modules.items():
        # print("{0}".format(module_name))
        # print("[+]正在使用{0}进行漏洞检测".format(module_name))
        # 执行poc检测
        if stop_flag.is_set():
            print("检测到强制停止,程序正在安全退出")
            return
        result = module.verify(target_url)
        if result is not None and result['vulnerable']:
            # print("目标存在漏洞")
            # print("[vulnerable]发现目标存在漏洞:{0}".format(target_url))
            # print("[+]漏洞名称:".format(result.get('name')))
            # print("[+]脚本名称:".format(module_name))
            # print_red("     [!] 发现目标存在漏洞: {}".format(target_url))
            # print("     [+] 漏洞名称: {}".format(result.get('Name')))
            # print("     [+] 脚本名称: {}".format(module_name))
            # 命令行输出获取和释放锁
            with output_lock:
                # print(1)
                a = print_aligned_output('[+]检测到漏洞----', target_url, result.get('Name'), module_name)
                print_green(str(a))
                # print(f"目标: {target_url}, 漏洞名称: {result.get('Name')}, 脚本名称: {module_name}")
            with found_vulnerabilities_lock:
                found_vulnerabilities.append(result)
        else:
            with output_lock:
                a = print_aligned_output('[*]未检测到漏洞----', target_url, result.get('Name'), module_name)
                print(a)
                # print(f"[+]未检测到漏洞----目标: {target_url}, 漏洞名称: {result.get('Name')}, 脚本名称: {module_name}")
            # print("     没检测到漏洞")
    # print_green("[*] 扫描完成: {}".format(target_url) + "\n")


def poc_attack(target_url, poc_modules, output_lock):
    # poc攻击模式函数
    for module_name, module in poc_modules.items():
        if hasattr(module, 'attack'):  # 判断模块中是否有攻击函数
            result = module.attack(target_url)
            if result:
                with output_lock:
                    print_green(f"[+] 攻击成功，目标: {target_url}, 脚本名称: {module_name}")
        else:
            with output_lock:
                print(f"[Alert] 没有找到脚本 {module_name} 的攻击函数，跳过攻击.\n")


def get_parser():
    # 命令行解析函数
    # 实例化一个命令行解析器对象
    parser = argparse.ArgumentParser(description='Usage: python CveScan -h')
    # u是段参数名,--url是长参数名
    parser.add_argument('-u', "--url", type=str, help='扫描单个url地址')
    parser.add_argument('-f', "--file", type=str, help='指定url文件进行扫描')
    parser.add_argument('-l', "--list", action='store_true', help='查看所有支持的poc')
    parser.add_argument('-p', "--poc", type=str, help='指定一个poc或者多个poc来检测目标,多个poc用英文逗号分割如')
    parser.add_argument('-a', "--attack", type=str, help='对漏洞进行检测后并尝试攻击')
    parser.add_argument('-t', "--thread", type=int, default=30, help="指定扫描的线程数")
    # 使用解析器来解析命令行参数
    args = parser.parse_args()
    # print(args)
    # args是一个Namespace对象
    return args


def main():
    # 主函数
    args = get_parser()
    # print(args)  #打印解析参数,清理注释得时候这个记得保留,好调式其他功能
    # ascii_alert = pyfiglet.figlet_format("hunter")  # 艺术字
    # print_cool(ascii_alert)
    print_cool("""\n████████ ████████ ███████  ██████  █████  ███    ██ 
   ██       ██    ██      ██      ██   ██ ████   ██ 
   ██       ██    ███████ ██      ███████ ██ ██  ██ 
   ██       ██         ██ ██      ██   ██ ██  ██ ██ 
   ██       ██    ███████  ██████ ██   ██ ██   ████ 
                                                    
                                                    """)
    title = '                  {https://github.com/tr0uble  Bounty hunter}  Version 1.0\n\n'
    print_cool(title)
    # 打印帮助信息
    print("            常用组合:")
    print("                 -l --list  列出支持的所有POC\n")
    print("                 -u --url   指定要扫描的URL\n")
    print("                 -f -file   指定要扫描的URL文件\n")
    print("                 -p --poc   指定要使用的POC,多个POC以逗号分割\n")
    print("                 -a --attack  检测漏洞后,尝试攻击   [示例:--attack shell]\n")
    print("                 -t --thread  指定线程默认为30\n")
    print("                 Ctrl+C       强制终止程序\n")
    # 加载poc模块,字典。
    poc_modules = load_poc_modules()
    # 定义最后输出的漏洞列表
    found_vulnerabilities = []
    # 创建最后输出的漏洞列表锁防止少写入,数据错误
    found_vulnerabilities_lock = threading.Lock()
    # 命令行输出全局锁
    output_lock = threading.Lock()
    # 1.打印所有poc
    if args.list:
        print_green("已更新poc如下:绿色代表可以进行exp攻击,默认上传冰蝎木马\n")
        for module_name, module in poc_modules.items():
            info = module.get_info()
            if info['Attack']:
                print_green("[+] Name: {}".format(info["Name"]))
                print("    Attack: {}".format(info["Attack"]))
                print("    Script: {}".format(info["Script"]))
                print("    Path: {}".format(info["Path"]))
            else:
                print("[+] Name: {}".format(info["Name"]))
                print("    Attack: {}".format(info["Attack"]))
                print("    Script: {}".format(info["Script"]))
                print("    Path: {}".format(info["Path"]) + "\n")

    # 2.根据输入的url或者url文件来扫描
    if args.url:  # 单个url扫描
        # 3.根据单个poc或者多个poc来扫描
        if args.poc:
            specified_pocs = args.poc.split(',')  # 逗号分割从命令行中获取的脚本名称
            for poc in specified_pocs:
                if poc in poc_modules:
                    # print(poc)
                    # print("开始漏洞扫描..................")
                    print_yellow("٩(๑❛ᴗ❛๑)۶٩(๑❛ᴗ❛๑)۶开始漏洞扫描..................\n")
                    poc_scanner(args.url, {poc: poc_modules[poc]}, found_vulnerabilities,
                                found_vulnerabilities_lock,
                                output_lock)
                    # print(poc_modules[poc])
                else:
                    print(f"未找到名称为({poc})的poc")
        else:
            # print("开始漏洞扫描..................")
            print_yellow("٩(๑❛ᴗ❛๑)۶٩(๑❛ᴗ❛๑)۶开始漏洞扫描..................\n")
            poc_scanner(args.url, poc_modules, found_vulnerabilities, found_vulnerabilities_lock, output_lock)
    elif args.file:  # 根据文件中读取url扫描
        # 3.根据单个poc或者多个poc来扫描
        if args.poc:
            specified_pocs = args.poc.split(',')  # 逗号分割从命令行中获取的脚本名称
            try:
                with ThreadPoolExecutor(max_workers=args.thread) as executor:
                    futures = []
                    # print("开始漏洞扫描..................\n")
                    print_yellow("٩(๑❛ᴗ❛๑)۶٩(๑❛ᴗ❛๑)۶开始漏洞扫描..................\n")
                    with open(args.file, 'r') as f:
                        for url in f:
                            for poc in specified_pocs:
                                if poc in poc_modules:
                                    # print(poc)
                                    # 提交线程,并传入停止得标志stop
                                    # 提交线程
                                    future = executor.submit(poc_scanner, url.strip(), {poc: poc_modules[poc]},
                                                             found_vulnerabilities, found_vulnerabilities_lock,
                                                             output_lock, stop_flag)
                                    # poc_scanner(url.strip(), {poc: poc_modules[poc]}, found_vulnerabilities)
                                    # print(poc_modules[poc])
                                    futures.append(future)
                                else:
                                    print(f"未找到名称为({poc})的poc")
                    for future in as_completed(futures):
                        future.result()
            except KeyboardInterrupt:
                # stop_flag.set()
                # print("检测到ctrl+c,程序正在退出..........")
                # os._exit(0)
                # os.kill(os.getpid(), signal.SIGKILL)
                pass

        else:  # 不指定poc
            try:
                with ThreadPoolExecutor(max_workers=args.thread) as executor:
                    futures = []
                    with open(args.file, 'r') as f:
                        print_yellow("٩(๑❛ᴗ❛๑)۶٩(๑❛ᴗ❛๑)۶开始漏洞扫描..................\n")

                        for url in f:
                            # poc_scanner(url.strip(), poc_modules, found_vulnerabilities,found_vulnerabilities_lock)
                            future = executor.submit(poc_scanner, url.strip(), poc_modules, found_vulnerabilities,
                                                     found_vulnerabilities_lock, output_lock, stop_flag)
                            futures.append(future)
                            # print(123)
                    for future in as_completed(futures):
                        future.result()
            except KeyboardInterrupt:
                # stop_flag.set()
                # print("检测到ctrl+c,程序正在退出..............")
                # os._exit(0)  # 这个函数,不会执行清理工作,如关闭文件,网络连接啥的
                # os.kill(os.getpid(), signal.SIGKILL)  # 直接杀死python进程
                pass



    else:
        pass
        # print("请输入扫描的URL或者URL文件.")

    # 打印所有发现的漏洞
    if args.url or args.file:
        if found_vulnerabilities:
            print_yellow("\n[+]扫描结束发现以下漏洞٩(๑❛ᴗ❛๑)۶٩(๑❛ᴗ❛๑)۶")
            for vulnerability in found_vulnerabilities:
                # pass
                # print("[+] 目标: {} ,漏洞名称: {} ,脚本名称: {} ".format(_['url'], _['Name'], _['Script']))
                a = print_aligned_output("", vulnerability['url'], vulnerability['Name'],
                                         vulnerability['Script'] + "")
                print_green(a)
                # attack = input("发现漏洞，是否进行攻击？ (y/N) ")
            if args.attack and args.attack.lower() == "shell":
                print_yellow("\n检测到: --attack shell参数,开始执行攻击函数")
                for vulnerability in found_vulnerabilities:
                    a = print_aligned_output("", vulnerability['url'], vulnerability['Name'],
                                             vulnerability['Script'] + " ")
                    print(a.strip())
                    poc_attack(vulnerability['url'], poc_modules, output_lock)
            else:
                pass
        else:
            print_yellow("[-]扫描完成,很可惜没有发现漏洞(⁎˃ᆺ˂)\n")


# 初始化颜色库
init()


def print_red(text):
    print(Fore.RED + text + Style.RESET_ALL)


def print_green(text):
    print(Fore.GREEN + text + Style.RESET_ALL)


# 黄色
def print_yellow(text):
    print(Fore.YELLOW + text + Style.RESET_ALL)


# 紫色
def print_magenta(text):
    print(Fore.MAGENTA + text + Style.RESET_ALL)


# 工具logo样式,
def print_cool(text):
    # cool_text = colored(text, 'blue', 'on_grey', ['blink'])  #带字体闪动
    cool_text = colored(text, 'blue', )
    print(cool_text)


# 命令行输出对齐输出函数
def print_aligned_output(prefix, target_url, vulnerability_name, module_name):
    target_url = target_url.ljust(30)
    vulnerability_name = vulnerability_name.ljust(20)
    module_name = module_name.ljust(20)
    formatted_string = f"{prefix}目标: {target_url}  漏洞名称: {vulnerability_name}  脚本名称: {module_name}""\n"
    return formatted_string


# ctrl+C线程停止函数
def stop_task(stop_flag):
    while not stop_flag.is_set():
        # 执行其他操作
        pass
    print("任务已停止。")


if __name__ == '__main__':
    get_parser()
    main()
