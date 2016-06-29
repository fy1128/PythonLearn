#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import MySQLdb
import random
import sys


class GetProxyIP:
	def __init__(self):
		try:
			self.dbconnect = MySQLdb.connect(user='baicai', passwd='baicai', db='proxyip')
			self.dbcursor = self.dbconnect.cursor()

			# connect success,we check if it first run
			if 0 == self.dbcursor.execute('show tables like "IPPort"'):
				print 'This is First time run,we will creat sql table etc.'
				self.dbcursor.execute('create table if not exists IPPort '
				                      '(IPPort varchar(22) NOT NULL primary key,'
				                      'Type TINYINT NOT NULL,'
				                      'Quality TINYINT)')
				self.dbcursor.execute('create table if not exists UnuseIP '
				                      '(IPPort varchar(22) NOT NULL primary key,'
				                      'Type TINYINT NOT NULL,'
				                      'CheckTimes TINYINT NOT NULL)')
				self.dbcursor.execute('create table if not exists LastCaptureTime ('
				                      'Domain varchar(128) NOT NULL primary key,'
				                      'LastTime varchar(32))')
				self.dbconnect.commit()
				self.FirstRun = 1
			else:
				self.FirstRun = 0
				try:
					self.dbcursor.execute('select * from IPPort limit 0,10')
					self.ProxyIPPool = list(self.dbcursor.fetchall())
					self.ProxyIPPos = 0
				except MySQLdb.Error,e:
					print e
				except:
					print 'Expection @ ',sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno
		except MySQLdb.Error, e:
			print e
			exit(-1)
		except:
			print 'Expection @ ',sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno
		self.UseProxyIP = 0

	def Close(self):
		self.dbcursor.close()
		self.dbconnect.close()

	def CheckIPFormat(self, ip):
		iptab = ip.split('.')
		if 4 != len(iptab):
			return -1
		for i in range(0, 4):
			try:
				addr = int(iptab[i])
				if (addr < 0) or (addr > 255):
					return -1
			except:
				print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
				return -1
		return 0

	def InsertIP(self, ip, port, type):
		proxytype = 0
		if 'HTTP' == type.upper():
			proxytype = 0
		elif 'HTTPS' == type.upper():
			proxytype = 1
		elif 'SOCKS4/5' == type.upper():
			proxytype = 2
		else:
			print('invalid proxy type', type)
			return

		if 0 != self.CheckIPFormat(ip):
			print 'Invalid IP address', ip
			return

		try:
			ip += ':'+str(port)
			self.dbcursor.execute('insert into IPPort (IPPort,Type) values (%s,%s)',
			                      (ip, proxytype))

			self.dbconnect.commit()
		except MySQLdb.Error, e:
			print e
		except:
			print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno

	def RemoveUnuseProxyIP(self, ipport, type):
		# some ProxyIP is unuse,we remove it to other table
		try:
			self.dbcursor.execute('delete from IPPort where IPPort=%s', (ipport,))
			self.dbcursor.execute('insert into UnuseIP (IPPort,Type,CheckTimes) values (%s,%s,%s)',
			                      (ipport, type, 10))
		except MySQLdb.Error,e:
			print sys._getframe().f_code.co_name,e
		except:
			print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
		finally:
			self.dbconnect.commit()

	def ChangeProxyIP(self):
		#print 'ProxyIPPool number',str(len(self.ProxyIPPool))
		if len(self.ProxyIPPool) < 1:
			#print 'ProxyIPPool empty'
			try:
				self.dbcursor.execute('select * from IPPort limit 0,10')
				self.ProxyIPPool = list(self.dbcursor.fetchall())
			except MySQLdb.Error,e:
				print e
				self.UseProxyIP = 0
				return
			except:
				print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
		if len(self.ProxyIPPool) >= 1:
			self.ProxyIPPos = random.randint(0, len(self.ProxyIPPool) - 1)
			#print 'Use new pos',self.ProxyIPPos
			self.UseProxyIP = 1
		else:
			self.UseProxyIP = 0

	def CaptureWebPage(self,Url,ProxyEnable = 1):
		soup = None
		WebErr = 0
		try:
			headers = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'
			}
			proxy_set = None
			if ProxyEnable:
				if self.UseProxyIP:
					proxy_set = {'http': 'http://' + self.ProxyIPPool[self.ProxyIPPos][0]}
				else:
					print 'Warning!!!,not use proxy ip'
					self.ChangeProxyIP()
			req = requests.get(Url, timeout=5, headers=headers, proxies=proxy_set)
			req.raise_for_status()
			soup = BeautifulSoup(req.text, 'lxml')
		except requests.HTTPError,e:
			print e
			WebErr = 1
		except requests.Timeout,e:
			print e
		except BaseException,e:
			print e
		except:
			print 'Unknow Expect @',sys._getframe().f_code.co_name, sys._getframe().f_lineno
		finally:
			if None == soup:
				if ProxyEnable:
					if self.UseProxyIP:
						randip = self.ProxyIPPool[self.ProxyIPPos]
						# print 'ProxyIP unuse', randip[0], randip[1]
						self.RemoveUnuseProxyIP(randip[0], randip[1])
						del self.ProxyIPPool[self.ProxyIPPos]
					self.ChangeProxyIP()
			return WebErr,soup

	def TimeToINT(self,time):
		# time format is YY-MM-DD HH-MM
		try:
			T = time.split(' ')
			if 2 != len(T):
				return None
			d = T[0].split('-')
			m = T[1].split(':')
			if (3 != len(d)) or (len(m) < 2):
				return None
			return (int)(d[0]) << 20 | (int)(d[1]) << 16 | (int)(d[2]) << 11 | (int)(m[0]) << 6 | (int)(m[1])
		except:
			print 'Unknow Time', time
			return None

	def PareWebPageFunc_xicidaili(self,soup,lt):
		NewLastTime = None
		try:
			trs = soup.find('table', {'id': 'ip_list'}).findAll('tr')
			for tr in trs[1:]:
				tds = tr.findAll('td')
				if None == NewLastTime:
					NewLastTime = tds[9].text.strip()
				nlt = self.TimeToINT(tds[9].text.strip())
				if None == nlt or lt <= nlt:
					self.InsertIP(tds[1].text.strip(), int(tds[2].text.strip()), tds[5].text.strip())
				else:
					return 1,NewLastTime
		except:
			print 'Page Web Page failure'
			return -1,NewLastTime
		return 0,NewLastTime

	def PareWebPageFunc_kuaidaili(self,soup,lt):
		NewLastTime = None
		try:
			trs = soup.find('tbody').findAll('tr')
			for tr in trs:
				tds = tr.findAll('td')
				if None == NewLastTime:
					NewLastTime = tds[6].text.strip()
				nlt = self.TimeToINT(tds[6].text.strip())
				if None == nlt or lt <= nlt:
					self.InsertIP(tds[0].text.strip(), int(tds[1].text.strip()), tds[3].text.strip())
				else:
					return 1,NewLastTime
		except:
			print 'Pare Web Page failure'
			return -1,NewLastTime
		return 0,NewLastTime

	def PareWebPageFunc_proxylist(self,soup,lt):
		def proxylist_ParseFunctionZ2Str(text):
			zs = text.split(';')
			str = ''
			try:
				for z in zs:
					s = z[2:-1]
					if 0 == len(s):
						continue
					na = s.split('-')
					n = (int)(na[0]) - (int)(na[1])
					str += chr(n)
			except BaseException, e:
				print e, 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
				str = None
			finally:
				return str

		try:
			trs = soup.find('table', border='1', cellspacing='0', cellpadding='0').findAll('tr')
			for tr in trs[1:]:
				tds = tr.findAll('td')
				ip = proxylist_ParseFunctionZ2Str(tds[1].text.strip())
				port = proxylist_ParseFunctionZ2Str(tds[2].text.strip())
				type = 'HTTP' if 'N' == tds[4].text.strip() else 'HTTPS'
				self.InsertIP(ip,port,type)
				return 1,None
		except:
			print 'Page Web Page failure'
			return -1,None
		return 0,None

	def GetTotalPageLastTime_xicidaili(self,url):
		weberr,soup = self.CaptureWebPage(url,ProxyEnable = 0)
		if None == soup:
			return None,None
		TotalPage = None
		LastTime = None
		try:
			trs = soup.find('div', {'class': 'pagination'}).findAll('a')
			if len(trs) < 3:
				return -1
			TotalPage = (int)(trs[-2].text.strip())
			trs = soup.find('table', {'id': 'ip_list'}).findAll('tr')
			tr = trs[1]
			tds = tr.findAll('td')
			LastTime = tds[9].text.strip()
		except:
			print 'Get TotalPage and LastTime Failure'
		finally:
			return TotalPage,LastTime

	def GetTotalPageLastTime_kuaidaili(self,url):
		weberr,soup = self.CaptureWebPage(url, ProxyEnable=0)
		if None == soup:
			return None, None
		TotalPage = None
		LastTime = None
		try:
			trs = soup.find('div', {'id': 'listnav'}).findAll('a')
			if len(trs) < 3:
				return -1
			TotalPage = (int)(trs[-1].text.strip())
			trs = soup.find('tbody').findAll('tr')
			tds = trs[0].findAll('td')
			LastTime = tds[6].text.strip()
		except:
			print 'Get TotalPage and LastTime Failure'
		finally:
			return TotalPage,LastTime

	def GetTotalPageLastTime_proxylist(self, url):
		weberr,soup = self.CaptureWebPage(url, ProxyEnable=0)
		if None == soup:
			return None, None
		TotalPage = None
		LastTime = '0000-00-00 00:01'
		try:
			trs = soup.find('table', border='0', cellspacing='0', cellpadding='0').findAll('tr')
		except:
			print 'Get TotalPage and LastTime Failure'
		finally:
			return TotalPage, LastTime

	def GetUrlWithPageFuncDict_proxylist(self,url,page):
		if 1 == page:
			return url
		else:
			return url + '/free-fresh-proxy-list-' + str(page - 1) + '.html'

	def GetUrlWithPageFuncDict_kuaidaili(self, url, page):
		if 1 == page:
			return url
		else:
			return url + str(page - 1) + '/'

	def GetUrlWithPageFuncDict_default(self, url, page):
		return url + '/' + str(page)

	PareWebPageFuncDict = {
		'xicidaili': PareWebPageFunc_xicidaili,
		'kuaidaili': PareWebPageFunc_kuaidaili,
		'proxylist': PareWebPageFunc_proxylist
	}

	GetTotalPageLastTimeFuncDict = {
		'xicidaili': GetTotalPageLastTime_xicidaili,
		'kuaidaili': GetTotalPageLastTime_kuaidaili,
		'proxylist': GetTotalPageLastTime_proxylist
	}

	GetUrlWithPageFuncDict = {
		'xicidaili': GetUrlWithPageFuncDict_default,
		'kuaidaili': GetUrlWithPageFuncDict_kuaidaili,
		'proxylist': GetUrlWithPageFuncDict_proxylist,
	}

	WebUrlDict = {
		#'xicidaili': ('http://www.xicidaili.com/nn','http://www.xicidaili.com/nt','http://www.xicidaili.com/wn','http://www.xicidaili.com/wt'),
		'kuaidaili': ('http://www.kuaidaili.com/free/inha/','http://www.kuaidaili.com/free/intr/','http://www.kuaidaili.com/free/outha/','http://www.kuaidaili.com/free/outtr/'),
		'proxylist': ('http://www.proxylist.ro',)
	}

	def CaptureMainLoop(self):
		def CaptureWithLoop(web,url,TotalPage,lt):
			ErrorCnt = 0
			WebErrorCnt = 0
			LastTime = self.TimeToINT(lt)
			if None == LastTime:
				return -1,lt
			NewLastTime = None #last time of this loop
			page = 1
			while 0 == TotalPage or page <= TotalPage:
				Url = (self.GetUrlWithPageFuncDict.get(web))(self,url,page)
				weberr,soup = self.CaptureWebPage(Url)
				if weberr:
					WebErrorCnt += 1

				if None != soup:
					WebErrorCnt = 0
					ret,rett = (self.PareWebPageFuncDict.get(web))(self,soup,LastTime)
					if None != rett and None == NewLastTime:
						NewLastTime = rett
					if ret >= 0:
						page += 1
						print 'Get page',Url,'Success,',ret,'Total page',TotalPage
						if 1 == ret:
							return 0,NewLastTime
				else:
					ErrorCnt += 1
				if ErrorCnt > 50 or WebErrorCnt > 5:
					print 'Capture reach MaxTryTimes',ErrorCnt,WebErrorCnt
					return -1,lt
			return 0,NewLastTime


		for web in self.WebUrlDict:
			Url = self.WebUrlDict.get(web)
			for url in Url:
				try:
					if 0 == self.dbcursor.execute('select LastTime from LastCaptureTime where '
					                              'Domain = %s', (url,)):
						TotalPage,LastTime = (self.GetTotalPageLastTimeFuncDict.get(web))(self,url)
						if None != TotalPage and None != LastTime:
							print url,'Total Page',TotalPage
							TotalPage = 3
							ret,lasttime = CaptureWithLoop(web,url,TotalPage,'0000-00-00 00:01')
							if 0 == ret:
								self.dbcursor.execute('insert into LastCaptureTime (Domain,LastTime) values '
								                      '(%s,%s)', (url, LastTime))
								self.dbconnect.commit()
					else:
						lasttime = self.dbcursor.fetchone()
						ret,lasttime = CaptureWithLoop(web,url,10,lasttime[0])
						self.dbcursor.execute('update LastCaptureTime set LastTime=%s where Domain=%s', (lasttime, url))
						self.dbconnect.commit()
				except MySQLdb.Error, e:
					print e
				except BaseException,e:
					print 'Expection:',e,'@ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno


if '__main__' == __name__:
	getproxyop = GetProxyIP()
	getproxyop.ChangeProxyIP()
	getproxyop.CaptureMainLoop()
	getproxyop.Close()
