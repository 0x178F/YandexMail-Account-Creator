import threading, time
from base.YandexRegister import YandexRegister
from colorama import Fore
from utils.Helper import connect_device, device_mobile_data, new_account
from utils._2captcha import TwoCaptcha

print(Fore.LIGHTBLUE_EX + "===============================")
print("      Yandex Creator Bot       ")
print("===============================")
while True:
    print(Fore.LIGHTMAGENTA_EX + "-------------------------------")
    print("[0] - Only yandex account" + '\n' + "[1] - Yandex account imap enabled.")
    print("-------------------------------" + Fore.RESET)
    choose_creator_type = input("[#] Please choose account creator method: -> " )
    if choose_creator_type == "0" or choose_creator_type == "1": break
while True:
    print(Fore.LIGHTMAGENTA_EX + "-------------------------------")
    print("[0] - Same ip address (no recommend max: 25-30 acc)" + '\n' + "[1] - Proxy" + "\n" + "[2] - Android adb")
    print("-------------------------------" + Fore.RESET)
    choose_ip_method = input("[#] Please choose ip method: -> ")
    print(Fore.LIGHTMAGENTA_EX + "-------------------------------")
    if choose_ip_method == "2":
        adb = connect_device()
        if not adb:
            i = 0
            while True:
                print(Fore.LIGHTMAGENTA_EX + "-------------------------------")
                adb = connect_device()
                if not adb:
                    time.sleep(1)
                    i+= 1
                    if i >= 10: 
                        print(Fore.LIGHTMAGENTA_EX + "-------------------------------")
                        print(Fore.LIGHTYELLOW_EX + "Creator was stopped because the device was not connected.")
                        print(Fore.LIGHTMAGENTA_EX + "-------------------------------")
                        quit()
                    continue
                else:
                    break
    if choose_ip_method == "0" or choose_ip_method == "1" or choose_ip_method == "2": break
    
while True:
    print(Fore.LIGHTMAGENTA_EX + "-------------------------------" + Fore.RESET)
    choose_acc_count = input("[#] How many accounts do you want to create? -> ")
    if choose_acc_count.isdecimal() and int(choose_acc_count) != 0:
        break
    
if choose_ip_method == "0" or choose_ip_method == "1":  
    while True:
            print(Fore.LIGHTMAGENTA_EX + "-------------------------------" + Fore.RESET)
            threads = input(f"[#] How many threads do you want to use? (max={choose_acc_count}) -> ")
            print(Fore.LIGHTMAGENTA_EX + "-------------------------------" + Fore.RESET)
            if threads.isdecimal() and int(threads) > 0 and int(threads) <= int(choose_acc_count):
                break
else:
    threads = "1"
    
prevent_loop = 0
acc_counter = 0
def main():
    global prevent_loop
    global acc_counter
    while(prevent_loop < int(choose_acc_count)):         
        prevent_loop += 1  #! prevent infinite loop for multi-threading.
        
        account_info = new_account()
        if not account_info: break
        
        twoCaptcha = TwoCaptcha(account_info['api_key'])
        
        Bot = YandexRegister(account_info['firstname'],
                            account_info['lastname'],
                            account_info['mail'],
                            account_info['password'], 
                            account_info['secret_question'],
                            account_info['secret_answer'],
                            twoCaptcha
                            )
        botStart = Bot.start(choose_creator_type, choose_ip_method)
        
        if type(botStart) is tuple:
            if "proxy_none" in botStart:
                break
            
        #no proxy left. the creator will stop when the process is complete.
        if not botStart:                
            prevent_loop -= 1
            continue
        
        acc_counter += 1
        print(Fore.GREEN + f"*** [Yandex] - {acc_counter} accounts created. ***" + Fore.RESET)
        
        if choose_ip_method == "2":
            device_mobile_data(adb)
if threads:       
    for x in range(int(threads)):
        threading.Thread(target=main).start()