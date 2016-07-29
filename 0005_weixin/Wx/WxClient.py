import requests



class WxClient():
    def __init__(self):
        self.Session = requests.Session()

    def WebLog(self):
        self.Session.get()
