import requests
import random
import traceback
import base64

class JDLogin() :
    def __init__ (self):
        self.Session = requests.Session()
        self.Session.headers.update({'User-Agent' : 'Android WJLoginSDK 2.2.0'})
        self.Session.proxies = {'http': '127.0.0.1:9690', 'https': '127.0.0.1:9690'}

    def GetRandomByteArray(self,len):
        arr = bytearray(len)
        while len:
            arr[len - 1] = random.randint(0,255)
            len -= 1
        return arr

    def Login (self):
        try:
            data = self.GetRandomByteArray(296)
            i = 0
            while i < 16:
                data[i] = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                i += 1
            Data = 'akQ5a2RNTGJHWEo4RGtqSnVZN3hTAYdkA7on60ZjszPzRWSFlo4uaPB3szsHT8gFHZ5UdAlVVKMgJH0MQtyDdjyJoSgopExBQYi2+2oAVvHoFX8QZbLYFXQvUFK4W3EWhOp/r6t6Xu0zDbq2d2u32WZGCzUlOjjJh0Z7RrXcBkp3lv+K1qdP0ghqYg+U3Wt0WeV1AVqHjKYggGITY9SLC2hgKRyHkHXhJzRf/lmJwadW07NwaItxfSkMppUVHGsvfxj98ctia6cL7RAJx+2RGRzLWZHHE5UlhRG2bYRdJI5rSSVR2z7dSPpqYKbVUOZoLtD1O96VWRucEb/wg/LF4qE1Pw7hrhareQYlJBv5DRbAWGSacKo+BHeg32RaGg1Jlfmhu7TY9Sk='
            #Data = base64.b64encode(data)
            r = self.Session.post('http://wlogin.m.jd.com/applogin_v2',data = Data)
            print r.text
            Data = 'AOUAAAAAAAAAAQAAAAEAAAABAAAAAAACAAYAZAERAAAEADQwMDBhMDAwMTAwMDAwNTAxMDAyMEM1NkEwRTYyN0M1NUJGMDAyOEU3NzQ2NkUyRTFFNTEwAAgAYwACAGQAB2FuZHJvaWQAAzUuMQAFNS4yLjAACTE5MjAqMTA4MAAFamRhcHAABHdpZmkABzAuMF8wLjAAHDg2ODM0OTAyMzg5OTQwNi02ODNlMzQzNzk4ZDgAAAABAAUyLjIuMAAQAAtiYWljYWktMjAxNQATAAUAABlnAAAYAAsxMzMzODI4OTc0NQ=='
            r = self.Session.post('http://wlmonitor.m.jd.com/login_report',data = Data,verify = False)
            print r.text
            r =
        except Exception as e:
            print e.message, traceback.format_exc()


if __name__ == '__main__':
    jd = JDLogin()
    jd.Login()
    r = '''
    00 e5 00 00 00 00 00 00 00 01 00 00 00 01 00 00
    00 03 00 00 00 00 00 02 00 06 00 64 01 11 00 00
    04 00 34 30 30 30 61 30 30 30 31 30 30 30 30 30
    35 30 31 30 30 32 30 43 35 36 41 30 45 36 32 37
    43 35 35 42 46 30 30 32 38 45 37 37 34 36 36 45
    32 45 31 45 35 31 30
    00 08 00 63
        00 02 00 64 00
            07 61 6e 64 72 6f 69 64 00 03 35 2e 31 00 05 35
            2e 32 2e 30 00 09 31 39 32 30 2a 31 30 38 30 00
            05 6a 64 61 70 70 00 04 77 69 66 69 00 07 30 2e
            30 5f 30 2e 30 00 1c 38 36 38 33 34 39 30 32 33
            38 39 39 34 30 36 2d 36 38 33 65 33 34 33 37 39
            38 64 38 00 00
        00 01 00 05 32 2e 32 2e 30
    00 10 00 0b 62 61 69 63 61 69 2d 32 30 31 35
    00 13 00 05 00 00 02 69 00
    00 18 00 0b 31 33 33 33 38 32 38 39 37 34 35
    '''

