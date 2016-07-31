import requests
import time
import random
import re
import pyqrcode
import Image
import xml.dom.minidom
import json
import traceback

class WxClient():
    def __init__(self):
        self.Session = requests.Session()
        self.Session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5'})
        self.BaseRequest = {
                'DeviceID' : 'e' + repr(random.random())[2:17],
            }
        self.Info_Base = {}
        self.Info_SyncKey = {}
        self.Info_User = {}
        self.IsLogin = False

    def WxLogin(self):
        '''
            web weixin login
        '''
        def WaitForLogin(self):
            '''
                wait for user to scan it,after login,get base info
            '''
            for loop in range(1,10):
                '''
                    #because user param in self.Session.get,the uuid will be urlencode,so we not use params
                    LoginParam = {
                        '_' : int(time.time()),
                        #'loginicon' : 'true',
                        #'r' : -947878708,
                        'tip' : 0,
                        'uuid' : self.Info_Base['UUID'],
                    }
                    #r = self.Session.get('https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login',params = LoginParam)
                '''
                r = self.Session.get('https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=0&uuid=%s&_=%s' % (self.Info_Base['UUID'], int(time.time())))
                r.encoding = 'utf-8'
                code = re.search(r'window.code=(\d+);', r.content)
                reurl = re.search(r'window.redirect_uri="(\S+)"', r.content)
                redirect_url = None
                if code:
                    if '200' == code.group(1):
                        print 'Login Success...'
                        redirect_url = reurl.group(1)
                        break;
                    elif '201' == code.group(1):
                        print 'Wait for Sure...'
                    elif '408' == code.group(1):
                        print 'Wait for Scan...'
                    else:
                        print 'Unknow login return code',code.group(1)
                time.sleep(1)
            if None == redirect_url:
                return False
            r = self.Session.get(redirect_url + '&fun=new')
            r.encoding = 'utf-8'

            #get base info
            doc = xml.dom.minidom.parseString(r.text)
            root = doc.documentElement
            for info in root.childNodes:
                if 'skey' == info.nodeName:
                    self.BaseRequest['Skey'] = info.childNodes[0].data
                elif 'wxsid' == info.nodeName:
                    self.BaseRequest['Sid'] = info.childNodes[0].data
                elif 'wxuin' == info.nodeName:
                    self.BaseRequest['Uin'] = info.childNodes[0].data
                elif 'pass_ticket' == info.nodeName:
                    self.Info_Base['pass_ticket'] = info.childNodes[0].data
                else:
                    pass
            print self.BaseRequest
            #post to get SyncKey and my user info
            PostParams = {
                'BaseRequest' : self.BaseRequest,
                }
            r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=%s&lang=zh_CN&pass_ticket=%s' % (int(time.time()),self.Info_Base['pass_ticket'])
                                  ,json.dumps(PostParams))
            r.encoding = 'utf-8'
            infoDict = json.loads(r.text)
            self.Info_User = infoDict['User']
            self.Info_SyncKey = infoDict['SyncKey']
            if 0 != infoDict['BaseResponse']['Ret']:
                print 'Get SyncKey and MyUserInfo Failure...'
                return False

            #finnaly,post to make sure
            PostParams = {
                'BaseRequest' : self.BaseRequest,
                'ClientMsgId' : int(time.time()),
                'Code' : 3,
                'FromUserName' : self.Info_User['UserName'],
                'ToUserName' : self.Info_User['UserName'],
                }
            r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % self.Info_Base['pass_ticket'],data = json.dumps(PostParams))
            r.encoding = 'utf-8'
            retjson = json.loads(r.text)
            if 0 == retjson['BaseResponse']['Ret']:
                return True
            else:
                print 'Make sure failure',retjson['BaseResponse']['Ret']
                return False

        #First,we get UUID
        TimeTick = int(time.time())
        GetParam = {
            '_': TimeTick,
            'appid': 'wx782c26e4c19acffb',
            'fun' : 'new',
            'lang': 'zh_CN',
            'redirect_uri' : 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
        }
        try:
            r = self.Session.get('https://login.weixin.qq.com/jslogin',params = GetParam)
            r.encoding = 'utf-8'
            regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
            pm = re.search(regx, r.text)
            if pm:
                code = pm.group(1)
                self.Info_Base['UUID'] = pm.group(2)
                if code != '200':
                    print 'Get UUID Failure,return code',code
                    return False
            else:
                print 'Get UUID with re Failure...'
                return False

            #second,we get QR
            r = self.Session.get('https://login.weixin.qq.com/qrcode/' + self.Info_Base['UUID'])
            with open('QR.jpeg','wb') as f:
                f.write(r.content)
                f.close()
            Image.open("QR.jpeg").show()
            print 'Save QR to QR.jpeg,please scan it by phone...'

            #qr = pyqrcode.create('https://login.weixin.qq.com/qrcode/' + self.Info_Base['UUID'])
            #print qr.terminal(quiet_zone=1)

            if True != WaitForLogin(self):
                return False
            print 'Login Success...'
            self.IsLogin = True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def SyncCheck(self):
        try:
            r = self.Session.get('https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1469866755970&skey=%40crypt_319dbe2b_4cb380ebd18a2bedec4d28f7b5f00b5d&sid=u4%2BialGnZh7vYKbU&uin=1137975161&deviceid=e478565114849544&synckey=1_652566122%7C2_652566184%7C3_652566107%7C11_652565551%7C13_652560047%7C201_1469865939%7C1000_1469856425%7C1001_1469851411&_=1469865972055')
        except:
            pass
    def GetAllFriends(self):
        if True == self.IsLogin:
            try:
                r = self.Session.get('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&pass_ticket=%s&r=%s&seq=0&skey=%s' % (self.Info_Base['pass_ticket'],int(time.time()),self.BaseRequest['Skey']))
                r.encoding = 'utf-8'
                print r.text
            except Exception as e:
                print e.message, traceback.format_exc()






