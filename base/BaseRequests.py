import json, re, time, requests
from base.Logger import Logger

class YandexRequests:  
    def __init__(self, firstname, lastname, login, password, secret_question, secret_answer):
        self.firstname = firstname
        self.lastname = lastname
        self.login = login
        self.password = password
        self.secret_question = secret_question
        self.secret_answer = secret_answer
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'X-Requested-With': 'XMLHttpRequest'
            }
        self.tokens = None
        self.error = ""
    
    def set_proxy(self, proxy):
        _proxy = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        self.session.proxies = _proxy
        
    def post_request(self, url, data, headers=None):
        try:
            return self.session.post(url, data=data, headers=headers, timeout=10)
        except requests.exceptions.ConnectionError:
            self.error = "proxy_error"
            return False           
        except Exception:
            return False
        
    def get_request(self, url):
        try:
            return self.session.get(url, timeout=10)
        except requests.exceptions.ConnectionError:
            self.error = "proxy_error"
            return False
        except Exception:
            return False
        
    def get_tokens(self):
        web_content = self.get_request('https://passport.yandex.com.tr/registration/')
        if "proxy_error" in self.error or not web_content: return False
        self.tokens = dict(re.findall(r'.?(csrf|track_id)"\s?:\s?"([:\w\s]+)', web_content.text))
        if not "track_id" in self.tokens or not "csrf" in self.tokens: return False
        return self.tokens
    
    def generate_mail_name(self):
        generated = self.post_request('https://passport.yandex.com.tr/registration-validations/suggestV2', 
                            data={
                                'track_id': self.tokens['track_id'],
                                'csrf_token': self.tokens['csrf'],
                                'login': self.login,
                                'firstname': self.firstname,
                                'lastname': self.lastname
                                })
        return generated.json()['logins'] if generated else False

    def logger_post(self, log):
        self.post_request("https://passport.yandex.com.tr/registration-validations/logger",
            data={
            'track_id': self.tokens['track_id'], 
            'csrf_token': self.tokens['csrf'], 
            'log': log
            })
        
    def logger_sync(self):
        #Required so that created accounts are not spam.
        #But not yet completed. Because Javascript codes are obfuscate on the yandex side.
        #It takes time to solve.
        
        params = self.firstname, self.lastname, self.login, self.password, self.password, self.secret_question, self.secret_answer
        input_names = "firstname", "lastname", "login", "password", "password_confirm", "hint_question_custom", "hint_answer", "captcha"
        
        for name in input_names:
            self.logger_post(Logger(self.tokens['track_id'], "field:blur", name, 0).encrypt())
            self.logger_post(Logger(self.tokens['track_id'], "field:focus", name, 0).encrypt())
            
            length = 0
            while length < len(params):
                self.logger_post(Logger(self.tokens['track_id'], "keydown:symbol").encrypt())
                self.logger_post(Logger(self.tokens['track_id'], "keyup:symbol").encrypt())
                length+=1
        
    def get_captcha(self):
        response = self.post_request('https://passport.yandex.com.tr/registration-validations/textcaptcha',
                        data={
                            'track_id': self.tokens['track_id'], 
                            'csrf_token': self.tokens['csrf'], 
                            'language': 'tr', 
                            'ocr': 'true'
                            })
        return response.json()['image_url'] if response else False

    def check_solved_captcha(self, answer):
        '''return true if captcha is true'''
        response = self.post_request('https://passport.yandex.com.tr/registration-validations/checkHuman', 
                        data={
                            'track_id': self.tokens['track_id'],
                            'csrf_token': self.tokens['csrf'],
                            'answer': answer
                            })
        return response.json()['status'] == 'ok' if response else False

    def confirm_register(self, captchaAnswer):
        register = self.post_request('https://passport.yandex.com.tr/registration-validations/registration-alternative', 
                        data={
                            'track_id': self.tokens['track_id'],
                            'csrf_token': self.tokens['csrf'],
                            'firstname': self.firstname, 
                            'lastname': self.lastname,
                            'surname': '',
                            'login': self.login,
                            'password': self.password,
                            'password_confirm': self.password,
                            'hint_question_id': '99',
                            'hint_question': self.secret_question,
                            'hint_question_custom': self.secret_question,
                            'hint_answer': self.secret_answer,
                            'captcha': captchaAnswer,
                            'phone': '',
                            'phoneCode': '',
                            'publicId': '',
                            'human-confirmation': 'captcha',
                            'from': 'mail',
                            'origin': 'hostroot_homer_reg_tr',
                            'eula_accepted': 'on',
                            'type': 'alternative'
                            })
        return 'ok' in register.json()['status'] if register else False
    # 'code': 'notavailable'      kullanıcı bilgileri kullanılıyor olabilir.

    
    def get_imap_tokens(self):
        web_content = self.get_request('https://passport.yandex.com.tr/profile/access/apppasswords/create')
        if not web_content: return False
        self.tokens['track_id'] = re.findall(r'(?:track_id[^\w].value[^\w]).([:\w\=]*)', web_content.text)[0]
        self.tokens['csrf'] = re.findall(r'(?:csrf[^\w].value[^\w]).([:\w\=]*)', web_content.text)[0]
        self.tokens['scope'] = re.findall(r'(?:scope[^\w].value[^\w]).([:\w\=]*)', web_content.text)[0]
        self.tokens['uid'] = re.findall(r'(?:data-uid=?).([\w]*)', web_content.text)[0]
        return True
    
    def imap_app_enable(self): 
        if self.get_imap_tokens():
            result = self.post_request('https://passport.yandex.com.tr/registration-validations/appPwdActivate',
                        data={'track_id': self.tokens['track_id'], 
                        'csrf_token': self.tokens['csrf'],
                        })
            if not result: return False
            return result.text
        
    def imap_create_password(self):
        if self.imap_app_enable():
            result = self.post_request('https://passport.yandex.com.tr/registration-validations/profile/apppassword/create/',
                                data={'track_id': self.tokens['track_id'],
                                    'csrf_token': self.tokens['csrf'],
                                    'appPasswordsStatus': 'enabled',
                                    'clientId': self.tokens['scope'],
                                    'deviceName': 'imap',
                                    'lang': 'tr'
                                    })
            return result.json()['alias'] if result else False 
        
    def imap_perm_tokens(self):
        result = self.get_request("https://mail.yandex.com.tr/#setup/other")
        if not result: return False
        self.tokens['connection_id'] = re.findall(r'(?:connection_id[^\w]+)([\w=!-]+)', result.text)[0]
        self.tokens['ckey'] = re.findall(r'(?:ckey[^\w]+)([\w\\=!+%&!&?_-]*)', result.text)[0].replace(r'\\u002F', '/').replace(r'\u002F', '/')
        self.tokens['exp_boxes'] = re.findall(r'(?:\bexp-boxes[^\w]+)([\w!,;]+)', result.text)[0]
        self.tokens['eexp_boxes'] = re.findall(r'(?:eexp-boxes[^\w]+)([\w!,;]+)', result.text)[0]
        return True 

    def imap_perm(self):
        if self.imap_perm_tokens():
            result = self.post_request('https://mail.yandex.com.tr/web-api/models/liza1?_m=do-settings,settings', 
                                    data=json.dumps({
                                    "models": [
                                        {
                                            "name": "do-settings",
                                            "params": {
                                                "params": '{"enable_imap":true,"disable_imap_autoexpunge":"","fid":[]}'
                                            },
                                            "meta": {"requestAttempt": 1},
                                        },
                                        {
                                            "name": "settings",
                                            "params": {
                                                "list": "enable_imap,disable_imap_autoexpunge,fid",
                                                "actual": "true",
                                                "withoutSigns": "true",
                                            },
                                            "meta": {"requestAttempt": 1},
                                        },
                                    ],
                                    "_ckey": self.tokens['ckey'],
                                    "_uid": self.tokens['uid'],
                                    "_locale": "tr",
                                    "_timestamp": round(time.time() * 1000),
                                    "_product": "TUR",
                                    "_connection_id": self.tokens['connection_id'],
                                    "_exp": self.tokens['exp_boxes'],
                                    "_eexp": self.tokens['eexp_boxes'],
                                    "_service": "LIZA",
                                    "_version": "33.0.0",
                                    "_messages_per_page": "30",
                                }), headers={'content-type': 'application/json'})
            if not result: return False
            if result.json()['models'][0]['status'] == 'ok': return True
