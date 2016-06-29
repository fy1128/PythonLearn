
import requests
import sys
from bs4 import BeautifulSoup
import time

class Text:
	def __init__(self):
		pass
	def GetWebPage(self,Url):
		soup = None
		try:
			headers = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'}
			req = requests.get(url=Url, headers=headers, timeout=10)
			req.raise_for_status()
			req.encoding = 'gb2312'
			#print req.text
			soup = BeautifulSoup(req.text, 'lxml')
		except requests.HTTPError, e:
			print e
		except requests.Timeout, e:
			print e
		except:
			print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
		finally:
			return soup

	def GetProxyIP_proxylist(self):
		UrlAndTitle = []
		for page in range(1,6):
			Url = 'http://www.hksiqile.com/news.asp?mudi=&page=' + str(page)
			soup = self.GetWebPage(Url)
			if None != soup:
				tbs = soup.findAll('table',width="692" ,border="0", cellspacing="0", cellpadding="0" ,style=" background:url(images/x_17.jpg) bottom no-repeat;")
				for tb in tbs:
					tds = tb.findAll('td')
					td = tds[1]
					UrlAndTitle.append(((td.a)['href'],td.text.strip()))
		for urlandtitle in UrlAndTitle:
			url,title = urlandtitle
			soup = self.GetWebPage('http://www.hksiqile.com/' + url)
			if None != soup:
				print '********************************************\r\nTitle',title
				trs = soup.find('table', border="0", cellspacing="0", cellpadding="0",
				                style="margin-top:10px; ").findAll('tr')
				print trs[1].text.strip()
			time.sleep(1)
		return

	def test(self):
		soup = self.GetWebPage('http://www.hksiqile.com/news.asp?mudi=listShow&typeStr=product&type1ID=0&type2ID=0&dataID=667&type1CN=3%2E8%B9%D8%B0%AE%C5%AE%D0%D4%BD%A1%BF%B5%CF%B5%C1%D0%BD%B2%D7%F9%D4%B2%C2%FA%C2%E4%C4%BB')
		if None != soup:
			tbs = soup.find('table',border="0",cellspacing="0",cellpadding="0",style="margin-top:10px; ").findAll('tr')
			print tbs[1].text.strip()

if '__main__' == __name__:
    t = Text()
    t.GetProxyIP_proxylist()
    #t.test()