import WxClient

class Wx():
    def __init__(self):
        self.WxClient = WxClient.WxClient()
        if True == self.WxClient.WxLogin():
            self.WxClient.GetAllFriends()
            self.WxClient.Run()
    def WxRecvMsg(self):
        pass

