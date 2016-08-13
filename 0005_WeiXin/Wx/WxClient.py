#coding:utf-8

import requests
import time
import random
import re
import pyqrcode
import Image
import xml.dom.minidom
import json
import traceback
import os
import mimetypes


class WxClient():
    def __init__(self):
        self.Session = requests.Session()
        self.Session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5'})
        #self.Session.proxies = {'http': '127.0.0.1:8888', 'https': '127.0.0.1:8888'}
        self.BaseRequest = {
                'DeviceID' : 'e' + repr(random.random())[2:17],
            }
        self.Info_Base = {}
        self.Info_SyncKey = {}
        self.Info_SyncKeyStr = None
        self.Info_User = {}
        self.IsLogin = False
        self.UploadFileIndex = 0

    def SaveLoginInfo(self):
        return False
        try:
            info = {
                'BaseRequest' : self.BaseRequest,
                'Info_Base' : self.Info_Base,
                'Info_SyncKey' : self.Info_SyncKey,
                'Info_SyncKeyStr' : self.Info_SyncKeyStr,
                'Info_User' : self.Info_User,
                'Cookies' : requests.utils.dict_from_cookiejar(self.Session.cookies)
                }
            with open('LoginInfo.json','wb') as f:
                f.write(json.dumps(info))
                f.close
        except Exception as e:
            print e.message, traceback.format_exc('DeviceID')

    def LoadLoginInfo(self):
        return False
        try:
            with open('LoginInfo.json','r') as f:
                info = json.loads(f.read())
                self.BaseRequest = info['BaseRequest']
                self.Info_Base = info['Info_Base']
                self.Info_SyncKey = info['Info_SyncKey']
                self.Info_SyncKeyStr = info['Info_SyncKeyStr']
                self.Info_User = info['Info_User']
                self.Session.cookies = requests.utils.cookiejar_from_dict(info['Cookies'])
                f.close()
                return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False


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
                r = self.Session.get('https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=0&'
                                     'uuid=%s&_=%s' % (self.Info_Base['UUID'], int(time.time())))
                r.encoding = 'utf-8'
                code = re.search(r'window.code=(\d+);', r.content)
                reurl = re.search(r'window.redirect_uri="(\S+)"', r.content)
                redirect_url = None
                if code:
                    if '200' == code.group(1):
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

            #post to get SyncKey and my user info
            PostParams = {
                'BaseRequest' : self.BaseRequest,
                }
            r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?'
                                  'r=%s&lang=zh_CN&pass_ticket=%s' % (int(time.time()),self.Info_Base['pass_ticket'])
                                  ,json.dumps(PostParams))
            r.encoding = 'utf-8'
            infoDict = json.loads(r.text)
            self.Info_User = infoDict['User']
            self.Info_SyncKey = infoDict['SyncKey']
            self.Info_SyncKeyStr = '|'.join(str(KeyVal['Key']) + '_' + str(KeyVal['Val']) for KeyVal in self.Info_SyncKey['List'])

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
            r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&'
                                  'pass_ticket=%s' % self.Info_Base['pass_ticket'],data = json.dumps(PostParams))
            r.encoding = 'utf-8'
            retjson = json.loads(r.text)
            if 0 == retjson['BaseResponse']['Ret']:
                return True
            else:
                print 'Make sure failure',retjson['BaseResponse']['Ret']
                return False

        if True == self.LoadLoginInfo():
            Exit,MsgDic = self.SyncCheck()
            if 0 == Exit:
                print 'User Last LoginInfo'
                return True
            else:
                print Exit,MsgDic

        self.BaseRequest['DeviceID'] = 'e' + repr(random.random())[2:17]
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
            try:
                Image.open("QR.jpeg").show()
            except:
                print 'Cant show QR.jpeg by image'
            print 'Save QR to QR.jpeg,please scan it by phone...'

            #qr = pyqrcode.create('https://login.weixin.qq.com/qrcode/' + self.Info_Base['UUID'])
            #print qr.terminal(quiet_zone=1)

            if True != WaitForLogin(self):
                return False

            print 'Login Success...'
            self.IsLogin = True
            return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def SyncCheck(self):
        '''
            return : Exit , MsgDic
        '''
        def PostSyncCheck(self):
            PostParam = {
                'BaseRequest' : self.BaseRequest,
                'SyncKey' : self.Info_SyncKey,
                'rr' : ~int(time.time())
                }
            r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?'
                                  'sid=%s&skey=%s&lang=zh_CN&pass_ticket=%s' %
                                  (self.BaseRequest['Sid'],self.BaseRequest['Skey'],self.Info_Base['pass_ticket']),
                                  data = json.dumps(PostParam))
            r.encoding = 'utf-8'
            retjson = json.loads(r.text)
            if 0 == retjson['BaseResponse']['Ret']:
                self.Info_SyncKey = retjson['SyncKey']
                self.Info_SyncKeyStr = '|'.join(str(KeyVal['Key']) + '_' + str(KeyVal['Val']) for KeyVal in self.Info_SyncKey['List'])
                #sync key OK,we delete it from ret
                del retjson['SyncKey']
                del retjson['BaseResponse']
                self.SaveLoginInfo()
                return retjson
            else:
                print 'POST SyncCkeck is not zero',retjson['BaseResponse']['Ret']
                return None

        Exit = 1
        MsgDic = None
        try:

            params = {
                'r': int(time.time()),
                'sid': self.BaseRequest['Sid'],
                'uin': self.BaseRequest['Uin'],
                'skey': self.BaseRequest['Skey'],
                'deviceid': self.BaseRequest['DeviceID'],
                'synckey': self.Info_SyncKeyStr,
                '_': int(time.time()),
            }

            r = self.Session.get('https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck',
                                 params = params)
            pm = re.search(r'window.synccheck=\{retcode:"(\d+)",selector:"(\d+)"\}',r.text)
            retcode = pm.group(1)
            selector = pm.group(2)
            if '1100' == retcode:
                print 'login from Wx App,so we logout'
            elif '1101' == retcode:
                print 'xxxxx'
            elif '0' == retcode:
                Exit = 0
                if selector not in ('0','2','6','7'):
                    print 'selector',selector
                if '0' != selector:
                    MsgDic = PostSyncCheck(self)
                if '7' == selector:
                    '''
                        maybe it means:user wan't send a msg by APP and
                        notify to web that change this DestUser to the first
                    '''
                    MsgDic = None
            else:
                print 'Unknow code',retcode,selector
                Exit = 1
        except Exception as e:
            print e.message, traceback.format_exc()
        finally:
            return Exit,MsgDic

    def GetAllFriends(self):
        if True == self.IsLogin:
            try:
                r = self.Session.get('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&'
                                     'pass_ticket=%s&r=%s&seq=0&skey=%s' %
                                     (self.Info_Base['pass_ticket'],int(time.time()),self.BaseRequest['Skey']))
                r.encoding = 'utf-8'
                #print r.text
                with open('contacts.json', 'w') as f:
                    f.write(r.text.encode('utf-8'))
                    f.close()
                retjson = json.loads(r.text)
                print 'Total friends number',retjson['MemberCount']
                self.Friends = retjson['MemberList']
                self.Friends.append(self.Info_User)
            except Exception as e:
                print e.message, traceback.format_exc()

    def UserID2Name(self,UserID):
        for username in self.Friends:
            if UserID == username['UserName']:
                if len(username['RemarkName']):
                    return username['RemarkName']
                else:
                    return username['NickName']
        return u'匿名人士'

    def UserName2ID(self,UserName):
        for userid in self.Friends:
            if UserName == userid['RemarkName'] or UserName == userid['NickName']:
                return userid['UserName']
        return None

    def ProcessMessage(self,msg):
        pass

    def ProcMsg(self,MsgDic):
        '''
            process msg
        '''
        for msg in MsgDic['AddMsgList']:

            From = self.UserID2Name(msg['FromUserName'])
            To = self.UserID2Name(msg['ToUserName'])
            MsgContent = ''
            MsgUrl = ''
            print msg['Content']
            if None == From or None == To:
                continue

            if '@@' == msg['FromUserName'][:2]:
                IsFromGroup = 1
                split = msg['Content'].split(':<br/>')
                if len(split) > 1:
                    MsgContent = msg['Content'][len(SubFrom + ':<br/>'):]
                    SubFrom = self.UserID2Name(split[0])
                    if None == SubFrom:
                        SubFrom = u'匿名人士'
                else:
                    SubFrom = u'匿名人士'
                    MsgContent = msg['Content']
            else:
                IsFromGroup = 0
                SubFrom = ''
                MsgContent = msg['Content']


            if 1 == msg['MsgType']:
                #this is text
                MsgType = 'Text'
            elif 3 == msg['MsgType']:
                #this is picture
                MsgType = 'Picture'
                MsgUrl = msg['NewMsgId']
                MsgContent = ''
            elif 34 == msg['MsgType']:
                #this is voice
                MsgType = 'Voice'
                MsgUrl = msg['NewMsgId']
            elif 51 == msg['MsgType']:
                #server notify msg
                MsgType = 4
                continue
            elif 62 == msg['MsgType']:
                #this is video
                MsgUrl = msg['NewMsgId']
                MsgType = 'Video'
            else:
                MsgType = 'Unknow MsgType' + str(msg['MsgType'])

            Message = {
                'From' : From,
                'To' : To,
                'IsFromGroup' : IsFromGroup,
                'SubFrom' : SubFrom,
                'MsgType' : MsgType,
                'Msg' : MsgContent,
                'MsgUrl' : MsgUrl,
                }
            self.ProcessMessage(Message)

    def SendMsg(self,username,Content):
        From = self.Info_User['UserName']
        To = self.UserName2ID(username)
        if None == From or None == To:
            print 'Not found',username
            return False
        try:
            TimeTick = int(time.time())
            PostData = {
                'BaseRequest' : self.BaseRequest,
                'Msg' :{
                    'ClientMsgId' : TimeTick,
                    'Content' : Content,
                    'FromUserName':From,
                    'LocalID' : TimeTick,
                    'ToUserName' : To,
                    'Type' : 1
                    },
                #'Scene' : 0,
                }
            r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&'
                                  'pass_ticket=%s' % (self.Info_Base['pass_ticket']),
                                  data = json.dumps(PostData,ensure_ascii=False).encode('utf8'),
                                  headers = {'content-type': 'application/json; charset=UTF-8'})
            r.encoding = 'utf-8'

            retjson = json.loads(r.text)
            if 0 != retjson['BaseResponse']['Ret']:
                print 'Send Msg Failure',retjson['BaseResponse']['Ret']
                return False
            return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def GetPicture(self,Url,SaveName):
        try:
            Params = {
                'MsgID' : Url,
                'skey' : self.BaseRequest['Skey'],
            }
            r = self.Session.get('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetmsgimg',
                                 params = Params,stream = True)
            print r.url
            with open(SaveName,'wb') as f:
                f.write(r.content)
                f.close()
            return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def SendPicture(self,ToUserName,File,IsPic = False):
        if not os.path.exists(File):
            print 'File',File,'Not exist'
            return False

        fileName = os.path.basename(File)
        fileLength = os.path.getsize(File)
        fileType = mimetypes.guess_type(File)[0] or 'application/octet-stream'
        try:
            Headers = {
                'Host' : 'file.wx.qq.com',
                'Referer' : 'https://wx.qq.com',
                'User-Agent': 'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5'
            }

            Files = {
                'id' : (None,'WU_FILE_' + str(self.UploadFileIndex)),
                'name' : (None,fileName),
                'type' : (None,fileType),
                'lastModifiedDate' : (None,time.strftime('%w %m %d %Y %H:%M:%S GMT+0800')),
                'size' : (None,str(fileLength)),
                'mediatype' : (None,'pic' if IsPic else 'doc'),
                'uploadmediarequest' : (None,json.dumps({
                    'UploadType' : 2,
                    'BaseRequest' : self.BaseRequest,
                    'ClientMediaId' : int(time.time()),
                    'TotalLen' : fileLength,
                    'StartPos' : 0,
                    'DataLen' : fileLength,
                    'MediaType' : 4,
                    'FromUserName' : self.Info_User['UserName'],
                    'ToUserName' : self.UserName2ID(ToUserName),
                    'FileMd5' : 1,
                })),
                'webwx_data_ticket' : (None,self.Session.cookies['webwx_data_ticket']),
                'pass_ticket' : (None,self.Info_Base['pass_ticket']),
                'filename' : (fileName,open(File,'rb'),fileType)
            }
            self.UploadFileIndex += 1
            r = self.Session.post('https://file.wx.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json',
                                  headers = Headers,files = Files)
            retjson = json.loads(r.text)
            if 0 == retjson['BaseResponse']['Ret']:
                Data = {
                    'BaseRequest' : self.BaseRequest,
                    'Msg' : {
                        'Type' : 3,
                        'MediaId' : retjson['MediaId'],
                        'ClientMsgId' : int(time.time()),
                        'LocalID' : int(time.time()),
                        'FromUserName' : self.Info_User['UserName'],
                        'ToUserName' : self.UserName2ID(ToUserName),
                    },
                    'Scene' : 0,
                }
                r = self.Session.post('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsgimg?fun=async&f=json&'
                                      'pass_ticket=%s' % (self.Info_Base['pass_ticket']),
                                      data = json.dumps(Data))
                retjson = json.loads(r.text)
                if 0 == retjson['BaseResponse']['Ret']:
                    print 'Upload',File,'Success'
                    return True
                else:
                    print 'Upload Check',File,'Failure',retjson['BaseResponse']['Ret']
                    return False
            else:
                print 'Upload',File,'Failure',retjson['BaseResponse']['Ret']
                return False
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def GetVoice(self,Url,SaveName):
        try:
            #Params = {
            #    'msgid' : Url,
            #    'skey' : self.BaseRequest['Skey'],
            #}
            r = self.Session.get('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetvoice?msgid=%s&skey=%s'
                                 % (Url,self.BaseRequest['Skey']),stream = True)
            print r.url
            with open(SaveName,'wb') as f:
                f.write(r.content)
                f.close()
            return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def GetVideo(self,Url,SaveName):
        try:
            Params = {
                'msgid' : Url,
                'skey' : self.BaseRequest['Skey'],
            }
            r = self.Session.get('https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetvideo',
                                 params=Params,stream = True)
            print r.url
            with open(SaveName,'wb') as f:
                f.write(r.content)
                f.close()
            return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False

    def Run(self):
        while True:
            Exit,MsgDic = self.SyncCheck()
            if Exit:
                return False
            if None != MsgDic:
                self.ProcMsg(MsgDic)
            time.sleep(1)






