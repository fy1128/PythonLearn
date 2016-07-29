#coding:utf8

#15319660275

import requests
from bs4 import BeautifulSoup

class Maya:
	def __init__(self):
		#we login and get cookies
		print 'Try to Login'
		self.BaseWebAddress = 'http://www.mayaonl.com/index.php'
		E = None
		try:
			headers = {
				'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'
			}
			PostData = {
				'referer' : 'http://www.mayaonl.com/index.php',
				'formhash' : '0ca30c27',
				'answer' : '',
				'cookietime' : '315360000',
				'loginfield ' : 'username',
				'loginmode' : '',
				'loginsubmit' : u'提交'.encode('gbk'),
				'questionid' : '0',
				'styleid' : '',
				'username' : u'白菜爱吃白菜'.encode('gbk'),
				'password' : '881211',
			}
			req = requests.post('http://www.mayaonl.com/logging.php?action=login',headers = headers,data = PostData)
			req.raise_for_status()
			self.WebCookies = req.cookies
		except requests.HTTPError,e:
			E = e
		except requests.Timeout,e:
			E = e
		except BaseException,e:
			E = e
		finally:
			if None != E:
				print 'Login Failure',E
				exit -1
		return

	def GetWebPage(self,Url):
		E = None
		Soup = None
		try:
			headers = {
				'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'
			}
			req = requests.get(Url,headers = headers,cookies = self.WebCookies)
			req.raise_for_status()
			req.encoding = 'gbk'
			#print req.text
			Soup = BeautifulSoup(req.text,'lxml')
		except requests.HTTPError,e:
			E = e
		except requests.Timeout,e:
			E = e
		except BaseException,e:
			E = e
		finally:
			return Soup
	def DownloadPic(self,url,name):
		E = None
		try:
			headers = {
				'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'
			}
			req = requests.get(url,headers = headers,stream = True)
			req.raise_for_status()
			print 'Download Picture',name
			with open(name,'wb') as imgsave:
				for chunk in req.iter_content():
					if chunk:
						imgsave.write(chunk)
						imgsave.flush()
				imgsave.close()
		except requests.HTTPError,e:
			E = e
		except requests.Timeout,e:
			E = e
		except BaseException,e:
			E = e
		finally:
			if None != E:
				print 'DownloadPic Failure',E
				
	def GetContent(self,url,name):
		soup = self.GetWebPage(url)
		cnt = 0
		if None != soup:
			tds = soup.find('form').find('div',class_='t_msgfont').findAll('img')
			for td in tds:				
				subfix = td['src'].split('.') 
				self.DownloadPic(td['src'],name + '__' + str(cnt) + '.' + subfix[-1])
				cnt += 1
				
	def GetTuBaTianXia(self):
		for Page in range(1,564):
			print 'Get Web Page',Page
			url = 'http://www.mayaonl.com/forumdisplay.php?fid=5&page=' + str(Page)
			soup = self.GetWebPage(url)
			if None != soup:
				tds = soup.find('form').findAll('td',class_ = 'f_title')
				for td in tds:
					if None != td.a:
						print 'Get',td.a.string
						self.GetContent('http://www.mayaonl.com/' + td.a['href'],td.a.string)
			else:
				print 'Exit GetTuBaTianXia'
				
			

if '__main__' == __name__:
	maya = Maya()
	#maya.GetWebPage('http://www.mayaonl.com/index.php')
	maya.GetTuBaTianXia()
