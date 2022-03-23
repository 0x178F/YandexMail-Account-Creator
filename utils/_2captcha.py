import base64
from time import sleep
import requests

class TwoCaptcha():
    def __init__(self, api):
        self.api = api
        self.counter = 0
        
    def post_request(self, url, data=None):
        try:
            return requests.post(url, data=data)
        except Exception:
            return False
        
    def get_request(self, url, data=None):
        try:
            return requests.get(url, data=data)
        except Exception:
            return False
            
    def report_captcha(self, id):
        return self.post_request("http://2captcha.com/res.php",
                                data={'key': self.api,
                                    'action': 'reportbad',
                                    'id': id
                                    })
    
    def send_captcha(self, imgUrl):
        response = self.post_request('http://2captcha.com/in.php', 
                data={'key': self.api,
                'method': 'base64',
                'body': base64.b64encode(self.get_request(imgUrl).content),
                'json': '1'
                })
        if response:
            response = response.json()
            if 'ERROR_ZERO_BALANCE' in response['request']:
                print('2CAPTCHA: ERROR_ZERO_BALANCE')
                quit()
            return response['request']
        else:
            return False
        
    def check_captcha(self, captcha_id):
        '''returns the result of the sent captcha'''
        '''true if successful, false if unsuccessful'''
        while True:
            if self.counter>=40: #120 seconds.
                return False
            response = self.post_request('http://2captcha.com/res.php', 
                        data={'key': self.api, 'action': 'get', 'id': captcha_id, 'json': '1'})
            if response:
                sleep(3)
                if not 'CAPCHA_NOT_READY' in response.json()['request']: break
            else:
                return False
            self.counter+=1
        return response.json()['request']
    
    def solve(self, imgUrl):  
        captcha_id = self.send_captcha(imgUrl)
        if not captcha_id: return False, False
        
        captcha_result = self.check_captcha(captcha_id)
        if not captcha_result: return False, False
        
        return captcha_id, captcha_result
    
if __name__ == "__main__":
    print ("Executed when invoked directly")
else:
    print ("Executed when imported")