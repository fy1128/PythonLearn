#!/usr/bin/env python

import urllib2
from bs4 import BeautifulSoup
import MySQLdb

def MySQL_Init():
	

def GetProxyIP_xicidaili(page):
	if 1 == page:
		req = urllib2.Request('http://www.xicidaili.com/nn')
	else:
		req = urllib2.Request('http://www.xicidaili.com/nn/' + str(page))
		
	req.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0')
	rsp = urllib2.urlopen(req)
	soup = BeautifulSoup(rsp,'lxml')
	trs = soup.find('table',{'id':'ip_list'}).findAll('tr')
	for tr in trs[1:]:
		tds = tr.findAll('td')
		print tds[1].text.strip(),tds[2].text.strip(),tds[5].text.strip()
	
if '__main__' == __name__:
	GetProxyIP_xicidaili(1)