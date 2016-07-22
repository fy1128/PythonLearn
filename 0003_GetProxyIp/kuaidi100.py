
import requests
from bs4 import BeautifulSoup
import json
import sys
import time

class KuaiDi100:
	def __init__(self):
		pass

	def SearchKuaiDi(self,Type,DanHao,ProxyEnable = 0):
		Url = 'http://www.kuaidi100.com/query?type=' + Type + '&postid=' + str(DanHao)\
		      + '&id=1&valicode=&temp=0.9689380031843594'
		jr = None
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
			jr = json.loads(req.text)
			print jr['message']
			print jr['data']
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
			if None == jr:
				if ProxyEnable:
					if self.UseProxyIP:
						randip = self.ProxyIPPool[self.ProxyIPPos]
						# print 'ProxyIP unuse', randip[0], randip[1]
						self.RemoveUnuseProxyIP(randip[0], randip[1])
						del self.ProxyIPPool[self.ProxyIPPos]
					self.ChangeProxyIP()
			return WebErr,jr

if '__main__' == __name__:
	get = KuaiDi100()
	for i in range(405783781466,405783781499):
		get.SearchKuaiDi('zhongtong',i)
		time.sleep(1)