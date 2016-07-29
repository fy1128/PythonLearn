import requests


req = requests.get('http://wx.qq.com')
print req.text