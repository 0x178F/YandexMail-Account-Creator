import os, random, string, json
import platform
import subprocess
import time
import requests
from colorama import Fore
from utils._2captcha import TwoCaptcha
from utils.Capmonster import CapMonster
from ppadb.client import Client as AdbClient
path = os.getcwd()
def connect_device():
    osName = platform.system()
    if "Windows" in osName:
        subprocess.Popen(f"{path}/adb/win/adb.exe start-server", stdout=subprocess.PIPE, shell=True).wait()
    elif "Darwin" in osName:
        subprocess.Popen(f"{path}/adb/mac/adb start-server", stdout=subprocess.PIPE, shell=True).wait()
    
    client =AdbClient(host="127.0.0.1",port=5037)
    devices=client.devices()
    if not devices:
        print(Fore.LIGHTRED_EX + "Device not found." + Fore.RESET)
        return False
    print(Fore.LIGHTCYAN_EX + "Device is connected." + Fore.RESET)
    return devices[0]
def device_airplane(device, x_y):
    device.shell("am start -a android.settings.AIRPLANE_MODE_SETTINGS")
    while True:
        if "AirplaneModeSettings" in device.shell("dumpsys window windows | grep -E 'mObscuringWindow'"):
            break
    
    while True:
        if "0" in device.shell("settings get global airplane_mode_on"):
            device.shell(f'input touchscreen tap {x_y}')
                    
        elif "1" in device.shell("settings get global airplane_mode_on"): 
            device.shell(f'input touchscreen tap {x_y}')
            device.shell('input keyevent 3')
            break
def device_mobile_data(device):
    old_ip = whatismyip()
    while True:
        if "1" in device.shell("settings get global mobile_data"):
            device.shell("svc data disable")
            
        elif "0" in device.shell("settings get global mobile_data"):
            device.shell("svc data enable")
            new_ip = whatismyip()
        if not old_ip == new_ip: break
def whatismyip():
    '''If it does not return a value within 10 seconds, it will return false'''
    i = 0
    while i < 10:
        try:
            i += 1
            return requests.get("https://api.ipify.org").text
        except:
            time.sleep(1)
            continue
    return False
def read_file(file):
    with open(f"{path}{file}", "r") as f:
        data = f.read()
        if data:
            lines = data.splitlines()
            return lines
def remove_firstline(file):
    proxy_path = f"{path}{file}"
    file_content = ''
    with open(proxy_path,'r') as f:
            next(f)  # skip line
            for line in f:
                file_content = file_content + line
    with open(proxy_path, "w") as f:
        f.write(file_content)
        return True
def firstname():
    with open(f"{path}/data/firstname.txt", 'r') as f:
        lines = f.read().splitlines()
        return random.choice(lines)
def lastname():
    with open(f"{path}/data/firstname.txt", 'r') as f:
        lines = f.read().splitlines()
        return random.choice(lines)
def generate_password(password_length):
    characters = string.ascii_letters + string.digits
    password =  "".join(random.sample(characters, password_length))
    return password
def w_file(file, text):
    with open(f"{path}{file}", "a") as f:
        f.write(text + '\r\n')
def w_acc(text):
    w_file("/data/createdAccs.txt", text)
def w_proxy(text):
    w_file("/data/usedproxy.txt", text)
def get_proxies():
    return read_file("/data/proxies.txt") if True else False
def remove_proxy():
    return remove_firstline("/data/proxies.txt")
def get_settings():
    with open(f"{path}/settings.json", "r") as f:
        data = json.load(f)
    if not data:
        return False
    return data
def proxy_use_and_delete():
    proxy = get_proxies() #get all proxy
    if not proxy:
        return False
    if not remove_proxy(): #remove firstline
        return False
    return proxy[0] #return firstline
def new_account():
    first_name = firstname()
    last_name = lastname()
    mail_name = first_name + " " + last_name
    
    settings = get_settings()
    api_key = settings['api_key']
    if not api_key:
        print(Fore.LIGHTRED_EX + "api_key is wrong." + Fore.RESET)
        return False
    
    captcha_service = settings['captcha_service']
    if not captcha_service:
        print(Fore.LIGHTRED_EX + "captcha_service is wrong." + Fore.RESET)
        return False
    
    if captcha_service == "twocaptcha":
        captcha = TwoCaptcha(api_key)
    elif captcha_service == "capmonster":
        captcha = CapMonster(api_key)
        
    secret_question = settings['secret_question']
    if not secret_question:
        print(Fore.LIGHTRED_EX + "secret_question is wrong." + Fore.RESET)
        return False
        
    secret_answer = settings['secret_answer']
    if not secret_answer:
        print(Fore.LIGHTRED_EX + "secret_answer is wrong." + Fore.RESET)
        return False

    return {
        'firstname':first_name,
        'lastname':last_name,
        'mail': mail_name,
        'password':generate_password(8),
        'secret_question' : secret_question,
        'secret_answer' : secret_answer,
        'obj_captcha': captcha
        }