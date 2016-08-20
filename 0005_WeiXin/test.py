#coding:utf-8
import Wx
#from Wx import *

class MyWx (Wx.Wx):

    def ProcessMessage(self,Message):
        print Message
        if Message['IsFromGroup']:
            print 'From',Message['SubFrom'],'@',Message['From'],'To',Message['To']
        else:
            print 'From', Message['From'], 'To', Message['To']
        if 'Text' == Message['MsgType']:
            print '    Msg',Message['Msg']
            if Message['Msg'] == u'发送图片':
                pass
                #self.SendFile(u'詹丽金','LoginInfo.json',IsPic=True)
                ##self.SendFile(u'詹丽金','LoginInfo.json',IsPic=False)
                ##self.SendFile(u'詹丽金','1.jpeg',IsPic=False)
                ##self.SendFile(u'詹丽金','1.jpeg',IsPic=True)
        elif 'Picture' == Message['MsgType']:
            Wx.Wx.GetPicture(self,Message['MsgUrl'],'1.jpeg')
        elif 'Video' == Message['MsgType']:
            Wx.Wx.GetVideo(self,Message['MsgUrl'],'1.mp4')
        elif 'Voice' == Message['MsgType']:
            Wx.Wx.GetVoice(self,Message['MsgUrl'],'1.mp3')
        else:
            pass

if __name__ == '__main__':
    wx = MyWx()
    wx.Run()


