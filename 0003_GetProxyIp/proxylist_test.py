
import requests
import sys
from bs4 import BeautifulSoup

class Text:
    def __init__(self):
        pass
    def GetProxyIP_proxylist(self):
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
            except BaseException,e:
                print e,'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
                str = None
            finally:
                return str

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.7.1'}
            Url = 'http://www.proxylist.ro'
            req = requests.get(url=Url, headers=headers)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, 'lxml')
            trs = soup.find('table', border='1', cellspacing='0', cellpadding='0').findAll('tr')
            for tr in trs[1:]:
                tds = tr.findAll('td')
                ipport = proxylist_ParseFunctionZ2Str(tds[1].text.strip())+':'+proxylist_ParseFunctionZ2Str(tds[2].text.strip())
                type = 'HTTP' if 'N' == tds[4].text.strip() else 'HTTPS'
                print ipport,type
        except Exception, e:
            print e
            return -1
        except:
            print 'Expection @ ', sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno
            return -1

if '__main__' == __name__:
    t = Text()
    t.GetProxyIP_proxylist()