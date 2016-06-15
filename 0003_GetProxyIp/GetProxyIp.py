#!/usr/bin/env python

import urllib2
from bs4 import BeautifulSoup
import MySQLdb
import random

class GetProxyIP:
	def __init__(self):
		try:
			self.dbconnect = MySQLdb.connect(user = 'baicai',passwd = 'baicai',db = 'proxyip')
			self.dbcursor = self.dbconnect.cursor()

			#connect success,we check if it first run
			if 0 == self.dbcursor.execute('show tables like "IP"'):
				print 'This is First time run,we will creat sql table etc.'
				self.dbcursor.execute('create table if not exists IP '
									  '(IP varchar(16) NOT NULL primary key,'
									  'Port int NOT NULL,'
									  'Type TINYINT NOT NULL,'
									  'Quality TINYINT)')
				self.dbcursor.execute('create table if not exists UnuseIP '
				                      '(IP varchar(16) NOT NULL primary key,'
				                      'Port int NOT NULL,'
				                      'Type TINYINT NOT NULL,'
				                      'CheckTimes TINYINT NOT NULL)')
				self.dbcursor.execute('create table if not exists LastCaptureTime ('
				                      'Domain varchar(32) NOT NULL primary key,'
				                      'LastTime varchar(32))')
				self.dbconnect.commit()
				self.FirstRun = 1
			else:
				self.FirstRun = 0
				try:
					self.dbcursor.execute('select * from IP limit 0,100')
					self.ProxyIPPool = self.dbcursor.fetchall()
					self.dbcursor.execute('delete from LastCaptureTime where Domain="www.xicidaili.com"')
					self.dbconnect.commit()
				except MySQLdb.Error as e:
					print e
		except MySQLdb.Error,e:
			print e
			exit(-1)
		self.UseProxyIP = 0

	def Close(self):
		self.dbcursor.close()
		self.dbconnect.close()

	def CheckIPFormat(self,ip):
		iptab = ip.split('.')
		if 4 != len(iptab):
			return -1
		for i in range(0,4):
			try:
				addr = int(iptab[i])
				if(addr < 0) or (addr > 255):
					return -1
			except:
				return -1
		return 0

	def InsertIP(self,ip,port,type):
		proxytype = 0
		if 'HTTP' == type.upper():
			proxytype = 0
		elif 'HTTPS' == type.upper():
			proxytype = 1
		elif 'SOCKS4/5' == type.upper():
			proxytype = 2
		else:
			print('invalid proxy type',type)
			return

		if 0 != self.CheckIPFormat(ip):
			print 'Invalid IP address',ip
			return

		try:
			self.dbcursor.execute('insert into IP (IP,Port,Type) values (%s,%s,%s)',
								  (ip,port,proxytype))

			self.dbconnect.commit()
		except MySQLdb.Error,e:
			print e

	def RemoveUnuseProxyIP(self,ip,port,type):
		#some ProxyIP is unuse,we remove it to other table
		self.dbcursor.execute('delete from IP where ip=%s',ip)
		self.dbcursor.execute('insert into UnuseIP (IP,Port,Type,CheckTimes) values (%s,%s,%s,%s)',
		                      (ip,port,type,10))
		self.dbconnect.commit()
	def ChangeProxyIP(self):
		if len(self.ProxyIPPool) < 1:
			self.UseProxyIP = 0
			try:
				self.dbcursor.execute('select * from IP limit 0,100')
				self.ProxyIPPool = self.dbcursor.fetchall()
			except MySQLdb.Error as e:
				print e
			return
		self.ProxyIPPos = random.randint(0,len(self.ProxyIPPool) - 1)
		self.UseProxyIP = 1


	def GetProxyIP_xicidaili(self,page):

		#get proxy ip from xicidaili
		def xicidaili_CaptureIp(page):
			if self.UseProxyIP:
				randip = self.ProxyIPPool[self.ProxyIPPos]
				# req.set_proxy(randip[0] + ':' + str(randip[1]),'http')
				proxy_set = {'http': randip[0] + ':' + str(randip[1])}
				proxy_support = urllib2.ProxyHandler(proxy_set)
				opener = urllib2.build_opener(proxy_support)
				urllib2.install_opener(opener)
			else:
				self.ChangeProxyIP()

			if 1 == page:
				req = urllib2.Request('http://www.xicidaili.com/nn')
			else:
				req = urllib2.Request('http://www.xicidaili.com/nn/' + str(page))

			req.add_header('User-Agent',
			               'Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0')
			try:
				rsp = urllib2.urlopen(req, timeout=5)
			except urllib2.URLError, e:
				#this Proxy IP is unuseable,change it
				randip = self.ProxyIPPool[self.ProxyIPPos]
				self.RemoveUnuseProxyIP(randip[0],randip[1],randip[2])
				self.ChangeProxyIP()
				print 'ProxyIP unuse',randip[0],randip[1]
				return -1

			try:
				soup = BeautifulSoup(rsp, 'html5lib')
				trs = soup.find('table', {'id': 'ip_list'}).findAll('tr')
				for tr in trs[1:]:
					tds = tr.findAll('td')
					self.InsertIP(tds[1].text.strip(), int(tds[2].text.strip()), tds[5].text.strip())
			except Exception as e:
				print e
			return 0

		#check if we was first capture
		try :
			if 0 == self.dbcursor.execute('select * from LastCaptureTime where '
			                              'Domain="www.xicidaili.com"'):
				#yes,it first run
				#get total page
				req = urllib2.Request('http://www.xicidaili.com/nn')
				req.add_header('User-Agent',
		               'Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0')
				try:
					soup = BeautifulSoup(urllib2.urlopen(req,timeout=5),'html5lib')
					trs = soup.find('div', {'class': 'pagination'}).findAll('a')
					if len(trs) < 3:
						return
					TotalPage = trs[-2].text.strip()
				except:
					return -1

				self.dbcursor.execute('insert into LastCaptureTime (Domain) values '
				                      '("www.xicidaili.com")')
				self.dbconnect.commit()
				print 'First time to capture www.xicidaili.com ,tatal page :',TotalPage
				page = 1
				while page <= TotalPage:
					#WARNING!!! IT WILL TASK A LONG LONG TIME
					if 0 == xicidaili_CaptureIp(page):
						print 'xicidaili GetPage',page,'Success'
						page += 1
					else:
						print 'xicidaili GetPage', page, 'Failure'
				print 'OK,first time run over'
				return

		except :
			return -1






if '__main__' == __name__:
	getproxyop = GetProxyIP()
	#getproxyop.ChangeProxyIP()
	getproxyop.GetProxyIP_xicidaili(1)
	#getproxyop.Close()