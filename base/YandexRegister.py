import threading, random
from base.BaseRequests import YandexRequests
from colorama import Fore
from utils.Helper import proxy_use_and_delete, w_acc, w_proxy

lock = threading.Lock()

class YandexRegister(YandexRequests):
    proxy_status = True
    
    def __init__(self, firstname, lastname, mail, password, secret_question, secret_answer, Captcha):
        super().__init__(firstname, lastname, mail, password, secret_question, secret_answer,)
        self.Captcha = Captcha
        
    def set_proxy(self):
        with lock:
            proxy = proxy_use_and_delete()
            if proxy:
                super().set_proxy(proxy)
                print(f"Proxy: {proxy}")
            else:
                if YandexRegister.proxy_status:
                    YandexRegister.proxy_status = False
                    print(Fore.LIGHTRED_EX + "[ no proxy ]" + Fore.RESET)
                    return False
            return proxy
        
    def start(self, choose_creator_type = None, choose_ip_method = None):
        if choose_ip_method == "1":
            proxy = self.set_proxy()
            if not proxy: return False, "proxy_none"
            
        if self.register():
            if choose_creator_type == "1": #if imap active 
                imap = self.imap()
                if imap:
                    w_acc(self.login + '@yandex.com:' + self.password + ":" + imap)
                    if choose_ip_method == "1": #method proxy
                        w_proxy(proxy)
                else:
                    return False
            else:
                w_acc(self.login + '@yandex.com:' + self.password)
                if choose_ip_method == "1": #method proxy
                    w_proxy(proxy)
            return True
        
    def captcha(self): #! if captcha is false, it tries a second time.
        err_counter = 0
        while(err_counter < 2): 
            yandexCaptcha_url = super().get_captcha()
            if not yandexCaptcha_url:
                err_counter += 1
                continue
        
            print("[Yandex] - captcha solving.")
            captcha_answer = self.Captcha.solve(yandexCaptcha_url)
            if type(captcha_answer) is tuple:
                captcha_id, captcha_answer = captcha_answer
                
            if not captcha_answer:
                print("[Yandex] - captcha not solved.")
                err_counter += 1
                continue
            
            print("[Yandex] - captcha check pending.")
            check_answer = super().check_solved_captcha(captcha_answer)
            if not check_answer: #captcha hatalı mesajı gönder. bakiye için.
                print(Fore.LIGHTRED_EX + "[Yandex] - captcha failed." + Fore.RESET)
                if type(captcha_answer) is tuple:
                    self.Captcha.report_captcha(captcha_id)
                err_counter += 1
                continue
            print("[Yandex] - captcha successful.")
            return check_answer
        print(Fore.LIGHTRED_EX + "[Yandex] - captcha failed." + Fore.RESET)
        return False
    
    def register(self):
        if not super().get_tokens():
            if "proxy_error" in self.error:
                self.error = ""
                print("invalid proxy")
                return False
            
        if not self.rand_mail():
            return False
        
        solvedCaptcha = self.captcha()
        if not solvedCaptcha:
            return False
        
        #super().logger_sync()
        
        register_result = super().confirm_register(solvedCaptcha)
        if not register_result:
            return False
        
        print(f"[Yandex] - {self.login}@yandex.com:{self.password}")
        print("[Yandex] - registration completed.")
        return True
    
    def imap(self): #! if imap is false, it tries a second time.
        err_counter = 0
        while(err_counter < 2):
            imap_password = super().imap_create_password()
            if not imap_password:
                err_counter += 1
                continue
            
            imap_perm = super().imap_perm()
            if not imap_perm:
                err_counter += 1
                continue
            
            print(Fore.GREEN + "[Yandex] - imap permissions enabled successfully." + Fore.RESET)
            return imap_password
        return False
                
    def rand_mail(self):
        '''
        Generates random mail name with firstname and lastname.
        '''
        generated = super().generate_mail_name() #bazen boş oluyor
        if generated:
            rand_select = random.randrange(len(generated))
            self.login = generated[rand_select]
            return self.login
        else:
            print("random mail not created")
            return False

