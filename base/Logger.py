import json, math, time
#"{\"ev_tsf\":1647869324346,\"loglevel\":\"info\",\"track_id\":\"0af58542c0222b66e512ebf7da7ad1abcb\",\"url\":\"https://passport.yandex.com.tr/registration/",\"action\":\"field:blur\",\"withTrackId\":true,\"field\":{\"name\":\"firstname\",\"length\":2}}"
#"{\"ev_tsf\":1647869444934,\"loglevel\":\"info\",\"track_id\":\"0af58542c0222b66e512ebf7da7ad1abcb\",\"url\":\"https://passport.yandex.com.tr/registration/",\"action\":\"field:focus\",\"withTrackId\":true,\"field\":{\"name\":\"lastname\",\"length\":0}}"
#"{\"ev_tsf\":1647869686541,\"loglevel\":\"info\",\"track_id\":\"0af58542c0222b66e512ebf7da7ad1abcb\",\"url\":\"https://passport.yandex.com.tr/registration/",\"action\":\"keydown:symbol\",\"withTrackId\":true}"
#"{\"ev_tsf\":1647868788641,\"loglevel\":\"info\",\"track_id\":\"0af58542c0222b66e512ebf7da7ad1abcb\",\"url\":\"https://passport.yandex.com.tr/registration/",\"action\":\"keyup:symbol\",\"withTrackId\":true}"

class Logger:
    ''' inputname = firstname, lastname, login, password, password_confirm, hint_question_custom, hint_answer, captcha'''
    ''' action = "field:blur", "field:focus", "keydown:symbol", "keyup:symbol" '''
    def __init__(self, track_id, action, input_name = None, length = None):
        self.track_id = track_id
        self.input_name = input_name
        self.length = length
        self.char_list = []
        self.data_array={
        "ev_tsf": round(time.time() * 1000),
        "loglevel":"info",
        "track_id": track_id,
        "url":"https://passport.yandex.com.tr/registration/",
        "action": action,
        "withTrackId": True
        }
        if "field" in action: self.data_array['field'] = {"name":self.input_name, "length":self.length}
    def charCodeAt(self, index):
        return ord(self.track_id[math.floor(index % len(self.track_id))])
    def uni_list(self):
        self.data_array = json.dumps(self.data_array).replace(" ","")
        for index, i in enumerate(self.data_array):
            a = self.charCodeAt(index)
            b = ord(i) ^ a
            self.char_list.append(b)
    def encrypt(self):
        self.uni_list()
        u = 0
        log = ""
        char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        while(u < len(self.char_list)):
            try:                    
                bit1= self.char_list[u] << 16
                bit2 = self.char_list[u+1] << 8
                bit3 = self.char_list[u+2]
            except:
                x = len(self.char_list) % 3
                if x == 1:
                    bit1 = 0
                    bit2 = 0
                if x == 2:
                    bit3 = 0
            o = (bit1 | bit2 | bit3)
            e = o >> 12 & 63
            r = o >> 6 & 63
            i = 63 & o
            log += char[o >> 18 & 63] + char[e] + char[r] + char[i]
            u = u+3
        a = len(self.data_array) % 3
        if a:
            return log[0:a-3] + "=" * (3 - a)
        else:
            return log