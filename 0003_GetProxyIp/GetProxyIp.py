#!/usr/bin/env python

import urllib2
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
				                      'Domain varchar(32) NOT NULL primary key,'
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

	def GetProxyIP_xicidaili(self):
		def xicidaili_TimeToINT(time):
			#time format is YY-MM-DD HH-MM
			try:
				T = time.split(' ')
				if 2 != len(T):
					return 0
				d = T[0].split('-')
				m = T[1].split(':')
				if (3 != len(d)) or (2 != len(m)):
					return 0
				return (int)(d[0]) << 20 | (int)(d[1]) << 16 | (int)(d[2]) << 11 | (int)(m[0]) << 6 | (int)(m[1])
			except:
				print 'Unknow Time',time
				return 0

		# get proxy ip from xicidaili
		def xicidaili_CaptureIp(requrl,lasttime):
			LastTime = xicidaili_TimeToINT(lasttime)
			if 0 == LastTime:
				return -1
			NewLastTime = None

			req = urllib2.Request(requrl)
			req.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 Firefox/32.0 Iceweasel/31.8.0')

			if self.UseProxyIP:
				#req.set_proxy(self.ProxyIPPool[self.ProxyIPPos],'http')
				proxy_set = {'http': self.ProxyIPPool[self.ProxyIPPos][0]}
				proxy_support = urllib2.ProxyHandler(proxy_set)
				opener = urllib2.build_opener(proxy_support)
				urllib2.install_opener(opener)
			else:
				print 'Warning!!!,not use proxy ip'
				self.ChangeProxyIP()
				urllib2.install_opener(None)


			rsp = None
			try:
				rsp = urllib2.urlopen(req, timeout=5)
			except BaseException,e:
				# this Proxy IP is unuseable,change it
				print e,'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
				return -1

			try:
				soup = BeautifulSoup(rsp, 'lxml')
				trs = soup.find('table', {'id': 'ip_list'}).findAll('tr')
				for tr in trs[1:]:
					tds = tr.findAll('td')
					if None == NewLastTime:
						NewLastTime = tds[9].text.strip()
					if LastTime <= xicidaili_TimeToINT(tds[9].text.strip()):
						self.InsertIP(tds[1].text.strip(), int(tds[2].text.strip()), tds[5].text.strip())
					else:
						print 'Capture Over,New LastTime',NewLastTime
						return NewLastTime
			except Exception,e:
				print e
				print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
				return -1
			except:
				print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
				return -1
			return 0

		urlarr = ('nn','nt','wn','wt')
		for url in urlarr:
			# check if we was first capture
			try:
				Url = 'http://www.xicidaili.com/' + url
				if 0 == self.dbcursor.execute('select * from LastCaptureTime where '
												'Domain = %s',(Url,)):
					# yes,it first run
					# get total page
					LastTime = '00-00-00 00:00'
					TotalPage = None
					req = urllib2.Request(Url)
					req.add_header('User-Agent',
									'Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0')
					try:
						soup = BeautifulSoup(urllib2.urlopen(req, timeout=5), 'lxml')
						trs = soup.find('div', {'class': 'pagination'}).findAll('a')
						if len(trs) < 3:
							return -1
						TotalPage = trs[-2].text.strip()
						trs = soup.find('table', {'id': 'ip_list'}).findAll('tr')
						tr = trs[1]
						tds = tr.findAll('td')
						LastTime = tds[9].text.strip()
					except BaseException,e:
						print e
						return -1
					except:
						print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
						return -1

					try:
						self.dbcursor.execute('insert into LastCaptureTime (Domain,LastTime) values '
											'(%s,%s)',(Url,LastTime))
						self.dbconnect.commit()
					except BaseException,e:
						print e
						return -1

					print 'First time to capture www.xicidaili.com ,tatal page :', TotalPage
					page = 1
					while page <= TotalPage:
						# WARNING!!! IT WILL TASK A LONG LONG TIME
						requrl = Url
						if 1 != page:
							requrl = Url + '/' + str(page)
						if 0 == xicidaili_CaptureIp(requrl,'00-00-00 00:01'):
							print 'xicidaili GetPage', page, 'Success'
							page += 1
						else:
							print 'xicidaili GetPage', page, 'Failure'
							if self.UseProxyIP:
								randip = self.ProxyIPPool[self.ProxyIPPos]
								#print 'ProxyIP unuse', randip[0], randip[1]
								self.RemoveUnuseProxyIP(randip[0], randip[1])
								del self.ProxyIPPool[self.ProxyIPPos]
								self.ChangeProxyIP()
							else:
								raise ValueError('Expect when not use proxy ip')
						if 0 == self.UseProxyIP:
							self.ChangeProxyIP()

					print 'OK,first time run over'
					return
				else:
					lasttime = self.dbcursor.fetchall()
					print lasttime
					print 'else'

			except Exception as e:
				print e
				return -1
			except:
				print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
				return -1


if '__main__' == __name__:
	getproxyop = GetProxyIP()
	getproxyop.ChangeProxyIP()
	getproxyop.GetProxyIP_xicidaili()
	getproxyop.Close()
