from WxClient import *

class Wx (WxClient):

    def __init__(self):
        WxClient.__init__(self)
        if True == WxClient.WxLogin(self):
            WxClient.GetAllFriends(self)

    def ProcessMessage(self,Message):
        print Message
