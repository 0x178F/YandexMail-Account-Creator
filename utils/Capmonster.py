import base64, json, requests
from colorama import Fore
from time import sleep

class CapMonster():
    def __init__(self, api):
        self.api = api
        self.counter  = 0
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
    
    def check_balance(self):
        response = self.post_request("https://api.capmonster.cloud/getBalance", data=json.dumps({"clientKey": self.api}))
        try:
            if response.json()['errorId'] == 0:
                if response.json()['balance'] <= 0.010:
                    print(Fore.LIGHTRED_EX + "[CapMonster] - ERROR_ZERO_BALANCE" + Fore.RESET)
                    quit()
            else:
                print(Fore.LIGHTRED_EX + f"[CapMonster] - {response.json()['errorCode']}" + Fore.RESET)
                quit()
            return True
        except Exception:
            return False 
        
    def send_captcha(self, img):
        response = self.post_request('https://api.capmonster.cloud/createTask', 
        data=json.dumps({'clientKey': self.api + "__yandexwave",
        'task': {'type':'ImageToTextTask', 'body': base64.b64encode(self.get_request(img).content).decode("utf-8")}
        }))
        if not response: return False
        if response.json()["errorId"] == 0:
            return response.json()["taskId"]
        else:
            return False
            
    def result_captcha(self, taskId):
        while True:
            if self.counter>=40: #120 seconds.
                return False
            response = self.post_request('https://api.capmonster.cloud/getTaskResult', 
            data=json.dumps({'clientKey': self.api, 'taskId': taskId }))
            if response:
                if response.json()["status"] == "processing":
                    sleep(3)
                    self.counter+=1
                    continue
                elif response.json()["status"] == "ready":
                    return response.json()["solution"]["text"]

    def solve(self, img):
        if not self.check_balance(): return False
        taskId = self.send_captcha(img)
        if not taskId: return False
        result = self.result_captcha(taskId)
        if not result: return False
        return result