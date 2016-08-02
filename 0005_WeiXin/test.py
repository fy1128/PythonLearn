#import Wx
from Wx import *

class MyWx (Wx):

    def ProcessMessage(self,Message):
        print 'From',Message['From'],'->','To',Message['To']
        print '    Msg',Message['Msg']

if __name__ == '__main__':
    wx = MyWx()
    wx.Run()


