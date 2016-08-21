import requests
import traceback


class Login():
    def __init__ (self):
        self.Session = requests.Session()
        self.Session.headers.update({'User-Agent' :
                                     'Mozilla/5.0 (Linux; Android 5.1; MZ-m2 note Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/45.0.2454.94 Mobile Safari/537.36'})
        #self.Session.proxies = {'http': '127.0.0.1:9690', 'https': '127.0.0.1:9690'}

    def Plogin (self):
        try:
            #r = self.Session.get('http://m.jd.com')
            r = self.Session.get('https://passport.m.jd.com/user/login.action?returnurl=http://m.jd.com?indexloc=1')
            r = self.Session.get('https://plogin.m.jd.com/cgi-bin/m/authcode?mod=login')
            with open('a.png','wb') as f:
                f.write(r.content)
                f.close()

        except Exception as e:
            print e.message, traceback.format_exc()



if __name__ == '__main__':
    tt = Login()
    tt.Plogin()
